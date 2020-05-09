from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes
from .txxx import Txxx


class HClips(Txxx):
    number_of_flip_images = 15

    # @property
    # def video_data_request_url(self):
    #     """
    #     Most viewed videos page url.
    #     :return:
    #     """
    #     return urljoin(self.base_url, '/sn4diyux.php')

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 50000

    @property
    def object_urls(self):
        res = super(HClips, self).object_urls
        res.pop(PornCategories.PORN_STAR_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://hclips.com/'

    def __init__(self, source_name='HClips', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HClips, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)
        self.search_json = urljoin(self.base_url, '/api/videos.php?params=259200/{gender}/relevance/{npp}/'
                                                  'search..{p}.{type}.{length}.{period}&s={query}&sort={sort}&'
                                                  'date={period}&type={type}')

    def _prepare_filters(self):
        general_filters, _, _, _, _, channels_filters = \
            super(HClips, self)._prepare_filters()
        video_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Popularity', 'most-popular'),
                                        (PornFilterTypes.DateOrder, 'Date', 'latest-updates'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        (PornFilterTypes.CommentsOrder, 'Number of Comments', 'most-commented'),
                                        (PornFilterTypes.ViewsOrder, 'Number of Views', 'most-viewed'),
                                        ),
                         'period_filters': (((PornFilterTypes.AllDate, 'All time', ''),
                                             (PornFilterTypes.TwoDate, 'Week', 'week'),
                                             (PornFilterTypes.OneDate, 'Month', 'month'),
                                             (PornFilterTypes.ThreeDate, 'Today', 'day'),
                                             ),
                                            (('sort_order', [PornFilterTypes.PopularityOrder,
                                                             PornFilterTypes.ViewsOrder,
                                                             PornFilterTypes.RatingOrder]),
                                             ),
                                            ),
                         'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', 'all'),
                                             (PornFilterTypes.HDQuality, 'HD quality', 'hd'),
                                             ),
                         'length_filters': ((PornFilterTypes.AllLength, 'Any duration', ''),
                                            (PornFilterTypes.OneLength, '0-10 min', '1'),
                                            (PornFilterTypes.TwoLength, '10-40 min.', '2'),
                                            (PornFilterTypes.ThreeLength, '40+ min.', '3'),
                                            ),
                         }
        return general_filters, video_filters, video_filters, None, None, channels_filters

    def _prepare_json_params_from_request(self, page_data, url, page_filter, conditions):
        obj_id, gender_value, sort, length, quality, period = \
            super(HClips, self)._prepare_json_params_from_request(page_data, url, page_filter, conditions)
        length = page_filter.length.value if page_filter.length.value != 'all' else ''
        return obj_id, gender_value, sort, length, quality, period
