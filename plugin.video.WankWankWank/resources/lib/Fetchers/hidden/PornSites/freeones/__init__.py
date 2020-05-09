# -*- coding: UTF-8 -*-
from .freeones import FreeOnes

if __name__ == '__main__':
    module = FreeOnes()
    module.download_category_input_from_user(use_web_server=False)
