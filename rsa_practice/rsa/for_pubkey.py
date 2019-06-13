#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/6/12 10:52
software: PyCharm
description:
在线Rsa 公私钥分解 Exponent、Modulus，Rsa公私钥指数、系数(模数)分解，网址为：http://tool.chacuo.net/cryptrsakeyparse
Python代码实现rsa的指数模数生成公钥，参考网址：https://blog.csdn.net/jmh1996/article/details/78815005/，该网址是利用cryptography包的rsa模块实现
'''

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import rsa


#方法一
def populate_public_key(rsaExponent, rsaModulus):
    '''
    根据cryptography包下的rsa模块，对指数模数进行处理生成公钥
    :param rsaExponent:指数
    :param rsaModulus:模数
    :return:公钥
    '''
    rsaExponent = int(rsaExponent, 16)  # 十六进制转十进制
    rsaModulus = int(rsaModulus, 16)

    pubkey = rsa.RSAPublicNumbers(rsaExponent, rsaModulus).public_key(default_backend())

    return pubkey

# 将公钥以PEM格式保存到文件中
def save_pub_key(pub_key, pem_name):
    # 将公钥编码为PEM格式的数据
    pem = pub_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    # print(pem)

    # 将PEM个数的数据写入文本文件中
    with open(pem_name, 'w+') as f:
        f.writelines(pem.decode())

#方法二
def rsa_ne_key(rsaExponent, rsaModulus):
    '''
    通过rsa包依据模数和指数生成公钥，实现加密
    :param rsaExponent:
    :param rsaModulus:
    :return:
    '''
    rsaExponent = int(rsaExponent, 16)  # 十六进制转十进制
    rsaModulus = int(rsaModulus, 16)
    key = rsa.PublicKey(rsaModulus, rsaExponent)
    return key

if __name__ == '__main__':
    rsaExponent = "010001"
    rsaModulus = "008baf14121377fc76eaf7794b8a8af17085628c3590df47e6534574efcfd81ef8635fcdc67d141c15f51649a89533df0db839331e30b8f8e4440ebf7ccbcc494f4ba18e9f492534b8aafc1b1057429ac851d3d9eb66e86fce1b04527c7b95a2431b07ea277cde2365876e2733325df04389a9d891c5d36b7bc752140db74cb69f"

    pubkey = populate_public_key(rsaExponent, rsaModulus)

    # pem_file = r'pub_key.pem'
    # save_pub_key(pubkey, pem_file)

    key = rsa_ne_key(rsaModulus, rsaExponent)
    print(key)
