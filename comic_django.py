import asyncio
import json
import websockets

from comic import *


class ComicTranslateDjango(ComicTranslate):
    def __init__(self, parent=None):
        super().__init__(self, parent)
        self.threadpool.submit(self.start_websocket_server)
        self.translation_queue = dict() # {manhwa: {chapter: {'image_set':{}, tranlated:False}}}

    def parse_message(self, message):
        try:
            data = json.loads(message)
            if len(data) == 0:
                return None
            
            for chapter in data.values():
                if not chapter.is_digit():
                    return None
                
                image_set = chapter.get('images_set')
                if image_set is None:
                    return None
                chapter['images_set'] = set(image_set)

                for path in image_set:
                    if not os.path.exists(path):
                        return None
                    
            return data
                        
        except json.JSONDecodeError:
            print("Failed to decode JSON")
            return None

    async def connect_to_server(self):
        self.websocket = await websockets.connect('ws://localhost:8765')
        print("Connected to WebSocket server")

    def receive_message(self, message):
        data = self.parse_message(message)
        for manhwa, chapters in data.items():
            images_set = chapters['images_set']
            
            for chapter in chapters:
                manhwa_dict = self.translation_queue.setdefault(manhwa, {})
                chapter_dict = manhwa_dict.setdefault(chapter, {'images_set': set(), 'translated': False})
                chapter_dict['images_set'].update(images_set)

                if not chapter_dict['translated']:
                    self.thread_load_images(images_set)
                    self.batch_mode_selected()
                    self.start_batch_process()
                    chapter_dict['translated'] = True

                reply = json.dumps({manhwa: chapter})
                self.send_message(reply)

    async def send_message(self, message):
        await self.websocket.send(message)
        response = await self.websocket.recv()
        print(f"Received response from server: {response}")
    
    def process_events(self):
        self.loop.stop()
        self.loop.run_forever()
        
def init_gui():
    import sys
    from PySide6.QtGui import QIcon
    from app.ui.dayu_widgets.qt import application
    from app.translations import ct_translations
    from app import icon_resource

    if sys.platform == "win32":
        # Necessary Workaround to set to Taskbar Icon on Windows
        import ctypes
        myappid = u'ComicLabs.ComicTranslate' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    with application() as app:
        # Set the application icon
        icon = QIcon(":/icons/window_icon.png")  
        app.setWindowIcon(icon)

        settings = QSettings("ComicLabs", "ComicTranslate")
        selected_language = settings.value('language', get_system_language())
        if selected_language != 'English':
            load_translation(app, selected_language)  

        test = ComicTranslate()
        test.show()
