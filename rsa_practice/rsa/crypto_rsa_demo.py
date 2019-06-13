#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/6/13 8:11
software: PyCharm
description:  Python 利用Crypto包进行rsa加密/解密， 签名/验证
'''

from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5    #用于加密
import base64
import Crypto.Signature.PKCS1_v1_5 as sign_PKCS1_v1_5 #用于签名/验签
from Crypto import Hash

def generate_rsa_keys():

    random_generator = Random.new().read
    key = RSA.generate(1024, random_generator) #使用伪随机数来辅助生成

    # key = RSA.generate(1024)

    pubkey = key.publickey().export_key('PEM')  #默认是 PEM的
    privkey = key.export_key('PEM')

    return pubkey, privkey

def rsaEncrypt(message, pubkey):
    '''
    RSA加密
    :param message: 被加密的字符串
    :param pubkey: 公钥
    :return:
    '''
    rsakey = RSA.import_key(pubkey)
    cipher = PKCS1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(message.encode()))


    print(cipher_text)
    return cipher_text

def rsaDecrypt(result, privkey):
    '''
    私钥解密
    :param result:
    :param privkey:
    :return:
    '''
    result = base64.b64decode(result)

    rsakey = RSA.import_key(privkey)
    cipher = PKCS1_v1_5.new(rsakey)
    content = cipher.decrypt(result, Random.new().read).decode()
    print(content)


def save(key, filename):
    # 保存密钥
    with open(filename, 'w+') as f:
        f.write(key)

def read(filename):
    # 导入密钥
    with open(filename, 'rb') as f:
        key = f.read()
        return key

def skey_to_pkey(privkey):
    '''
    已知私钥的情况下，生成公钥
    :param privkey:
    :return:
    '''
    s_key = RSA.import_key(privkey)
    p_key = s_key.publickey().export_key()

    return p_key

def sign_with_privkey(message, privkey):
    '''
    私钥签名
    :param message:明文
    :param privkey:
    :return:密文
    '''
    signer = sign_PKCS1_v1_5.new(RSA.import_key(privkey))
    rand_hash = Hash.SHA256.new()
    rand_hash.update(message.encode())
    signature = signer.sign(rand_hash)

    return signature

def verify_with_pubkey(signature, message, pubkey):
    '''
    公钥验签
    :param signature:密文
    :param message:明文
    :param pubkey:公钥
    :return:
    '''
    verifier = sign_PKCS1_v1_5.new(RSA.import_key(pubkey))
    rand_hash = Hash.SHA256.new()
    rand_hash.update(message.encode())
    verify = verifier.verify(rand_hash, signature)

    return verify

def execute_without_signature(pubkey, privkey):
    '''
    公钥加密，私钥解密
    :param pubkey:
    :param privkey:
    :return:
    '''
    message = 'acorn'
    result = rsaEncrypt(message, pubkey)
    rsaDecrypt(result, privkey)
    print("rsa test success！")


def execute_with_signature(pubkey, privkey):
    '''
    签名验证，不加密
    :param pubkey:
    :param privkey:
    :return:
    '''
    text = 'herish'
    assert verify_with_pubkey(sign_with_privkey(text,privkey), text, pubkey)
    print("rsa Signature verified!")

if __name__ == '__main__':
    pubkey, privkey = generate_rsa_keys()
    print(pubkey, privkey)

    ############ 使用公钥 - 私钥对信息进行"加密" + "解密" ##############
    execute_without_signature(pubkey, privkey)

    ############ 使用私钥 - 公钥对信息进行"签名" + "验签" ##############
    execute_with_signature(pubkey, privkey)
