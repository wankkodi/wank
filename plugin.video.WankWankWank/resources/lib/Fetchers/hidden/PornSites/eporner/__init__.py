# -*- coding: UTF-8 -*-
from .eporner import EPorner

if __name__ == '__main__':
    module = EPorner()
    module.download_category_input_from_user()
