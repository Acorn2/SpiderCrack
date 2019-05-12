#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/5/8 19:46
software: PyCharm
description: 
'''

import requests
from pyquery import PyQuery as pq
from multiprocessing.pool import Pool
import time
import multiprocessing

headers = {
    'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'accept-encoding' : 'gzip, deflate, br',
    'upgrade-insecure-requests' : '1',
    'cookie' : 'UM_distinctid=16a97460c0359-0dc67e4a2a1a1-6353160-1fa400-16a97460c046c4; CNZZDATA1262975970=78124181-1557313537-%7C1557313537; Hm_lvt_59a3be2dc00f62179c757cb93353934b=1557316112; Hm_lpvt_59a3be2dc00f62179c757cb93353934b=1557316143',
    'usr-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
}


def get_text(url):
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding

    try:
        if 200 == response.status_code:
            return response.text
        return None
    except requests.ConnectionError as e:
        print(e.args)
        return None


def spider(url):
    html = get_text(url)
    doc = pq(html)
    items = doc('.excerpt-c5').items()

    for item in items:
        title = item.find('h2').text()
        photo_url = item.find('.thumbnail > img').attr('data-src')
        photo_page_url = item.find('h2 > a').attr('href')

        print(title,photo_url)


if __name__ == '__main__':
    start_time = time.time()
    num_cpus = multiprocessing.cpu_count()
    print('将会启动进程数为：', num_cpus)
    pool = Pool(num_cpus)
    url_list = []

    for i in range(1, 10):
        url = 'https://www.lovemmtu.net/page/{}'.format(i)
        url_list.append(url)
        # spider(url)

    # print(get_text('https://www.lovemmtu.net/page/4'))
    pool.map(spider, url_list)
    pool.close()
    pool.join()

    end_time = time.time()
    print('耗时{}s'.format((end_time-start_time)))
