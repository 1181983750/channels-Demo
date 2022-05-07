from django.db import models

from BaseOrm import BaseModel
from User.models import User
from User.models import group


class Message(BaseModel, models.Model):
    """消息记录表"""
    msg_type = models.SmallIntegerField(verbose_name="消息标识1,方便查询,群发还是单聊")
    data_type = models.SmallIntegerField(verbose_name="消息标识2，方便查询，发送文件的属性", null=True)
    txt = models.TextField(verbose_name="消息本身")
    file = models.FileField(verbose_name='文件路径', upload_to='file/')
    send = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="发送者用户id", related_name="send")
    to = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="接收者用户id", related_name="to", null=True)
    group = models.ForeignKey(group, on_delete=models.PROTECT, verbose_name="接收群id", null=True)
    create_date = models.DateTimeField(verbose_name="消息时间")
    client_id = models.BigIntegerField(verbose_name='客户端消息id')
    is_read = models.IntegerField(verbose_name='已读未读 0-未读 1-已读')
    is_send = models.IntegerField(verbose_name='是否已经发送 0-未发送 1-已发送')

    class Meta:
        db_table = 'chat_msg'
        verbose_name_plural = "消息记录表"
        # unique_together = ['Primary_User', 'accepted']  # 联合唯一  暂时不用

# class UsertoMessage(BaseModel, models.Model):
#     """用户对应消息表"""
#     Primary_User = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="用户id", related_name="toPrimary_User")
#     message = models.ForeignKey(Message, on_delete=models.PROTECT, verbose_name="对应消息记录", null=True)
#     group = models.ForeignKey(group, on_delete=models.PROTECT, verbose_name="对应群id，群聊", null=True)
#     Deputy_User = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="对应好友id，单聊",
#                                     related_name="toDeputy_User", null=True)
#     isRead = models.BooleanField(verbose_name="已读未读", default=False)
#     sxs = models.BigIntegerField(verbose_name="顺序数,也就是条数", null=True)
#
#     class Meta:
#         verbose_name_plural = "用户对应消息表"
#         # unique_together = ['Primary_User', 'accepted']  # 联合唯一  暂时不用
