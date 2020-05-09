# -*- coding: UTF-8 -*-
from .goforporn import GoForPorn

if __name__ == '__main__':
    module = GoForPorn()
    module.download_category_input_from_user(use_web_server=False)
