# ! /usr/bin/env python
# -*- coding: utf-8 -*-
import conf
import jpush
from jpush import common

_jpush = jpush.JPush(conf.app_key, conf.master_secret)
_jpush.set_logging("INFO")


# 给指定用户发送消息
def push_alias(alias_list, push_msg):
    push = _jpush.create_push()
    alias = alias_list
    alias1 = {"alias": alias}
    print(alias1)
    push.audience = jpush.audience(
        # jpush.tag("tag1", "tag2"),
        alias1
    )
    push.notification = jpush.notification(alert=push_msg)
    push.platform = jpush.all_
    print (push.payload)
    push.send()


def push_all(push_msg):
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.notification = jpush.notification(alert=push_msg)
    push.platform = jpush.all_
    try:
        response = push.send()
    except common.Unauthorized:
        raise common.Unauthorized("Unauthorized")
    except common.APIConnectionException:
        raise common.APIConnectionException("conn")
    except common.JPushFailure:
        print ("JPushFailure")
    except:
        print ("Exception")


if __name__ == '__main__':
    push_msg = u'测试server发送消息'
    alias = []
    alias.append("bf0bfa78-c919-11e7-9dc3-6a00027160c0")
    push_alias(alias_list=alias, push_msg=push_msg)
