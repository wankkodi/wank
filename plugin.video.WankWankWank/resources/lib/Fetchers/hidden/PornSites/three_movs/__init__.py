# -*- coding: UTF-8 -*-
from .threemovs import ThreeMovs

if __name__ == '__main__':
    module = ThreeMovs()
    module.download_category_input_from_user(use_web_server=True)
