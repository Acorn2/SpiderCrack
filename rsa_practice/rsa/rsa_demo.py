#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/6/12 14:27
software: PyCharm
description: Python 利用RSA包加密/解密， 签名/验证
'''

import rsa
import base64

def rsaEncrypt(content, pubkey):
    '''
    对字符串进行公钥加密
    :param content: 被加密的字符串
    :return: 加密后的内容
    '''
    # content = content.encode('utf-8')#明文编码格式

    result = rsa.encrypt(content.encode(), pubkey)
    return result

def rsaDecrypt(result, privkey):
    '''
    利用rsa包进行私钥解密
    :param result: 被加密的内容
    :param privkey: 私钥
    :return: 解密后的内容
    '''
    result = base64.b64decode(result)
    print(result)
    content = rsa.decrypt(result, privkey).decode()
    # content = content.decode('utf-8')

    return content

def save(pubkey, filename):
    # 保存密钥
    with open(filename, 'w+') as f:
        f.write(pubkey.save_pkcs1().decode())

def read():
    # 导入密钥
    with open('public.pem', 'r') as f:
        pubkey = rsa.PublicKey.load_pkcs1(f.read().encode())


if __name__ == '__main__':
    ############ 使用公钥 - 私钥对信息进行"加密" + "解密" ##############
    message = 'acorn'

    #利用rsa包生成公钥、私钥，
    (pubkey, privkey) = rsa.newkeys(1024)
    print(pubkey, privkey)
    print(pubkey.save_pkcs1())

    # filename = 'public.pem'
    # save(pubkey, filename)


    result = rsaEncrypt(message, pubkey)
    result = base64.b64encode(result)
    print('加密后的密文为：{}'.format(result))

    content = rsaDecrypt(result, privkey)
    print('解密后的明文为：{}'.format(content))

    ############ 使用私钥 - 公钥对信息进行"签名" + "验签" ##############
    #明文
    mss = '重要指令'
    #私钥签名
    signature = rsa.sign(mss.encode(), privkey, 'SHA-1')
    print(signature)
    #根据收到的明文、密文，然后用公钥验证，进行身份确认
    rsa.verify(mss.encode(), signature, pubkey)
