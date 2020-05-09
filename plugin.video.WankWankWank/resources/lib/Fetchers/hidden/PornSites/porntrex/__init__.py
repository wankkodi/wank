# -*- coding: UTF-8 -*-
from .camwhoresbay import CamWhoresBay
from .javbangers import JAVBangers
from .porntrex import PornTrex

if __name__ == '__main__':
    # module = PornTrex()
    # module = JAVBangers()
    module = CamWhoresBay()
    module.download_category_input_from_user(use_web_server=True)
