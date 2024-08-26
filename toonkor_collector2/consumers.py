import asyncio
import base64
import comic_django
import json
import multiprocessing

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from toonkor_collector2.models import Manhwa, Chapter
from toonkor_collector2.toonkor_api import toonkor_api


def encode_name(name):
    return base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")

def decode_name(encoded_name):
    padded_encoded_name = encoded_name + "=" * (4 - len(encoded_name) % 4)
    return base64.urlsafe_b64decode(padded_encoded_name).decode()

class QtConsumer(AsyncWebsocketConsumer):
    """
    QtConsumer is an AsyncWebsocketConsumer responsible for managing a WebSocket
    connection that handles the translation process. It interacts with the comic_django 
    GUI and listens for translation requests.

    Attributes:
        COMIC_TRANSLATE_PROC (multiprocessing.Process): A process to run the comic_django GUI.
    """
    COMIC_TRANSLATE_PROC: multiprocessing.Process = None

    def start_proc(self):
        """
        Starts the comic_django GUI in a separate process if it is not already running.
        The process is set as a daemon to terminate with the main program.
        """
        if self.COMIC_TRANSLATE_PROC is None:
            self.COMIC_TRANSLATE_PROC = multiprocessing.Process(target=comic_django.init_gui)
            self.COMIC_TRANSLATE_PROC.daemon = True
            self.COMIC_TRANSLATE_PROC.start()

    async def connect(self):
        """
        Handles a new WebSocket connection. Adds the connection to the 'qt' group
        and starts the comic_django GUI process. Accepts the WebSocket connection.
        """
        self.group_name = 'qt'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await sync_to_async(self.start_proc)()
        await self.accept()

    async def send_translation_request(self, event):
        """
        Sends a translation request event to the WebSocket client.

        Args:
            event (dict): The event data containing the text_data to be sent.
        """
        to_translate = event['to_translate']
        await self.send(to_translate)

    async def receive(self, text_data):
        """
        Receives data from the WebSocket client, processes the translation request,
        updates the chapter status in the database, and triggers the download/translate process.

        Args:
            text_data (str): JSON string containing the manhwa slug and chapter index.
        """
        data = json.loads(text_data)
        manhwa_slug = data['slug']
        chapter = data['chapter']

        manhwa_obj = await sync_to_async(Manhwa.objects.get)(slug=manhwa_slug)
        chapter_obj = await sync_to_async(Chapter.objects.get)(manhwa=manhwa_obj, index=chapter)
        chapter_obj.translated = True
        await sync_to_async(chapter_obj.save)()

        await self.channel_layer.group_send(
            f'download_translate_{encode_name(manhwa_slug)}',
            {
                'type': 'send_progress',
                'event': data
            }
        )

    async def send_progress(self, event):
        """
        Sends progress updates to the WebSocket client.

        Args:
            event (dict): The event data containing progress information.
        """
        await self.send(text_data=json.dumps(event['event']))

    async def disconnect(self, close_code):
        """
        Handles the disconnection of the WebSocket client by removing it from the 'qt' group.

        Args:
            close_code (int): The WebSocket close code.
        """
        await self.channel_layer.group_discard(self.group_name, self.channel_name)


class DownloadTranslateConsumer(AsyncWebsocketConsumer):
    """
    DownloadTranslateConsumer is an AsyncWebsocketConsumer responsible for managing
    the download and translation tasks. It listens for download/translate requests,
    manages the downloading of chapters, and communicates progress back to the client.

    Attributes:
        group_name (str): The name of the channel group for managing download and translation tasks.
    """

    async def connect(self):
        """
        Handles a new WebSocket connection. Adds the connection to the 'download_translate' group
        and accepts the WebSocket connection.
        """
        self.manhwa_name = self.scope['url_route']['kwargs']['manhwa_slug']
        self.group_name = f'download_translate_{encode_name(self.manhwa_name)}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        """
        Receives data from the WebSocket client, starts the download process for the specified chapters,
        and optionally triggers the translation process.

        Args:
            text_data (str): JSON string containing the task, manhwa slug, and chapters to download.
        """
        data = json.loads(text_data)
        task = data['task']
        manhwa_slug = data['slug']
        chapters = data['chapters']

        # Start the download process
        download_dict = await self.download_chapters(manhwa_slug, chapters)

        if task == 'download_translate':
            await self.channel_layer.group_send(
                'qt',
                {
                    'type': 'send_translation_request',
                    'to_translate': download_dict
                }
            )

    async def download_chapters(self, manhwa_slug, chapters):
        """
        Downloads the specified chapters of a manhwa, updates progress, and stores the paths
        to the downloaded images.

        Args:
            manhwa_slug (str): The slug of the manhwa to download.
            chapters (list): A list of chapter indices to download.
            progress (dict): A dictionary to track the download progress.

        Returns:
            dict: A dictionary containing the paths to the downloaded images for each chapter.
        """
        download_dict = {}
        progress = {
            'current': 0,
            'total': len(chapters)
        }

        try:
            manhwa_obj = await sync_to_async(Manhwa.objects.get)(slug=manhwa_slug)
            for chapter in chapters:
                pages_path = await asyncio.to_thread(toonkor_api.download_chapter, manhwa_slug, chapter)
                if pages_path is not None:
                    progress['current'] += 1
                    chapter_obj, created = await sync_to_async(Chapter.objects.get_or_create)(
                        manhwa=manhwa_obj,
                        index=chapter
                    )

                    # Send progress to WebSocket client
                    await self.send_progress({
                        'task': 'download',
                        'current_chapter': chapter,
                        'progress': progress
                    })

                    # Initialize nested dictionary if not already done
                    if manhwa_slug not in download_dict:
                        download_dict[manhwa_slug] = {}
                    if chapter not in download_dict[manhwa_slug]:
                        download_dict[manhwa_slug][chapter] = {}
                        
                    download_dict[manhwa_slug][chapter]['images_set'] = pages_path

        except Exception as e:
            # Handle exceptions and maybe log them
            await self.send(text_data=json.dumps({'error': str(e)}))
        return download_dict

    async def send_progress(self, event):
        """
        Sends progress updates to the WebSocket client.

        Args:
            event (dict): The event data containing progress information.
        """
        await self.send(text_data=json.dumps(event))

    async def disconnect(self, close_code):
        """
        Handles the disconnection of the WebSocket client by removing it from the 'download_translate' group.

        Args:
            close_code (int): The WebSocket close code.
        """
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
