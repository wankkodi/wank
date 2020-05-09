# -*- coding: UTF-8 -*-
from .jizzbunker import JizzBunker
from .xxxdan import XXXDan

if __name__ == '__main__':
    # module = JizzBunker()
    module = XXXDan()
    module.download_category_input_from_user(use_web_server=True)
