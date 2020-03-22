# -*- coding: utf-8 -*-
"""
通过一些b站抽奖up抽奖发的动态进行分析，获得动态抽奖的动态的页面url

"""
from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException


def write_to_pool(which_pool, href_lists):
    href_list = href_lists
    if which_pool == 'all_pool':
        with open('D:/Pycharm_file/selenium_study/pool/all_pool', 'a') as write_to:
            for href in href_list:
                href = href + '\n'
                write_to.write(href)
    elif which_pool == 'send_pool':
        with open('D:/Pycharm_file/selenium_study/pool/send_pool', 'w') as write_to:
            for href in href_list:
                href = href + '\n'
                write_to.write(href)
    else:
        pass


def read_to_pool(which_pool):
    send_pool = []
    if which_pool == 'all_pool':
        with open('D:/Pycharm_file/selenium_study/pool/all_pool', 'r') as read_to:
            for line in read_to.readlines():
                send_pool.append(line.strip())
        return send_pool
    elif which_pool == 'send_pool':
        with open('D:/Pycharm_file/selenium_study/pool/send_pool', 'r') as read_to:
            for line in read_to.readlines():
                send_pool.append(line.strip())
        return send_pool
    else:
        pass


class AnalyzeUrl:
    def __init__(self, url_num):
        """
        获得抽奖页面的url
        :param url_num: 抽奖up主的页面序号
        """
        # 抽奖up主的主页
        urls_list = ['https://space.bilibili.com/319100603/dynamic',
                     'https://space.bilibili.com/513791996/dynamic',
                     'https://space.bilibili.com/414846453/dynamic'
                     ]
        self.url = urls_list[url_num]
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument(
            "user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 "
            "Safari/537.36'")
        self.driver = webdriver.Chrome(options=options)

    def get_hrefs(self):
        """
        筛选出有价值的动态
        :return: 抽奖页面的url
        """
        self.driver.get(self.url)
        # 延迟一秒
        time.sleep(2)
        # 获得所有动态的列表
        ret = self.driver.find_elements_by_css_selector('#page-dynamic > div.col-1 > div > div > div')
        # 有抽奖价值的动态的URL列表
        hrefs = []
        for i in range(len(ret)):
            try:
                # 选择转发别人动态的动态
                ret1 = ret[i].find_element_by_class_name('original-card-content')
                # 选择动态中的文字部分
                ret2 = ret1.find_element_by_class_name('dynamic-link-hover-bg')
                # 筛选出含有动态抽奖的动态
                if ret2.text == '互动抽奖':
                    try:
                        # 动过class_name点击文字转到动态详情页
                        ret1.find_element_by_class_name('content-full').click()
                    except ElementNotInteractableException:
                        # 如果动态的文字过多，出现折叠时，定位的class-name为content-ellipsis
                        ret1.find_element_by_class_name('content-ellipsis').click()
                    time.sleep(1)
                    handles = self.driver.window_handles
                    # 转到动态详情页，注意：selenium的操控页面和浏览器正在显示的页面不一定相同，要先切换页面再操作
                    self.driver.switch_to.window(handles[1])
                    # 获得当前页面的url
                    url = self.driver.current_url
                    self.driver.close()
                    # 切换到原本的页面
                    self.driver.switch_to.window(handles[0])
                    hrefs.append(url)
            except NoSuchElementException:
                pass
        self.driver.quit()
        return hrefs

    def analyze_hrefs(self):
        """
        分析链接（转发人数）（开奖时间）
        :return: None
        """
        # 定义selenium对象
        hrefs_list = []
        hrefs_list1 = self.get_hrefs()
        for href in hrefs_list1:
            if href[-5:-1] == 'tab=':
                hrefs_list.append(href)
        return hrefs_list

    def manage_href_pool(self):
        """
        添加href列表
        :return:
        """
        href_list_pool = []
        send_href_list_pool = []
        new_hrefs = self.analyze_hrefs()
        for href in new_hrefs:
            if href not in read_to_pool('all_pool'):
                href_list_pool.append(href)
                send_href_list_pool.append(href)
        write_to_pool('all_pool', href_list_pool)
        write_to_pool('send_pool', send_href_list_pool)


if __name__ == '__main__':
    test = AnalyzeUrl(1)
    test.manage_href_pool()
