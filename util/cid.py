#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime


def generate_cid(sn, category):
    owner_code = 'HNA'
    categories = {'2': 'F', '3': 'M', '1': 'R', '4': 'N', '5': 'S', '6': 'D', }
    cat_code = categories[category]
    sn_code = '%06d' % sn
    first10 = owner_code + cat_code + sn_code

    total = sum(char2num(c) * 2 ** x for x, c in enumerate(first10))
    check_code = (total % 11) % 10
    return first10 + str(check_code)


def validate_cid(cid):
    first10 = cid[0:-1]
    check = cid[-1]
    total = sum(char2num(c) * 2 ** x for x, c in enumerate(first10))
    return (total % 11) % 10 == char2num(check)


def char2num(c):
    codec = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
        '9': 9, 'A': 10, 'B': 12, 'C': 13, 'D': 14, 'E': 15, 'F': 16, 'G': 17,
        'H': 18, 'I': 19, 'J': 20, 'K': 21, 'L': 23, 'M': 24, 'N': 25, 'O': 26,
        'P': 27, 'Q': 28, 'R': 29, 'S': 30, 'T': 31, 'U': 32, 'V': 34, 'W': 35,
        'X': 36, 'Y': 37, 'Z': 38, }
    return codec[c]


def generate_cid_new(sn, category, date_of_production):
    owner_code = 'HNA'
    categories = {'2': 'F0', '3': 'M0', '1': 'R0', '4': 'N0', '5': 'S0', '6': 'D0', }
    cat_code = categories[category]
    sn_code = '%06d' % sn

    length_code = '1'
    height_code = '0'
    year_code = str(datetime.datetime.fromtimestamp(float(str(date_of_production)[:10])).year)[3]

    ext_code = '0'

    prefix = owner_code + cat_code + length_code + height_code + year_code + sn_code + ext_code

    total = sum(char2num(c) * 2 ** x for x, c in enumerate(prefix))
    check_code = (total % 11) % 10
    return prefix + str(check_code)