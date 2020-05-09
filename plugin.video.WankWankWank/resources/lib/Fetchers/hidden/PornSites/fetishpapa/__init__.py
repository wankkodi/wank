# -*- coding: UTF-8 -*-
from .ashemaletube import AShemaleTube
from .boyfriendtv import BoyfriendTV
from .pornoxo import Pornoxo
from .fetishpapa import FetishPapa


if __name__ == '__main__':
    # module = FetishPapa()
    # module = Pornoxo()
    # module = BoyfriendTV()
    module = AShemaleTube()
    module.download_category_input_from_user(use_web_server=False)
