#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
from rentservice.utils import logger

log = logger.get_logger(__name__)

def retcode(data, code, msg):
    ret = {}
    ret['data'] = data
    ret['code'] = code
    ret['message'] = msg
    return ret


def errcode(code, msg):
    err_code = {}
    err_code['code'] = code
    err_code['message'] = msg
    return err_code
