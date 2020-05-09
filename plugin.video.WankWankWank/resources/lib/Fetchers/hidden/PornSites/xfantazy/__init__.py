# -*- coding: UTF-8 -*-
from .xfantazy import XFantazy

if __name__ == '__main__':
    module = XFantazy()
    module.download_category_input_from_user(use_web_server=False)
