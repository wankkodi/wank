# -*- coding: UTF-8 -*-
from .veporns import VePorns

if __name__ == '__main__':
    module = VePorns()
    module.download_category_input_from_user(use_web_server=True)
