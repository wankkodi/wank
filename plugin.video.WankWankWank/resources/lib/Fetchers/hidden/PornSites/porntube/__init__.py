# -*- coding: UTF-8 -*-
from .fourtube import FourTube
from .fux import Fux
from .pornerbros import PornerBros
from .porntube import PornTube

if __name__ == '__main__':
    # module = PornTube()
    # module = FourTube()
    # module = Fux()
    module = PornerBros()
    module.download_category_input_from_user(use_web_server=True)
