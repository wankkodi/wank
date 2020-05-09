# -*- coding: UTF-8 -*-
from .hdtubeporn import HDTubePorn
from .zbporn import ZBPorn
from .pornid import PornID
from .sexvid import SexVid


if __name__ == '__main__':
    # module = HDTubePorn()
    # module = SexVid()
    # module = PornID()
    module = ZBPorn()
    module.download_category_input_from_user(use_web_server=False)
