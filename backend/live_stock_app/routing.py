from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/stock-notifier/', consumers.StockNotifierConsumer.as_asgi()),
]
