# -*- coding: UTF-8 -*-
from .porndig import PornDig

if __name__ == '__main__':
    module = PornDig()
    module.download_category_input_from_user(use_web_server=False)
