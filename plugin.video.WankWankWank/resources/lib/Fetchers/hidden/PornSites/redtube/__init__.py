# -*- coding: UTF-8 -*-
from .redtube import RedTube

if __name__ == '__main__':
    module = RedTube()
    module.download_category_input_from_user(use_web_server=True)
