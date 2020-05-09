# -*- coding: UTF-8 -*-
from .netfapx import Netfapx

if __name__ == '__main__':
    module = Netfapx()
    module.download_category_input_from_user(use_web_server=True)
