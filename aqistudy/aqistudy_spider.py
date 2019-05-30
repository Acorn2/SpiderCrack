#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/5/28 18:46
software: PyCharm
description: 中国空气质量分析平台 https://www.aqistudy.cn/html/city_detail.html
js解密，进行页面信息爬取
'''

import requests
from pyquery import PyQuery as pq
import re
import execjs
from urllib.request import quote
import json


class AqiStudy():
    def __init__(self, city='',startTime='', endTime=''):
        self.login_api = 'https://www.aqistudy.cn/apinew/aqistudyapi.php'
        self.city = city
        self.startTime = '2019-05-27 00:00:00'
        self.endTime = '2019-05-28 13:00:00'
        self.checkTime(startTime, endTime)

        self.headers = {
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }
        self.login_data = {
            "city": '',
            "type": "HOUR",
            "startTime": '',
            "endTime": ''
        }

    def get_html(self):
        '''
        向服务器发送post请求，获取返回信息
        :return:
        '''

        self.login_data.update({
            "city": self.city,
            "type": "HOUR",
            "startTime": self.startTime,
            "endTime": self.endTime
        })
        data = self.encrypt(self.login_data)

        '''
        在用Python发起网络请求的时候，有一些场景会需要对传入的参数进行URL编码后再进行请求
         针对字符、字符串的URL编码,urllib.quote()函数（在处理空格的时候，urllib.quote()会将空格替换成「%20」，而urllib.quote_plus()会将空格替换成「+」号）
        '''
        data = quote(data)#必须经过urlencode编码，不然response返回值错误
        form_data = 'd={}'.format(data)
        print('FORM_DATA:' + form_data)
        # 将Form-Data 加密才能进行 POST 传递，
        try:
            response = requests.post(self.login_api, data=form_data, headers=self.headers)
            if 200 == response.status_code:
                response.encoding = response.apparent_encoding

                resp_text = response.text
                print(resp_text)
                return self.decrypt(resp_text)
            return None
        except requests.ConnectionError as e:
            return None

    def encrypt(self, form_data):
        '''
        对查询条件栏的数据，进行加密
        :param form_data: 查询条件栏的数据，包括城市名称，开始结束时间等
        :return:加密后的字符串
        '''
        with open('encrypt.js',encoding='utf-8') as f:
            js = execjs.compile(f.read())
            return js.call('getAQIData',form_data)

    def decrypt(self, resp_text):
        '''
        对服务器请求成功后返回的数据，进行解密
        :param resp_text: 返回的数据
        :return:解密后的字符串，json格式
        '''
        with open('encrypt.js',encoding='utf-8') as f:
            js = execjs.compile(f.read())
            return js.call('decodeData',resp_text)

    def parse(self, json_data):
        '''
        对获取的数据，进行解析
        :param json_data:
        :return:
        '''
        data = json_data['result']['data']
        total = data['total']

        for line_data in data['rows']:
            print(line_data)

    def checkTime(self, startTime, endTime):
        '''
        对输入的时间格式进行校验，如果有误，则使用默认值
        :param startTime:
        :param endTime:
        :return:
        '''
        try:
            self.startTime = re.match(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}', startTime).group(0)
            self.endTime = re.match(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}', endTime).group(0)
        except:
            print('时间格式错误！')

    def run(self):
        json_data = self.get_html()
        print(json_data)
        self.parse(json_data)


if __name__ == '__main__':
    aqi = AqiStudy(city='北京', startTime='2019-05-27 13:00:00', endTime='2019-05-28 16:00:00')
    aqi.run()

