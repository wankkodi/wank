# -*- coding: UTF-8 -*-
from .spankbang import SpankBang

if __name__ == '__main__':
    module = SpankBang()
    module.download_category_input_from_user(use_web_server=True)
