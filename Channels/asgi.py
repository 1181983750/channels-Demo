"""
ASGI config for Channels project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os



from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

# def ws():
#     return Channels.urls.websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Just HTTP for now. (We can add other protocols later.)
    # 下面自定义的websocket

})
