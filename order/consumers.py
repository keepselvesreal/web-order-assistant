import json
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth.models import AbstractUser

from .order_manager import OrderManager


class ChatConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive_json(self, chat_data, **kwargs):
        message = chat_data['message']
        print(message)
        
        self.save_message(message)
        # todo: 모델 답변 생성
        # todo: 일반 문의와 주문 관련 요청 경우로 나눠 처리
        # 주문 관련 요청 경우 dummy data 기반 구현
        ## order_data에 대한 dummy data 생성
        order_data = {
            'user': 'nadle',
            'request_type': 'order_change',
            'products': [
                {'name': '커피', 'price': 1000, 'quantity': 1},
                {'name': '케이크', 'price': 5000, 'quantity': 1},
            ],
            'order_date': '2023-12-15T12:14:38+09:00',
        }
        
        order_manager = OrderManager(order_data)
        response_message = order_manager.process_request()
        self.send_json(
            {'type': 'assistant-message',
             'message': response_message}
            )

            
        # self.send_json(
        #     {'type': 'assistant-message',
        #      "message": "하드 코딩 메시지"}
        # )
        
    def save_message(self, message):
        print('데이터 저장 완료!')