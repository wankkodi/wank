# -*- coding: UTF-8 -*-
from .saypornplease import SayPornPlease
from .yespornpleasex import YesPornPleaseX
from .yespornplease import YesPornPlease

if __name__ == '__main__':
    # module = YesPornPlease()
    # module = YesPornPleaseX()
    module = SayPornPlease()
    module.download_category_input_from_user(use_web_server=False)
