import redis

from ..utils.constants import REDIS_CONNECTION_CONFIG


def create_redis():
    return redis.ConnectionPool(**REDIS_CONNECTION_CONFIG)


pool = create_redis()
