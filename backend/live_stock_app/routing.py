from django.urls import path
from live_stock_app import consumers

websocket_urlpatterns = [
    path('ws/stock-notifier/', consumers.StockConsumer.as_asgi()),
]