from django.db import models

# Create your models here.
from BaseOrm import BaseModel


class User(BaseModel, models.Model):
    identity_choices = (
        ('0', '员工'),
        ('1', '管理员')
    )
    userName = models.CharField(max_length=64, verbose_name='用户昵称', null=False)
    phone = models.BigIntegerField(verbose_name="phone", unique=True)
    password = models.CharField(max_length=32, verbose_name='密码', null=False)
    avatar = models.CharField(max_length=255, verbose_name="网络头像", null=False,
                              default="https://img1.baidu.com/it/u=1257658679,2047150679&fm=253&fmt=auto&app=138&f=JPEG?w=450&h=400")
    identity = models.CharField(choices=identity_choices, default='员工', max_length=32, verbose_name="身份权限", null=False,
                                blank=False)

    class Meta:
        verbose_name_plural = "用户初始化信息表"


class Contacts(BaseModel, models.Model):
    Primary_User = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="主用户id", related_name="Primary_id")
    Deputy_User = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="好友id", related_name="Deputy_id")

    class Meta:
        verbose_name_plural = "用户联系人关系表"
        unique_together = ['Primary_User', 'Deputy_User']  # 联合唯一


class group(BaseModel, models.Model):
    group_name = models.CharField(max_length=255, verbose_name="群名称", null=True)
    group_author = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="群创始人")
    group_remark = models.TextField(verbose_name="群备注", null=True)

    class Meta:
        verbose_name_plural = "群初始化表"


class group_chat(BaseModel, models.Model):
    """用户对应聊天群"""
    Primary_User = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="主用户id")
    group = models.ForeignKey(group, on_delete=models.PROTECT, verbose_name="群聊房间id")

    class Meta:
        verbose_name_plural = "用户群关系表"
        unique_together = ['Primary_User', 'group']  # 联合唯一


class ReplyFriend(BaseModel, models.Model):
    """用户好友同意or拒绝 记录表"""
    Primary_User = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="主用户id", related_name="Primary_User")
    accepted = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="添加好友申请用户", related_name="accepted")
    message = models.CharField(max_length=255, verbose_name="附带消息", null=True)
    status = models.CharField(max_length=16, verbose_name="状态：待处理，接受，拒绝", null=True)
    Date = models.DateTimeField(verbose_name="申请时间")

    class Meta:
        verbose_name_plural = "添加好友消息状态表"
        unique_together = ['Primary_User', 'accepted']  # 联合唯一  暂时不用

#
# class Task(models.Model):
#     """ 工单、任务表、请假|调休|采购 """
#     title = models.CharField(verbose_name="标题",max_length=64)
#     detail = models.TextField(verbose_name="描述",null=True,blank=True)
#
#
# class AuditTask(models.Model):
#     """用户审批关系"""
#     task = models.ForeignKey(to='Taks',verbose_name="任务工单",on_delete=models.CASCADE)
#     status_choices = (
#         (1,"未审批"),
#         (2,"待审批"),
#         (3,"通过"),
#         (4,"未通过"),
#     )
#     status = models.SmallIntegerField(verbose_name="状态",choices=status_choices)
#     user = models.ForeignKey(verbose_name="审批者",to="User",on_delete=models.PROTECT)
