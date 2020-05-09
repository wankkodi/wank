# -*- coding: UTF-8 -*-
from .homemoviestube import HomeMoviesTube


if __name__ == '__main__':
    module = HomeMoviesTube()
    module.download_category_input_from_user(use_web_server=False)
