#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/5/11 20:02
software: PyCharm
description: 使用多线程下载图片，提高效率
'''

import threading
import queue
import os
from photos_download.download_text import request
from hashlib import md5
from photos_download.mongo_db import MongoDB
import time


class PhotoThread(threading.Thread):
    def __init__(self, que):
        threading.Thread.__init__(self)
        self.que = que

    def run(self):
        while True:
            photo = self.que.get()
            self.que.task_done()
            if photo == None:
                break
            self.download_photo(photo)

    def download_photo(self,photo):
        title = photo['title']
        url = photo['photo_url']
        fpath = 'MM_photo/' + title
        if not os.path.exists(fpath):
            os.mkdir(fpath)

        response = request.get(url, 3)
        if response != None:
            file_path = '{0}/{1}.{2}'.format(fpath, md5(response.content).hexdigest(), 'jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as fw:
                    fw.write(response.content)
            else:
                print('Already Download', file_path)
        else:
            print('Failed to Save Image')

photos_queue = queue.Queue()

def get_photo():
    mongo = MongoDB()
    datas = mongo.read()
    for photo in datas:
        photos_queue.put(photo)

def photo_download():
    # 爬取图片详情页面，获取所有图片地址
    threads_photo_download = []
    for i in range(8):
        t = PhotoThread(photos_queue)
        threads_photo_download.append(t)

    for t in threads_photo_download:
        t.start()

    for t in threads_photo_download:
        t.que.put(None)

    photos_queue.join()
    print('所有图片下载完毕！')

if __name__ == '__main__':
    start_time = time.time()

    get_photo()
    time.sleep(1)
    print('图片相关信息读取完毕，已放入到队列中。')
    photo_download()
    # for i in range(photos_queue.qsize()):
    #     print(photos_queue.get_nowait())

    end_time = time.time()
    print('耗时{}s'.format((end_time - start_time)))
