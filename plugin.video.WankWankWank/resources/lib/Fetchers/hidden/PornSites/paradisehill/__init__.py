# -*- coding: UTF-8 -*-
from .paradisehill import ParadiseHill

if __name__ == '__main__':
    module = ParadiseHill()
    module.download_category_input_from_user(use_web_server=True)
