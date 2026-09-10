import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SellerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']

        if not user.is_authenticated or not user.is_vendor:
            await self.close()
            return

        self.group_name = f'seller_{user.id}'
        await self.accept()
        await self.send(
            text_data=json.dumps({
            'type': 'connection',
            'message': 'websocket connected',
            })
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def order_notification(self, event):
        await self.send(
            text_data=json.dumps(event['data'])
        )