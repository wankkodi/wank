# -*- coding: UTF-8 -*-
from .tubev import TubeV

if __name__ == '__main__':
    module = TubeV()
    module.download_category_input_from_user(use_web_server=True)
