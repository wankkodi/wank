# -*- coding: UTF-8 -*-
from .tubexxporn import TubeXXPorn
from .rushporn import RushPorn
from .pornky import PornKy
from .pornktube import PornKTube

if __name__ == '__main__':
    # module = PornKTube()
    # module = PornKy()
    # module = RushPorn()
    module = TubeXXPorn()
    module.download_category_input_from_user(use_web_server=True)
