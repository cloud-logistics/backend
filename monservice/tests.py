#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase

# Create your tests here.

import redis


if __name__ == '__main__':
    rcon = redis.Redis(host="127.0.0.1", port=6379, db=0)
    rcon.rpush('command_list', "{\"service\":\"command\",\"action\":\"reset\",\"result\":\"\",\"id\":\"\"}")
    rcon.save()





