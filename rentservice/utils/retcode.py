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