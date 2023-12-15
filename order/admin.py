from django.contrib import admin

from .models import ChatMessage, Order, OrderItem, OrderStatus, Product, UserProfile

admin.site.register(ChatMessage)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderStatus)
admin.site.register(Product)
