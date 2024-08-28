import json

from comic import *
from pipeline import *
from PySide6.QtCore import QUrl
from PySide6.QtWebSockets import QWebSocket
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


class ManhwaFileHandler(FileHandler):
    def sanitize_and_copy_files(self, file_paths):
        return file_paths


class ManhwaPipeline(ComicTranslatePipeline):
    def skip_save(self, directory, timestamp, base_name, extension, archive_bname, image):
        path = os.path.join(directory, "translated", archive_bname)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        image_save = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2.imwrite(os.path.join(path, f"{base_name}{extension}"), image_save)

    def log_skipped_image(self, directory, timestamp, image_path):
        with open(os.path.join(directory, f"translated", "skipped_images.txt"), 'a', encoding='UTF-8') as file:
            file.write(image_path + "\n")
            
    def batch_process(self):
        timestamp = datetime.now().strftime("%b-%d-%Y_%I-%M-%S%p")
        total_images = len(self.main_page.image_files)

        for index, image_path in enumerate(self.main_page.image_files):

            # index, step, total_steps, change_name
            self.main_page.progress_update.emit(index, total_images, 0, 10, True)

            settings_page = self.main_page.settings_page
            source_lang = self.main_page.image_states[image_path]['source_lang']
            target_lang = self.main_page.image_states[image_path]['target_lang']

            target_lang_en = self.main_page.lang_mapping.get(target_lang, None)
            trg_lng_cd = get_language_code(target_lang_en)
            
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            extension = os.path.splitext(image_path)[1]
            directory = os.path.dirname(image_path)

            archive_bname = ""
            for archive in self.main_page.file_handler.archive_info:
                images = archive['extracted_images']
                archive_path = archive['archive_path']

                for img_pth in images:
                    if img_pth == image_path:
                        directory = os.path.dirname(archive_path)
                        archive_bname = os.path.splitext(os.path.basename(archive_path))[0]

            image = cv2.imread(image_path)

            # Text Block Detection
            self.main_page.progress_update.emit(index, total_images, 1, 10, False)
            if self.main_page.current_worker and self.main_page.current_worker.is_cancelled:
                self.main_page.current_worker = None
                break

            if self.block_detector_cache is None:
                bdetect_device = 0 if self.main_page.settings_page.is_gpu_enabled() else 'cpu'
                self.block_detector_cache = TextBlockDetector('models/detection/comic-speech-bubble-detector.pt', 
                                                            'models/detection/comic-text-segmenter.pt', 'models/detection/manga-text-detector.pt', 
                                                            bdetect_device)
            
            blk_list = self.block_detector_cache.detect(image)

            self.main_page.progress_update.emit(index, total_images, 2, 10, False)
            if self.main_page.current_worker and self.main_page.current_worker.is_cancelled:
                self.main_page.current_worker = None
                break

            if blk_list:
                self.ocr.initialize(self.main_page, source_lang)
                try:
                    self.ocr.process(image, blk_list)
                except Exception as e:
                    error_message = str(e)
                    print(error_message)
                    self.skip_save(directory, timestamp, base_name, extension, archive_bname, image)
                    self.main_page.image_skipped.emit(image_path, "OCR", error_message)
                    self.log_skipped_image(directory, timestamp, image_path)
                    continue
            else:
                self.skip_save(directory, timestamp, base_name, extension, archive_bname, image)
                # self.main_page.image_skipped.emit(image_path, "Text Blocks", "")
                self.log_skipped_image(directory, timestamp, image_path)
                continue

            self.main_page.progress_update.emit(index, total_images, 3, 10, False)
            if self.main_page.current_worker and self.main_page.current_worker.is_cancelled:
                self.main_page.current_worker = None
                break

            # Clean Image of text
            export_settings = settings_page.get_export_settings()

            if self.inpainter_cache is None or self.cached_inpainter_key != settings_page.get_tool_selection('inpainter'):
                device = 'cuda' if settings_page.is_gpu_enabled() else 'cpu'
                inpainter_key = settings_page.get_tool_selection('inpainter')
                InpainterClass = inpaint_map[inpainter_key]
                self.inpainter_cache = InpainterClass(device)
                self.cached_inpainter_key = inpainter_key

            config = get_config(settings_page)
            mask = generate_mask(image, blk_list)

            self.main_page.progress_update.emit(index, total_images, 4, 10, False)
            if self.main_page.current_worker and self.main_page.current_worker.is_cancelled:
                self.main_page.current_worker = None
                break

            inpaint_input_img = self.inpainter_cache(image, mask, config)
            inpaint_input_img = cv2.convertScaleAbs(inpaint_input_img) 
            inpaint_input_img = cv2.cvtColor(inpaint_input_img, cv2.COLOR_BGR2RGB)

            if export_settings['export_inpainted_image']:
                path = os.path.join(directory, f"comic_translate_{timestamp}", "cleaned_images", archive_bname)
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                cv2.imwrite(os.path.join(path, f"{base_name}_cleaned{extension}"), inpaint_input_img)

            self.main_page.progress_update.emit(index, total_images, 5, 10, False)
            if self.main_page.current_worker and self.main_page.current_worker.is_cancelled:
                self.main_page.current_worker = None
                break

            # Get Translations/ Export if selected
            extra_context = settings_page.get_llm_settings()['extra_context']
            translator = Translator(self.main_page, source_lang, target_lang)
            try:
                translator.translate(blk_list, image, extra_context)
            except Exception as e:
                error_message = str(e)
                print(error_message)
                self.skip_save(directory, timestamp, base_name, extension, archive_bname, image)
                self.main_page.image_skipped.emit(image_path, "Translator", error_message)
                self.log_skipped_image(directory, timestamp, image_path)
                continue

            entire_raw_text = get_raw_text(blk_list)
            entire_translated_text = get_raw_translation(blk_list)

            if (not entire_raw_text) or (not entire_translated_text):
                self.skip_save(directory, timestamp, base_name, extension, archive_bname, image)
                self.main_page.image_skipped.emit(image_path, "Translator", "")
                self.log_skipped_image(directory, timestamp, image_path)
                continue

            if export_settings['export_raw_text']:
                path = os.path.join(directory, f"comic_translate_{timestamp}", "raw_texts", archive_bname)
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                file = open(os.path.join(path, os.path.splitext(os.path.basename(image_path))[0] + "_raw.txt"), 'w', encoding='UTF-8')
                file.write(entire_raw_text)

            if export_settings['export_translated_text']:
                path = os.path.join(directory, f"comic_translate_{timestamp}", "translated_texts", archive_bname)
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                file = open(os.path.join(path, os.path.splitext(os.path.basename(image_path))[0] + "_translated.txt"), 'w', encoding='UTF-8')
                file.write(entire_translated_text)

            self.main_page.progress_update.emit(index, total_images, 7, 10, False)
            if self.main_page.current_worker and self.main_page.current_worker.is_cancelled:
                self.main_page.current_worker = None
                break

            # Text Rendering
            text_rendering_settings = settings_page.get_text_rendering_settings()
            upper_case = text_rendering_settings['upper_case']
            outline = text_rendering_settings['outline']
            format_translations(blk_list, trg_lng_cd, upper_case=upper_case)
            get_best_render_area(blk_list, image, inpaint_input_img)

            font = text_rendering_settings['font']
            font_color = text_rendering_settings['color']
            font_path = f'fonts/{font}'
            set_alignment(blk_list, settings_page)

            max_font_size = self.main_page.settings_page.get_max_font_size()
            min_font_size = self.main_page.settings_page.get_min_font_size()

            rendered_image = draw_text(inpaint_input_img, blk_list, font_path, colour=font_color, init_font_size=max_font_size, min_font_size=min_font_size, outline=outline)

            self.main_page.progress_update.emit(index, total_images, 9, 10, False)
            if self.main_page.current_worker and self.main_page.current_worker.is_cancelled:
                self.main_page.current_worker = None
                break

            # Display or set the rendered Image on the viewer once it's done
            self.main_page.image_processed.emit(index, rendered_image, image_path)
            
            render_save_dir = os.path.join(directory, f"translated", archive_bname)
            if not os.path.exists(render_save_dir):
                os.makedirs(render_save_dir, exist_ok=True)
            rendered_image_save = cv2.cvtColor(rendered_image, cv2.COLOR_BGR2RGB)
            cv2.imwrite(os.path.join(render_save_dir, f"{base_name}{extension}"), rendered_image_save)

            self.main_page.progress_update.emit(index, total_images, 10, 10, False)

        archive_info_list = self.main_page.file_handler.archive_info
        if archive_info_list:
            save_as_settings = settings_page.get_export_settings()['save_as']
            for archive_index, archive in enumerate(archive_info_list):
                archive_index_input = total_images + archive_index

                self.main_page.progress_update.emit(archive_index_input, total_images, 1, 3, True)
                if self.main_page.current_worker and self.main_page.current_worker.is_cancelled:
                    self.main_page.current_worker = None
                    break

                archive_path = archive['archive_path']
                archive_ext = os.path.splitext(archive_path)[1]
                archive_bname = os.path.splitext(os.path.basename(archive_path))[0]
                archive_directory = os.path.dirname(archive_path)
                save_as_ext = f".{save_as_settings[archive_ext.lower()]}"

                save_dir = os.path.join(archive_directory, f"comic_translate_{timestamp}", "translated_images", archive_bname)
                check_from = os.path.join(archive_directory, f"comic_translate_{timestamp}")

                self.main_page.progress_update.emit(archive_index_input, total_images, 2, 3, True)
                if self.main_page.current_worker and self.main_page.current_worker.is_cancelled:
                    self.main_page.current_worker = None
                    break

                # Create the new archive
                output_base_name = f"{archive_bname}"
                target_lang = self.main_page.image_states[archive['extracted_images'][0]]['target_lang']
                target_lang_en = self.main_page.lang_mapping.get(target_lang, target_lang)
                trg_lng_code = get_language_code(target_lang_en)
                make(save_as_ext=save_as_ext, input_dir=save_dir, 
                    output_dir=archive_directory, output_base_name=output_base_name, 
                    trg_lng=trg_lng_code)

                self.main_page.progress_update.emit(archive_index_input, total_images, 3, 3, True)
                if self.main_page.current_worker and self.main_page.current_worker.is_cancelled:
                    self.main_page.current_worker = None
                    break

                # Clean up temporary directories
                shutil.rmtree(save_dir)
                shutil.rmtree(archive['temp_dir'])

                if is_directory_empty(check_from):
                    shutil.rmtree(check_from)


class ComicTranslateDjango(ComicTranslate):
    def __init__(self, parent=None):
        super(ComicTranslateDjango, self).__init__(parent)
        self.file_handler = ManhwaFileHandler()
        self.pipeline = ManhwaPipeline(self)
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
        self.connect_to_server()
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