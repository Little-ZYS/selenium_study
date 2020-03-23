# -*- coding: utf-8 -*-
"""
模拟人登录b站
调用BiliBili类的crack方法即可
"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from io import BytesIO
import time

BORDER = 6


class BiliBili:
    def __init__(self, account):
        options = webdriver.ChromeOptions()
        # 设置为开发者模式，避免被识别
        options.add_experimental_option('excludeSwitches',
                                        ['enable-automation'])
        options.add_argument('--headless')
        options.add_argument('–no-sandbox')
        options.add_argument('–disable-dev-shm-usage')
        options.add_argument('–disable-extensions')
        options.add_argument(
            "user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 "
            "Safari/537.36'")
        self.url = 'https://passport.bilibili.com/login'
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)
        self.username = account[0]
        self.password = account[1]

    def get_position(self):
        """
        获取验证码图片的位置
        :return: 位置的四个点参数
        """
        img_xpath = '/html/body/div[2]/div[2]/div[6]/div/div[1]/div[1]/div/a/div[1]/div/canvas[2]'
        img = self.wait.until(EC.presence_of_element_located((By.XPATH, img_xpath)))
        time.sleep(1)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return top, bottom, left, right

    def get_button(self):
        """
        获取滑动块, 并且返回
        :return: button
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'gt_slider_knob')))
        return button

    def login(self):
        """
        进入登录界面，输入账号密码，点击登录
        :return: None
        """
        self.driver.get(self.url)
        self.driver.set_window_size(1920, 1080)
        username = self.wait.until(EC.element_to_be_clickable((By.ID, 'login-username')))
        password = self.wait.until(EC.element_to_be_clickable((By.ID, 'login-passwd')))
        time.sleep(1)
        username.send_keys(self.username)
        time.sleep(1)
        password.send_keys(self.password)
        self.driver.find_element_by_xpath('//*[@id="geetest-wrap"]/div/div[5]/a[1]').click()

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        return slider

    def get_geetest_image(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def delete_style(self):
        """
        删除图片对应的一个元素可以使网页显示原本的图
        执行js脚本，获取无滑块图
        :return None
        """
        js = 'document.querySelectorAll("canvas")[3].style=""'
        self.driver.execute_script(js)

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def get_gap(self, image1, image2):
        """
        获取缺口偏移量
        :param image1: 带缺口图片
        :param image2: 不带缺口图片
        :return:
        """
        left = 60
        print(image1.size[0])
        print(image1.size[1])
        for i in range(left, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    left = i
                    return left
        return left

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        track = list(range(3))
        track[0] = int(distance * 3 / 15)
        track[1] = int(distance * 7 / 15)
        # 此处多十五分之一的值，模仿最后滑超过指定位置的行为
        track[2] = int(distance * 6 / 15)
        current = track[0] + track[1] + track[2]
        x = distance - current
        xx = [x / 2 + 5, x / 2 - 8, 5, -3, 2]
        for ii in range(5):
            track.append(int(xx[ii]))
        return track

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        i = 0
        ActionChains(self.driver).click_and_hold(slider).perform()
        for x in track:
            i += 1
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
            if i == len(track) - 1:
                ActionChains(self.driver).pause(0.7)
            elif i == len(track):
                ActionChains(self.driver).pause(1)
        ActionChains(self.driver).pause(2)
        time.sleep(1)
        ActionChains(self.driver).release().perform()

    def crack(self):
        """
        登录b站
        :return:完成后的页面的url
        """
        self.login()
        # 确认图片加载完成
        time.sleep(1)
        # 获取滑块
        slider = self.get_slider()
        # 获取带缺口验证码图片
        image1 = self.get_geetest_image('captcha1.png')
        # 获取不带缺口的验证码图片
        self.delete_style()
        time.sleep(1)
        image2 = self.get_geetest_image('captcha2.png')
        # self.delete_style_test()
        # 获取缺口位置
        gap = self.get_gap(image2, image1)
        print('缺口位置', gap)
        # 减去缺口位移
        gap -= BORDER
        # 获取移动轨迹
        track = self.get_track(gap)
        print('滑动轨迹', track)
        # 拖动滑块
        self.move_to_gap(slider, track)
        time.sleep(3)

    def login_bilibili(self):
        """
        登录，并检查是否登录成功，如果没成功再次尝试，最多5次
        :return:
        """
        self.crack()
        for i in range(5):
            # 获取当前页面的url
            web_current_url = self.driver.current_url
            if not web_current_url == 'https://www.bilibili.com/':
                self.crack()
            else:
                print(web_current_url)
                web_driver = self.driver
                return web_driver


if __name__ == '__main__':
    account_list = [['19881666971', 'zys12345678'],
                    ]
    test = BiliBili(account_list[0])  # 输入账号和密码
    driver = test.login_bilibili()
    driver.close()
