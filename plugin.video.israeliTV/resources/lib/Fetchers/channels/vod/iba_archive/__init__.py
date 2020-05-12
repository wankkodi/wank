# -*- coding: UTF-8 -*-
from .iba import IBA

if __name__ == '__main__':
    iba = IBA(store_dir='D:\\')
    iba.download_category_input_from_user()
