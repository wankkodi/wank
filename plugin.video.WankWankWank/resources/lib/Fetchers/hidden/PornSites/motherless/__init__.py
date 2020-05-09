# -*- coding: UTF-8 -*-
from .motherless import MotherLess

if __name__ == '__main__':
    module = MotherLess()
    module.download_category_input_from_user(use_web_server=True)
