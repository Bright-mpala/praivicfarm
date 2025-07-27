import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'orders'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Optional: for testing receiving from frontend
        await self.send(text_data=json.dumps({
            'message': text_data
        }))

    async def send_order_update(self, event):
        await self.send(text_data=json.dumps(event['content']))
