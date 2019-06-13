#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/6/12 8:53
software: PyCharm
description: 
'''

import execjs
import base64

# with open('crypto.js', encoding='utf-8') as f:
#     js = execjs.compile(f.read())
#     print(js.call('encrypt'))
#
#
with open('crypto.js', encoding='utf-8') as f:
    js = execjs.compile(f.read())
    print(js.call('encryption',['acorn','12345678']))

# with open('rsa_jsencrypt.js', encoding='utf-8') as f:
#     js = execjs.compile(f.read())
#     result = js.call('rsa')
#     print(result)