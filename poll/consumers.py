from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels_redis.core import RedisChannelLayer

from BaseOrm import Container
from Channels.settings import SECRET_KEY
# 这里的通讯视图类继承自WebsocketConsumer,还有AsyncWebsocketConsumer的 ∵要声明使用websocket协议才能进行长连接通讯
from Message.models import Message
from Message.services import MessageService
from User.models import group_chat
from User.services import ChartRoomService
from utils.public.detoken import detoken
from utils.public.onlineTime import getBeijinTime
from utils.public.redisUtils import RedisUtils
from utils.public.response_result import socket_send
from utils.public.standard import Standard

salt = SECRET_KEY

list = [{'id': 3, 'name': '王五'}, {'id': 3, 'name': '赵六'}, {'id': 4, 'name': '赵丽颖'}, {'id': 5, 'name': '古力娜扎'},
        {'id': 6, 'name': '玛卡扎哈'}, {'id': 7, 'name': '李媛媛'}]
staff_list = [{'id': 1, 'name': '张三'}, {'id': 2, 'name': '李四'}]


class PollConsumer(AsyncJsonWebsocketConsumer, Standard):
    """添加了一个chats来记录每一个group中的连接数。以此根据这个连接数来判断，聊天双方是否都已连接进入该个聊天group,同时，我们设定聊天组的命名形式为user_a的id加上下划线_加上user_b的id，其中id值从小到大放置"""

    def __init__(self, *args, **kwargs):
        super(PollConsumer, self).__init__(*args, **kwargs)
        self.msg_service = MessageService(Message)

    def Reuse(self):
        token = ''
        for i in self.scope['headers']:
            if str(i[0]) == "b'authorization'":
                token = str(i[1]).split("b'")[1].split("'")[0]

        print(1)
        try:
            info = detoken(token)
            del info['exp']
        except Exception as e:
            raise Exception(e)
        return info

    # chats = dict()  # 保存一个组里的连接数
    # one = dict() #保存发信息的人
    # @database_sync_to_async
    # def get_orm(self, ids):
    #     # return User.objects.get(id=ids)
    #     return group_chat.objects.filter(Primary_User_id=ids)

    # @database_sync_to_async
    # def save_orm(self, query, channel_name):
    #     query.socket_id = channel_name
    #     return query.save()

    async def connect(self):
        # print(self.scope['headers'])
        # print('生成了socket链接：', self.channel_name)
        try:
            self.info = self.Reuse()
        except Exception as e:
            print('查询用户token异常：', e)
            raise StopConsumer  # 终止链接

        user_id = self.info.get('id')
        self.room = ChartRoomService(group_chat)  # 实例化对象
        await self.room.get_chart_rooms(user_id)
        await self.room.get_chart_room_members()

        # 将聊天室对象放入容器中
        con = Container.get_instance()
        con.add_obj_to_container('user_id_' + str(user_id), self.room)

        self.ser_data = await self.room.add_group(self.info.get('id'))
        for obj in self.ser_data:
            if obj.get('group'):
                self.room_group_name = str(obj.get('group'))
                # Join room group
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
        self.r = RedisUtils().get_redis()
        self.r.hset(name="socket", key=self.info['id'], value=str(self.channel_name))
        # print(self.r.hget("socket", self.info['id']))  # 单个取hash的key对应的值
        """
        ex - 过期时间（秒）
        px - 过期时间（毫秒）
        nx - 如果设置为True，则只有name不存在时，当前set操作才执行
        xx - 如果设置为True，则只有name存在时，当前set操作才执行
        """
        # self.r.set(self.info['id'], self.channel_name, ex=9999999999999999)  # 设置 name 对应的值
        # print('生成socket链接', self.r.get(self.info['id']))
        # print('判断键是否存在 存在为1,不存在为0：', self.r.exists(self.info['id']))
        # print(self.r.keys())  # 查询所有的Key
        # print(self.r.dbsize())  # 当前redis包含多少条数据
        # self.r.sadd("set1", 33, 44, 55, 66)  # 往集合中添加元素
        # print(self.r.scard("set1"))  # 集合的长度是4
        # print(self.r.smembers("set1"))  # 获取集合中所有的成员
        # print(self.r.sismember('set1', '33'))  # 检查value是否是name对应的集合的成员，结果为True和False
        # self.r.save()  # 执行"检查点"操作，将数据以RDB文件格式保存到硬盘。保存时阻塞
        # self.r.flushdb()        # 清空r中的所有数据 写在服务器重启 ready钩子函数里了
        """
            占位置，封装一个通知类，如：好友申请通知、系统通知、单聊消息、群聊消息
        """
        await self.accept()

    async def disconnect(self, close_code):
        # 连接关闭时调用
        print("执行关闭链接:", self.channel_name, close_code)
        for obj in self.ser_data:
            if obj.get('group'):
                await self.channel_layer.group_discard(
                    str(obj.get('group')),
                    self.channel_name
                )
        # 删除在线用户
        self.r.hdel('socket', self.info['id'])
        await self.close()

    # 收到客户端信息
    async def receive_json(self, message, **kwargs):
        # 收到信息时调用 首先要获得发送者id
        print(message, '**收到信息**', kwargs)

        if not message["data"].get('data'):
            message["data"]["data"] = {}

        sender_result = socket_send(tip=0,
                                    data=message.get('data').get('data', None),
                                    data_type=message.get('data').get('data').get('tip'),
                                    recipient=self.info.get('id'),
                                    client_msg_id=message.get('data').get('data').get('client_msg_id'))

        recipient_result = socket_send(tip=message.get('tip'),
                                       sender=self.info,
                                       data=message.get('data').get('data', None),
                                       data_type=message.get('data').get('data').get('tip'),
                                       recipient=message.get('data').get('to'),
                                       client_msg_id=message.get('data').get('data').get('client_msg_id'))
        sender_result['type'] = 'chat.message'
        recipient_result['type'] = 'chat.message'

        self.channel_layer: RedisChannelLayer
        sender_channel_name = self.r.hget('socket', self.info.get('id'))
        recipient_channel_name = self.r.hget("socket", message['data'].get('to'))

        self.msg_service.add(Message(msg_type=message.get('tip'),
                                     data_type=message.get('data').get('data').get('tip'),
                                     txt=message.get('data').get('data').get('txt'),
                                     file=None,
                                     send_id=self.info.get('id'),
                                     to_id=message.get('data').get('to'),
                                     group_id=message.get('data').get('group_id'),
                                     create_date=getBeijinTime()))

        await self.channel_layer.send(sender_channel_name, sender_result)

        if recipient_channel_name:
            await self.channel_layer.send(recipient_channel_name, recipient_result)
        else:
            """
            "tip": event.get('data').get('tip'),
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
            print('不在线')

    # 发送消息函数
    async def chat_message(self, event):
        print('携带过来的数据chat_message', event)
        del event['type']
        await self.send_json(event)
        # await self.send_json({
        #     "tip": event.get('tip'),
        #     "data": {  # 这里只定义第二层格式
        #         'group_id': event.get('data').get('group_id'),
        #         'send': event.get('data').get('send'),  # 发送者我自己取得token
        #         'to': event.get('data').get('to'),  # 接收者id
        #         'data': event.get('data').get('data'),  # 这里是第三层 传值自己定义了:{}
        #     },
        # })

    # 添加好友通知消息
    async def add_friends(self, event):
        print('携带过来的数据add_friends', event)
        await self.send_json({
            "tip": event.get('tip'),
            "message": event.get('message'),
            "data": event.get('data'),
        })


"""
            "tip": event.get('data').get('tip'),
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
