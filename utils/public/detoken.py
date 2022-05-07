import traceback

import jwt
from django.http import JsonResponse
from Channels.settings import SECRET_KEY
from User.models import User
from utils.public.response_result import response_result

salt = SECRET_KEY


def detoken(dtoken):
    # print('要解析的token',dtoken)
    ticket = dtoken.split('Bearer ')[1]
    # 判断取出的内容是否有效
    # 判断cookies中有没有ticket
    print(ticket)
    try:
        info = jwt.decode(jwt=ticket, key=salt, algorithms=['HS256'])
        return info
    except jwt.ExpiredSignatureError:
        # traceback.print_exc()
        raise jwt.ExpiredSignatureError
        # return JsonResponse({"message": 'Token过期', "code": -1, "data": {}})
    except jwt.DecodeError:
        # traceback.print_exc()
        raise jwt.DecodeError
        # return JsonResponse({"message": 'Token不合法', "code": -1, "data": {}})
    except jwt.InvalidTokenError as e:
        # traceback.print_exc()
        raise jwt.InvalidTokenError
        # return response_result(msg='出现了无法预料的view视图错误：{}'.format(e))
        # return JsonResponse({"message": "出现了无法预料的view视图错误：%s" % e, "code": -1, "data": {}})


# def gene_filter_params(model, search=()):
#     def warpper(func):
#         def inner(self, request, *args, **kwargs):
#             print('装饰器被调用,通用搜索:', model, '调用函数名:', func.__name__)
#             return inner()
#         return warpper()


def login_Info(func):
    def wrapper(self, request, *args, **kwargs):
        if 'Authorization' not in request.headers:
            return JsonResponse({"message": '未登录', "code": -1, "data": {}})
        token = request.headers.get('Authorization')
        id = detoken(token).get('id')
        print("login_Info执行，request.info有此用户信息")
        try:
            info = User.objects.get(id=id)
        except:
            return JsonResponse({"message": '未登录', "code": -1, "data": {}})
        payload = {
            "id": info.id,
            "userName": info.userName,
            "phone": info.phone,
            "avatar": info.avatar,
            "identity": info.identity,
        }
        request.info = payload
        result = func(self, request, *args, **kwargs)
        return result

    return wrapper
