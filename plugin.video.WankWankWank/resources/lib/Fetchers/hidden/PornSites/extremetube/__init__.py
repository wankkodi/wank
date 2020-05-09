# -*- coding: UTF-8 -*-
from .extremetube import ExtremeTube
# from .keezmovies import KeezMoovies
from .spankwire import SpankWire

if __name__ == '__main__':
    # module = ExtremeTube()
    # module = KeezMoovies()
    module = SpankWire()
    module.download_category_input_from_user(use_web_server=True)
