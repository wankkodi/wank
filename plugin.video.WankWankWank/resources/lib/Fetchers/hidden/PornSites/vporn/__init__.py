# -*- coding: UTF-8 -*-
from .vporn import VPorn

if __name__ == '__main__':
    module = VPorn()
    module.download_category_input_from_user(use_web_server=True)
