import redis


class RedisUtils:
    def __init__(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True, max_connections=10000)
        self.r = redis.Redis(connection_pool=pool, db=0)

    def get_redis(self):
        return self.r