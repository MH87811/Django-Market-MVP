from django.urls import path
from .consumer import SellerConsumer

websocket_urlpatterns = [
    path('ws/seller/', SellerConsumer.as_asgi(), name='asgi_seller')
]