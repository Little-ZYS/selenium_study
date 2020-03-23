# -*- coding: utf-8 -*-
"""
通过抽奖链接定时转发抽奖动态
"""
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from login import BiliBili
import time
import random
forward_words = ['冲冲冲', '来了来了', '这次一定，这次一定', '冲冲冲，中中中', '666', '你们能看到这句话，就说明我中了',
                 '佛系佛系', '因为我没中，所以我中了', '不想再当分母了', ' ', '6', '害', '中', '一定', '我我我', '66',
                 '来了', '支持', '!', '嘿嘿']


class ForwardActivity:
    def __init__(self, account_serial_num, urls):
        """
        实现转发
        :param account_serial_num: 账户序号
        :param urls: 要转发的动态的页面
        """
        self.urls = urls
        # 登录的账号密码
        self.account = [['19881666971', 'zys12345678'],
                        ['13733042335', 'zys12345678'],
                        ]
        login_bug = BiliBili(self.account[account_serial_num])
        # 登录
        self.driver = login_bug.login_bilibili()

    def enter_page(self):
        """
        转发动态
        :return:
        """
        # 进入页面
        if self.urls == '':
            self.driver.quit()
            return
        try:
            for url in self.urls:
                if url == '':
                    continue
                self.driver.get(url)
                # 延迟两秒
                time.sleep(2)
                self.driver.find_element_by_class_name('user-decorator').click()
                time.sleep(1)
                handles = self.driver.window_handles
                self.driver.switch_to.window(handles[1])
                time.sleep(1)
                try:
                    get_text = self.driver.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div[2]/div[4]/span').text
                except NoSuchElementException:
                    get_text = self.driver.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div[2]/div[4]/div[1]/div').text
                if get_text == '关注':
                    self.driver.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div[2]/div[4]/span').click()
                    time.sleep(1)
                    self.driver.find_element_by_css_selector('body > div.follow-dialog-wrap > div > div.bottom > button')
                    time.sleep(1)
                    self.driver.close()
                    self.driver.switch_to.window(handles[0])
                else:
                    self.driver.close()
                    self.driver.switch_to.window(handles[0])
                #              进入转发模式按钮的xpath
                xpath_list = ['//*[@id="app"]/div/div[2]/div/div/div[1]/div[4]/div[1]/span/i',
                              # 发送转发留言的xpath
                              '//*[@id="app"]/div/div[2]/div/div/div[5]/div/div[1]/div[1]/div[2]/textarea',
                              # 转发的xpath
                              '//*[@id="app"]/div/div[2]/div/div/div[5]/div/div[1]/div[1]/div[2]/div[2]/div[2]',
                              # 进入转发模式按钮的备用xpath
                              '//*[@id="app"]/div/div[2]/div/div/div[1]/div[4]/div[1]/span/span',
                              # 转发的备用xpath
                              '//div[@class="card"]/div[6]/div[1]/div[1]/div[1]/div[2]/div[2]/div[2]',
                              ]
                try:
                    self.driver.find_element_by_xpath(xpath_list[0]).click()
                except NoSuchElementException:
                    self.driver.find_element_by_xpath(xpath_list[3]).click()
                time.sleep(1)
                try:
                    self.driver.find_element_by_xpath(xpath_list[1]).send_keys(forward_words[random.randint(0, 19)])
                except NoSuchElementException:
                    pass
                time.sleep(1)
                try:
                    self.driver.find_element_by_xpath(xpath_list[2]).click()
                except NoSuchElementException:
                    self.driver.find_element_by_xpath(xpath_list[4]).click()
                time.sleep(20)
        finally:
            self.driver.quit()


if __name__ == '__main__':
    url_list = ['https://t.bilibili.com/369052078596177784?tab=2',
                ]

    test0 = ForwardActivity(1, url_list)
    test0.enter_page()
