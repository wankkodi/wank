# -*- coding: UTF-8 -*-
from .fakings import FakingsTV

if __name__ == '__main__':
    module = FakingsTV()
    module.download_category_input_from_user(use_web_server=False)
