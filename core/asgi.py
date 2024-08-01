import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls.resolvers import URLPattern

from messenger.routing import websocket_notification_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_asgi')

asgi_application = get_asgi_application()

application = ProtocolTypeRouter({
    'http': asgi_application,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(websocket_notification_urlpatterns)),
    ),
})
