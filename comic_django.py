import asyncio
import json
import websockets

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QThread, Signal, Slot, QObject
from qasync import QEventLoop, asyncSlot
from comic import *


class WebSocketWorker(QObject):
    message_received = Signal(str)

    def __init__(self, uri):
        super().__init__()
        self.uri = uri
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.websocket_handler())

    async def websocket_handler(self):
        async with websockets.connect(self.uri) as websocket:
            self.websocket = websocket
            print("Connected to WebSocket server")
            while True:
                message = await websocket.recv()
                self.message_received.emit(message)

    async def send_message(self, message):
        await self.websocket.send(message)


class ComicTranslateDjango(ComicTranslate):
    def __init__(self, parent=None):
        super(ComicTranslate, self).__init__(parent)
        self.translation_queue = dict()  # {manhwa: {chapter: {'image_set':{}, translated:False}}}

        # WebSocket worker thread
        self.websocket_thread = QThread()
        self.websocket_worker = WebSocketWorker('ws://127.0.0.1:8000/ws/qt/')
        self.websocket_worker.moveToThread(self.websocket_thread)
        self.websocket_worker.message_received.connect(self.receive_message)
        self.websocket_thread.started.connect(self.websocket_worker.run)
        self.websocket_thread.start()

    @Slot(str)
    async def receive_message(self, message):
        data = json.loads(message)
        progress = {
            'current': 0,
            'total': len(data.values())
        }

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

                reply = json.dumps({'slug': manhwa, 'chapter': chapter, 'progress': progress})
                await self.websocket_worker.send_message(reply)

    def closeEvent(self, event):
        self.websocket_thread.quit()
        self.websocket_thread.wait()
        event.accept()


def init_gui():
    import sys
    from PySide6.QtGui import QIcon
    from app.ui.dayu_widgets.qt import application
    from app.translations import ct_translations
    from app import icon_resource
    from PySide6.QtCore import QSettings
    from qasync import QEventLoop

    if sys.platform == "win32":
        import ctypes
        myappid = u'ComicLabs.ComicTranslate'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Set the application icon
    icon = QIcon(":/icons/window_icon.png")  
    app.setWindowIcon(icon)

    settings = QSettings("ComicLabs", "ComicTranslate")
    selected_language = settings.value('language', get_system_language())
    if selected_language != 'English':
        load_translation(app, selected_language)  

    test = ComicTranslateDjango()
    test.show()

    with loop:
        loop.run_forever()

if __name__ == "__main__":
    init_gui()
