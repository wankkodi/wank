# -*- coding: UTF-8 -*-
from .porn00 import Porn00

if __name__ == '__main__':
    module = Porn00()
    module.download_category_input_from_user(use_web_server=True)
