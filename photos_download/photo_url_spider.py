#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/5/12 9:01
software: PyCharm
description: 通过多线程实现图片url地址爬取，并保存到Mongodb中
'''

from pyquery import PyQuery as pq
import time
import queue
import threading
from photos_download.download_text import request
from photos_download.mongo_db import MongoDB

page_urlqueue = queue.Queue()
detail_urlqueue = queue.Queue()
total = 0


class Thread_Crawl(threading.Thread):
    def __init__(self, que):
        threading.Thread.__init__(self)
        self.que = que

    def run(self):
        while True:
            url = self.que.get()
            self.que.task_done()
            if url == None:
                break
            self.page_spider(url)

    def page_spider(self, url):
        html = get_text(url)
        doc = pq(html)
        items = doc('.excerpt-c5').items()

        for item in items:
            title = item.find('h2').text()#标题
            photo_page_url = item.find('h2 > a').attr('href')#图片集详情地址

            detail_urlqueue.put(photo_page_url)


class Thread_Parser(threading.Thread):
    def __init__(self, que):
        threading.Thread.__init__(self)
        self.que = que

    def run(self):
        while True:
            url = self.que.get(False)
            self.que.task_done()
            if not url:
                break
            self.parse_data(url)


    def parse_data(self, url):
        global total
        html = get_text(url)
        doc = pq(html)

        items = doc('.article-content .gallery-item').items()

        title = doc('.article-title').text()
        for item in items:
            # 由于图片尺寸有限制，经测试，可以修改获取大图
            # https://pic.bsbxjn.com/wp-content/uploads/2019/05/7ee81646f32f97d-240x320.jpg
            # 改为：https://pic.bsbxjn.com/wp-content/uploads/2019/05/7ee81646f32f97d.jpg
            photo_url = item.find('.gallery-icon > a > img').attr('src')
            purl = str(photo_url)[:-12] + str(photo_url)[-4:]
            photo = {
                'title': title,
                '_id': purl,
                'status' : 1
            }
            mongo.insert(photo)
            total += 1


def get_text(url):
    response = request.get(url, 3)
    if response != None:
        return response.text
    else:
        return None


def photo_page_crawl():
    # 爬取图片列表，获取图片详情url地址
    threads_crawl = []
    for i in range(1, 2):
        url = 'https://www.lovemmtu.net/page/{}'.format(i)
        page_urlqueue.put(url)

    for i in range(2):
        t = Thread_Crawl(page_urlqueue)
        threads_crawl.append(t)

    for t in threads_crawl:
        t.start()

    for t in threads_crawl:
        t.que.put(None)

    page_urlqueue.join()
    time.sleep(1)
    print('页面图片详情url地址爬取完毕')


mongo = MongoDB()


def photo_detail_crawl():
    # 爬取图片详情页面，获取所有图片地址
    threads_parse = []
    for i in range(4):
        t = Thread_Parser(detail_urlqueue)
        threads_parse.append(t)

    for t in threads_parse:
        t.start()

    for t in threads_parse:
        t.que.put(None)

    detail_urlqueue.join()
    print('一共{0}张图片下载地址获取完毕！保存到mongodb中。'.format(total))


if __name__ == '__main__':
    start_time = time.time()

    photo_page_crawl()
    photo_detail_crawl()
    # for i in range(photos_queue.qsize()):
    #     print(photos_queue.get_nowait())

    end_time = time.time()
    print('耗时{}s'.format((end_time - start_time)))
