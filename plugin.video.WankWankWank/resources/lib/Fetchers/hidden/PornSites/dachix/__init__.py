# -*- coding: UTF-8 -*-
from .deviantclip import DeviantClip
from .dachix import DaChix
from .dagay import DaGay

if __name__ == '__main__':
    module = DaChix()
    # module = DeviantClip()
    # module = DaGay()
    module.download_category_input_from_user(use_web_server=False)
