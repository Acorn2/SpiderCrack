#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/5/7 20:20
software: PyCharm
description: 
'''
from hashlib import md5
import hashlib



def md5(str):
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    print(m.hexdigest())

md5('爬虫')


