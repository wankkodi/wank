# -*- coding: UTF-8 -*-
from .faapy import Faapy

if __name__ == '__main__':
    module = Faapy()
    module.download_category_input_from_user(use_web_server=False)
