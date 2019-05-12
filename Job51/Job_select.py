#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/5/7 16:40
software: PyCharm
description: 
'''

import requests
from pyquery import PyQuery as pq
from collections import namedtuple
from Job51.jobarea_setting import *
import os
import csv
from multiprocessing.pool import Pool
from functools import partial
import time
import threading,queue

class Job51():
    base_url = 'https://search.51job.com/list/{jobarea},000000,0000,00,9,99,{key},2,1.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
    headers  ={
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"
    }

    Job = namedtuple('Job','job_name job_href company work_place date_time salary')


    def __init__(self, jobarea_name='全国', job_name=''):
        self.job_name = job_name
        self.jobarea_code = JOBAREA[jobarea_name]
        self.next_flag = 0      #0代表搜索页面首页，1表示存在下一页，2表示下一页没有链接，即翻页结束
        self.next_url = None    #下一页的详情地址
        self.urlqueue = queue.Queue()

    def get_text(self, url):
        response = requests.get(url, headers=self.headers)
        response.encoding = response.apparent_encoding

        try:
            if 200 == response.status_code:
                return response.text
            return None
        except requests.ConnectionError as e:
            print(e.args)
            return None

    def parse(self, html):
        doc = pq(html)

        jobs_list = []
        items = doc('.dw_table .el').items()

        for item in items:
            job_name = item.find('.t1 > span > a').attr('title')
            if job_name:
                job_href = item.find('.t1 > span > a').attr('href')
                company = item.find('.t2 > a').text()
                work_place = item.find('.t3').text()
                salary = item.find('.t4').text()
                date_time = item.find('.t5').text()

                job = self.Job(job_name,job_href,company,work_place,date_time,salary)
                # print(job)
                jobs_list.append(job)
        print('当前页面共有{}个职位信息'.format(len(jobs_list)))
        return jobs_list

    Job_Detail = namedtuple('Job_Detal','job_name salary welfare job_info work_place company_name company_info')

    def parse_detail(self, urlqueue):
        while True:
            if urlqueue.empty():
                break
            url = urlqueue.get_nowait()
            html = self.get_text(url)
            doc = pq(html)

            job_name = doc('.cn > h1').text()
            salary = doc('.cn > strong').text()
            welfare = doc('.cn .jtag .t1 ').text()
            job_info = doc('.tCompany_main .job_msg').text().replace('\n',' ')
            work_place = doc('.tCompany_main > div:nth-child(2) .fp').text().replace('上班地址：','')
            company_name = doc('.cn .cname > a').text().replace('查看所有职位', '').strip()
            company_info = doc('.tCompany_main .tBorderTop_box .tmsg ').text().replace('\n',' ')

            job_detail = self.Job_Detail(job_name, salary, welfare, job_info, work_place, company_name, company_info)
            print(job_detail)
            # return job_detail

    def parse_detail2(self, url):
        html = self.get_text(url)
        doc = pq(html)

        job_name = doc('.cn > h1').text()
        salary = doc('.cn > strong').text()
        welfare = doc('.cn .jtag .t1 ').text()
        job_info = doc('.tCompany_main .job_msg').text().replace('\n',' ')
        work_place = doc('.tCompany_main > div:nth-child(2) .fp').text().replace('上班地址：','')
        company_name = doc('.cn .cname > a').text().replace('查看所有职位', '').strip()
        company_info = doc('.tCompany_main .tBorderTop_box .tmsg ').text().replace('\n',' ')

        job_detail = self.Job_Detail(job_name, salary, welfare, job_info, work_place, company_name, company_info)
        print(job_detail)
        return job_detail

    def get_next_page(self):
        html = ''
        if self.next_flag == 0:#首页内容爬取
            url = self.base_url.format(jobarea=self.jobarea_code, key=self.job_name)

        elif self.next_flag == 1:#翻页
            url = self.next_url

        print(url)
        html = self.get_text(url)
        doc = pq(html)
        items = doc('.dw_page .p_in .bk > a').items()

        if items:
            for item in items:
                if item.text() == '下一页':
                    self.next_url = item.attr('href')
                    self.next_flag = 1
                else:
                    self.next_flag = 2
        else:
            self.next_flag = 2
        return html

    def run(self):
        all_jobs_list = []
        jobs_detail_list = []
        html = self.get_next_page()

        # while self.next_flag == 1:
        #     jobs_list = self.parse(html)
        #     all_jobs_list.extend(jobs_list)
        #
        #     html = self.get_next_page()
        #
        # if self.next_flag == 2 and self.next_url:
        #     html = self.get_text(self.next_url)
        #     jobs_list = self.parse(html)
        #     all_jobs_list.extend(jobs_list)

        jobs_list = self.parse(html)
        all_jobs_list.extend(jobs_list)

        # for job in all_jobs_list:
        #     job_href = job.job_href
        #     jobs_detail_list.append(self.parse_detail2(job_href))

        urlqueue = queue.Queue()
        for job in all_jobs_list:
            urlqueue.put(job.job_href)

        threads = []
        for i in range(10):
            t = threading.Thread(target=self.parse_detail,args=(urlqueue,))
            threads.append(t)

        for t in threads:
            t.start()

        while not self.urlqueue.empty():
            pass

        for t in threads:
            t.join()

        print('共有{}个职位信息'.format(len(all_jobs_list)))
        # self.write_to_csv(jobs_detail_list)
        # print('招聘信息写入到csv文件中完毕！')

    def write_to_csv(self, jobs_detail_list):
        catalog_path = 'E:/PycharmWspace/SpiderCrack/Job51/data/'
        if not os.path.exists(catalog_path):
            os.mkdir(catalog_path)

        path = '{0}{1}.csv'.format(catalog_path, self.job_name)
        with open(path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            #写入列头
            writer.writerow('job_name salary welfare job_info work_place company_name company_info'.split(' '))
            for job in jobs_detail_list:
                writer.writerow([job.job_name,job.salary,job.welfare,job.job_info,job.work_place,job.company_name,job.company_info])


if __name__ == '__main__':
    start_time = time.time()
    # key = input("请输入关键词：")
    # jobarea_name = '全国'
    key = "爬虫工程师"
    # Job51(jobarea_name, key).run()
    job51 = Job51(job_name=key)
    # html = job51.get_text('https://jobs.51job.com/shanghai-jaq/110577565.html?s=01&t=0', job51.headers)
    # print(html)

    job51.run()

    end_time = time.time()
    print('耗时' + str(end_time-start_time))
