from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import chat.routing
#指明websocket协议
application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            # 指定使用的路由路径列表
            chat.routing.websocket_urlpatterns
        )
    ),
})
