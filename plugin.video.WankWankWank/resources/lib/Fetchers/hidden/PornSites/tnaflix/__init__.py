# -*- coding: UTF-8 -*-
from .empflix import EmpFlix
from .moviefap import MovieFap
from .tnaflix import TnaFlix

if __name__ == '__main__':
    # module = TnaFlix()
    # module = EmpFlix()
    module = MovieFap()
    module.download_category_input_from_user(use_web_server=True)
