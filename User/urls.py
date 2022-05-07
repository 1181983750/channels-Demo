from django.urls import path

from User.views import UserLoginView, FriendsView, ReplyFriendView, AddresListView, ChatGroupView
from User.views import UserCheckTokenView

urlpatterns = [
    # 这里放聊天app的接口
    path('login/', UserLoginView.as_view()),
    path('checktoken/', UserCheckTokenView.as_view()),
    path('add_friends/', FriendsView.as_view()), # POST添加好友 | GET搜索好友
    path('reply_friend/',ReplyFriendView.as_view()), #接受或者拒绝 好友申请
    path('friend_list/',AddresListView.as_view()),#用户好友列表
    path('group_list/', ChatGroupView.as_view()),#用户群聊列表GET 、新增群聊POST、拉人进群patch
]