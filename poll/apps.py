import redis
from django.apps import AppConfig



class PollConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'poll'

    def ready(self):
        r1 = redis.Redis(host='localhost',port=6379,db=1,decode_responses=True)
        r0 = redis.Redis(host='localhost',port=6379,db=0,decode_responses=True)
        r1.flushdb()        # 清空r中的所有数据
        r0.flushdb()        # 清空r中的所有数据

