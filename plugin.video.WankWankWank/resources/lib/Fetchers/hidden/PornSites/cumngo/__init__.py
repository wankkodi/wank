# -*- coding: UTF-8 -*-
from .cumngo import CumNGo

if __name__ == '__main__':
    module = CumNGo()
    module.download_category_input_from_user(use_web_server=False)
