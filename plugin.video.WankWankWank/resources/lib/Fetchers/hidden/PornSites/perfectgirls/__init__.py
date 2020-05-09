# -*- coding: UTF-8 -*-
from .perfectgirls import PerfectGirls

if __name__ == '__main__':
    module = PerfectGirls()
    module.download_category_input_from_user(use_web_server=True)
