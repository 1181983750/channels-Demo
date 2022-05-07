import time

import jwt
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from Channels.settings import SECRET_KEY
from User.models import User


class TokenAuthMiddleware(MiddlewareMixin):
    def process_request(self, request, salt=SECRET_KEY):
        # 如果为下面的两个请求不做任何处理 return可以终止函数
        # print(request.path)
        if request.path == '/user/login/' or request.path == '/docs/':
            pass
        else:
                # 从cookies中找ticket
            print('token 拦截中间件执行')
            try:
                ticket = request.headers.get('Authorization').split('Bearer ')[1]
            except Exception as e:
                return JsonResponse({"message": "没有登录：%s" %e, "code": -1, "data": {}})
            # 判断取出的内容是否有效

            # 判断cookies中有没有ticket
            try:
                info = jwt.decode(jwt=ticket, key=salt, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return JsonResponse({"message": 'Token过期', "code": -1, "data": {}})
            except jwt.DecodeError:
                return JsonResponse({"message": 'Token不合法', "code": -1, "data": {}})
            except jwt.InvalidTokenError as e:
                return JsonResponse({"message": "出现了无法预料的view视图错误：%s" %e, "code": -1, "data": {}})
            users = User.objects.filter(phone=info.get('phone'))
            if not users:
                return JsonResponse({'code': -1, 'message': '没有此用户', 'data': '/user/login/'})



