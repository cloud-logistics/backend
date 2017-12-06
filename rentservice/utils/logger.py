#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging


def get_logger(module_name):
    logger = logging.getLogger("django")  # 为loggers中定义的名称
    return logger
    #
    # # 创建一个logger
    # logger = logging.getLogger(str(module_name))
    # logger.setLevel(logging.DEBUG)
    #
    # # 创建一个handler，用于写入日志文件
    # # fh = logging.FileHandler('runlog.log')
    # if os.path.exists(settings.LOG_ROOT_PATH):
    #     log_path = settings.LOG_ROOT_PATH + '/runlog.log'
    # else:
    #     log_path = 'runlog.log'
    # fh = logging.handlers.RotatingFileHandler(log_path, mode='a', maxBytes=10485760, backupCount=10)
    # fh.setLevel(logging.DEBUG)
    #
    # # 再创建一个handler，用于输出到控制台
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)
    #
    # # 定义handler的输出格式
    # formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(filename)s %(lineno)s %(message)s')
    # fh.setFormatter(formatter)
    # ch.setFormatter(formatter)
    #
    # # 给logger添加handler
    # logger.addHandler(fh)
    # logger.addHandler(ch)
    #
    # return logger
