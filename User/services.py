import time
from typing import Type, Dict, Optional

import jwt
from channels.db import database_sync_to_async

from BaseOrm import BaseService
from Channels.settings import SECRET_KEY
from User.models import User, Contacts, ReplyFriend, group_chat
from User.serializers import UserModelSerializer
from User.userORM import UserORM, ContactsORM, ReplyFriendORM
from poll.chatroomorm import ChatRoomORM
from utils.public.onlineTime import getBeijinTime
from utils.public.response_result import response_result


class ChartRoomService(BaseService):

    def __init__(self, model: Type[group_chat]):
        super(ChartRoomService, self).__init__(model)
        self.chart_room_orm = ChatRoomORM(group_chat)
        self.chart_room_rooms = []

    @database_sync_to_async
    def add_group(self, ids: str):
        query = self.chart_room_orm.add_group(ids)
        return query

    @database_sync_to_async
    def get_chart_rooms(self, user_id: str):
        my_chart_rooms = self.chart_room_orm.get_chart_rooms(user_id)
        for i in my_chart_rooms:
            i: group_chat
            self.chart_room_rooms.append({
                'room_id': i.group_id,
                'group_name': i.group.group_name,
                'group_author': i.group.group_author.id,
                'group_remark': i.group.group_remark,
                'members': []
            })

    @database_sync_to_async
    def get_chart_room_members(self):
        for i in self.chart_room_rooms:
            i: Dict
            room_members = self.chart_room_orm.get_chart_room_member(i.get('room_id'))
            for j in room_members:
                ser_user = UserModelSerializer(instance=j.Primary_User).data
                i['members'].append(ser_user)


class UserService(BaseService):

    def __init__(self, model: Type[User]):
        super(UserService, self).__init__(model)
        self.orm = UserORM(model)
        self._contacts_service = ContactsService(Contacts)
        self._reply_friend_service = ReplyFriendService(ReplyFriend)

    def user_login(self, phone, password) -> Dict:
        try:
            result = self.orm.get_user_by_phone_and_password(phone=phone, password=password)
        except User.DoesNotExist:
            return response_result(msg='请检查用户名密码')
        ser = UserModelSerializer(instance=result)
        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }
        data = ser.data
        data['exp'] = int(time.time() + 9999999999999999999999)
        token = jwt.encode(payload=data, key=SECRET_KEY, algorithm='HS256', headers=headers)
        token = 'Bearer ' + token
        return response_result(msg='登录成功', data=data, code=1, token=token)

    def search_friends(self, phone):
        """
        查询好友

        Args:
            phone: 好友电话号码

        Returns:

        """
        try:
            result = self.orm.get_user_by_phone(phone)
            serializer = UserModelSerializer(instance=result)
            return response_result(code=1, msg='查找成功', data=serializer.data)
        except User.DoesNotExist:
            return response_result(msg='查无此人')

    def add_friend(self, user_id, friend_id, add_msg: str):
        is_not_friend = self._contacts_service \
            .get_contacts_by_primary_user_id_and_deputy_user_id(primary_user_id=user_id, deputy_user_id=friend_id)
        if is_not_friend:
            return response_result(msg='你和该用户已经是好友了', code=0)
        else:
            result = self._reply_friend_service \
                .get_reply_friend_by_accepted_id_and_primary_user_id(accepted_id=user_id, primary_user_id=friend_id)
            if result:
                result.message = add_msg
                result.Date = getBeijinTime()[1]
                result.save()
            else:
                self._reply_friend_service.add({'accepted_id': user_id, 'Primary_User_id': friend_id,
                                                'Date': getBeijinTime()[1],
                                                'message': add_msg, 'status': None})


class ContactsService(BaseService):

    def __init__(self, model: Type[Contacts]):
        super(ContactsService, self).__init__(model=model)
        self.orm = ContactsORM(model=model)

    def get_contacts_by_primary_user_id_and_deputy_user_id(self, primary_user_id, deputy_user_id) -> bool:
        """
        查询自己和目标是否是好友

        Args:
            primary_user_id: 自己id
            deputy_user_id: 添加好友id

        Returns:
            不是好友返回false
            是好友返回true
        """
        try:
            self.orm.get_contacts_by_primary_user_id_and_deputy_user_id(primary_user_id, deputy_user_id)
            return True
        except Contacts.DoesNotExist:
            return False


class ReplyFriendService(BaseService):

    def __init__(self, model: Type[ReplyFriend]):
        super(ReplyFriendService, self).__init__(model=model)
        self.orm = ReplyFriendORM(model=model)

    def get_reply_friend_by_accepted_id_and_primary_user_id(self, accepted_id, primary_user_id) \
            -> Optional[ReplyFriend]:
        try:
            result = self.orm.get_reply_friend_by_accepted_id_and_primary_user_id(accepted_id, primary_user_id)
        except ReplyFriend.DoesNotExist:
            result = None
        return result
