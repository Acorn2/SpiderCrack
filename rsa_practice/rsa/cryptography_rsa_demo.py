#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/6/13 9:46
software: PyCharm
description: Python 利用cryptography包进行rsa加密/解密， 签名/验证
'''

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives.serialization import NoEncryption,\
    Encoding, PrivateFormat, PublicFormat
import base64
from cryptography.exceptions import InvalidSignature

ALGORITHM_DICT = {
        'sha1': hashes.SHA1(),
        'sha224': hashes.SHA224(),
        'sha256': hashes.SHA256(),
        'sha384': hashes.SHA384(),
        'sha512': hashes.SHA512()
    }

def generate_keys():
    '''
    生成公钥和私钥
    :return:
    '''
    privkey = rsa.generate_private_key(
        public_exponent=65537,
        key_size=1024,
        backend=default_backend(),
    )

    new_privkey = privkey.private_bytes(
        Encoding.PEM,
        PrivateFormat.PKCS8,
        NoEncryption()
    )

    pubkey = privkey.public_key()

    new_pubkey = pubkey.public_bytes(
        Encoding.PEM,
        PublicFormat.SubjectPublicKeyInfo,
    )

    print(new_pubkey, new_privkey)
    return pubkey, privkey

def rsaEncrypt(message, pubkey, algorithm='sha1'):
    '''
    公钥加密
    :param message:
    :param pubkey:
    :param algorithm:密码散列函数算法
    :return:
    '''
    if not isinstance(message, bytes):
        message = message.encode()

    algorithm = ALGORITHM_DICT.get(algorithm)
    padding_data = padding.OAEP(
        mgf=padding.MGF1(algorithm=algorithm),
        algorithm=algorithm,
        label=None
    )
    ciphertext = pubkey.encrypt(message, padding_data)
    ciphertext = base64.b64encode(ciphertext)
    print(ciphertext)

    return ciphertext

def rsaDecrypt(result, privkey, algorithm='sha1'):
    '''
    私钥解密
    :param result:加密后的内容
    :param privkey:
    :param algorithm:密码散列函数算法
    :return:
    '''
    algorithm = ALGORITHM_DICT.get(algorithm)
    padding_data = padding.OAEP(
        mgf=padding.MGF1(algorithm=algorithm),
        algorithm=algorithm,
        label=None
    )

    result = base64.b64decode(result)

    content = privkey.decrypt(result, padding_data).decode()
    print(content)

    return content

def execute_without_signature(pubkey, privkey):
    #公钥加密，私钥解密
    message = 'herish'
    ciphertext = rsaEncrypt(message, pubkey, 'sha256')
    content = rsaDecrypt(ciphertext, privkey, 'sha256')

    print("rsa test success！")

def sign(message, privkey, algorithm='sha1'):
    '''
    私钥签名
    :param message:
    :param privkey:
    :param algorithm:
    :return:
    '''
    if not isinstance(message, bytes):
        message = message.encode()

    algorithm = ALGORITHM_DICT.get(algorithm)
    padding_data = padding.PSS(
        mgf=padding.MGF1(algorithm),
        salt_length=padding.PSS.MAX_LENGTH
    )

    return privkey.sign(message, padding_data, algorithm)


def verify(message, signature, pubkey, padding_mode='pss', algorithm='sha1'):
    '''
    公钥验签
    :param message:
    :param signature:
    :param pubkey:
    :param padding_mode:
    :param algorithm:
    :return:
    '''
    if not isinstance(message, bytes):
        message = message.encode()

    algorithm = ALGORITHM_DICT.get(algorithm)

    if padding_mode == 'pkcs1':
        padding_data = padding.PKCS1v15()
    else:
        padding_data = padding.PSS(
        mgf=padding.MGF1(algorithm),
        salt_length=padding.PSS.MAX_LENGTH
    )

    try:
        pubkey.verify(signature, message,
                          padding_data, algorithm)
    except InvalidSignature:
        padd_verify = False
    else:
        padd_verify = True

    return padd_verify

def execute_with_signature(pubkey, privkey):

    text = 'herish'
    signature = sign(text, privkey, 'sha256')
    assert verify(message=text, signature=signature, pubkey=pubkey, algorithm='sha256')
    print("rsa Signature verified!")

if __name__ == '__main__':
    pubkey, privkey = generate_keys()

    ############ 使用公钥 - 私钥对信息进行"加密" + "解密" ##############
    # execute_without_signature(pubkey, privkey)

    ############ 使用私钥 - 公钥对信息进行"签名" + "验签" ##############
    execute_with_signature(pubkey, privkey)