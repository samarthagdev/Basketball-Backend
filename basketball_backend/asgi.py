import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basketball_backend.settings')
django_asgi_app = get_asgi_application()
from channels.security.websocket import AllowedHostsOriginValidator
import main_app.routing
from .auth import TokenAuthMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddleware(
            URLRouter(
                main_app.routing.websocket_urlpatterns
            )
        )
    )
})