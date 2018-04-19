#! /usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
import redis


def singleton(cls):
    instances = {}
    @wraps(cls)
    def getinstance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return getinstance


@singleton
class RedisTool(object):
    _redis_host = '127.0.0.1'
    _redis_server_port = 6379
    _redis_server_max_connections = 128
    _redis_pool_setting = redis.ConnectionPool(host=_redis_host, port=_redis_server_port)

    def get_connection(self):
        _connection = redis.Redis(connection_pool=self._redis_pool_setting)
        return _connection


