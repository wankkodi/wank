# -*- coding: UTF-8 -*-
from .mako import Mako
from .bip import Bip
from .channel24 import Channel24

if __name__ == '__main__':
    mako = Mako()
    # mako = Bip()
    # mako = Channel24()
    mako.download_category_input_from_user()
