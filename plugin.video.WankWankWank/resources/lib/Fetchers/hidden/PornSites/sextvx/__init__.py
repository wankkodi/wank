# -*- coding: UTF-8 -*-
from .sextvx import SexTvX

if __name__ == '__main__':
    module = SexTvX()
    module.download_category_input_from_user(use_web_server=True)
