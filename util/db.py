#! /usr/bin/env python
# -*- coding: utf-8 -*-

from psycopg2.pool import ThreadedConnectionPool
import psycopg2
from cloudbox import settings
import logger

# logging
log = logger.get_logger('db')


def get_conn_pool():
    conn_params = settings.DATABASES['default']
    pool = ThreadedConnectionPool(
        minconn=5,
        maxconn=20,
        database=conn_params['NAME'],
        user=conn_params['USER'],
        password=conn_params['PASSWORD'],
        host=conn_params['HOST'],
        port=conn_params['PORT']
    )
    return pool


def save_to_db(sql):
    try:
        pool = get_conn_pool()
        conn = pool.getconn()
        cur = conn.cursor()
        log.debug('sql: ' + sql)
        cur.execute(sql)
        cur.close()
    except Exception, e:
        log.error('save_to_db error,sql:' + sql)
        conn.rollback()
    finally:
        if conn:
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
