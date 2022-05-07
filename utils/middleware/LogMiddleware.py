from rest_framework.response import Response
from rest_framework import utils
import json, os, copy, re, jwt, time
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status
import urllib
from django.http import QueryDict, HttpResponse, JsonResponse
from django.conf import settings
from django.core.cache import cache


from django.db import connection
from utils.logger import logger

'''
0 没有错误
1 未知错误  针对此错误  线上版前端弹出网络错误等公共错误
2 前端弹窗错误(包括：字段验证错误、自定义错误、账号或数据不存在、提示错误)
'''


# 将 put 请求转为 patch 请求 中间件
# class PUTtoPATCHMiddleware(MiddlewareMixin):
#
#     def process_request(self, request):
#         if request.method == 'PUT':
#             request.method = 'PATCH'


# 日志中间件
class LogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            logger.info(
                '************************************************* 下面是新的一条日志 ***************************************************')
            logger.info('拦截请求的地址：%s；请求的方法：%s' % (request.path, request.method))
            logger.info(
                '==================================== headers 头信息 ====================================================')
            for key in request.META:
                if key[:5] == 'HTTP_':
                    logger.debug('%s %s' % (str(key), str(request.META[key])))
            logger.info('代理IP：%s' % request.META.get('REMOTE_ADDR'))
            logger.info('真实IP：%s' % request.META.get('HTTP_X_FORWARDED_FOR'))  # HTTP_X_REAL_IP
            logger.info(
                '==================================== request body信息 ==================================================')
            logger.info('params参数：%s' % request.GET)
            if request.path == '/uploadfile/':
                logger.info('body参数：文件类型')
            else:
                logger.info('body参数：%s' % request.body.decode())
                # if 'application/x-www-form-urlencoded' in request.META['CONTENT_TYPE']:
                #     print('body参数：', urllib.parse.unquote(request.body.decode()))
            logger.info(
                '================================== View视图函数内部信息 ================================================')
        except Exception as e:
            logger.error('发生错误：已预知的是上传文件导致，非预知错误见下：')
            logger.error('未知错误：%s' % str(e))
            return JsonResponse({"message": "出现了无法预料的错误：%s" % e, "code": -1, "data": {}})

    def process_exception(self, request, exception):
        logger.error('发生错误的请求地址：%s；错误原因：%s' % (request.path, str(exception)))
        return JsonResponse({"message": "出现了无法预料的view视图错误：%s" % exception.__str__(), "code": -1, "data": {}})

    def process_response(self, request, response):
        rd = json.loads(response.content.decode())
        if type(response) == JsonResponse:
            if type(rd) == dict and (
                    rd.get('code') and rd.get('code') != 1):
                logger.error(
                    '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>      出现异常的日志       <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
                logger.error(rd)
                logger.error(
                    '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>      异常日志结束       <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
            else:
                logger.error(
                    '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>      正常的日志       <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
                logger.error(rd)
                logger.error(
                    '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>      正常日志结束       <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')

        if type(response) == Response:
            pass
        return response


