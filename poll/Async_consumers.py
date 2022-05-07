import json
import threading
import traceback
from datetime import datetime

from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer

from Channels.settings import SECRET_KEY
import jwt

from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer, \
    JsonWebsocketConsumer

# 这里的通讯视图类继承自WebsocketConsumer,还有AsyncWebsocketConsumer的 ∵要声明使用websocket协议才能进行长连接通讯
from User.models import User, Contacts
from chat.views import chat_code_to_msg
from utils.public.detoken import detoken
from utils.public.onlineTime import getBeijinTime
from utils.public.standard import Standard
from utils.public.UserMeassge import ChatUser

salt = SECRET_KEY

list = [{'id': 3, 'name': '王五'}, {'id': 3, 'name': '赵六'}, {'id': 4, 'name': '赵丽颖'}, {'id': 5, 'name': '古力娜扎'},
        {'id': 6, 'name': '玛卡扎哈'}, {'id': 7, 'name': '李媛媛'}]
staff_list = [{'id': 1, 'name': '张三'}, {'id': 2, 'name': '李四'}]


class PollConsumer(AsyncJsonWebsocketConsumer, Standard):
    """添加了一个chats来记录每一个group中的连接数。以此根据这个连接数来判断，聊天双方是否都已连接进入该个聊天group,同时，我们设定聊天组的命名形式为user_a的id加上下划线_加上user_b的id，其中id值从小到大放置"""

    ChatUserDict = dict()

    def Reuse(self):
        token = ''
        for i in self.scope['headers']:
            if str(i[0]) == "b'authorization'":
                token = str(i[1]).split("b'")[1].split("'")[0]
        try:
            info = detoken(token)
            del info['exp']
        except Exception:
            raise Exception
        return info

    # chats = dict()  # 保存一个组里的连接数
    # one = dict() #保存发信息的人
    @database_sync_to_async
    def get_orm(self,info):
        return User.objects.get(id=info['id'])

    @database_sync_to_async
    def save_orm(self, query, channel_name):
        query.socket_id = channel_name
        return query.save()

    async def connect(self):
        # print(self.scope['headers'])
        # print('url,query:',self.scope['url_route']['kwargs']['uid'], '开始链接了！%s' % info['userName'])
        # print('生成了socket链接：', self.channel_name)
        # # 元组取值
        try:
            info = self.Reuse()
            # Contacts_query = Contacts.objects.filter()
        except Exception as e:
            print('查询用户表异常：', e)
            raise StopConsumer  # 终止链接
        self.target_id = await self.get_orm(info)
        await self.save_orm(self.target_id, self.channel_name)
        print(self.target_id)
        # self.target_id.update(socket_id=self.channel_name)
        # self.target_id = self.channel_name
        # self.target_id.save()
        print(info['id'], "用户链接了")

        self.ChatUserDict[info['id']] = ChatUser(info['id'], self.channel_name)

        # print(self.ChatUserDict[info['id']].socket_id)
        """
            占位置，封装一个通知类，如：好友申请通知、系统通知、单聊消息、群聊消息
        """
        await self.accept()

    async def disconnect(self, close_code):
        # 连接关闭时调用
        # 将关闭的连接从群组中移除对应的socket字段
        filter_query = lambda channel_name: User.objects.filter(socket_id=channel_name).first()
        database_sync_to_async(filter_query)(self.channel_name)

        print(filter_query)
        await self.save_orm(self.target_id, self.channel_name)
        # save_orm
        # self.channel_layer.send()
        # await self.channel_layer.group_discard(self.group_name, self.channel_name)
        # 将该客户端移除聊天组连接信息
        print("执行关闭链接:", self.channel_name, close_code)

        # 删除用户
        self.delUser()

        await self.close()

    def delUser(self):
        """删除在线用户"""
        for obj in self.ChatUserDict.values():
            if obj.socket_id == self.channel_name:
                obj.socket_id = None

    # 收到客户端信息
    async def receive_json(self, message, **kwargs):
        # {
        # code: 110,
        # from:this.self,
        # to: this.friend,
        # data: {type: 'txt', txt: "", img: "", audio: ""},
        # }
        # 收到信息时调用 首先要获得发送者id
        print(message, '**and**', kwargs)
        # print(self.ChatUserDict[message.get('to')])
        print(self.ChatUserDict.get(message.get('data')['to']))

        try:
            info = self.Reuse()
            self.send_receive(object=message, checkarr=['tip', 'data'])
            # self.success_message('成功')
        except:
            pass
            # message = json.dumps({
            #     "tip": 1,
            #     "data": {
            #         "send": 1,
            #         "to": 1,
            #         "data": {
            #             "tip": "txt",
            #             "txt": ""
            #         }
            #     }
            # })
            # return self.chat_error('消息数据没传全')
        # if not all([message.get('code'),message.get('from'),message.get('to'),message.get('data')]):
        #     return self.chat_error(event={})
        # 这里判断发送消息的目标人物是否存在
        # try:
        #     User_query = User.objects.get(id=message.get('to'))
        # except User.DoesNotExist:
        #     # 这里同样发送给发送者 发送失败信息
        #     return self.chat_error('你发送消息给了一个空用户')
        print(message['data']['send'])
        print(datetime.now())
        now_date = datetime.strptime(getBeijinTime()[1],'%Y-%m-%d %H:%M:%S').date()
        print(now_date)
        message['data']['data']['Date'] = int(datetime.timestamp(datetime.now()))
        message['data']['send'] = info
        channel_name = await self.ChatUserDict[message['data']['to']].socket_id
        # if User_query.socket_id:
        if self.ChatUserDict.get(message.get('data')['to']):
            async_to_sync(self.channel_layer.send)(channel_name, {
                "type": "chat.message",  # 自定义使用发送的方法
                "tip": message['tip'],
                "message": message.get('message'),
                "data": message['data']
            })
        else:
            """
            "tip": event.get('data').get('tip'),
            "message": event.get('data').get('message'),
            "data": {  # 这里只定义第二层格式
                'group_id':1,
                'send': event.get('data').get('send'),  # 发送者我自己取得token
                'to': event.get('data').get('to'),  # 接收者id
                "data": {  # 这里是第三层    !!!!!!!!传值自己定义了!!!!!!!!!!!!!
                    'tip': txt, audio, video, file, img, record  # 发送者我自己取得token  其中record 
                    'txt': ....,  # 接收者id
                    'audio': {fileurl, time},  # 这里是第三层 传值自己定义了
                    'video,img': {fileurl, size, width, height},  # 这里是第三层 传值自己定义了
                    'file': {url:}
                },
            }
            """
            pass
        #
        #     print('执行发送函数：')
        # else:
        # await self.channel_layer.group_send(
        #     to_user,
        #     {
        #         "type": "push.message",
        #         "event": {'message': message, 'group': self.group_name}
        #     },
        # )

    # 发送消息函数
    def chat_message(self, event):
        # Handles the "chat.message" event when it's sent to us.
        print('执行特定发送函数：chat_message')
        print('携带过来的数据', event)

        self.send_json({
            "tip": event.get('tip'),
            # "message": event.get('data').get('message'),
            "data": {  # 这里只定义第二层格式
                'group_id': event.get('data').get('group_id'),
                'send': event.get('data').get('send'),  # 发送者我自己取得token
                'to': event.get('data').get('to'),  # 接收者id
                'data': event.get('data').get('data'),  # 这里是第三层 传值自己定义了:{}
            },
        })

    def add_friends(self, event):
        print('执行特定发送函数：add_friends')
        print('携带过来的数据', event)
        self.send_json({
            "tip": event.get('tip'),
            "message": event.get('message'),
            "data": event.get('data'),
        })

    # 格式异常调用函数
    def chat_error(self, event):
        print('chat_error,数据格式错误')
        self.send_json({
            "tip": 0,
            "message": event,
        })

        # 客户端发送消息格式要求通过验证 回执函数 self.send_receive(object=message,checkarr=['tip', 'send', 'to', 'data'])

    def success_message(self, event):
        self.send_json({
            "tip": 3,
            "message": event
        })


"""
            "tip": event.get('data').get('tip'),
            "message": event.get('data').get('message'),
            "data": {      #这里只定义第二层格式
                'send': event.get('data').get('send'),  #发送者我自己取得token
                'to': event.get('data').get('to'),  #接收者id
                "data": {  # 这里是第三层    !!!!!!!!传值自己定义了!!!!!!!!!!!!!
                    'tip': txt,audio,video,file,img,record  # 发送者我自己取得token  其中record 
                    'txt': ....,  # 接收者id
                    'audio': {fileurl,time},  # 这里是第三层 传值自己定义了
                    'video,img': {fileurl,size,width,height},  # 这里是第三层 传值自己定义了
                    'file':{url:},
                    'date':321564569165,
                },
            }
"""

"""
tip : 1 聊天消息收发标识   2好友添加通知    3对方成功收到消息回执、
二级tip: 2-1 申请好友通知 2-2 同意或拒绝通知
send: 发送者id
to:接受者id
data:object 数据
"""
