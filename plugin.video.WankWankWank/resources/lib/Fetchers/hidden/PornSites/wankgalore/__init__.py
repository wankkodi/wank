# -*- coding: UTF-8 -*-
from .wankgalore import WankGalore

if __name__ == '__main__':
    module = WankGalore()
    module.download_category_input_from_user(use_web_server=True)
