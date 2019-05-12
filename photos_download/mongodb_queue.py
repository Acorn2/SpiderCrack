#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/5/12 9:44
software: PyCharm
description: 
'''

from datetime import datetime, timedelta
from pymongo import MongoClient, errors
from photos_download.setting import *

class MogoQueue():

    OUTSTANDING = 1 ##初始状态
    PROCESSING = 2 ##正在下载状态
    COMPLETE = 3 ##下载完成状态

    def __init__(self, timeout=10):##初始mongodb连接
        self.client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        self.db = self.client[MONGO_DB]
        self.collection = self.db[MONGO_COL]
        self.timeout = timeout

    def __bool__(self):
        """
        $ne的意思是不匹配，如果所有图片都是下载完成状态，则返回False
        """
        record = self.collection.find_one(
            {'status': {'$ne': self.COMPLETE}}
        )
        return True if record else False

    def push(self, url, title): ##这个函数用来添加新的URL进队列
        try:
            self.collection.insert({'_id': url, 'status': self.OUTSTANDING, 'title': title})
            print(url, '插入队列成功')
        except errors.DuplicateKeyError as e:  ##报错则代表已经存在于队列之中了
            print(url, '已经存在于队列中了')
            pass
        

    def pop(self):
        """
        这个函数会查询队列中的所有状态为OUTSTANDING的值，
        更改状态，（query后面是查询）（update后面是更新）
        并返回_id（就是我们的ＵＲＬ），MongDB好使吧，^_^
        如果没有OUTSTANDING的值则调用repair()函数重置所有超时的状态为OUTSTANDING，
        $set是设置的意思，和MySQL的set语法一个意思
        """
        record = self.collection.find_one_and_update(
            {'status': self.OUTSTANDING},
            {'$set': {'status': self.PROCESSING,'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
        )
        if record:
            return record
        else:
            self.repair()
            raise KeyError


    def pop_title(self, url):
        record = self.collection.find_one({'_id': url})
        return record['title']

    def peek(self):
        """这个函数是取出状态为 OUTSTANDING的文档并返回_id(URL)"""
        record = self.collection.find_one({'status': self.OUTSTANDING})
        if record:
            return record['_id']

    def complete(self, url):
        """这个函数是更新已完成的URL完成"""
        self.collection.update({'_id': url}, {'$set': {'status': self.COMPLETE}})

    def repair(self):
        """这个函数是重置状态$lt是小于，该方法主要是用于判断2状态的可能下载失败"""
        dl = datetime.now() - timedelta(seconds=self.timeout)
        record = self.collection.update_many(
            {
                'timestamp': {'$lt': dl.strftime("%Y-%m-%d %H:%M:%S")},
                'status': self.PROCESSING
            },
            {'$set': {'status': self.OUTSTANDING}}
        )

    def clear(self):
        """这个函数只有第一次才调用、后续不要调用、因为这是删库啊！"""
        self.collection.drop()

    def num(self):
        record = self.collection.find(
            {'status': self.PROCESSING}
        ).count()
        return record

    def reset(self):
        record = self.collection.update_many(
            {
                'status': self.PROCESSING
            },
            {'$set': {'status': self.OUTSTANDING}}
        )
