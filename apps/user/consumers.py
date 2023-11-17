import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Chat


class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        # Leave room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.room_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        sender = data['sender']
        receiver = data['receiver']
        message = data['message']
        type_message = data['type']
        if type_message == 'message':
            await self.create_message(receiver=receiver, sender=sender, message=message)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': event['type']
        }))

    @sync_to_async
    def create_message(self, sender, receiver, message):
        message = Chat.objects.create(message=message, sender=sender, receiver=receiver)
        return message
