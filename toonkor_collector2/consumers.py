from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'progress_updates'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()  # Notify client connection established

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)  # Handle disconnect

    async def send_progress(self, event):
        await self.send(text_data=json.dumps(event["progress"]))  # Send data to client
