import json

from PySide6.QtCore import QUrl
from PySide6.QtWebSockets import QWebSocket
from comic import *
from typing import Union


class Manhwa:
    def __init__(self, name) -> None:
        self.name: str = name
        self.chapters_dict: dict[str, dict[str, Union[set[str], bool]]] = {}
        self.progress = {'current': 0, 'total': 0}

    @property
    def progress_current(self) -> int:
        return self.progress['current']
    
    @progress_current.setter
    def progress_current(self, value: int):
        self.progress['current'] = value
    
    @property
    def progress_total(self) -> int:
        return self.progress['total']

    @progress_total.setter
    def progress_total(self, value: int):
        self.progress['total'] = value

    def get_images_set(self, chapter: str) -> set[str]:
        info = self.chapters_dict.setdefault(chapter, {'images_set': set(), 'translated': False})
        return info['images_set']

    def is_translated(self, chapter: str) -> bool:
        info = self.chapters_dict.setdefault(chapter, {'images_set': set(), 'translated': False})
        return info['translated']
    
    def get_chapter(self, chapter: str) -> tuple[set[str], bool]:
        info = self.chapters_dict.setdefault(chapter, {'images_set': set(), 'translated': False})
        return info['images_set'], info['translated']

    def update_chapter(self, chapter: str, images_set: set[str] = None, translated: bool = None):
        info = self.chapters_dict.setdefault(chapter, {'images_set': set(), 'translated': False})
        if images_set is not None:
            info['images_set'].update(images_set)
        if translated is not None:
            info['translated'] = translated

    def update_progress(self) -> dict:
        self.progress_current = len([x for x in self.chapters_dict.values() if x['translated']])
        self.progress_total = len(self.chapters_dict)
        return self.progress


class ComicTranslateDjango(ComicTranslate):
    def __init__(self, parent=None):
        super(ComicTranslateDjango, self).__init__(parent)
        self.translation_queue: dict[str, Manhwa] = dict()

        self.websocket = QWebSocket()
        self.websocket.connected.connect(self.on_connected)
        self.websocket.disconnected.connect(self.on_disconnected)
        self.websocket.textMessageReceived.connect(self.receive_message)

        self.connect_to_server()

    def connect_to_server(self):
        self.websocket.open(QUrl('ws://127.0.0.1:8000/ws/qt/'))

    def on_connected(self):
        print("ComicTranslate connected to WebSocket server")

    def on_disconnected(self):
        print("ComicTranslate disconnected from WebSocket server")

    def receive_message(self, message):
        data = json.loads(message)
        for manhwa, chapters in data.items():
            manhwa_instance = self.translation_queue.setdefault(manhwa, Manhwa(manhwa))
            for chapter, details in chapters.items():
                images_set = details['images_set']
                manhwa_instance.update_chapter(chapter, images_set=images_set)
                self.translate_chapter(manhwa_instance, chapter)

    def translate_chapter(self, manhwa_instance, chapter):
        images_set, translated = manhwa_instance.get_chapter(chapter)
        if translated:
            self.send_progress(manhwa_instance, chapter)
        else:
            finished_callback = lambda x=manhwa_instance, y=chapter: self.start_chapter_translate(x, y)
            self.run_threaded(self.load_images_threaded, self.on_images_loaded, self.default_error_handler, finished_callback, images_set)

    def start_chapter_translate(self, manhwa_instance, chapter):
        for image_path in self.image_files:
            source_lang = self.image_states[image_path]['source_lang']
            target_lang = self.image_states[image_path]['target_lang']

            if not validate_settings(self, source_lang, target_lang):
                return
        
        self.batch_mode_selected()
        self.translate_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        finished_callback = lambda x=manhwa_instance, y=chapter: self.on_chapter_translate_finished(x, y)
        self.run_threaded(self.pipeline.batch_process, None, self.default_error_handler, finished_callback)

    def on_chapter_translate_finished(self, manhwa_instance, chapter):
        self.progress_bar.setVisible(False)
        self.translate_button.setEnabled(True)
        self.send_progress(manhwa_instance, chapter)

    def send_progress(self, manhwa_instance, chapter):
        manhwa_instance.update_chapter(chapter, translated=True)
        progress = manhwa_instance.update_progress()
        reply = json.dumps({'task': 'download_translate', 
                            'slug': manhwa_instance.name, 
                            'chapter': chapter, 
                            'progress': progress})
        self.websocket.sendTextMessage(reply)

def run_comic_translate():
    import sys
    from PySide6.QtGui import QIcon
    from app.ui.dayu_widgets.qt import application
    from app.translations import ct_translations
    from app import icon_resource
    from PySide6.QtCore import QSettings

    if sys.platform == "win32":
        # Necessary Workaround to set to Taskbar Icon on Windows
        import ctypes
        myappid = u'ComicLabs.ComicTranslate'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    with application() as app:
        # Set the application icon
        icon = QIcon(":/icons/window_icon.png")
        app.setWindowIcon(icon)

        settings = QSettings("ComicLabs", "ComicTranslate")
        selected_language = settings.value('language', get_system_language())
        if selected_language != 'English':
            load_translation(app, selected_language)

        test = ComicTranslateDjango()
        test.show()


if __name__ == "__main__":
    run_comic_translate()