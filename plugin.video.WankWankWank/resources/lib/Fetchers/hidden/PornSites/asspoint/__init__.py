# -*- coding: UTF-8 -*-
from .base import Base1, Base2, Base3
from .asspoint import AssPoint
from .asianpornvideos import AsianPornVideos
from .analpornvideos import AnalPornVideos
from .ghettotube import GhettoTube
from .porntv import PornTV
from .youngpornvideos import YoungPornVideos
from .cartoonpornvideos import CartoonPornVideos
from .lesbianpornvideos import LesbianPornVideos
from .sexoasis import SexOasis
from .teenieporn import TeeniePorn
# from .bigboobstube import BigBoobsTube
from .hoodtube import HoodTube
from .porntitan import PornTitan
from .youngporno import YoungPorno
from .suzisporn import SuzisPorn
from .mobilepornvideos import MobilePornMovies
from .movieshark import MovieShark
from .movietitan import MovieTitan
from .xjizz import XJizz
# from .cartoonsextubes import CartoonSexTubes
# from .xxxmilfs import XXXMilfs

if __name__ == '__main__':
    # module = AssPoint()
    # module = AnalPornVideos()
    # module = AsianPornVideos()
    # module = GhettoTube()
    # module = PornTV()
    # module = YoungPornVideos()
    module = LesbianPornVideos()
    # module = SexOasis()
    # module = TeeniePorn()
    # module = CartoonPornVideos()
    # module = BigBoobsTube()
    # module = PornTitan()
    # module = YoungPorno()
    # module = SuzisPorn()
    # module = MobilePornMovies()
    # module = MovieShark()
    # module = MovieTitan()
    # module = XJizz()
    # module = CartoonSexTubes()
    # module = XXXMilfs()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=False)
