"""
ASGI config for django_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from toonkor_collector2.consumers import DownloadConsumer, TranslateConsumer


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")

websocket_urlpatterns = [
    re_path(r'ws/download/', DownloadConsumer.as_asgi()),
    re_path(r'ws/translate/', TranslateConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles traditional HTTP requests
    "websocket": AuthMiddlewareStack(  # Handles WebSocket connections
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
