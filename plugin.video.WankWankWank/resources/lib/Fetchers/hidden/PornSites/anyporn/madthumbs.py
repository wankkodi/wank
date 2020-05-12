from .... import parse_qsl

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter
from .fapster import Fapster
from .pervertsluts import PervertSluts


class MadThumbs(Fapster):
    @property
    def max_pages(self):
        return 8000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'http://www.madthumbs.com/categories/',
            PornCategories.CHANNEL_MAIN: 'http://www.madthumbs.com/sites/',
            PornCategories.PORN_STAR_MAIN: 'http://www.madthumbs.com/models/',
            PornCategories.TAG_MAIN: 'http://www.madthumbs.com/tags/',
            PornCategories.TOP_RATED_VIDEO: 'http://www.madthumbs.com/top-rated/',
            PornCategories.POPULAR_VIDEO: 'http://www.madthumbs.com/most-popular/',
            PornCategories.SEARCH_MAIN: 'http://www.madthumbs.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.madthumbs.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        category_params = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.ViewsOrder, 'Most viewed', 'avg_videos_popularity'),
                                          (PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          ],
                           }
        porn_stars_params = {'sort_order': [(PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                            (PornFilterTypes.ViewsOrder, 'Most viewed', 'avg_videos_popularity'),
                                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                            ],
                             }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                                       (PornFilterTypes.FavorOrder, 'Most Favourite', 'most_favourited'),
                                       ],
                        }
        search_params = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                                        (PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                        (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                                        (PornFilterTypes.FavorOrder, 'Most Favourite', 'most_favourited'),
                                        ],
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_params,
                                         porn_stars_args=porn_stars_params,
                                         channels_args=porn_stars_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='MadThumbs', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(MadThumbs, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="list-tags"]/div[@class="margin-fix"]/ul/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, None)
                                                for x in raw_objects]) if len(raw_objects) > 0 else ([], [], [])
        return links, titles, number_of_videos

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        if true_object.object_type == PornCategories.TAG:
            return super(Fapster, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                page_filter, fetch_base_url)
        if true_object.object_type == PornCategories.SEARCH_MAIN:
            headers = {
                'Accept': '*.*',
                'Cache-Control': 'max-age=0',
                'Referer': self.base_url,
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
            conditions = self.get_proper_filter(page_data).conditions
            true_sort_filter_id = self._default_sort_by[true_object.object_type] \
                if true_object.object_type in self._default_sort_by \
                else page_filter.sort_order.filter_id

            if page_number is None:
                page_number = 1
            params.update({
                'mode': 'async',
                'function': 'get_block',
            })
            if page_filter.length.value is not None:
                params.update(parse_qsl(page_filter.length.value))
            params['from'] = str(page_number).zfill(2)
            params['block_id'] = 'list_videos_videos_list_search_result'
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            if 'from' in params:
                params.pop('from')
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
            params['q'] = self._search_query if true_object.object_type == PornCategories.SEARCH_MAIN \
                else fetch_base_url.split('/')[-2]

            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            return super(PervertSluts, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                     page_filter, fetch_base_url)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(MadThumbs, self)._version_stack + [self.__version]
