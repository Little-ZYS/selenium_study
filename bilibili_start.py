# -*- coding: utf-8 -*-
from user_apscheduler import UserAps


def start():
    main_start = UserAps()
    main_start.useraps_start()


if __name__ == '__main__':
    start()
