# -*- coding: UTF-8 -*-
from .porngo import PornGo
from .xxxfiles import XXXFiles

if __name__ == '__main__':
    module = PornGo()
    # module = XXXFiles()
    module.download_category_input_from_user(use_web_server=True)
