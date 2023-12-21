from django.db import models
from django.contrib.auth.models import User
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser


# CASCADE 부분 살펴보고 필요한 경우 설정 변경하기
class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_message = models.TextField(blank=True)  # 사용자의 질문을 저장하는 필드
    gpt_response = models.TextField(blank=True)  # ChatGPT의 답변을 저장하는 필드
    message_time = models.DateTimeField()
    
    class Meta:
        ordering=('message_time',)
        
    def __str__(self):
        return f"사용자: {self.user}\n사용자 메시지{self.user_message}\n\AI 답변: {self.gpt_response}\n질문 시간{self.message_time}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    
    def __str__(self):
        return self.user.username
        
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    stock = models.IntegerField()
    description = models.TextField()
    
    def __str__(self):
        # 상품 이름 수량 안내
        return f"상품 이름: {self.name} | 가격: {self.price}원 | 재고: {self.stock}개"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    order_date = models.DateTimeField()
    
    def __str__(self):
        return f"주문인: {self.user.username} | 주문 날짜: {self.order_date}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.IntegerField()


class OrderStatus(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    update_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Order status"
    
    

