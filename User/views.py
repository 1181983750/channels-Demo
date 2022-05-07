from typing import Dict

from django.db import transaction
from django.http import JsonResponse
from rest_framework import generics, serializers
from rest_framework.views import APIView

from BaseOrm import Container
from User.models import User, Contacts, ReplyFriend, group_chat, group
from User.serializers import GetContactsModelSerializer, GetReplyFriendModelSerializer, \
    Group_chatModelSerializer
from User.services import UserService, ChartRoomService
from utils.public.UserMeassge import Ser_Msg
from utils.public.detoken import login_Info
from utils.public.onlineTime import getBeijinTime
from utils.public.redisUtils import RedisUtils
from utils.public.response_result import response_result, ResponseResult
from utils.public.standard import Standard

"""
tip : 1 聊天消息收发标识   2好友添加通知    3对方成功收到消息回执
send: 发送者id
to:接受者id
data:object 数据
"""

# json_body = request.body
# json_dict = json.loads(json_body)
# print(json_dict)
# staff_id = json_dict.get('staff_id')
# target_id = json_dict.get('target_id')
# message = json_dict.get('message')
r = RedisUtils().get_redis()
user_service = UserService(User)


class UserLoginView(APIView, Standard):
    """登录接口"""

    page_class = []

    def post(self, request):
        """登录接口"""
        try:
            self.check(request.data, {'1': ['phone', 'password']})
        except Exception as e:
            return JsonResponse(response_result(msg=str(e)))
        print('登录接口', request.data)
        Data: Dict = request.data

        result = user_service.user_login(phone=Data.get('phone'), password=Data.get('password'))
        return JsonResponse(result)


# checktoken
class UserCheckTokenView(APIView):
    @login_Info
    def post(self, request):
        """检查登录状态"""
        return JsonResponse({'code': 1, 'message': 'token通过', 'data': request.info})


#  添加好友api
class FriendsView(APIView, Standard, Ser_Msg):

    def get(self, request):
        """前端搜索手机号"""
        req_get = request.GET  # query 参数
        try:
            self.check(req_get, {'1': ['phone']})
        except Exception as e:
            return JsonResponse(response_result(msg=str(e)))
        result = user_service.search_friends(phone=req_get.get('phone'))
        return JsonResponse(result)

    # 点击添加进通讯录
    @login_Info
    # @transaction.atomic
    def post(self, request):
        """前端申请添加特定手机号"""
        Data: Dict = request.data
        Data['to'] = int(Data['to'])
        try:
            self.check(Data, {'1': ['to']})
        except Exception as e:
            return JsonResponse(response_result(code=0, msg=e.__str__(), data={}))

        if Data['to'] == request.info['id']:
            return JsonResponse(response_result(code=0, msg='添加的人不能是自己'))

        result = user_service.add_friend(request.info.get('id'), Data.get('to'), Data.get('message'))
        # 先保存下添加好友申请   status:None代表 未处理    0代表拒绝 1代表同意  并且 还要 判断 是否已经是好友了 是好友的话就不能申请了
        # contacts_query = Contacts.objects.filter(Primary_User=request.info['id'], Deputy_User=Data['to'])
        # if contacts_query:
        #     return JsonResponse({'code': 0, 'message': '你和该用户已经是好友了', 'data': {}})
        # reply_query = ReplyFriend.objects.filter(accepted_id=request.info['id'], Primary_User_id=Data['to'])
        # if len(reply_query) == 0:
        #     ReplyFriend.objects.create(accepted_id=request.info['id'], Primary_User_id=Data['to'],
        #                                Date=getBeijinTime()[1],
        #                                message=Data.get('message'), status=None)
        # else:
        #     for reply in reply_query:
        #         reply.message = Data.get('message')
        #         reply.status = None
        #         reply.Date = getBeijinTime()[1]
        #         reply.check()
        #         reply.save()

        # 然后判断被添加用户是否在线： 并且给接收方查看对方消息
        to_query = r.hget('socket', Data['to'])
        if to_query is not None:
            message = {
                "tip": 2,
                "message": Data.get('message'),
                "data": {
                    "send": request.info,
                    "to": Data['to'],
                    "tip": 1,
                }
            }
            self.serializer_msg(message, channel_name=to_query)
            # 发完以后
            # self.send_receive(object=message, checkarr=['to'])
        else:
            # HttpResponse.status_code = 500

            # 这里保存添加好友消息 ，因为对方不在线
            return JsonResponse(
                {'code': 1, 'message': '对方暂时不在线,可能稍后处理好友邀请', 'data': {}})
        return JsonResponse(
            {'code': 1, 'message': '发送添加好友申请成功', 'data': {}})


# 同意或者拒绝添加好友
class ReplyFriendView(APIView, Standard, Ser_Msg):
    """同意或者拒绝添加好友"""

    @login_Info
    def get(self, request):
        reply_query = ReplyFriend.objects.filter(Primary_User_id=request.info['id'])
        reply_ser = GetReplyFriendModelSerializer(instance=reply_query, many=True)
        # temp = []
        # for obj in reply_ser.data:
        #     temp.append(obj)
        return JsonResponse({'code': 1, 'message': '获取好友申请通知列表成功', 'data': reply_ser.data})

    @login_Info
    def post(self, request):
        Data = request.data
        print('回复好友申请，源数据：', Data)
        # to 对方id   apply：回复码 0为拒绝 1为同意
        try:
            self.send_receive(object=Data, checkarr=['to', 'apply'])
            Data['apply'] = int(Data['apply'])
            Data['to'] = int(Data['to'])
        except:
            return JsonResponse({'code': 0, 'message': '参数没齐全', 'data': {}})
        if Data['apply'] != 0 and Data['apply'] != 1 and Data['apply'] is not None:
            print('*' * 30, Data['apply'])
            return JsonResponse({'code': 0, 'message': 'apply参数没传对', 'data': {}})
        if Data['to'] == request.info['id']:
            return JsonResponse({'code': 0, 'message': '添加的人不能是自己', 'data': {}})
        # 先保存下添加好友申请   status:None代表 未处理    0代表拒绝 1代表同意  并且 还要 判断 是否已经是好友了 是好友的话就不能接受or 拒绝了
        try:
            reply_query = ReplyFriend.objects.get(Primary_User=request.info['id'], accepted=Data['to'])
        except ReplyFriend.DoesNotExist:
            return JsonResponse({'code': 0, 'message': '对方没有申请加你为好友', 'data': {}})
        contacts_query = Contacts.objects.filter(Primary_User=request.info['id'], Deputy_User=Data['to'])
        if contacts_query:
            return JsonResponse({'code': 0, 'message': '你和该用户已经是好友了', 'data': {}})
        # 以上校验完毕后  不管接受或者拒绝 先修改好友消息状态表 并且 发送给申请者一个接受or拒绝的回复
        reply_query.status = Data['apply']
        reply_query.save()
        # 更改完状态表后 判断是否添加进通讯录

        if Data['apply'] == 0 or Data['apply'] is None:
            # 拒绝
            Data['message'] = '拒绝了你的好友申请'
            # ReplyFriend.objects.filter(accepted_id=request.info['id'], Primary_User_id=Data['to']).delete()
        elif Data['apply'] == 1:
            # 接受
            Data['message'] = '同意了你的好友申请'
            # 通讯录表双方创建关系
            with transaction.atomic():  # 禁止自动提交,保证该函数中的所有数据库操作在同一个事物中，第一个数据库操作1即使成功保存到数据库中，只要第2个数据操作失败，那么所有该段代码所有设计的都会更改回滚到原来
                sid = transaction.savepoint()  # 开启事务设置事务保存点 可以设置多个保存点
                try:
                    ReplyFriend.objects.filter(Primary_User_id=request.info['id'], accepted_id=Data['to']).delete()
                    ReplyFriend.objects.filter(Primary_User_id=Data['to'], accepted_id=request.info['id']).delete()
                    Contacts.objects.create(Primary_User_id=request.info['id'], Deputy_User_id=Data['to'])
                    Contacts.objects.create(Primary_User_id=Data['to'], Deputy_User_id=request.info['id'])
                except:
                    transaction.savepoint_rollback(sid)  # 失败回滚事务(如果数据库操作发生异常，回滚到设置的事务保存点)
                    raise serializers.ValidationError("数据保存失败")
                else:
                    transaction.savepoint_commit(sid)  # 如果没有异常，成功提交事物
            # 暂时不删申请列表，反正有状态码标识 算了
            # reply_query.delete()
        # send_query = request.info['id']
        if r.hget(name='socket', key=Data['to']) is not None:
            # channel_name = to_query.socket_id
            # channel_layer = get_channel_layer()
            message = {
                "tip": 2,
                "message": Data.get('message'),
                "data": {
                    "tip": 1,
                    "send": request.info['id'],
                    "to": Data['to'],
                    "apply": Data['apply'],
                }
            }
            self.serializer_msg(message, channel_name=r.hget(name='socket', key=Data['to']))

        else:
            """预留逻辑处理，不在线的时候做什么"""
            return JsonResponse(
                {'code': 1, 'message': '对方暂时不在线,上线后通知对方', 'data': {}})
        return JsonResponse({'code': 1, 'message': '添加好友成功', 'data': {}})


class AddresListView(generics.GenericAPIView, APIView):
    """通讯录（好友列表）"""
    serializer_class = GetContactsModelSerializer

    @login_Info
    def get(self, request):
        # request.info在装饰器里
        contacts_query = Contacts.objects.filter(Primary_User_id=request.info['id'])
        contacts_serializer = GetContactsModelSerializer(instance=contacts_query, many=True)
        temp = []
        for obj in contacts_serializer.data:
            temp.append(obj['Deputy_User'])
        return JsonResponse({'code': 1, 'message': '获取用户通讯录成功', 'data': temp})


class ChatGroupView(APIView):
    @login_Info
    def get(self, request):
        user_id = request.info.get('id')
        chart_room: ChartRoomService = Container.get_instance().get_obj_of_key('user_id_{}'.format(user_id))
        return JsonResponse(ResponseResult(msg='OK', code=1, data=chart_room.chart_room_rooms)())

    @login_Info
    def post(self, request):
        """创建用户群聊"""
        print(request.data)
        # if 'to_id' in request.data and isinstance(request.data['to_id'],list):
        with transaction.atomic():  # 禁止自动提交,保证该函数中的所有数据库操作在同一个事物中，第一个数据库操作1即使成功保存到数据库中，只要第2个数据操作失败，那么所有该段代码所有设计的都会更改回滚到原来
            sid = transaction.savepoint()  # 开启事务设置事务保存点 可以设置多个保存点
            try:
                group_query = group.objects.create(group_name=request.data.get('group_name'),
                                                   group_author_id=request.info['id'],
                                                   group_remark=request.data.get('group_remark'))
                group_chat.objects.create(Primary_User_id=request.info['id'], group_id=group_query.id)
            except:
                transaction.savepoint_rollback(sid)  # 失败回滚事务(如果数据库操作发生异常，回滚到设置的事务保存点)
                raise serializers.ValidationError("创建群聊失败")
            else:
                if 'to_id' in request.data and isinstance(request.data['to_id'], list):
                    temp = []  # [{'to_id': [1, 2, 3, 4], 'group_id': 1}]
                    for obj in request.data['to_id']:
                        t = {'Primary_User': obj, 'group': group_query.id}
                        temp.append(t)
                        # try:
                        #     group_chat.objects.create(Primary_User_id=obj, group_id=group_query.id)
                        # except:
                        #     transaction.savepoint_rollback(sid)  # 失败回滚事务(如果数据库操作发生异常，回滚到设置的事务保存点)
                        #     raise serializers.ValidationError("创建群聊失败")
                    group_chat_ser = Group_chatModelSerializer(data=temp, many=True)
                    group_chat_ser.is_valid()
                    group_chat_ser.save()
                transaction.savepoint_commit(sid)  # 如果没有异常，成功提交事物
                return JsonResponse({"code": 1, "message": "创建群聊成功", "data": {"group_id": group_query.id}})

    @login_Info
    def patch(self, request):
        print(request.data)
        """添加用户到群聊"""
        with transaction.atomic():  # 禁止自动提交,保证该函数中的所有数据库操作在同一个事物中，第一个数据库操作1即使成功保存到数据库中，只要第2个数据操作失败，那么所有该段代码所有设计的都会更改回滚到原来
            sid = transaction.savepoint()  # 开启事务设置事务保存点 可以设置多个保存点
            if 'to_id' in request.data and isinstance(request.data['to_id'], list) and 'group_id' in request.data:
                temp = []  # [{'to_id': [1, 2, 3, 4], 'group_id': 1}]
                for obj in request.data['to_id']:
                    t = {'Primary_User': obj, 'group': request.data['group_id']}
                    temp.append(t)
                try:
                    group_chat_ser = Group_chatModelSerializer(data=temp, many=True)
                    group_chat_ser.is_valid()
                    group_chat_ser.save()
                except:
                    transaction.savepoint_rollback(sid)  # 失败回滚事务(如果数据库操作发生异常，回滚到设置的事务保存点)
                    raise serializers.ValidationError("拉入群聊失败")
                else:
                    transaction.savepoint_commit(sid)  # 如果没有异常，成功提交事物
                    return JsonResponse({"code": 1, "message": "成功拉入群聊", "data": {}})
            else:
                return JsonResponse({"code": 0, "message": "参数有误", "data": request.data})

    @transaction.atomic
    def put(self, request):
        print(isinstance(request.data['to_id'], list) == (type(request.data['to_id']) == list))
        if 'to_id' in request.data and type(
                request.data['to_id']) == list and 'group_id' in request.data:  # to_id:[] 必须是数组
            for obj in request.data['to_id']:
                query = group_chat.objects.filter(Primary_User_id=obj, group_id=request.data['group_id'])
                query.delete()
            return JsonResponse({"code": 1, "message": "成功将对方移出群聊", "data": request.data})
        else:
            return JsonResponse({"code": 0, "message": "参数有误", "data": request.data})
