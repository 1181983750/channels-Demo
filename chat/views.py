import json
import time

import jwt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from Channels.settings import SECRET_KEY
from User.models import User
from utils.public.detoken import detoken





"""
locals函数使用实例：用来返回全部变量，模拟聊天室之前说过的话用于临时保存
def foo(arg, a):
    x = 1
    y = 'xxxxxx'
    for i in range(10):
        j = 1
        k = i
    print locals()
    
foo(1,2)

打印输出{'a': 2, 'i': 9, 'k': 9, 'j': 1, 'arg': 1, 'y': 'xxxxxx', 'x': 1}
"""

userlist = []
salt = SECRET_KEY


# 业务逻辑
def chat_code_to_msg(code, msg):
    # msg.split('Bearer ')[1]

    if code == 100:
        info = detoken(msg)
        try:
            user = User.objects.get(phone=info['phone'])
        except:
            raise
        user_item = {
            'id': user.id,
            'username': user.userName
        }
        # 如果数据库存在但是暂存列表里没这个用户我们就添加一个
        if user_item not in userlist:
            userlist.append(user_item)
        res = {
            'code': 100,
            'userlist': userlist
        }
        print('进入长连接', res)
        return res
    # 退出长连接
    if code == 888:
        info = detoken(msg)
        try:
            user = User.objects.get(email=info['email'])
        except:
            raise
        user_item = {
            'id': user.id,
            'username': user.userName
        }
        # 如果在登录用户里面我们就移除用户
        if user_item in userlist:
            userlist.remove(user_item)
        res = {
            'code': 888,
            'userlist': userlist
        }
        print('退出长连接', res)

        return res
    # 收到客户端消息
    if code == 200:
        info = detoken(msg['token'])
        try:
            user = User.objects.get(phone=info['phone'])
        except:
            raise
        res = {
            'code': 200,
            'message': {
                'username': user.userName,
                'text': msg['text'],
                'file': msg['file']
            }
        }
        return res

#
# # 添加好友api
# def add_friend(request):
