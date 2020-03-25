# -*- coding: utf-8 -*-
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from analyze_urls import AnalyzeUrl, write_to_pool, read_to_pool
import datetime
import time
from selenium_bili import ForwardActivity
import random
from send_email import send_by_email

# 测试用的
def try67(n):
    print(n)
    print(2)


def today_time():
    today = datetime.date.today()
    formatted_today = today.strftime('%y%m%d')
    year = int(formatted_today[0:2]) + 2000
    month = int(formatted_today[2:4])
    day = int(formatted_today[4:6])
    return year, month, day


def forward_start(url):
    try:
        for i in range(2):
            forward = ForwardActivity(i, url)
            forward.enter_page()
    except:
        pass


def will_send_urls():
    send_urls = read_to_pool('send_pool')
    num = len(send_urls)
    if num <= 4:
        return send_urls
    else:
        num1 = int(num/4)
        x = num % 4
        if not x == 0:
            send_urls_list = list(range(5))
            for i in range(5):
                n = num1*i
                m = num1+num1*i
                send_urls_list[i] = send_urls[n: m]
            send_urls_list[4] = send_urls[num1*4: num]
            return send_urls_list
        else:
            send_urls_list = list(range(4))
            for i in range(4):
                n = num1 * i
                m = num1 + num1 * i
                send_urls_list[i] = send_urls[n: m]
            return send_urls_list


def clean_send_pool():
    send_body = '今日系统运行正常,今天发的链接有：' + str(read_to_pool('send_pool'))
    with open('pool/send_pool', 'r+') as clean_to:
        clean_to.truncate()
    send_by_email(send_body)


class UserAps:
    def __init__(self):
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(20),
            'processpool': ProcessPoolExecutor(10)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        self.scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
        self.scheduler.add_job(self.analyze_url_start, 'cron', hour=12, minute=1)
        self.scheduler.add_job(clean_send_pool, 'cron', hour=23, minute=59)

    def add_job(self, user_job, hour, minute, second, arg):
        year, month, day = today_time()
        add_job_id = str(year)+str(month)+str(day)+str(hour)+str(minute)
        self.scheduler.add_job(user_job, 'date',
                               run_date=datetime.datetime(year, month, day, hour, minute, second),
                               args=[arg], id=add_job_id)
        return add_job_id

    def useraps_start(self):
        try:
            self.scheduler.start()
            while True:
                time.sleep(10)
        except (SystemExit, KeyboardInterrupt):
            self.scheduler.shutdown()
            print('Exit The Scheduler!')
            send_body = '系统意外停止！'
            send_by_email(send_body)

    def analyze_url_start(self):
        try:
            for i in range(3):
                account = AnalyzeUrl(i)
                account.manage_href_pool()
            urls_list = will_send_urls()
            for urls in urls_list:
                if isinstance(urls, list):
                    random_time_hour = random.randint(12, 22)
                    random_time_minute = random.randint(1, 59)
                    random_time_second = random.randint(1, 39)
                    self.add_job(forward_start, random_time_hour, random_time_minute, random_time_second, urls)
                else:
                    random_time_hour = random.randint(12, 22)
                    random_time_minute = random.randint(1, 59)
                    random_time_second = random.randint(1, 39)
                    self.add_job(forward_start, random_time_hour, random_time_minute, random_time_second, urls_list)
        except:
            pass


if __name__ == '__main__':
    test = UserAps()
    job_id = test.add_job(try67, 12, 19, 5, 1)
    test.useraps_start()
    print(test.scheduler.get_jobs())