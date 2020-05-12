# -*- coding: UTF-8 -*-
from .hot import Hot
from .hot3 import HotThree
from .hot8 import HotEight
from .hot_bidur import HotBidur
from .hot_young import HotYoung
from .hot_zoom import HotZoom

if __name__ == '__main__':
    hot = Hot()
    # hot = HotThree()
    # hot = HotEight()
    # hot = HotBidur()
    # hot = HotYoung()
    # hot = HotZoom()
    hot.download_category_input_from_user()
