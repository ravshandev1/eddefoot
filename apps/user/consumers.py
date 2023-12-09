import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message


class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = self.scope['url_route']['kwargs']['room_name']

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        type_message = data['type']
        if type_message == 'send':
            sender_id = data['sender']
            receiver_id = data['receiver']
            message = data['message']
            mes = await self.create_message(sender_id, receiver_id, message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': mes
                }
            )
        elif type_message == 'seen':
            for i in data['ids']:
                mes = await self.seen_message(i)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'read_message',
                        'message': mes
                    }
                )

    async def read_message(self, event):
        mes = event['message']
        await self.send(text_data=json.dumps({
            'id': mes['id'],
            'message': mes['message'],
            'sender': mes['sender'],
            'receiver': mes['receiver'],
            'seen': mes['seen'],
            'created_at': mes['created_at'],
            'type': 'read'
        }))

    async def chat_message(self, event):
        mes = event['message']
        await self.send(text_data=json.dumps({
            'id': mes['id'],
            'message': mes['message'],
            'sender': mes['sender'],
            'receiver': mes['receiver'],
            'seen': mes['seen'],
            'created_at': mes['created_at'],
            'type': 'created'
        }))

    @sync_to_async
    def create_message(self, sender_id, receiver_id, message):
        mes = Message.objects.create(message=message, sender_id=sender_id, receiver_id=receiver_id,
                                     room_id=self.room_group_name)
        return {
            'id': mes.id,
            'message': mes.message,
            'sender': mes.sender.name,
            'receiver': mes.receiver.name,
            'seen': mes.seen,
            'created_at': mes.created_at.__format__("%m/%d/%Y, %H:%M")
        }

    @sync_to_async
    def seen_message(self, mes_id):
        mes = Message.objects.filter(id=mes_id).first()
        mes.seen = True
        mes.save()
        return {
            'id': mes.id,
            'message': mes.message,
            'sender': mes.sender.name,
            'receiver': mes.receiver.name,
            'seen': mes.seen,
            'created_at': mes.created_at.__format__("%m/%d/%Y, %H:%M")
        }
