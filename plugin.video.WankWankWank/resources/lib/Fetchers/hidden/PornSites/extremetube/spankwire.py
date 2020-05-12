# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote_plus, parse_qs

# Regex
import re

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

# Playlist tools
import m3u8

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoNode, VideoSource, VideoTypes
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter


class SpankWire(PornFetcher):
    category_json_url = 'https://www.spankwire.com/api/categories/list.json'
    porn_star_list_json_url = 'https://www.spankwire.com/api/pornstars'
    video_list_json_url = 'https://www.spankwire.com/api/video/list.json'
    video_request_format = 'https://www.spankwire.com/api/video/{vid}.json'
    search_request_format = 'https://www.spankwire.com/api/search'

    @property
    def possible_empty_pages(self):
        """
        Defines whether it is possible to have empty pages in the site.
        :return:
        """
        return True

    @property
    def category_json_params(self):
        if self.general_filter.current_filters.general.filter_id == \
                PornFilterTypes.StraightType:
            segment_id = 0
        elif self.general_filter.current_filters.general.filter_id == \
                PornFilterTypes.StraightType:
            segment_id = 1
        elif self.general_filter.current_filters.general.filter_id == \
                PornFilterTypes.ShemaleType:
            segment_id = 2
        else:
            raise TypeError('Not suppose to be here...')
        return {
            'segmentId': segment_id,
            'limit': 100,
            'sort': self._video_filters[PornCategories.CATEGORY_MAIN].current_filters.sort_order.value,
        }

    @property
    def porn_star_json_params(self):
        return {
            'limit': 25,
            'sort': self._video_filters[PornCategories.PORN_STAR_MAIN].current_filters.sort_order.value,
            'letter': '',
        }

    @property
    def video_from_category_json_params(self):
        return {
            'segment': self.general_filter.current_filters.general.value,
            'limit': 33,
            'sortby': self._video_filters[PornCategories.CATEGORY_MAIN].current_filters.sort_order.value,
            'period': self._video_filters[PornCategories.CATEGORY_MAIN].current_filters.added_before.value,
        }

    @property
    def video_from_porn_star_json_params(self):
        return {
            'hasLogged': False,
            'limit': 25,
            'sortby': self._video_filters[PornCategories.PORN_STAR].current_filters.sort_order.value,
        }

    @property
    def video_latest_json_params(self):
        return {
            'segment': self.general_filter.current_filters.general.value,
            'limit': 33,
            'sortby': 'recent',
        }

    @property
    def video_trending_json_params(self):
        return {
            'segment': self.general_filter.current_filters.general.value,
            'limit': 33,
            'sortby': 'trending',
        }

    @property
    def video_most_viewed_json_params(self):
        return {
            'segment': self.general_filter.current_filters.general.value,
            'limit': 33,
            'sortby': 'views',
            'period': self._video_filters[PornCategories.VIDEO].current_filters.period.value,
        }

    @property
    def video_top_rated_json_params(self):
        return {
            'segment': self.general_filter.current_filters.general.value,
            'limit': 33,
            'sortby': 'rating',
            'period': self._video_filters[PornCategories.VIDEO].current_filters.period.value,
        }

    @property
    def video_longest_json_params(self):
        return {
            'segment': self.general_filter.current_filters.general.value,
            'limit': 33,
            'sortby': 'duration',
            'period': self._video_filters[PornCategories.VIDEO].current_filters.period.value,
        }

    @property
    def video_most_talked_json_params(self):
        return {
            'segment': self.general_filter.current_filters.general.value,
            'limit': 33,
            'sortby': 'comments',
            'period': self._video_filters[PornCategories.VIDEO].current_filters.period.value,
        }

    @property
    def search_json_params(self):
        return {
            'segment': self.general_filter.current_filters.general.value,
            'limit': 33,
            'sort': self._video_filters[PornCategories.SEARCH_MAIN].current_filters.sort_order.value,
            'uploaded': self._video_filters[PornCategories.SEARCH_MAIN].current_filters.period.value,
        }

    max_flip_images = 16

    @property
    def object_urls(self):
        general_filter_value = self.general_filter.current_filters.general.value
        return {
            PornCategories.CATEGORY_MAIN:
                'https://www.spankwire.com/categories/{type}'.format(type=general_filter_value),
            PornCategories.PORN_STAR_MAIN:
                'https://www.spankwire.com/pornstars',
            PornCategories.LATEST_VIDEO:
                'https://www.spankwire.com/recentvideos/{type}'.format(type=general_filter_value),
            PornCategories.MOST_VIEWED_VIDEO:
                'https://www.spankwire.com/home1/{type}/Year/Views'.format(type=general_filter_value),
            PornCategories.TOP_RATED_VIDEO:
                'https://www.spankwire.com/home1/{type}/Year/Rating'.format(type=general_filter_value),
            PornCategories.MOST_DISCUSSED_VIDEO:
                'https://www.spankwire.com/home1/{type}/Year/Comments'.format(type=general_filter_value),
            PornCategories.LONGEST_VIDEO:
                'https://www.spankwire.com/home1/{type}/Year/Duration'.format(type=general_filter_value),
            PornCategories.POPULAR_VIDEO:
                'https://www.spankwire.com/trendingvideos/{type}'.format(type=general_filter_value),
            PornCategories.SEARCH_MAIN:
                'https://www.spankwire.com/search/{type}/keyword'.format(type=general_filter_value),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.spankwire.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', 'Straight'),
                                              (PornFilterTypes.GayType, 'Gay', 'Gay'),
                                              (PornFilterTypes.ShemaleType, 'Shemale', 'Tranny'),
                                              ],
                          }
        porn_stars_filter = {'sort_order': [(PornFilterTypes.PopularityOrder, 'By popularity', 'popular'),
                                            (PornFilterTypes.AlphabeticOrder, 'By alphabet', 'abc'),
                                            (PornFilterTypes.NumberOfVideosOrder, 'By no. of videos', 'number'),
                                            ],
                             }
        single_porn_star_filter = {'sort_order': [(PornFilterTypes.DateOrder, 'Recent videos', 'recent'),
                                                  (PornFilterTypes.ViewsOrder, 'Most viewed', 'views'),
                                                  (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                                  ],
                                   }
        categories_filter = {'sort_order': [(PornFilterTypes.DateOrder, 'Recently Updated', 'recent'),
                                            (PornFilterTypes.AlphabeticOrder, 'Alphabetical', 'abc'),
                                            (PornFilterTypes.NumberOfVideosOrder, 'No. of videos', 'number'),
                                            ],
                             }
        single_category_filter = {'sort_order': [(PornFilterTypes.ViewsOrder, 'Most viewed', 'views'),
                                                 (PornFilterTypes.DateOrder, 'Most recent', 'recent'),
                                                 (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                                 (PornFilterTypes.TrendingOrder, 'Trending', 'trending'),
                                                 (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                                 ],
                                  'period_filters': [(PornFilterTypes.AllAddedBefore, 'All time', 'All_time'),
                                                     (PornFilterTypes.OneAddedBefore, 'Today', 'today'),
                                                     (PornFilterTypes.TwoAddedBefore, 'Yesterday', 'yesterday'),
                                                     (PornFilterTypes.ThreeAddedBefore, 'Week', 'week'),
                                                     (PornFilterTypes.FourAddedBefore, 'Month', 'month'),
                                                     (PornFilterTypes.FiveAddedBefore, 'Year', 'year'),
                                                     ],
                                  }
        video_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Most recent', 'recent'),
                                        (PornFilterTypes.ViewsOrder, 'Most viewed', 'views'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        (PornFilterTypes.RelevanceOrder, 'Most relevant', 'relevance'),
                                        (PornFilterTypes.PopularityOrder, 'Popularity', 'popularity'),
                                        (PornFilterTypes.NumberOfVideosOrder, 'Number of videos', 'number'),
                                        (PornFilterTypes.AlphabeticOrder, 'Alphabetic', 'abc'),
                                        ],
                         'period_filters': [(PornFilterTypes.AllAddedBefore, 'All time', 'All_time'),
                                            (PornFilterTypes.OneAddedBefore, 'Today', 'today'),
                                            (PornFilterTypes.TwoAddedBefore, 'Yesterday', 'yesterday'),
                                            (PornFilterTypes.ThreeAddedBefore, 'Week', 'week'),
                                            (PornFilterTypes.FourAddedBefore, 'Month', 'month'),
                                            (PornFilterTypes.FiveAddedBefore, 'Year', 'year'),
                                            ],
                         }
        search_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Most relevant', 'relevance'),
                                         (PornFilterTypes.DateOrder, 'Most recent', 'recent'),
                                         ],
                          'period_filters': [(PornFilterTypes.AllAddedBefore, 'All time', 'all_time'),
                                             (PornFilterTypes.OneAddedBefore, 'Past 24 hours', 'past_24_hours'),
                                             (PornFilterTypes.TwoAddedBefore, 'Past 2 days', 'past_2_days'),
                                             (PornFilterTypes.ThreeAddedBefore, 'Past week', 'past_week'),
                                             (PornFilterTypes.FourAddedBefore, 'Past month', 'past_month'),
                                             (PornFilterTypes.FiveAddedBefore, 'Past year', 'past_year'),
                                             ],
                          }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter,
                                         porn_stars_args=porn_stars_filter,
                                         categories_args=categories_filter,
                                         single_category_args=single_category_filter,
                                         single_porn_star_args=single_porn_star_filter,
                                         single_tag_args=video_filters,
                                         search_args=search_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='SpankWire', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SpankWire, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        page_json = page_request.json()

        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x['id'],
                                       url=urljoin(self.base_url, x['url']),
                                       title=x['name'],
                                       image_link=x['image'] if len(x['image']) > 0 else None,
                                       number_of_videos=x['videosNumber'],
                                       raw_data=x,
                                       object_type=PornCategories.CATEGORY,
                                       super_object=category_data,
                                       )
               for x in page_json['items']]
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        page_json = page_request.json()

        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x['id'],
                                       url=urljoin(self.base_url, x['url']),
                                       title=x['name'],
                                       image_link=x['thumb'] if len(x['thumb']) > 0 else None,
                                       number_of_videos=x['videos'],
                                       raw_data=x,
                                       object_type=PornCategories.PORN_STAR,
                                       super_object=porn_star_data,
                                       )
               for x in page_json['items']]
        porn_star_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        video_url = self.video_request_format.format(vid=video_data.raw_data['id'])
        headers = {
            'Accept': 'application/json, text/plain, */*, image/webp',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_url, headers=headers)
        request_data = tmp_request.json()

        res = [VideoSource(link=v, video_type=VideoTypes.VIDEO_REGULAR,
                           resolution=re.findall(r'(?:quality_)(\d+)(?:p*)', k)[0])
               for k, v in request_data['videos'].items()]
        if 'HLS' in request_data and request_data['HLS'] is not None:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;'
                          'q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Cache-Control': 'max-age=0',
                'Referer': video_data.url,
                'User-Agent': self.user_agent
            }
            segment_request = self.session.get(request_data['HLS'], headers=headers)
            video_m3u8 = m3u8.loads(segment_request.text)
            video_playlists = video_m3u8.playlists
            res.extend([VideoSource(link=urljoin(request_data['HLS'], x.uri),
                                    video_type=VideoTypes.VIDEO_SEGMENTS,
                                    quality=x.stream_info.bandwidth,
                                    resolution=x.stream_info.resolution[1],
                                    codec=x.stream_info.codecs)
                        for x in video_playlists])

        res.sort(key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=res)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        page_request = self.get_object_request(category_data) if fetched_request is None \
            else fetched_request
        if not self._check_is_available_page(category_data, page_request):
            return 1
        raw_res = page_request.json()
        return raw_res['pages']

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        assert page_request.status_code == 200
        videos = page_request.json()
        videos = [PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                           obj_id=x['id'],
                                           url=urljoin(self.base_url, x['url']),
                                           title=x['title'],
                                           description=x['description'],
                                           image_link=x['flipBookPath'].format(index=1),
                                           flip_images_link=[x['flipBookPath'].format(index=i)
                                                             for i in range(1, self.max_flip_images)],
                                           preview_video_link=x['videoPreview'] if x['videoPreview'] is not False
                                           else None,
                                           is_hd=x['isHD'],
                                           duration=x['duration'],
                                           added_before=x['time_approved_on'],
                                           rating=x['rating'],
                                           number_of_views=x['viewed'],
                                           raw_data=x,
                                           object_type=PornCategories.VIDEO,
                                           super_object=page_data,
                                           )
                  for x in videos['items']]
        page_data.add_sub_objects(videos)
        return videos

    def _prepare_request_params(self, object_data):
        """
        Prepares request params according to the object type.
        """
        object_type = object_data.true_object.object_type
        if object_type == PornCategories.PORN_STAR:
            url = self.video_list_json_url
            params = self.video_from_category_json_params.copy()
            params['pornstarId'] = object_data.raw_data['id']
        elif object_type == PornCategories.CATEGORY:
            url = self.video_list_json_url
            params = self.video_from_category_json_params.copy()
            params['category'] = object_data.raw_data['id']
        elif object_type == PornCategories.PORN_STAR_MAIN:
            url = self.porn_star_list_json_url
            params = self.porn_star_json_params.copy()
        elif object_type == PornCategories.CATEGORY_MAIN:
            url = self.category_json_url
            params = self.category_json_params.copy()
        elif object_type == PornCategories.LATEST_VIDEO:
            url = self.video_list_json_url
            params = self.video_latest_json_params.copy()
        elif object_type == PornCategories.MOST_VIEWED_VIDEO:
            url = self.video_list_json_url
            params = self.video_most_viewed_json_params.copy()
        elif object_type == PornCategories.TOP_RATED_VIDEO:
            url = self.video_list_json_url
            params = self.video_top_rated_json_params.copy()
        elif object_type == PornCategories.MOST_DISCUSSED_VIDEO:
            url = self.video_list_json_url
            params = self.video_most_talked_json_params.copy()
        elif object_type == PornCategories.LONGEST_VIDEO:
            url = self.video_list_json_url
            params = self.video_longest_json_params.copy()
        elif object_type == PornCategories.POPULAR_VIDEO:
            url = self.video_list_json_url
            params = self.video_trending_json_params.copy()
        elif object_type == PornCategories.SEARCH_MAIN:
            split_url = object_data.url.split('/')
            url = self.search_request_format
            params = self.search_json_params.copy()
            params['query'] = split_url[-1]
        else:
            raise RuntimeError('Wrong object type {o}!'.format(o=object_type))
            # url = object_data.url
            # params = {}
        return url, params

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        raise NotImplemented

    def _get_object_request_no_exception_check(self, page_data, override_page_number=None, override_params=None,
                                               override_url=None):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :param override_page_number: Override page number.
        :param override_params: Override params.
        :param override_url: Override url.
        :return: Page request
        """
        url, additional_params = self._prepare_request_params(page_data)

        base_url = page_data.url.split('?')[0]
        if len(page_data.url.split('?')) > 1:
            params = page_data.url.split('?')[1]
            params = parse_qs(params)
        else:
            params = {}

        params.update({k: v for k, v in additional_params.items() if k not in params})
        page_number = page_data.page_number if override_page_number is None else override_page_number
        if page_number is not None and page_number != 1:
            params['page'] = page_number

        headers = {
            'Accept': 'application/json, text/plain, */*, image/webp',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Referer': base_url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        page_request = self.session.get(url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '/{q}'.format(q=quote_plus(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(SpankWire, self)._version_stack + [self.__version]
