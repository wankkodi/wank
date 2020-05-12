from . import Base2
from ....catalogs.porn_catalog import PornFilterTypes, PornFilter


class CartoonSexTubes(Base2):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.cartoonsextube.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': [(PornFilterTypes.CartoonType, 'Cartoon', 'straight'),
                                                     ],
                                 }
        video_params = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most Popular', 'popular'),
                                       (PornFilterTypes.DateOrder, 'Most Recent', 'recent'),
                                       (PornFilterTypes.ViewsOrder, 'Most Viewed', 'view'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rate'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'length'),
                                       ],
                        'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', 'min_width=0'),
                                            (PornFilterTypes.HDQuality, 'HD quality', 'min_width=1280'),
                                            ],
                        'length_filters': ((PornFilterTypes.AllLength, 'Any duration', 'min_duration=0'),
                                           (PornFilterTypes.OneLength, 'Short (0-8 min)', 'min_duration=1-480'),
                                           (PornFilterTypes.TwoLength, 'Med (8-20 min)', 'min_duration=480-1200'),
                                           (PornFilterTypes.ThreeLength, 'Long (20+ min)', 'min_duration=1200'),
                                           ),
                        }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='CartoonSexTubes', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super().__init__(source_name, source_id, store_dir, data_dir, source_type,
                         use_web_server, session_id)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(CartoonSexTubes, self)._version_stack + [self.__version]
