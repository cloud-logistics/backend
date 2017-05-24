#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging


def get_logger(module_name):

    # 创建一个logger
    logger = logging.getLogger(str(module_name))
    logger.setLevel(logging.WARN)

    # 创建一个handler，用于写入日志文件
    fh = logging.FileHandler('runlog.log')
    fh.setLevel(logging.DEBUG)

    # 再创建一个handler，用于输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # 定义handler的输出格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # 给logger添加handler
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

