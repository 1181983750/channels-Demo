from django.urls import path
from chat.consumers import ChatConsumer
from poll.consumers import PollConsumer
websocket_urlpatterns = [
    path('chat-channel/<str:roomNo>/', ChatConsumer),
    path('chat-only/<str:uid>/',PollConsumer)
]