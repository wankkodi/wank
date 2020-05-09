# -*- coding: UTF-8 -*-
from .luxuretv import LuxureTV

if __name__ == '__main__':
    module = LuxureTV()
    module.download_category_input_from_user(use_web_server=True)
