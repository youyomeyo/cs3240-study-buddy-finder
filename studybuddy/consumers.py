import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync

from .models import Message, Room, User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.user_email = self.scope['url_route']['kwargs']['user_email']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        email = data['email']
        room_pk = data['room_pk']

        await self.save_message(email, room_pk, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'email': email,
                'room_pk': room_pk,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        email = event['email']
        room_pk = event['room_pk']
        name = User.objects.get(email=email).name

        print('name', name)

        await self.send(text_data=json.dumps({
            'message': message,
            'email': email,
            'room_pk': room_pk,
            'name': name
        }))

    @sync_to_async
    def save_message(self, email, room_pk, message):
        if User.objects.filter(email=email) and message != "":
            user = User.objects.get(email=email)
            room = Room.objects.get(pk=room_pk)

            Message.objects.create(user=user, room=room, content=message)
