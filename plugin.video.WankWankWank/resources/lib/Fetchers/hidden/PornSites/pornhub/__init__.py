# -*- coding: UTF-8 -*-
from .pornhub import PornHub
from .porndotcom import PornDotCom
from .tube8 import TubeEight
from .youporn import YouPorn

if __name__ == '__main__':
    module = PornHub()
    # module = PornDotCom()
    # module = TubeEight()
    # module = YouPorn()
    module.download_category_input_from_user(use_web_server=True)
