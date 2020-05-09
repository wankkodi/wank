# -*- coding: UTF-8 -*-
from .realgfporn import RealGfPorn

if __name__ == '__main__':
    module = RealGfPorn()
    module.download_category_input_from_user(use_web_server=True)
