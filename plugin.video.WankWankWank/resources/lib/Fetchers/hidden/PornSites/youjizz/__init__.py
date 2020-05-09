# -*- coding: UTF-8 -*-
from .youjizz import YouJizz

if __name__ == '__main__':
    module = YouJizz()
    module.download_category_input_from_user(use_web_server=False)
