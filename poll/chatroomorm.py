from typing import Type, Dict

from channels.db import database_sync_to_async
from django.db.models import QuerySet

from BaseOrm import BaseORM, BaseService
from User.models import group_chat
from User.serializers import Group_chatModelSerializer, UserModelSerializer


class ChatRoomORM(BaseORM):
    """
    聊天室类

    """

    def __init__(self, orm_obj: Type[group_chat]):
        super(ChatRoomORM, self).__init__(orm_obj)
        self.model = orm_obj

    # @database_sync_to_async
    def get_chart_rooms(self, user_id: str) -> QuerySet[group_chat]:
        result = self.model.objects.filter(Primary_User_id=user_id)
        return result

    # @database_sync_to_async
    def get_chart_room_member(self, room_id: str) -> QuerySet[group_chat]:
        result = self.model.objects.filter(group_id=room_id).only('Primary_User_id')
        return result

    def add_group(self, user_id: str) -> QuerySet[group_chat]:
        result = self.model.objects.filter(Primary_User_id=user_id)
        query_ser = Group_chatModelSerializer(instance=result, many=True)
        return query_ser.data
