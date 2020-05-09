# -*- coding: UTF-8 -*-
from .vintagetube import VintageTube

if __name__ == '__main__':
    module = VintageTube()
    module.download_category_input_from_user(use_web_server=True)
