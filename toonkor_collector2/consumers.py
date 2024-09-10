import asyncio
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from toonkor_collector2.models import Manhwa, Chapter, StatusChoices
from toonkor_collector2.toonkor_api import toonkor_api
from toonkor_collector2.api import update_cache_chapters


class QtConsumer(AsyncWebsocketConsumer):
    """
    QtConsumer is an AsyncWebsocketConsumer responsible for managing a WebSocket
    connection that handles the translation process. It interacts with the comic_django
    GUI and listens for translation requests.

    Attributes:
        COMIC_TRANSLATE_PROC (multiprocessing.Process): A process to run the comic_django GUI.
    """

    async def connect(self):
        """
        Handles a new WebSocket connection. Adds the connection to the 'qt' group
        and starts the comic_django GUI process. Accepts the WebSocket connection.
        """
        self.group_name = "qt"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def send_translation_request(self, event):
        """
        Sends a translation request event to the WebSocket client.

        Args:
            event (dict): The event data containing the text_data to be sent.
        """
        to_translate = event["to_translate"]
        await self.send(json.dumps(to_translate))

    async def receive(self, text_data):
        """
        Receives data from the WebSocket client, processes the translation request,
        updates the chapter status in the database, and triggers the download/translate process.

        Args:
            text_data (str): JSON string containing the manhwa toonkor_id and chapter index.
        """
        data = json.loads(text_data)
        toonkor_id = data["toonkor_id"]
        chapter = data["chapter"]

        manhwa_obj = await sync_to_async(Manhwa.objects.get)(toonkor_id=toonkor_id)
        chapter_obj = await sync_to_async(Chapter.objects.get)(
            manhwa=manhwa_obj, index=chapter
        )
        chapter_obj.status = StatusChoices.TRANSLATED
        await sync_to_async(chapter_obj.save)()
        update_cache_chapters(toonkor_id, [chapter], 'Translated')

        await self.channel_layer.group_send(
            f"download_translate_{toonkor_api.encode_name(toonkor_id)}",
            {
                "type": "send_progress",
                "task": data["task"],
                "progress": data["progress"],
            },
        )

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
        self.manhwa_name = self.scope["url_route"]["kwargs"]["toonkor_id"]
        self.group_name = (
            f"download_translate_{toonkor_api.encode_name(self.manhwa_name)}"
        )
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        """
        Receives data from the WebSocket client, starts the download process for the specified chapters,
        and optionally triggers the translation process.

        Args:
            text_data (str): JSON string containing the task, manhwa toonkor_id, and chapters to download.
        """
        data = json.loads(text_data)
        task = data["task"]
        toonkor_id = data["toonkor_id"]
        chapters = data["chapters"]
                            
        # Start the download process
        download_dict = await self.download_chapters(toonkor_id, chapters)

        if task == "download_translate":
            update_cache_chapters(toonkor_id, chapters, 'Translating')
            await self.channel_layer.group_send(
                "qt",
                {"type": "send_translation_request", "to_translate": download_dict},
            )

    async def download_chapters(self, toonkor_id, chapters):
        """
        Downloads the specified chapters of a manhwa, updates progress, and stores the paths
        to the downloaded images.

        Args:
            toonkor_id (str): The toonkor_id of the manhwa to download.
            chapters (list): A list of chapter indices to download.
            progress (dict): A dictionary to track the download progress.

        Returns:
            dict: A dictionary containing the paths to the downloaded images for each chapter.
        """
        download_dict = {}
        progress = {"current": 0, "total": len(chapters)}
        update_cache_chapters(toonkor_id, chapters, 'Downloading')

        try:
            manhwa_obj = await sync_to_async(Manhwa.objects.get)(toonkor_id=toonkor_id)
            for chapter in chapters:
                pages_path = await asyncio.to_thread(
                    toonkor_api.download_chapter, manhwa_obj, chapter
                )
                if pages_path is not None:
                    progress["current"] += 1
                    chapter_obj, created = await sync_to_async(
                        Chapter.objects.get_or_create
                    )(manhwa=manhwa_obj, index=chapter, status=StatusChoices.DOWNLOADED)

                    # Send progress to WebSocket client
                    await self.send_progress(
                        {
                            "task": "download",
                            "current_chapter": chapter,
                            "progress": progress,
                        }
                    )

                    # Initialize nested dictionary if not already done
                    if toonkor_id not in download_dict:
                        download_dict[toonkor_id] = {}
                    if chapter not in download_dict[toonkor_id]:
                        download_dict[toonkor_id][chapter] = {}

                    download_dict[toonkor_id][chapter]["images_set"] = pages_path
            update_cache_chapters(toonkor_id, chapters, 'Downloaded')

        except Exception as e:
            # Handle exceptions and maybe log them
            await self.send(text_data=json.dumps({"error": str(e)}))
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
