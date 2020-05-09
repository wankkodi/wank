# -*- coding: UTF-8 -*-
from .redwap import RedWap

if __name__ == '__main__':
    module = RedWap()
    module.download_category_input_from_user(use_web_server=True)
