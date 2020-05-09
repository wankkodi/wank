# -*- coding: UTF-8 -*-
from .palmtube import PalmTube

if __name__ == '__main__':
    module = PalmTube()
    module.download_category_input_from_user(use_web_server=False)
