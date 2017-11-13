#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
generate site code
'''
from monservice.models import Nation, City, SiteCode


def generate_sid(city):
    # nation_code = Nation.objects.filter(nation_name=nation).nation_code
    # city_code = City.objects.filter(city_name=city).city_code
    nation_code = 'CN'
    city_code = convert_chinese_character(city)
    pre_code = nation_code + city_code

    num = get_sid_num(pre_code)
    if is_binary_odd(num):
        check = 0
    else:
        check = 1
    num_code = '%05d' % num
    site_code = pre_code + str(check) + num_code
    return site_code


def get_sid_num(pre_code):
    try:
        sc = SiteCode.objects.get(pre_code=pre_code)
    except Exception, e:
        num = 1
        sc = SiteCode(pre_code=pre_code, max=num)
        sc.save()
        return num
    else:
        num = sc.max + 1
        sc.max = num
        sc.save()
        return num


def is_binary_odd(num):
    binary = "{0:b}".format(num)
    ones = binary.count('1')
    if ones % 2 == 0:
        return False
    else:
        return True


def multi_get_letter(str_input):
    if isinstance(str_input, unicode):
        unicode_str = str_input
    else:
        try:
            unicode_str = str_input.decode('utf8')
        except:
            try:
                unicode_str = str_input.decode('gbk')
            except:
                print
                'unknown coding'
                return

    return_list = []
    for one_unicode in unicode_str:
        return_list.append(single_get_first(one_unicode))
    return return_list


def single_get_first(unicode1):
    str1 = unicode1.encode('gbk')
    try:
        ord(str1)
        return str1
    except:
        asc = ord(str1[0]) * 256 + ord(str1[1]) - 65536
        if asc >= -20319 and asc <= -20284:
            return 'a'
        if asc >= -20283 and asc <= -19776:
            return 'b'
        if asc >= -19775 and asc <= -19219:
            return 'c'
        if asc >= -19218 and asc <= -18711:
            return 'd'
        if asc >= -18710 and asc <= -18527:
            return 'e'
        if asc >= -18526 and asc <= -18240:
            return 'f'
        if asc >= -18239 and asc <= -17923:
            return 'g'
        if asc >= -17922 and asc <= -17418:
            return 'h'
        if asc >= -17417 and asc <= -16475:
            return 'j'
        if asc >= -16474 and asc <= -16213:
            return 'k'
        if asc >= -16212 and asc <= -15641:
            return 'l'
        if asc >= -15640 and asc <= -15166:
            return 'm'
        if asc >= -15165 and asc <= -14923:
            return 'n'
        if asc >= -14922 and asc <= -14915:
            return 'o'
        if asc >= -14914 and asc <= -14631:
            return 'p'
        if asc >= -14630 and asc <= -14150:
            return 'q'
        if asc >= -14149 and asc <= -14091:
            return 'r'
        if asc >= -14090 and asc <= -13119:
            return 's'
        if asc >= -13118 and asc <= -12839:
            return 't'
        if asc >= -12838 and asc <= -12557:
            return 'w'
        if asc >= -12556 and asc <= -11848:
            return 'x'
        if asc >= -11847 and asc <= -11056:
            return 'y'
        if asc >= -11055 and asc <= -10247:
            return 'z'
        return ''


def convert_chinese_character(chinese):
    a = multi_get_letter(chinese)
    b = ''
    for i in a:
        b = b + i
    return b.upper()
