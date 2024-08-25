import asyncio
import comic_django
import json
import multiprocessing

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from toonkor_collector2.models import Manhwa, Chapter
from toonkor_collector2.toonkor_api import toonkor_api


class DownloadConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'download'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        manhwa_slug = data['slug']
        chapters = data['chapters']

        progress = {
            'current': 0,
            'total': len(chapters)
        }

        # Start the download process
        await self.download_chapters(manhwa_slug, chapters, progress)

    async def download_chapters(self, manhwa_slug, chapters, progress):
        manhwa_obj = await sync_to_async(Manhwa.objects.get)(slug=manhwa_slug)
        for chapter in chapters:
            result = await asyncio.to_thread(toonkor_api.download_chapter, manhwa_slug, chapter)
            if result:
                progress['current'] += 1
                chapter_obj, created = await sync_to_async(Chapter.objects.get_or_create)(
                    manhwa=manhwa_obj,
                    index=chapter
                )
                # Send progress to WebSocket client
                await self.send_progress({
                    'type': 'send_progress',
                    'current_chapter': chapter,
                    'progress': progress
                })

    async def send_progress(self, event):
        await self.send(text_data=json.dumps(event['progress']))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)


class TranslateConsumer(AsyncWebsocketConsumer):
    COMIC_TRANSLATE_PROC: multiprocessing.Process = None

    def start_proc(self):
        if self.COMIC_TRANSLATE_PROC is None:
            self.COMIC_TRANSLATE_PROC = multiprocessing.Process(target=comic_django.init_gui)
            self.COMIC_TRANSLATE_PROC.daemon = True
            self.COMIC_TRANSLATE_PROC.start()

    async def connect(self):
        self.start_proc()
        self.group_name = 'translate'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def send_progress(self, event):
        await self.send(text_data=json.dumps(event["translate"]))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
