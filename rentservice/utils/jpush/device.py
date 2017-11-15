# ! /usr/bin/env python
# -*- coding: utf-8 -*-
import conf
import jpush

_jpush = jpush.JPush(conf.app_key, conf.master_secret)
_jpush.set_logging("DEBUG")
device = _jpush.create_device()

def alias_user():
    alias = "alias1"
    platform = "android,ios"
    device.get_aliasuser(alias, platform)