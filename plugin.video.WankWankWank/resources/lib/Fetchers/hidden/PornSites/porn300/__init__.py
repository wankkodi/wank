# -*- coding: UTF-8 -*-
from .porn300 import Porn300

if __name__ == '__main__':
    module = Porn300()
    module.download_category_input_from_user(use_web_server=True)
