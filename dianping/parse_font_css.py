#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/4/29 9:48
software: PyCharm
description: 
'''

import re
from lxml import etree
# from requests_html import HTMLSession
import requests
import bisect
import time

html_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Host': 'www.dianping.com',
    'Cookie': 's_ViewType=10; _lxsdk_cuid=16a66be5838c8-0e92fe3848c569-e323069-1fa400-16a66be5838c8; _lxsdk=16a66be5838c8-0e92fe3848c569-e323069-1fa400-16a66be5838c8; _hc.v=a84aaa1c-edb5-f595-f6d2-34f37f1dbaa8.1556501912; _lxsdk_s=16a8afe0762-a2-25b-01f%7C%7C40',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
}

css_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
}


class DianPing(object):
    def __init__(self):
        # 此处以爬取第一页中的评论数为例
        self.stat_url = 'http://www.dianping.com/huizhou/ch10/g103'
        self.font_size = 14  # 字的大小font-size
        self.start_y = 23

    @staticmethod
    def parse_url(url, headers):
        # 解析并返回页面内容
        # headers = {
        #     'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        #     'Accept-Encoding': 'gzip, deflate',
        #     'Accept-Language': 'zh-CN,zh;q=0.9',
        #     'Host': 'www.dianping.com',
        #     'Cookie': 's_ViewType=10; _lxsdk_cuid=16a66be5838c8-0e92fe3848c569-e323069-1fa400-16a66be5838c8; _lxsdk=16a66be5838c8-0e92fe3848c569-e323069-1fa400-16a66be5838c8; _hc.v=a84aaa1c-edb5-f595-f6d2-34f37f1dbaa8.1556501912; _lxsdk_s=16a8afe0762-a2-25b-01f%7C%7C40',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
        # }
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        if 200 == response.status_code:
            return response.content.decode()
        else:
            return None
        # session = HTMLSession()
        # response = session.get(url)
        # return response.content.decode()

    # 定义css的URL地址
    def get_css(self, html, headers):
        # svg_text_css = re.search(r'href="([^"]+svgtextcss[^"]+)"', html, re.M)
        # svg_text_css = re.search(r'href="(.*?svgtextcss.*?css)">', html,re.S)
        svg_text_css = re.findall(r'href="(.*?svgtextcss.*?css)">', html, re.M)
        if not svg_text_css:
            return False
            # raise Exception("未找到链接")
        css_url = 'http:' + svg_text_css[0]
        print(css_url)
        content = self.parse_url(css_url, headers)
        return content

    # 获取定义偏移量的css文件后将结果以字典形式存储
    @staticmethod
    def get_css_offset(css_content):
        """
        通过传入页面中任意css获取其对应的偏移量
        :return: {'xxx': ['192', '1550']}
        """
        offset_item = re.findall(r'\.([a-zA-Z0-9]{5,6}).*?background:-(.*?).0px -(.*?).0px', css_content)
        if not offset_item:
            return False
        result = {}
        for item in offset_item:
            css_class = item[0]
            x_offset = int(item[1])
            y_offset = int(item[2])
            result[css_class] = [x_offset, y_offset]

        return result

    # 获取svg url组
    @staticmethod
    def get_svg_url_dict(css_content):
        # items = re.findall(r'span\[class\^="(.*?)"\].*?width: (\d+)px;.*?background-image: url\((.*?)\);', css_content)
        # items = re.findall(r'background-image:.*?\((.*?svg)\)', css_content)
        items = re.findall(r'\[class\^="(.*?)"\].*?width: (\d+)px;.*?background-image: url\((.*?)\);', css_content)

        result = {}
        for code, size, url in items:
            svg_list = [int(size), 'https:' + url]
            result[code] = svg_list
        return result

    # 根据偏移量找到对应的数字
    def parse_comment_css(self, svg_url, size, x_offset, y_offset):
        # print(size)  # 要用size做像素偏移
        svg_html = self.parse_url(svg_url, css_headers)
        pattern = re.compile(r'y=.*?(\d+)">(\d+)</text>', re.S)
        items = re.findall(pattern, svg_html)
        # font_dict = {}
        #
        # for y, string in items:
        #     y_offset = self.start_y - int(y)
        #     sub_font_dict = {}
        #     for j, font in enumerate(string):
        #         x_offset = -j * self.font_size
        #         sub_font_dict[x_offset] = font
        #
        #     font_dict[y_offset] = sub_font_dict
        svg_list = []

        y_list = []
        for item in items:
            y_list.append(int(item[0]))
            svg = {'y_key': int(item[0]), 'text': item[1]}
            svg_list.append(svg)
        x, y = int(x_offset), int(y_offset)
        x_position = x // 12
        y_position = bisect.bisect(y_list, y)
        return svg_list[y_position]['text'][x_position]
        # if y <= svg_list[0]['y_key']:
        #     return svg_list[0]['text'][x // 12]
        # elif y <= svg_list[1]['y_key']:
        #     return svg_list[1]['text'][x // 12]
        # else:
        #     return svg_list[2]['text'][x // 12]

    # 获取点评数
    def get_comment_num(self):
        content = self.parse_url(self.stat_url, html_headers)
        html = etree.HTML(content)
        shops = html.xpath('.//div[@id="shop-all-list"]/ul/li')  # 获取到所有店面
        content_css = self.get_css(content, css_headers)
        css_class_dirt = self.get_css_offset(content_css)  # 偏移量字典存储
        print(css_class_dirt)
        svg_url_dict = self.get_svg_url_dict(content_css)  # svg的url dict储存
        print(svg_url_dict)
        for shop in shops:
            shop_name = shop.xpath('.//div[@class="tit"]/a/@title')[0]  # 获取店名
            review_num = shop.xpath('.//div[@class="comment"]/a[contains(@class,"review-num")]/b')[0]  # 获取可见的数字
            num = 0
            if review_num.text:
                # if 有可见字
                num = int(review_num.text)
            for review_node in review_num:
                """每个字符解密一次"""
                css_class = review_node.attrib["class"]  # 取css名
                # 根据css名称获取偏移量
                x_offset, y_offset = css_class_dirt[css_class][0], css_class_dirt[css_class][1]
                # 根据偏移量来找到对应的数字
                svg = svg_url_dict.get(css_class[:2], None)
                if not svg:
                    svg = svg_url_dict[css_class[:3]]
                size = svg[0]
                svg_url = svg[1]
                new_num = self.parse_comment_css(svg_url, size, x_offset, y_offset)
                num = num * 10 + int(new_num)
            print("餐馆: {}, 点评数: {}".format(shop_name, num))

    def get_font_dict_by_offset(self, url):
        """
            获取坐标偏移的文字字典, 会有最少两种形式的svg文件（目前只遇到两种）
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
        }
        res = requests.get(url, headers=headers)
        html = res.text
        font_dict = {}
        y_list = re.findall(r'd="M0 (\d+?) ', html)
        if y_list:
            font_list = re.findall(r'<textPath .*?>(.*?)<', html)
            for i, string in enumerate(font_list):
                y_offset = self.start_y - int(y_list[i])

                sub_font_dict = {}
                for j, font in enumerate(string):
                    x_offset = -j * self.font_size
                    sub_font_dict[x_offset] = font

                font_dict[y_offset] = sub_font_dict
        else:
            font_list = re.findall(r'<text.*?y="(.*?)">(.*?)<', html)

            for y, string in font_list:
                y_offset = self.start_y - int(y)
                sub_font_dict = {}
                for j, font in enumerate(string):
                    x_offset = -j * self.font_size
                    sub_font_dict[x_offset] = font

                font_dict[y_offset] = sub_font_dict
            # print(font_dict)
        return font_dict


if __name__ == '__main__':
    dian_ping = DianPing()

    dian_ping.get_comment_num()
