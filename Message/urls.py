from django.urls import path

from Message.views import UsertoMessageView
from User.views import ChatGroupView

urlpatterns = [
    # 这里放聊天app的接口
    path('message_list/',UsertoMessageView.as_view()),#用户群聊列表GET 、新增群聊POST、拉人进群patch
]