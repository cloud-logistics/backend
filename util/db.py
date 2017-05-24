#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json

from psycopg2.pool import ThreadedConnectionPool

import logger

# logging
log = logger.get_logger('db')


def get_conn_pool():
    pool = ThreadedConnectionPool(
        minconn=5,
        maxconn=20,
        database="cloudbox",
        user="postgres",
        password="postgres",
        host="127.0.0.1",
        port="5432"
    )
    return pool


def save_to_db(sql):
    pool = get_conn_pool()
    conn = pool.getconn()
    cur = conn.cursor()
    log.debug('sql: ' + sql)
    cur.execute(sql)
    cur.close()
    conn.commit()
    pool.putconn(conn)


def query_list(sql):
    pool = get_conn_pool()
    conn = pool.getconn()
    cur = conn.cursor()
    log.debug('sql: ' + sql)
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    conn.commit()
    pool.putconn(conn)
    return rows
