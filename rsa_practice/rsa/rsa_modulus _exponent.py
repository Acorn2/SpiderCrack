#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/6/12 15:17
software: PyCharm
description: python利用rsa包分析公钥，得到模数和指数
参考网址：https://www.cnblogs.com/masako/p/7660418.html
'''

import rsa
import base64

def read():
    # 导入密钥
    with open('public.pem', 'r+') as f:
        pubkey = rsa.PublicKey.load_pkcs1(f.read().encode())
        return pubkey

def key_to_ne(pubkey):
    '''
    根据公钥的对照偏移表找出指数和模数
    :param pubkey:公钥
    :return:模数和指数
    '''
    pubkey = base64.b64decode(pubkey)

    print(pubkey)
    print(len(pubkey))
    if len(pubkey) < 162:
        return False
    hex_str = ''

    for x in pubkey:
        # print(x,hex(x)[2:] )
        # h = hex(ord(x))[2:]
        h = hex(x)[2:]#十进制转十六进制，
        h = h.rjust(2, '0')#原字符串右对齐，不足2位，左边补0
        hex_str += h

    m_start = 29 * 2
    e_start = 159 * 2
    m_len = 128 * 2
    e_len = 3 * 2

    modulus = hex_str[m_start:m_start+m_len]
    exponent = hex_str[e_start:e_start+e_len]

    return modulus,exponent

if __name__ == '__main__':
    pubkey = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCLrxQSE3f8dur3eUuKivFwhWKMNZDfR+ZTRXTvz9ge+GNfzcZ9FBwV9RZJqJUz3w24OTMeMLj45EQOv3zLzElPS6GOn0klNLiq/BsQV0KayFHT2etm6G/OGwRSfHuVokMbB+onfN4jZYduJzMyXfBDianYkcXTa3vHUhQNt0y2nwIDAQAB'

    modulus, exponent = key_to_ne(pubkey)

    print(modulus, exponent)

    #通过公钥指数和模数
    message = 'herish'

    #通过模数和指数来实现RSA加密
    modulus = int(modulus, 16)
    exponent = int(exponent, 16)
    rsa_pubkey = rsa.PublicKey(modulus, exponent)
    print(rsa_pubkey)
    crypto = rsa.encrypt(message.encode(), rsa_pubkey)
    b64str = base64.b64encode(crypto)
    print(b64str)


