# -*- coding: UTF-8 -*-
from .pornomovies import PornoMovies

if __name__ == '__main__':
    module = PornoMovies()
    module.download_category_input_from_user(use_web_server=False)
