#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/5/12 8:32
software: PyCharm
description: 
'''

from pymongo import MongoClient
from photos_download.setting import *

class MongoDB():
    def __init__(self):
        self.client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        self.db = self.client[MONGO_DB]
        self.collection = self.db[MONGO_COL]

    def insert(self, data):
        '''
        插入数据
        :return:
        '''
        try:
            if isinstance(data,dict):
                self.collection.insert_one(data)
            elif isinstance(data,list):
                self.collection.insert_many(data)
        except Exception as e:
            print(e)

    def read(self):
        '''
        读取数据，暂时设定读取所有
        :return:
        '''
        datas = []
        results = self.collection.find()
        for item in results:
            datas.append(item)
        return datas

    def count(self):
        '''
        统计数据条目
        :return:
        '''
        return self.collection.find().count()

    def delete(self):
        try:
            self.collection.delete_one()
        except Exception as e:
            print(e)

if __name__ == '__main__':
    mongo = MongoDB()