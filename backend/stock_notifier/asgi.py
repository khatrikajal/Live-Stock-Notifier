import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import live_stock_app.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_notifier.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            live_stock_app.routing.websocket_urlpatterns
        )
    ),
})
