from datetime import datetime

from rest_framework import serializers

from User.models import User, Contacts, ReplyFriend, group_chat


class UserDocsSerializer(serializers.ModelSerializer):
    """docs"""

    class Meta:
        model = User  # 使用的数据表模型
        fields = ['id']
        extra_kwargs = {  # 修改字段参数
            'id': {'required': True},
        }


class UserModelSerializer(serializers.ModelSerializer):
    # 定义一个属性选项
    class Meta:
        model = User  # 使用的数据表模型
        # fields = '__all__' #全部字段都映射
        exclude = ['password']  # 除了这个字段都要
        extra_kwargs = {  # 修改字段参数
            # 'purchaseNo': {'read_only': False},
            # "purchaseName": {'read_only': False},
            # "pinYinMa": {'read_only': False},
            # "spec": {'read_only': False},
            # "purchaseCount": {'read_only': False},
            # "purchasePrice": {'read_only': False}
        }


class ContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacts
        filter = '__all__'


class GetContactsModelSerializer(serializers.ModelSerializer):
    # Primary_User = serializers.SerializerMethodField()
    Deputy_User = serializers.SerializerMethodField()

    class Meta:
        model = Contacts
        exclude = ['Primary_User', 'id']  # 除了这个字段都要
        # depth = 1

    # def get_Primary_User(self, obj):
    #     print("序列化自定义输出的外键")
    #     print(obj)
    #     # print(obj.goodsNo)
    #     # print(obj.goodsNo.goodsName)
    #     goods_list = {
    #         'userName': obj.Primary_User.userName,
    #         'phone': obj.Primary_User.phone,
    #         'avatar': obj.Primary_User.avatar,
    #         'identity': obj.Primary_User.identity,
    #         'socket_id':obj.Primary_User.socket_id
    #     }
    #     return goods_list

    def get_Deputy_User(self, obj):
        goods_list = {
            'id': obj.Deputy_User.id,
            'userName': obj.Deputy_User.userName,
            'phone': obj.Deputy_User.phone,
            'avatar': obj.Deputy_User.avatar,
            'identity': obj.Deputy_User.identity,
        }
        return goods_list


class GetReplyFriendModelSerializer(serializers.ModelSerializer):
    accepted = serializers.SerializerMethodField()
    Date = serializers.SerializerMethodField()

    class Meta:
        model = ReplyFriend
        exclude = ['Primary_User', 'id']  # 除了这个字段都要

    def get_accepted(self, obj):
        goods_list = {
            'id': obj.accepted.id,
            'userName': obj.accepted.userName,
            'phone': obj.accepted.phone,
            'avatar': obj.accepted.avatar,
            'identity': obj.accepted.identity,
        }
        return goods_list

    def get_Date(self, obj):
        # 转时间戳
        return int(datetime.timestamp(obj.Date))


class GetGroup_chatModelSerializer(serializers.ModelSerializer):
    """用户对应聊天群序列化器"""

    class Meta:
        model = group_chat
        exclude = ['Primary_User', 'id']  # 除了这个字段都要
        depth = 1


class Group_chatModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = group_chat
        fields = '__all__'  # 全部字段都映射
