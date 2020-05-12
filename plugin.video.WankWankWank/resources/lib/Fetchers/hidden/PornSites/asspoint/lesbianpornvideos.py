from ....catalogs.porn_catalog import PornFilterTypes, PornFilter
from . import Base1


class LesbianPornVideos(Base1):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.lesbianpornvideos.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': [(PornFilterTypes.LesbianType, 'Lesbian', 'lesbian'),
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
        single_porn_star_params = video_params.copy()
        single_porn_star_params['sort_order'] = \
            [(PornFilterTypes.RelevanceOrder, 'Most Relevant', 'search_order=relevance'),
             (PornFilterTypes.BestOrder, 'Best', 'search_order=date-relevance'),
             (PornFilterTypes.PopularityOrder, 'Most Popular', 'search_order=popularity'),
             (PornFilterTypes.ViewsOrder, 'Most Viewed', 'search_order=views'),
             (PornFilterTypes.DateOrder, 'Most Recent', 'search_order=approval_date'),
             (PornFilterTypes.RatingOrder, 'Top Rated', 'search_order=rating'),
             (PornFilterTypes.LengthOrder, 'By duration', 'search_order=runtime'),
             ]
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         single_tag_args=single_porn_star_params,
                                         single_porn_star_args=single_porn_star_params,
                                         search_args=single_porn_star_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='LesbianPornVideos', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(LesbianPornVideos, self).__init__(source_name, source_id, store_dir, data_dir, source_type,
                                                use_web_server, session_id)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(LesbianPornVideos, self)._version_stack + [self.__version]
