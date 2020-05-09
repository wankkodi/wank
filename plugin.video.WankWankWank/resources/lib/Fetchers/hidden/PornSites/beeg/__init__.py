# -*- coding: UTF-8 -*-
from .beeg import Beeg

if __name__ == '__main__':
    module = Beeg()
    module.download_category_input_from_user()
