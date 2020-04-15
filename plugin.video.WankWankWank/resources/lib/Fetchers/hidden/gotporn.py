# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornErrorModule, PornFetchUrlError

# Internet tools
from .. import urljoin, urlparse, quote_plus

# Regex
import re

# Math
import math

# Request Exception
import json
try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# Generator id
from ..id_generator import IdGenerator


class GotPorn(PornFetcher):
    channel_json_request_template = 'https://www.gotporn.com/channels/{chid}/get-more-videos'

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.gotporn.com/categories?src=hm',
            PornCategories.TAG_MAIN: 'https://www.gotporn.com/categories?src=hm',
            PornCategories.CHANNEL_MAIN: 'https://www.gotporn.com/channels?src=hm',
            PornCategories.LATEST_VIDEO: 'https://www.gotporn.com/?page=2&amp;src=mn:mr',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.gotporn.com/most-viewed?src=hm',
            PornCategories.TOP_RATED_VIDEO: 'https://www.gotporn.com/top-rated?src=hm',
            PornCategories.LONGEST_VIDEO: 'https://www.gotporn.com/longest?src=hm',
            PornCategories.HD_VIDEO: 'https://www.gotporn.com/?hdFirst=1&amp;src=hm&amp;hdFirstClicked=1',
            PornCategories.ALL_VIDEO: 'https://www.gotporn.com/?src=mn:mr',
            PornCategories.SEARCH_MAIN: 'https://www.gotporn.com/results',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.HD_VIDEO: PornFilterTypes.HDOrder,
            PornCategories.ALL_VIDEO: PornFilterTypes.RecommendedOrder,
        }

    @property
    def number_of_videos_per_channel_page(self):
        return 16

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.gotporn.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filters = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', 'straight'),
                                               (PornFilterTypes.GayType, 'Gay', 'gay'),
                                               (PornFilterTypes.ShemaleType, 'Shemale', 'shemale'),
                                               ]
                           }
        channels_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Newest videos', None),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Most videos', 'videos-num'),
                                           (PornFilterTypes.AlphabeticOrder, 'A-Z', 'abc'),
                                           ],
                            }
        video_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Newest', None),
                                        (PornFilterTypes.RecommendedOrder, 'Recommended', 'recommended'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        (PornFilterTypes.RatingOrder, 'Rating', 'top-rated'),
                                        (PornFilterTypes.ViewsOrder, 'Views', 'most-viewed'),
                                        (PornFilterTypes.FeaturedOrder, 'Featured', 'featured'),
                                        ],
                         'length_filters': [(PornFilterTypes.AllLength, 'Any duration', None),
                                            (PornFilterTypes.OneLength, '0-5 min', 'duration=0-5'),
                                            (PornFilterTypes.TwoLength, '5-20 min', 'duration=5-20'),
                                            (PornFilterTypes.ThreeLength, '20+ min', 'duration=20-'),
                                            ],
                         'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', None),
                                             (PornFilterTypes.HDQuality, 'HD quality', 'hdFirst=1'),
                                             ],
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filters,
                                         channels_args=channels_filters,
                                         single_category_args=video_filters,
                                         single_tag_args=video_filters,
                                         video_args=video_filters,
                                         search_args=video_filters,
                                         )

    def __init__(self, source_name='GotPorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(GotPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/76.0.3809.100 Safari/537.36'

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//ul[@class="list categories-list clearfix"]/li/a')
        res = []
        for category in categories:
            title = category.xpath('./span[@class="text"]/text()')
            assert len(title) == 1

            number_of_videos = category.xpath('./span[@class="num"]/text()')
            assert len(number_of_videos) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(category_data.url, category.attrib['href']),
                                                  title=title[0],
                                                  number_of_videos=int(re.findall(r'\d+', number_of_videos[0])[0]),
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channels.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="channel-card channel-card-sm channel-list-card clearfix"]/'
                                'header[@class="clearfix"]')
        res = []
        for category in categories:
            link = category.xpath('./a')
            assert len(link) == 1

            image = category.xpath('./a/img/@src')
            assert len(image) == 1

            title = category.xpath('./div[@class="header-content"]/div[@class="top"]/h2[@class="title left"]/a/text()')
            assert len(title) == 1

            sub_categories = category.xpath('./div[@class="header-content"]/div[@class="description bottom"]/'
                                            'div[@class="content"]/div[@class="tags tags-sm tags-muted"]/a')
            assert len(sub_categories) > 0
            additional_data = [{'url': urljoin(channel_data.url, x.attrib['href']),
                                'name': self._clear_text(x.text)}
                               for x in sub_categories]

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(channel_data.url, link[0].attrib['href']),
                                                  image_link=urljoin(channel_data.url, image[0]),
                                                  title=title[0],
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.CHANNEL,
                                                  super_object=channel_data,
                                                  )
            res.append(object_data)
        channel_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles. The fetched objects MUST be sorted wrt title.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        links = tree.xpath('.//ul[@class="list tags-list clearfix"]/li/a/@href')
        titles = tree.xpath('.//ul[@class="list tags-list clearfix"]/li/a/span[@class="text"]/text()')
        numbers_of_videos = [re.findall(r'\d+', x) for x in tree.xpath('.//ul[@class="list tags-list clearfix"]/li/a/'
                                                                       'span[@class="num"]/text()')]
        return links, titles, numbers_of_videos

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        video_url = video_data.url
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_url, headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)

        video_links = sorted((VideoSource(link=x.attrib['src'],
                                          resolution=int(re.findall(r'\d+', x.attrib['label'])[0])
                                          if 'label' in x.attrib else None)
                              for x in tmp_tree.xpath('.//video/source')),
                             key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if (
                category_data.object_type in (PornCategories.CHANNEL,) and
                self.number_of_videos_per_channel_page is not None
        ):
            # We want to treat it in a special way
            page_request = self.get_object_request(category_data, force_fetch_channel_page=True) \
                if fetched_request is None else fetched_request
            tree = self.parser.parse(page_request.text)
            total_number_of_videos = tree.xpath('.//button[@id="show-more-videos-btn"]')
            assert len(total_number_of_videos) == 1
            total_number_of_videos = int(total_number_of_videos[0].attrib['data-videos-num'])
            videos = tree.xpath('.//span[@class="video-thumb"]')
            return math.ceil(total_number_of_videos / len(videos))
        else:
            page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
            tree = self.parser.parse(page_request.text)
            available_pages = self._get_available_pages_from_tree(tree)
            return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//div[@class="btn-group-squared pagination"]/a/text()') if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        try:
            tmp_html = page_request.json()
            tree = self.parser.parse(tmp_html['tpl'])
        except JSONDecodeError:
            tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//li[@class="video-item poptrigger"]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1
            url = urljoin(self.base_url, link[0].attrib['href'])
            title = self._clear_text(link[0].attrib['data-title'])

            video_length = video_tree_data.xpath('./a/span[@class="video-thumb"]/span[@class="video-data-wrap"]/'
                                                 'span[@class="duration"]/text()')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0])

            img = video_tree_data.xpath('./a/span[@class="video-thumb"]/span[@class="video-thumb"]/img')
            assert len(img) == 1

            is_hd = video_tree_data.xpath('./a/h3')
            assert len(is_hd) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['data-id'],
                                                  url=url,
                                                  title=title,
                                                  image_link=img[0].attrib['src'],
                                                  is_hd='hd' in is_hd[0].attrib['class'],
                                                  duration=self._format_duration(video_length),
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def get_object_request(self, page_data, override_page_number=None, override_params=None, override_url=None,
                           force_fetch_channel_page=False, send_error=True):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :param override_page_number: Override page number.
        :param override_params: Override params.
        :param override_url: Override url.
        :param force_fetch_channel_page: Flag that indicates whether we fetch the whole channel page or its, json.
        :param send_error: Flag that indicates whether we send the error to the server. True by default.
        :return: Page request
        """
        if page_data.object_type == PornCategories.CHANNEL and force_fetch_channel_page is True:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3',
                'Cache-Control': 'max-age=0',
                # 'Host': self.host_name,
                'Referer': self.base_url,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }

            page_request = self.session.get(page_data.url, headers=headers)
            if not self._check_is_available_page(page_request):
                if send_error is True:
                    current_page_filters = self.get_proper_filter(page_data).current_filters_text()
                    general_filters = self.general_filter.current_filters_text()
                    error_module = PornErrorModule(self.data_server,
                                                   self.source_name,
                                                   page_request.url,
                                                   'Could not fetch {url}'.format(url=page_request.url),
                                                   current_page_filters,
                                                   general_filters,
                                                   )
                else:
                    error_module = None
                raise PornFetchUrlError(page_request, error_module)

            return page_request
        else:
            return super(GotPorn, self).get_object_request(page_data, override_page_number, override_params,
                                                           override_url)

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        # split_url = urlparse(fetch_base_url)
        split_url = fetch_base_url.split('/')
        last_empty_element = False
        if len(split_url[-1]) != 0:
            last_empty_element = True
            split_url.append('')

        # We update the cookies as well for orientation
        self.session.cookies.set(domain=self.host_name, name='orientation',
                                 value=self.video_filters.general_filters.current_filters.general.value)
        if self.video_filters.general_filters.current_filters.general.filter_id != PornFilterTypes.StraightType:
            if split_url[3] != self.video_filters.general_filters.current_filters.general.value:
                split_url.insert(3, self.video_filters.general_filters.current_filters.general.value)

        if true_object.object_type in (PornCategories.CATEGORY, PornCategories.TAG, PornCategories.CHANNEL_MAIN,
                                       PornCategories.SEARCH_MAIN) + tuple(self._default_sort_by.keys()):
            if page_filter.sort_order.value is not None:
                if true_object.object_type in (PornCategories.CATEGORY, PornCategories.TAG,
                                               PornCategories.CHANNEL_MAIN):
                    split_url.insert(-1, page_filter.sort_order.value)
                elif true_object.object_type in (PornCategories.SEARCH_MAIN,):
                    params['sort'] = page_filter.sort_order.value
            if page_filter.length.filter_id != PornFilterTypes.AllLength:
                k, v = page_filter.length.value.split('=')
                params[k] = v
            if page_filter.quality.filter_id != PornFilterTypes.AllQuality:
                k, v = page_filter.quality.value.split('=')
                params[k] = v

        elif true_object.object_type in (PornCategories.CHANNEL,):
            # We treat it in a special way
            ch_id = split_url[4]
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Cache-Control': 'max-age=0',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                # 'Host': self.host_name,
                'Origin': self.base_url,
                'Referer': page_data.url,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
            request_url = self.channel_json_request_template.format(chid=ch_id)
            data = {'offset': 16 * page_number - 1 if page_number is not None else 0}
            page_request = self.session.post(request_url, headers=headers, data=data)
            return page_request

        if page_number is not None:
            params['page'] = page_number

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        if last_empty_element:
            split_url = split_url[:-1]
        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?search_query={q}'.format(q=quote_plus(query))


class PornHD(PornFetcher):
    prime_host_name = 'www.pornhdprime.com'

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.pornhd.com/category',
            PornCategories.CHANNEL_MAIN: 'https://www.pornhd.com/channel',
            PornCategories.PORN_STAR_MAIN: 'https://www.pornhd.com/pornstars',
            PornCategories.RECOMMENDED_VIDEO: 'https://www.pornhd.com/?order=featured',
            PornCategories.LATEST_VIDEO: 'https://www.pornhd.com/?order=newest',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.pornhd.com/?order=most-popular',
            PornCategories.LONGEST_VIDEO: 'https://www.pornhd.com/?order=longest',
            PornCategories.TOP_RATED_VIDEO: 'https://www.pornhd.com/?order=top-rated',
            PornCategories.LIVE_VIDEO: 'https://www.pornhd.com/live-sex',
            PornCategories.SEARCH_MAIN: 'https://www.pornhd.com/search',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.RECOMMENDED_VIDEO: PornFilterTypes.RecommendedOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LIVE_VIDEO: PornFilterTypes.LiveOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornhd.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        categories_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most Popular', 'most-popular'),
                                             (PornFilterTypes.AlphabeticOrder, 'Alphabetical ', 'alphabetical'),
                                             (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'video-count'),
                                             ],
                              }
        porn_stars_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most Popular', 'most-popular'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'video-count'),
                                             (PornFilterTypes.AlphabeticOrder, 'Alphabetical ', 'alphabetical'),
                                             ],
                              }
        channels_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most Popular', 'most-popular'),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'video-count'),
                                           (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                                           (PornFilterTypes.AlphabeticOrder, 'Alphabetical ', 'alphabetical'),
                                           ],
                            }
        video_filters = {'sort_order': [(PornFilterTypes.RecommendedOrder, 'Featured', 'featured'),
                                        (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                                        (PornFilterTypes.ViewsOrder, 'Views', 'most-popular'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        (PornFilterTypes.RatingOrder, 'Rating', 'top-rated'),
                                        ],
                         }
        search_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Relevant', 'mostrelevant'),
                                         (PornFilterTypes.RecommendedOrder, 'Featured', 'featured'),
                                         (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                                         (PornFilterTypes.ViewsOrder, 'Views', 'most-popular'),
                                         (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                         (PornFilterTypes.RatingOrder, 'Rating', 'top-rated'),
                                         ],
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         channels_args=channels_filters,
                                         porn_stars_args=porn_stars_filters,
                                         categories_args=categories_filters,
                                         single_category_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         single_tag_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='PornHD', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornHD, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_object(category_data,
                                             './/ul[@class="tag-150-list"]/li',
                                             PornCategories.CATEGORY)

    def _update_available_porn_stars(self, pornstar_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_object(pornstar_data,
                                             './/ul[@class="pornstar-tag-list"]/li',
                                             PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channels.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_object(channel_data,
                                             './/ul[@class="tag-150-list"]/li',
                                             PornCategories.CHANNEL)

    def _update_available_object(self, object_data, page_xpath, object_type):
        """
        Fetches all the available object.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(page_xpath)
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            if len(link_data) == 0:
                # dummy node
                continue

            image = category.xpath('./a/span/img/@data-original')
            if len(image) == 0:
                image = category.xpath('./a/span/img/@src')
                assert len(image) > 0

            title = category.xpath('./a/span/img/@alt')
            title = self._clear_text(title[0])

            additional_info = category.xpath('./div[@class="info"]/div[@class="video-count"]')
            number_of_videos = re.findall(r'\d+', additional_info[0].text) if len(additional_info) > 0 else None
            number_of_videos = int(number_of_videos[0]) \
                if number_of_videos is not None and len(number_of_videos) > 0 else None
            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link_data[0].attrib['href'],
                                                      url=urljoin(self.base_url, link_data[0].attrib['href']),
                                                      title=title,
                                                      image_link=image[0],
                                                      number_of_videos=number_of_videos,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        object_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """

        video_url = video_data.url
        if urlparse(video_url).hostname == self.prime_host_name:
            # In case of the prime video, we need to fetch it separately.
            return self._get_prime_video_links_from_video_data(video_data)

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_url, headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)

        request_data = re.findall(r'(?:sources:[ \n\r]*)({.*?})',
                                  [x for x in tmp_tree.xpath('.//script/text()') if 'window.players' in x][0])
        assert len(request_data) == 1
        new_video_data = json.loads(request_data[0])
        video_links = sorted((VideoSource(link=v, resolution=re.findall(r'\d*', k)[0])
                              for k, v in new_video_data.items()),
                             key=lambda x: x.resolution, reverse=True)

        return VideoNode(video_sources=video_links)

    def _get_prime_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """

        video_url = video_data.url
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_url, headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)

        request_data = tmp_tree.xpath('.//video[@id="html5-player"]/source')
        assert len(request_data) > 0
        video_links = sorted((VideoSource(link=x.attrib['src'], resolution=int(x.attrib['res'])) for x in request_data),
                             key=lambda y: y.resolution, reverse=True)

        return VideoNode(video_sources=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type == PornCategories.LIVE_VIDEO:
            return self._binary_search_max_number_of_live_pages(category_data)
        # We perform binary search
        start_page = category_data.page_number if category_data.page_number is not None else 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        max_page = max(pages)
        if (max_page - start_page) < self._binary_search_page_threshold:
            return max_page
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _binary_search_max_number_of_pages(self, category_data, last_available_number_of_pages):
        """
        Performs binary search in order to find the last available page.
        :param category_data: Category data.
        :param last_available_number_of_pages: Last available number of pages. Will be the pivot for our next search.
        By default is None, which mean the original pivot will be used...
        :return: Page request
        """
        left_page = 1
        right_page = self.max_pages
        page = last_available_number_of_pages if last_available_number_of_pages is not None \
            else int(math.ceil((right_page + left_page) / 2))
        use_max_page_flag = True
        while 1:
            page_request = self.get_object_request(category_data, page)
            if not self._check_is_available_page(page_request):
                # We moved too far...
                right_page = page - 1
                if left_page >= right_page:
                    use_max_page_flag = False
                    left_page = right_page - 1
            else:
                tree = self.parser.parse(page_request.text)
                pages = self._get_available_pages_from_tree(tree)
                if len(pages) == 0:
                    # We also moved too far...
                    right_page = page - 1
                else:
                    max_page = max(pages) if use_max_page_flag is True else page
                    if max_page - page < self._binary_search_page_threshold:
                        return max_page

                    left_page = max_page
            page = int(math.ceil((right_page + left_page) / 2))

    def _binary_search_max_number_of_live_pages(self, category_data):
        """
        Override of super method with local modifications...
        Performs binary search in order to find the last available page.
        :param category_data: Category data.
        :return: Page request
        """
        left_page = 1
        right_page = self.max_pages
        page = math.ceil((right_page + left_page) / 2)
        while 1:
            page_request = self.get_object_request(category_data, page)
            if not self._check_is_available_page(page_request):
                # We moved too far...
                right_page = page - 1
            else:
                tree = self.parser.parse(page_request.text)
                videos = tree.xpath('.//ul[@class="thumbs live-girls"]/li')
                if len(videos) == 0:
                    # We also moved too far...
                    right_page = page - 1
                else:
                    left_page = page

            if left_page == right_page:
                return left_page

            page = math.ceil((right_page + left_page) / 2)

    # def _check_is_available_page(self, page_request):
    #     """
    #     In binary search performs test whether the current page is available.
    #     :param page_request: Page request.
    #     :return:
    #     """
    #     return page_request.ok
    #     # tree = self.parser.parse(page_request.text)
    #     # return len(self._get_available_pages_from_tree(tree)) > 0

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        pages = tree.xpath('.//div[@class="pager paging"]/ul/li/span/@data-query-value')
        tmp_res = [int(x) for x in pages if x.isdigit()]
        if all(tmp_res[0] > x for x in tmp_res[1:]):
            return tmp_res[1:]
        return tmp_res

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 1

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = ([x for x in tree.xpath('.//ul[@class="thumbs"]/li') if 'data-video' in x.attrib] +
                  [x for x in tree.xpath('.//ul[@class="thumbs live-girls"]/li')])
        res = []
        for video_tree_data in videos:
            preview_video = video_tree_data.attrib['data-webm'] if 'data-webm' in video_tree_data.attrib else None
            if preview_video is None:
                preview_video = video_tree_data.attrib['data-mp4'] if 'data-mp4' in video_tree_data.attrib else None

            link_data = [x for x in video_tree_data.xpath('./a')
                         if 'class' in x.attrib and 'thumb' in x.attrib['class']]
            if len(link_data) == 0:
                # We want not to include premium content
                continue
                # link_data = video_tree_data.xpath('./a[@class="thumb videoThumb prime-video-thumb '
                #                                   'rotate-video-thumb popTrigger"]')

            if 'data-thumbs' in link_data[0].attrib:
                flix_image = re.findall(r'(?:")(.*?)(?:")', link_data[0].attrib['data-thumbs'])
                flix_image = [urljoin(page_data.url, re.sub(r'\\/', '/', x)) for x in flix_image]
            else:
                flix_image = None

            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            url = urljoin(self.base_url, link)

            img = link_data[0].xpath('./img/@src')
            assert len(img) == 1
            if 'data:image' in img[0]:
                img = link_data[0].xpath('./img/@data-original')
            assert len(img) == 1
            image = img[0]

            video_length = link_data[0].xpath('./div[@class="meta"]/time/text()')
            if len(video_length) == 0:
                video_length = link_data[0].xpath('./div[@class="meta transition"]/time/text()')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0])

            title = video_tree_data.xpath('./a[@class="title"]/text()')
            assert len(title) == 1
            title = self._clear_text(title[0])

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=url,
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  preview_video_link=preview_video,
                                                  duration=self._format_duration(video_length),
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            # 'Referer': self.base_url,
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_number is not None and page_number > 1:
            params['page'] = [page_number]

        if true_object.object_type not in self._default_sort_by:
            params['order'] = [page_filter.sort_order.value]

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        if (
                true_object.object_type == PornCategories.SEARCH_MAIN and len(page_request.history) > 0 and
                ((page_number is not None and page_number > 1) or
                 page_filter.sort_order.filter_id != PornFilterTypes.RelevanceOrder)
        ):
            # We have a redirection
            fetch_base_url = page_request.url
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)

        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?search={q}'.format(q=quote_plus(query))


class PinFlix(PornHD):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.pinflix.com/category',
            PornCategories.PORN_STAR_MAIN: 'https://www.pinflix.com/pornstars',
            PornCategories.RECOMMENDED_VIDEO: 'https://www.pinflix.com/?order=featured',
            PornCategories.LATEST_VIDEO: 'https://www.pinflix.com/?order=newest',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.pinflix.com/?order=most-popular',
            PornCategories.LONGEST_VIDEO: 'https://www.pinflix.com/?order=longest',
            PornCategories.TOP_RATED_VIDEO: 'https://www.pinflix.com/?order=top-rated',
            PornCategories.LIVE_VIDEO: 'https://www.pinflix.com/live-sex',
            PornCategories.SEARCH_MAIN: 'https://www.pinflix.com/search',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.RECOMMENDED_VIDEO: PornFilterTypes.RecommendedOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LIVE_VIDEO: PornFilterTypes.LiveOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pinflix.com/'

    def __init__(self, source_name='PinFlix', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PinFlix, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_object(category_data,
                                             './/section[@class="small-thumb-list lazy-load"]/article/a',
                                             PornCategories.CATEGORY)

    def _update_available_porn_stars(self, pornstar_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_object(pornstar_data,
                                             './/section[@class="section-margin small-thumb-list lazy-load"]/'
                                             'article/a',
                                             PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_object(channel_data,
                                             './/section[@class="section-margin small-thumb-list lazy-load"]/'
                                             'article/a',
                                             PornCategories.CHANNEL)

    def _update_available_object(self, object_data, page_xpath, object_type):
        """
        Fetches all the available object.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(page_xpath)
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./picture/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            title = category.xpath('./span[@class="thumb-title"]') + category.xpath('./div[@class="thumb-title"]')
            assert len(title) == 1
            title = title[0].text

            number_of_videos = category.xpath('./div[@class="video-count"]')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].text)[0]) if len(number_of_videos) == 1 else None

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image[0],
                                                      number_of_videos=number_of_videos,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        object_data.add_sub_objects(res)
        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _binary_search_max_number_of_pages(self, category_data, last_available_number_of_pages):
        """
        Performs binary search in order to find the last available page.
        :param category_data: Category data.
        :param last_available_number_of_pages: Last available number of pages. Will be the pivot for our next search.
        By default is None, which mean the original pivot will be used...
        :return: Page request
        """
        left_page = 1
        right_page = self.max_pages
        page = last_available_number_of_pages if last_available_number_of_pages is not None \
            else math.ceil((right_page + left_page) / 2)
        while 1:
            page_request = self.get_object_request(category_data, page)
            if not self._check_is_available_page(page_request):
                # We moved too far...
                right_page = page - 1
            else:
                tree = self.parser.parse(page_request.text)
                videos = self._get_available_pages_from_tree(tree)
                if len(videos) == 0:
                    # We also moved too far...
                    right_page = page - 1
                else:
                    left_page = page

            if left_page == right_page:
                return left_page

            page = math.ceil((right_page + left_page) / 2)

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        our_page = tree.xpath('.//a[@class="btn page active"]')
        our_page = int(self._clear_text(our_page[0].text)) if len(our_page) > 0 else None
        pages = tree.xpath('.//a[@id="paginator-btn"]')
        if our_page is not None:
            pages += [int(self._clear_text(x.text))
                      for x in tree.xpath('.//div[@class="btn-group btn-group-squared pagination"]/a')
                      if x.text is not None and x.text.isdigit() and int(self._clear_text(x.text)) >= our_page]
        return pages

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = ([x for x in tree.xpath('.//div[@class="video-list-container"]/article[@class="video-item "]')] +
                  [x for x in tree.xpath('.//div[@class="video-list-container live-sex"]/'
                                         'article[@class="video-item live-video-item"]')]
                  )
        res = []
        for video_tree_data in videos:
            link_data = [x for x in video_tree_data.xpath('./a')
                         if 'class' in x.attrib and 'thumb-bottom' in x.attrib['class']]
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = self._clear_text(link_data[0].text)
            description = link_data[0].attrib['aria-label'] if 'aria-label' in link_data[0].attrib else None

            image_data = video_tree_data.xpath('./section[@class="thumb-top"]/a/picture/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            image = urljoin(page_data.url, image)

            video_length = video_tree_data.xpath('./section[@class="thumb-top"]/span[@class="meta"]/time/text()')
            if len(video_length) == 0:
                video_length = video_tree_data.xpath('./section[@class="thumb-top"]/'
                                                     'span[@class="meta transition"]/time/text()')
            video_length = self._clear_text(video_length[0]) if len(video_length) == 1 else None

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  description=description,
                                                  image_link=image,
                                                  duration=self._format_duration(video_length)
                                                  if video_length is not None else None,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res


class PornRox(PinFlix):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.pornrox.com/category',
            PornCategories.PORN_STAR_MAIN: 'https://www.pornrox.com/pornstars',
            PornCategories.CHANNEL_MAIN: 'https://www.pornrox.com/channel',
            PornCategories.RECOMMENDED_VIDEO: 'https://www.pornrox.com/?order=featured',
            PornCategories.LATEST_VIDEO: 'https://www.pornrox.com/?order=newest',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.pornrox.com/?order=most-popular',
            PornCategories.LONGEST_VIDEO: 'https://www.pornrox.com/?order=longest',
            PornCategories.TOP_RATED_VIDEO: 'https://www.pornrox.com/?order=top-rated',
            PornCategories.LIVE_VIDEO: 'https://www.pornrox.com/live-sex',
            PornCategories.SEARCH_MAIN: 'https://www.pornrox.com/search',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.RECOMMENDED_VIDEO: PornFilterTypes.RecommendedOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LIVE_VIDEO: PornFilterTypes.LiveOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pinflix.com/'

    def __init__(self, source_name='PornRox', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornRox, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.gotporn.com/categories/amateur')
    tag_id = IdGenerator.make_id('https://www.gotporn.com/tags/1080p')
    channel_id = IdGenerator.make_id('https://www.gotporn.com/channels/5049/Affect3dStore')
    # module = GotPorn()
    module = PornHD()
    # module = PinFlix()
    # module = PornRox()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['channels']['obj'], (channel_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user()
