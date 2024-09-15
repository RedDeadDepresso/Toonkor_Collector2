import asyncio
import json
import threading
from collections import deque
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from toonkor_collector2.api import update_cached_chapter
from toonkor_collector2.models import Manhwa, Chapter, StatusChoices
from toonkor_collector2.toonkor_api import toonkor_api


class Downloader:
    def __init__(self):
        self.queue = deque()
        self.thread = None
        self.channel_layer = get_channel_layer()

    def append(self, manhwa_id, group_name, text_data):
        """Add a new download task to the queue and start the worker thread if necessary."""
        self.queue.append([manhwa_id, group_name, text_data])

        # Start the worker thread if not already running
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._run_loop)
            self.thread.daemon = True  # Ensure the thread terminates with the program
            self.thread.start()

    def _run_loop(self):
        """Worker loop that processes tasks from the queue."""
        while self.queue:
            try:
                # Get the next task from the queue
                manhwa_id, group_name, text_data = self.queue.popleft()
                data = json.loads(text_data)
                task = data["task"]
                chapters = data["chapters"]

                # Run the asynchronous download task
                asyncio.run(self._handle_task(manhwa_id, group_name, task, chapters))

            except Exception as e:
                print(f"Error processing task: {e}")

    async def _handle_task(self, manhwa_id, group_name, task, chapters):
        """Handle the task of downloading chapters asynchronously."""
        try:
            download_dict = await self.download_chapters(manhwa_id, group_name, task, chapters)

            # If the task is download + translation, send the translation request
            if task == "download_translate":
                await self._send_translation_request(download_dict)

        except Exception as e:
            await self._send_error(group_name, str(e))

    async def download_chapters(self, manhwa_id, group_name, task, chapters):
        """Download chapters and update progress in real-time."""
        download_dict = {}
        new_status = 'Downloaded' if task == 'download' else 'Translating'
        progress = {"current": 0, "total": len(chapters)}

        # Update chapter status to "Downloading"
        for chapter in chapters:
            chapter['status'] = 'Downloading'
            update_cached_chapter(manhwa_id, chapter['index'], 'Downloading')

        await self._send_progress(group_name, chapters, progress)

        try:

            # Process each chapter in the list
            for chapter in chapters:
                pages_path = await asyncio.to_thread(toonkor_api.download_chapter, manhwa_id, chapter)

                if pages_path:
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

                    # Store downloaded chapter information
                    if manhwa_id not in download_dict:
                        download_dict[manhwa_id] = {}
                    download_dict[manhwa_id][chapter['index']] = {"images_set": pages_path}

        except Exception as e:
            await self._send_error(group_name, str(e))
            raise e  # Re-raise exception to handle it in the outer scope

        return download_dict

    async def _send_progress(self, group_name, chapters, progress):
        """Send progress updates to the WebSocket group."""
        await self.channel_layer.group_send(
            group_name,
            {
                "type": "send_progress",
                "chapters": chapters,
                "progress": progress,
            }
        )

    async def _send_error(self, group_name, error_message):
        """Send an error message to the WebSocket group."""
        await self.channel_layer.group_send(
            group_name,
            {
                "type": "send_progress",
                "error": error_message,
            }
        )

    async def _send_translation_request(self, download_dict):
        """Send translation request to the 'qt' group."""
        await self.channel_layer.group_send(
            "qt",
            {
                "type": "send_translation_request",
                "to_translate": download_dict,
            }
        )


# Create a global downloader instance
downloader = Downloader()
