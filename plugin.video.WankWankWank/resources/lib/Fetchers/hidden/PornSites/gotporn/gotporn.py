# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher, PornFetchUrlError

# Internet tools
from .... import urljoin, quote_plus

# Regex
import re

# Math
import math

# # Request Exception
# import json

try:
    from json import \
        JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter


class GotPorn(PornFetcher):
    max_search_results = 40
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
    def possible_empty_pages(self):
        """
        Defines whether it is possible to have empty pages in the site.
        :return:
        """
        return True

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

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
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
            total_number_of_videos = tree.xpath('.//div[@class="stats right"]/dl/dd')
            assert len(total_number_of_videos) == 2
            if total_number_of_videos[0].text.isdigit():
                total_number_of_videos = int(total_number_of_videos[0].text)
            else:
                total_number_of_videos = tree.xpath('.//button[@id="show-more-videos-btn"]')
                assert len(total_number_of_videos) == 1
                total_number_of_videos = int(total_number_of_videos[0].attrib['data-videos-num'])

            videos = tree.xpath('.//span[@class="video-thumb"]')
            return math.ceil(total_number_of_videos / len(videos))
        else:
            page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
            tree = self.parser.parse(page_request.text)
            available_pages = self._get_available_pages_from_tree(tree)
            if category_data.true_object.object_type == PornCategories.SEARCH_MAIN:
                return min(self.max_search_results, max(available_pages)) if len(available_pages) > 0 else 1
            else:
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
        videos = (tree.xpath('.//li[@class="video-item poptrigger"]') +
                  tree.xpath('.//li[@class="video-item  poptrigger "]'))
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
                                                  image_link=urljoin(self.base_url, img[0].attrib['src']),
                                                  is_hd='hd' in is_hd[0].attrib['class'],
                                                  duration=self._format_duration(video_length),
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def get_object_request(self, object_data, override_page_number=None, override_params=None, override_url=None,
                           force_fetch_channel_page=False):
        """
        Fetches the page number with respect to base url.
        :param object_data: Page data.
        :param override_page_number: Override page number.
        :param override_params: Override params.
        :param override_url: Override url.
        :param force_fetch_channel_page: Flag that indicates whether we fetch the whole channel page or its, json.
        :return: Page request
        """
        res = self._get_object_request_no_exception_check(object_data, override_page_number, override_params,
                                                          override_url, force_fetch_channel_page)
        if not self._check_is_available_page(object_data, res):
            error_module = self._prepare_porn_error_module(
                object_data, 0, res.url,
                'Could not fetch {url} in object {obj}'.format(url=res.url, obj=object_data.title))
            raise PornFetchUrlError(res, error_module)
        return res

    def _get_object_request_no_exception_check(self, page_data, override_page_number=None, override_params=None,
                                               override_url=None, force_fetch_channel_page=False, ):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :param override_page_number: Override page number.
        :param override_params: Override params.
        :param override_url: Override url.
        :param force_fetch_channel_page: Flag that indicates whether we fetch the whole channel page or its, json.
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
            return page_request
        else:
            return super(GotPorn, self)._get_object_request_no_exception_check(page_data, override_page_number,
                                                                               override_params, override_url)

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        # split_url = urlparse(fetch_base_url)
        split_url = fetch_base_url.split('/')
        last_empty_element = False
        if len(split_url[-1]) != 0:
            last_empty_element = True
            split_url.append('')

        # We update the cookies as well for orientation
        self.session.cookies.set(domain=self.host_name, name='orientation',
                                 value=self.general_filter.current_filters.general.value)
        if self.general_filter.current_filters.general.filter_id != PornFilterTypes.StraightType:
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
            if page_filter.length.value is not None:
                k, v = page_filter.length.value.split('=')
                params[k] = v
            if page_filter.quality.value is not None:
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
