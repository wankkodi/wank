# -*- coding: UTF-8 -*-
from .pornhd import PornHD
from .gotporn import GotPorn
from .pornrox import PornRox
from .pinflix import PinFlix

if __name__ == '__main__':
    # module = GotPorn()
    module = PornHD()
    # module = PinFlix()
    # module = PornRox()
    module.download_category_input_from_user()
