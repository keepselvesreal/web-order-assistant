import json
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth.models import AbstractUser


class ChatConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive_json(self, chat_data, **kwargs):
        message = chat_data['message']
        
        self.save_message(message)
        self.send_json(
            {'type': 'assistant-message',
             "message": "하드 코딩 메시지"}
        )
        
    def save_message(self, message):
        print('데이터 저장 완료!')