# -*- coding: UTF-8 -*-
from .nubilefilmxxx import NubileFilmXXX
from .plusone8 import PlusOne8

if __name__ == '__main__':
    module = NubileFilmXXX()
    # module = PlusOne8()
    module.download_category_input_from_user(use_web_server=True)
