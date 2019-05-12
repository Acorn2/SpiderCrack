#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/5/12 9:08
software: PyCharm
description: 将多进程和多线程结合使用，用来下载图片
'''

import time
import threading
from photos_download.download_text import request
import multiprocessing
from photos_download.mongodb_queue import MogoQueue
import os
from hashlib import md5



def mzitu_crawler(max_threads=10):
    crawl_queue = MogoQueue()
    def pageurl_crawler():
        while True:
            try:
                photo = crawl_queue.pop()#取出的同时，设置url为正在下载状态
                url = photo['_id']
                print(url)
            except KeyError:
                print('队列没有数据')
                break
            else:
                download_flag = download_photo(photo)
                if download_flag:
                    crawl_queue.complete(url)  ##设置为完成状态


    def download_photo(photo):
        title = photo['title']
        url = photo['_id']
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
            return True
        else:
            return False
            print('Failed to Save Image')

    threads = []
    while crawl_queue:
        # print('Process----------{0}-------len(threads)---{1}'.format(multiprocessing.current_process().name,len(threads)))
        """
        这儿crawl_queue用上了，就是我们__bool__函数的作用，为真则代表我们MongoDB队列里面还有数据
        crawl_queue为真都代表我们还没下载完成，程序就会继续执行
        """
        for thread in threads:
            # print('Thread-------{0}-------{1}'.format(thread.name,thread.is_alive()))
            if not thread.is_alive():  ##is_alive是判断是否为空,不是空则在队列中删掉
                threads.remove(thread)
        while len(threads) < max_threads or crawl_queue.peek():  ##线程池中的线程少于max_threads 或者 crawl_qeue时
            # thread = PhotoThread(photos_queue)  ##创建线程
            thread = threading.Thread(target=pageurl_crawler) ##创建线程
            thread.setDaemon(True)  ##设置守护线程
            thread.start()  ##启动线程
            threads.append(thread)  ##添加进线程队列
        time.sleep(1)

def process_crawler():
    process = []
    num_cpus = multiprocessing.cpu_count()
    print('将会启动进程数为：', num_cpus)
    for i in range(num_cpus):
        p = multiprocessing.Process(target=mzitu_crawler)  ##创建进程
        p.start()  ##启动进程
        process.append(p)  ##添加进进程队列
    for p in process:
        p.join()  ##等待进程队列里面的进程结束

if __name__ == '__main__':
    start_time = time.time()

    process_crawler()

    end_time = time.time()
    print('耗时{}s'.format((end_time - start_time)))