from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter # type: ignore
from consumers import StockConsumer # type: ignore

application = ProtocolTypeRouter({
    # WebSocket handler
    "websocket": URLRouter([
        path("ws/stock/<str:room_name>/", StockConsumer.as_asgi()),
    ])
})
