from django.db import transaction

# Create your views here.
from django.http import JsonResponse
from rest_framework.views import APIView

from utils.public.detoken import login_Info


class UsertoMessageView(APIView):
    """获取用户对应消息表"""
    def get(self,request):
        return JsonResponse({'code': 0, 'message': '添加的人不能是自己', 'data': {}})

    @transaction.atomic
    @login_Info
    def post(self,request):
        return JsonResponse({'code': 0, 'message': '添加的人不能是自己', 'data': {}})