# -*- coding: UTF-8 -*-
from .kan import Kan
from .kan_education import KanEducation
from .makan import Makan

if __name__ == '__main__':
    kan = Kan()
    kan.download_category_input_from_user()
