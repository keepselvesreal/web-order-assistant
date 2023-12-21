import json
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth.models import User

from .order_manager import OrderManager
from .chains import response_chain
from .models import ChatMessage


class ChatConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive_json(self, chat_data, **kwargs):
        user = chat_data["user"]
        user_message = chat_data["message"]
        message_time = chat_data["date"]
        print(user_message)
        print(message_time)
        
        message_history = self.load_messages()
        print("message_history: ", message_history)
        # merged_message = message_history + f"\nHumanMessage: {user_message}"
        print("user_message: ", user_message)
        
        # print("merged_message: ", merged_message)
        pydantic_response = response_chain.invoke({"user": user, 
                                                   "message_history": message_history, 
                                                   "user_message": user_message,
                                                   "message_time": message_time})
        print(pydantic_response)
        response_type = pydantic_response.response_type
        model_response = pydantic_response.response
        
        if response_type == "response_to_request":
            order_manager = OrderManager(pydantic_response)
            model_response = order_manager.process_request()
        
        self.send_json(
            {'type': 'assistant-message',
            'response_to_request': True,
            'message': model_response}
            )
        
        self.save_messages(user, user_message, model_response, message_time)
        
        # self.send_json(
        #     {'type': 'assistant-message',
        #      "message": "하드 코딩 메시지"}
        # )
        
    def save_messages(self, user, user_message, model_response, message_time):
        # print('데이터 저장 완료!')
        print("save_message 진입")
        user = User.objects.get(username=user)
        ChatMessage.objects.create(user=user, 
                                   user_message=user_message, 
                                   gpt_response=model_response,
                                   message_time=message_time)
        
    
    def load_messages(self):
        messages = ChatMessage.objects.all()
        message_history = ""
        for message in messages:
            message_history += f"HumanMessage: {message.user_message}\nAIResponse: {message.gpt_response}\n"
        return message_history