# -*- coding: UTF-8 -*-
from .sexu import SexU

if __name__ == '__main__':
    module = SexU()
    module.download_category_input_from_user(use_web_server=True)
