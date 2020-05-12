# -*- coding: UTF-8 -*-
from .knesset import Knesset

if __name__ == '__main__':
    knesset = Knesset(store_dir='D:\\')
    knesset.download_category_input_from_user()
