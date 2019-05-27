#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/5/26 10:22
software: PyCharm
description:
参考资料：https://zhuanlan.zhihu.com/p/57375111
https://zhuanlan.zhihu.com/p/34073256
'''

import getpass
import threading

import base64
import hashlib
import hmac
import json, re, time
from http import cookiejar
from urllib.parse import urlencode
import execjs
import requests
from PIL import Image
import matplotlib.pyplot as plt


class ZhihuAccount():
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

        self.login_data = {
            'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
            'grant_type': 'password',
            'source': 'com.zhihu.web',
            'username': '',
            'password': '',
            'lang': 'en',
            'ref_source': 'homepage',
            'utm_source': ''
        }

        self.session = requests.session()
        self.session.headers = {
            'accept-encoding': 'gzip, deflate, br',
            'Host': 'www.zhihu.com',
            'Referer': 'https://www.zhihu.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }

        self.session.cookies = cookiejar.LWPCookieJar(filename='./cookies/zhihu_cookie.txt')  # 检索cookie信息并将cookie存储到文件中

    def login(self, captcha_lang='en', load_cookies=True):
        """
        模拟登录知乎
        :param captcha_lang: 验证码类型 'en' or 'cn'
        :param load_cookies: 是否读取上次保存的 Cookies
        :return: bool
        若在 PyCharm 下使用中文验证出现无法点击的问题，
        需要在 Settings / Tools / Python Scientific / Show Plots in Toolwindow，取消勾选
        """
        #如果有登录成功的cookie文件，则直接进行利用cookie进行登录
        if load_cookies and self.load_cookies():
            print('读取 Cookies 文件')
            if self.check_login():
                print('登录成功')
                return True
            print('Cookies 已过期')

        #获取帐号和密码
        # self._check_user_pass()
        self.login_data.update({
            'username': self.username,
            'password': self.password,
            'lang': captcha_lang
        })

        #获取时间戳（13位）int(1558944432.1055813 * 1000)= 1558944432105
        timestamp = int(time.time() * 1000)
        print('signature:' + self._get_signature(timestamp))
        self.login_data.update({
            'captcha': self._get_captcha(self.login_data['lang']),
            'timestamp': timestamp,
            'signature': self._get_signature(timestamp)
        })

        headers = self.session.headers.copy()
        print('x-xsrftoken: ' + self._get_xsrf())
        #x-xsrftoken则是防 Xsrf 跨站的 Token 认证,用于登录验证
        headers.update({
            'content-type': 'application/x-www-form-urlencoded',
            'x-zse-83': '3_1.1',
            'x-xsrftoken': self._get_xsrf()
        })

        #将帐号和密码以及验证码，signature进行加密，提交到api中
        data = self._encrypt(self.login_data)
        print('FORM_DATA:' +data)
        login_api = 'https://www.zhihu.com/api/v3/oauth/sign_in'

        #将Form-Data 加密才能进行 POST 传递，
        response = self.session.post(login_api, data=data, headers=headers)

        if 'error' in response.text:
            print(json.loads(response.text)['error'])
        if self.check_login():
            print('登录成功')
            return True
        print('登录失败')
        return False

    def load_cookies(self):
        """
       读取 Cookies 文件加载到 Session
       :return: bool
       """
        try:
            # 从文件加载cookie
            # ignore_discard的意思是即使cookies将被丢弃也将它保存下来，ignore_expires的意思是如果在该文件中 cookies已经存在，则覆盖原文件写入
            self.session.cookies.load(ignore_discard=True)
            return True
        except FileNotFoundError:
            return False

    def check_login(self):
        """
       检查登录状态，访问登录页面出现跳转则是已登录，
       如登录成功保存当前 Cookies
       :return: bool
       """
        login_url = 'https://www.zhihu.com/signin'
        response = self.session.get(login_url)

        print(response.text.encode('utf-8'))
        if response.status_code == 200:
            # self.session.cookies.save()
            return True
        return False

    def _get_xsrf(self):
        """
        从登录页面获取 xsrf
        :return: str
        """
        self.session.get('https://www.zhihu.com/', allow_redirects=False)#禁止重定向
        for c in self.session.cookies:
            if c.name == '_xsrf':
                return c.value
        raise AssertionError('获取xsrf失败')

    def _get_captcha(self, lang):
        """
        请求验证码的 API 接口，无论是否需要验证码都需要请求一次
        如果需要验证码会返回图片的 base64 编码
        根据 lang 参数匹配验证码，需要人工输入
        :param lang: 返回验证码的语言(en/cn)
        :return: 验证码的 POST 参数
        """
        if lang == 'cn':
            api = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=cn'
        else:
            api = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'

        response = self.session.get(api)

        if response.status_code == 200 and 'true' in response.text:
            put_response = self.session.put(api)
            # json_data = json.loads(put_response.text)
            json_data = put_response.json()
            img_base64 = json_data['img_base64'].replace(r'\n', '')

            with open('./img/captcha.jpg', 'wb') as f:
                f.write(base64.b64decode(img_base64))

            img = Image.open('./img/captcha.jpg')

            if lang == 'cn':
                plt.imshow(img)
                print('点击所有倒立的汉字，在命令行中按回车提交')
                points = plt.ginput(7)
                capt = json.dumps({'img_size': [200, 44],
                                   'input_points': [[i[0] / 2, i[1] / 2] for i in points]})

            else:
                # img.show()
                img_thread = threading.Thread(target=img.show, daemon=True)
                img_thread.start()
                capt = input('请输入图片里的验证码：')

            self.session.post(api, data={'input_text': capt})

            return capt
        return ''

    def _get_signature(self, timestamp):
        """
        通过 Hmac 算法计算返回签名
        实际是几个固定字符串加时间戳
        :param timestamp: 时间戳
        :return: 签名
        """
        ha = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod=hashlib.sha1)#js中可以找这个字符串
        grant_type = self.login_data['grant_type']
        client_id = self.login_data['client_id']
        source = self.login_data['source']
        ha.update(bytes((grant_type + client_id + source + str(timestamp)), 'utf-8'))
        return ha.hexdigest()

    def _check_user_pass(self):

        if not self.username:
            self.username = input('请输入手机号或邮箱：')

        # 如果输入的是手机号，则进行校验
        if self.username.isdigit() and '+86' not in self.username:
            self.username = '+86' + self.username

        if not self.password:
            # 输入密码不可见
            self.password = getpass.getpass('password:')

    @staticmethod
    def _encrypt(form_data: dict):
        with open('./encrypt.js') as f:
            js = execjs.compile(f.read())
            return js.call('Q', urlencode(form_data))

    def run(self):
        '''
        知乎模拟登录，默认不需要校验，如果需要校验，假设默认是输入图片验证码；其次是点击图片中倒立的汉字
        :return:
        '''

        flag = False

        while flag:
            try:
                flag = self.login(captcha_lang='en',load_cookies=False)
            except:
                print('需要点击倒立的中文汉字进行校验')
                flag = self.login(captcha_lang='cn',load_cookies=True)


if __name__ == '__main__':
    account = ZhihuAccount(uusername='', password='')
    account.run()
