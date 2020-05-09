# -*- coding: UTF-8 -*-
from .taxi69 import Taxi69

if __name__ == '__main__':
    module = Taxi69()
    module.download_category_input_from_user(use_web_server=False)
