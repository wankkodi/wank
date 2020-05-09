# -*- coding: UTF-8 -*-
from .okxxx import OkXXX
from .pornhat import PornHat

if __name__ == '__main__':
    # module = OkXXX()
    module = PornHat()
    module.download_category_input_from_user(use_web_server=True)
