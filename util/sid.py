#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
generate site code
'''
from monservice.models import Nation, City, SiteCode


def generate_sid(nation, city):
    nation_code = Nation.objects.filter(nation_name=nation).nation_code
    city_code = City.objects.filter(city_name=city).city_code
    pre_code = nation_code + city_code
    try:
        sc = SiteCode.objects.get(pre_code=pre_code)
    except Exception, e:
        num = 1
        sc = SiteCode(pre_code=pre_code, max=num)
    else:
        num = sc.max + 1
        sc.max = num

    sc.save()

    if is_binary_odd(num):
        check = 0
    else:
        check = 1
    num_code = '%05d' % num
    site_code = pre_code + str(check) + num_code
    return site_code


def is_binary_odd(num):
    binary = "{0:b}".format(num)
    ones = binary.count('1')
    if ones % 2 == 0:
        return False
    else:
        return True
