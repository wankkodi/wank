# -*- coding: UTF-8 -*-
from .likuoo import Likuoo

if __name__ == '__main__':
    module = Likuoo()
    module.download_category_input_from_user(use_web_server=True)
