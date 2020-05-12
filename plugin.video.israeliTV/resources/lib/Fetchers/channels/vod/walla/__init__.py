# -*- coding: UTF-8 -*-
from .walla import Walla

if __name__ == '__main__':
    walla = Walla()
    # todo: to run test on viva
    walla.download_category_input_from_user()
