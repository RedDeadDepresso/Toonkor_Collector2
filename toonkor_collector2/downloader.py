import asyncio
import json
import threading
import multiprocessing

from collections import deque
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from toonkor_collector2.api import update_cached_chapter
from toonkor_collector2.models import Manhwa, Chapter, StatusChoices
from toonkor_collector2.toonkor_api import toonkor_api


class Downloader:
    def __init__(self):
        self._queue = deque()
        self._thread = None
        self._channel_layer = get_channel_layer()
        self._comic_proc = None

    def append(self, manhwa_id, group_name, task, chapters):
        """Add a new download task to the queue and start the worker thread if necessary."""
        self._queue.append([manhwa_id, group_name, task, chapters])

        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run_loop)
            self._thread.daemon = True
            self._thread.start()

    def _run_comic(self):
        from comic_django import run_comic_translate
        if self._comic_proc is None or not self._comic_proc.is_alive():
            ready_event = multiprocessing.Event()
            self._comic_proc = multiprocessing.Process(target=run_comic_translate, args=(ready_event,))
            self._comic_proc.daemon = True
            self._comic_proc.start()
            ready_event.wait()

    def _run_loop(self):
        """Worker loop that processes tasks from the queue."""
        while self._queue:
            try:
                # Get the next task from the queue
                manhwa_id, group_name, task, chapters = self._queue.popleft()
                asyncio.run(self._download_chapters(manhwa_id, group_name, task, chapters))

            except Exception as e:
                print(f"Error processing task: {e}")

    async def _download_chapters(self, manhwa_id, group_name, task, chapters):
        """Download chapters and update progress in real-time."""
        new_status = 'Downloaded' if task == 'download' else 'Translating'
        progress = {"current": 0, "total": len(chapters)}

        try:
            for chapter in chapters:
                chapter_index: int = chapter['index']
                download_dict: dict = {manhwa_id: {chapter_index: {}}}
                page_paths: list[str] = await asyncio.to_thread(toonkor_api.download_chapter, manhwa_id, chapter)

                if page_paths:
                    progress["current"] += 1

                    chapter_obj, _ = await sync_to_async(Chapter.objects.get_or_create)(
                        manhwa_id=manhwa_id,
                        index=chapter['index'],
                        toonkor_id=chapter['toonkor_id'],
                        date_upload=chapter['date_upload']
                    )
                    if not chapter_obj.status == StatusChoices.TRANSLATED:
                        chapter_obj.status = StatusChoices.DOWNLOADED
                    await sync_to_async(chapter_obj.save)()

                    chapter['status'] = new_status
                    update_cached_chapter(manhwa_id, chapter['index'], new_status)

                    # Send progress update
                    await self._send_progress(group_name, [chapter], progress)
                    download_dict[manhwa_id][chapter_index] = {"page_paths": page_paths}
                    if task == 'download_translate':
                        self._run_comic()
                        await self._send_translation_request(download_dict)

                else:
                    await self._send_error(group_name, f"Failed to download chapter {chapter['index'] + 1} of {manhwa_id}")

        except Exception as e:
            await self._send_error(group_name, str(e))
            raise e

    async def _send_progress(self, group_name, chapters, progress):
        """Send progress updates to the WebSocket group."""
        await self._channel_layer.group_send(
            group_name,
            {
                "type": "send_progress",
                "chapters": chapters,
                "progress": progress,
            }
        )

    async def _send_error(self, group_name, error_message):
        """Send an error message to the WebSocket group."""
        await self._channel_layer.group_send(
            group_name,
            {
                "type": "send_progress",
                "error": error_message,
            }
        )

    async def _send_translation_request(self, download_dict):
        """Send translation request to the 'qt' group."""
        await self._channel_layer.group_send(
            "qt",
            {
                "type": "send_translation_request",
                "to_translate": download_dict,
            }
        )


downloader = Downloader()
