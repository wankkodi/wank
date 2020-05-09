# -*- coding: UTF-8 -*-
from .xvideos import XVideos
from .xnxx import Xnxx

if __name__ == '__main__':
    # module = Xnxx()
    module = XVideos()
    module.download_category_input_from_user(use_web_server=True)
