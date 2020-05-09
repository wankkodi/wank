# -*- coding: UTF-8 -*-
from .xpaja import XPaja

if __name__ == '__main__':
    module = XPaja()
    module.download_category_input_from_user(use_web_server=True)
