# -*- coding: UTF-8 -*-
from .drtuber import DrTuber

if __name__ == '__main__':
    module = DrTuber()
    module.download_category_input_from_user(use_web_server=True)
