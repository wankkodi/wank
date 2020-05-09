# -*- coding: UTF-8 -*-
from .eroprofile import EroProfile

if __name__ == '__main__':
    module = EroProfile()
    module.download_category_input_from_user(use_web_server=True)
