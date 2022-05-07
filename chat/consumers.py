import json

from asgiref.sync import async_to_sync
from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

# 这里的通讯视图类继承自WebsocketConsumer,还有AsyncWebsocketConsumer的 ∵要声明使用websocket协议才能进行长连接通讯
from chat.views import chat_code_to_msg


class ChatConsumer(WebsocketConsumer):
    # 连接 房间
    def connect(self):
        # print(self.scope['user']) # AnonymousUser
        # print(self.scope['user'].is_authenticated) #是否通过验证 Django自带的权限那一套 用不到
        # print(self.channel_name)
        # self.room_name = '1'
        self.room_group_name = self.scope['url_route']['kwargs']['roomNo']
        # a0a137527054111875ef9a2b88b4b58!cace06beffbe47858f06004a13a624e5
        print('*' * 30)
        print(self.channel_name)
        print('*' * 30)

        # 进入房间 group_add添加
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        print("websocket群聊连接成功了")
        # self.room_name = self.scope['url_route']['kwargs']['room_name']
        # self.room_group_name = 'chat_%s' % self.room_name
        # await self.channel_layer.group_add(
        #     self.room_group_name,
        #     self.channel_name
        # )
        # print('有人了')
        # raise StopConsumer
        self.accept()

    # 断开 链接
    def disconnect(self, close_code):
        print("连接关闭了",close_code)
        # group_discard 销毁
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # 获取客户端消息
    def receive(self, text_data=None, bytes_data=None):
        # 自定义好一个 解析json格式，
        text_data_json = json.loads(text_data)
        print('获取客户端',text_data_json['code'], text_data_json['message'],'***',bytes_data)
        message = chat_code_to_msg(text_data_json['code'], text_data_json['message'],)
        # self.send(text_data=json.dumps(message))
        event = {
            'type': 'chat.message',
            'message': message
        }
        # 发送消息到房间 group_send
        print(self.room_group_name)
        print(event)
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, event)


    # 发送到客户端消息  什么type属性 chat.message
    def chat_message(self, event):
        message = event['message']
        print(message)
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))
