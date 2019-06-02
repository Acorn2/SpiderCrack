#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/5/31 20:11
software: PyCharm
description: 七麦数据网，中国App Store 排行榜
参考网址：https://blowingdust.com/encrypted-compression-javascript-analysis.html
'''

import requests
import json
import base64
import time
from urllib.request import quote
from urllib.parse import urlencode


class Qimai():
    def __init__(self, date):
        self.base_url = 'https://api.qimai.cn'

        self.url = '/rank/indexPlus/brand_id/'

        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.qimai.cn/rank",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
        }

        self.params = {
            "brand": "all",
            "country": "cn",
            "date": date,
            "device": "iphone",
            "genre": "5000",
            "page": 1
        }

    def get_html(self, url):
        '''
        获取网页内容
        :param url:
        :return:
        '''
        response = requests.get(url, headers=self.headers)

        response.encoding = response.apparent_encoding
        try:
            if 200 == response.status_code:
                return response.text
            return None
        except requests.ConnectionError as e:
            return None

    def encrypt(self, a, n="00000008d78d46a"):
        '''
        加密函数，
        :param a:拼接后的数据
        :param n:加密时需要的数据，具有时间性，会有变化
        :return:加密后的字段
        '''
        s = list(a)
        n = list(n)
        nl = len(n)
        for i in range(len(s)):
            #ord()函数主要用来返回对应字符的ascii码
            #chr()主要用来表示ascii码对应的字符他的输入时数字
            s[i] = chr(ord(s[i]) ^ ord(n[i % nl]))
        return "".join(s)

    def analysis(self, url):
        '''
        实现analysis参数数据
        :param url: 三个榜单的简要url信息，形如'/rank/indexPlus/brand_id/0'，'/rank/indexPlus/brand_id/1'，'/rank/indexPlus/brand_id/2'
        :return:
        '''
        # 提取查询参数值并排序
        s = "".join(sorted([str(v) for v in self.params.values()]))
        # Base64 Encode
        s = base64.b64encode(bytes(s, encoding="ascii"))
        # 时间差
        t = str(int((time.time() * 1000) - 1515125653845))

        # 拼接自定义字符串
        s = "@#".join([s.decode(), url, t, "1"])

        # 自定义加密 & Base64 Encode
        s = base64.b64encode(bytes(self.encrypt(a=s), encoding="ascii"))
        return quote(s.decode())

    def run(self):
        '''
        爬取指定页码的APP排行信息，包括免费榜，付费榜，畅销榜
        :return:
        '''
        for page in range(1, PAGE_NUM + 1):
            self.params['page'] = page
            for i in range(3):
                url = self.url + str(i)
                analysis = self.analysis(url)
                # 拼接 URL
                url_splicing = "".join([self.base_url, url, '?analysis=', analysis, '&', urlencode(self.params)])
                print(url_splicing)

                text = self.get_html(url_splicing)
                json_data = json.loads(text)
                print(json_data)


# 页数
PAGE_NUM = 5
if __name__ == '__main__':
    qimai = Qimai("2019-06-01")
    qimai.run()
