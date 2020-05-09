# -*- coding: UTF-8 -*-
# Regex

# Internet tools
from .sheshaft import SheShaft
from .fetishshrine import FetishShrine
from .pornicom import PorniCom
from .sleazyneasy import SleazyNEasy
from .wankoz import WankOz
from .vikiporn import VikiPorn
from .pornwhite import PornWhite
from .katestube import KatesTube
from .pervclips import PervClips

if __name__ == '__main__':
    # module = KatesTube()
    # module = PervClips()
    # module = PornWhite()
    # module = SleazyNEasy()
    # module = VikiPorn()
    module = WankOz()
    # module = PorniCom()
    # module = FetishShrine()
    # module = SheShaft()
    module.download_category_input_from_user(use_web_server=True)
