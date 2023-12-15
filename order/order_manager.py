from django.contrib.auth.models import User
from django.db import transaction
from django.utils.dateparse import parse_datetime

from .models import Order, OrderItem, OrderStatus, Product

class OrderManager:

    def __init__(self, order_data):
        self.order_data = order_data
        self.user = User.objects.get(username=order_data.get('user'))
        self.request_type = order_data.get('request_type')
        # 날짜를 datetime 객체로 파싱
        self.order_date = parse_datetime(order_data.get('order_date'))
    
    def create_order(self):
        products_data = self.order_data.get('products', [])
        
        # 'products'가 빈 리스트인 경우는 처리하지 않음
        if not products_data:
            return '주문 상품이 담겨 있지 않습니다.'
        
        with transaction.atomic():
            new_order = Order.objects.create(user=self.user, order_date=self.order_date)
            for product_data in products_data:
                product_name = product_data['name']
                try:
                    # 상품이 존재하는지 확인
                    product = Product.objects.get(name=product_name)
                except Product.DoesNotExist:
                    return f'{product_name}이란 상품은 저희 가게에 없습니다.'
                
                OrderItem.objects.create(
                    order=new_order,
                    product=product,
                    price=product_data['price'],
                    quantity=product_data['quantity']
                )
                # 주문 후 재고 감소
                product.stock -= product_data['quantity']
                product.save()
            # 주문 상태 생성
            OrderStatus.objects.create(order=new_order, status='pending')
            return  f'주문이 완료되었습니다. 주문시간->{self.order_date}'
    
    def inquiry_order(self):
        try:
            Order.objects.filter(user=self.user, order_date=self.order_date)
            return f'주문이 조회되었습니다.'
        except:
            return '조회되는 주문이 없습니다.'
    
    def change_order(self):
        print(self.order_data)
        with transaction.atomic():
            try:
                existing_order = Order.objects.get(user=self.user, order_date=self.order_date)
                # 현재 입력받은 order_data를 기준으로 기존 주문을 업데이트
                # 이 예제에서는 기존 주문을 삭제하고 새로운 주문을 만듭니다.
                existing_order.orderitem_set.all().delete()
                existing_order.delete()
                self.create_order()  # 새로운 주문 생성
                return f'주문이 변경되었습니다. 주문 변경 시간->{self.order_date}'
            except Order.DoesNotExist:
                return '주문을 변경하려 하였으나 조회되는 주문이 없습니다.'
    
    def cancel_order(self):
        try:
            order_to_cancel = Order.objects.get(user=self.user, order_date=self.order_date)
            with transaction.atomic():
                order_to_cancel.orderitem_set.all().delete()
                order_to_cancel.delete()
            return f'주문이 취소되었습니다. 주문 취소 시간->{self.order_date}'
        except Order.DoesNotExist:
            return '주문을 취소하려 하였으나 조회되는 주문이 없습니다.'
    
    def process_request(self):
        if self.request_type == 'order':
            message = self.create_order()
        elif self.request_type == 'order_inquiry':
            message = self.inquiry_order()
        elif self.request_type == 'order_change':
            message = self.change_order()
        elif self.request_type == 'order_cancel':
            message = self.cancel_order()
        else:
            raise ValueError('정의되지 않은 요청 유형입니다.')
        return message