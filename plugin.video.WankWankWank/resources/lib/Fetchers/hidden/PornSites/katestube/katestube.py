# -*- coding: UTF-8 -*-
# Regex
import re

# Internet tools
from .... import urljoin, quote_plus
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter
# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ....fetchers.porn_fetcher import PornFetcher
# JSON
from ....tools.text_json_manioulations import prepare_json_from_not_formatted_text


class KatesTube(PornFetcher):
    _pagination_class = 'holder'
    _video_page_videos_xpath = './/div[@class="thumbs-list"]/div/a'
    _first_not_mandatory_category_field_index = 5
    _first_not_mandatory_general_video_field_index = 4

    @property
    def max_pages(self):
        return 8000

    @property
    def possible_empty_pages(self):
        """
        Defines whether it is possible to have empty pages in the site.
        :return:
        """
        return True

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.katestube.com/categories/',
            PornCategories.CHANNEL_MAIN: 'https://www.katestube.com/channels/',
            PornCategories.TAG_MAIN: 'https://www.katestube.com/tags/',
            PornCategories.LATEST_VIDEO: 'https://www.katestube.com/latest-updates/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.katestube.com/top-rated/',
            PornCategories.POPULAR_VIDEO: 'https://www.katestube.com/most-popular/',
            PornCategories.LONGEST_VIDEO: 'https://www.katestube.com/tube/longest/',
            PornCategories.SEARCH_MAIN: 'https://www.katestube.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.katestube.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        self._video_filters = PornFilter(**self._prepare_filters())

    def _prepare_filters(self):
        categories_filters = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'alphabetical'),
                                             (PornFilterTypes.RatingOrder, 'Video Rating', 'rating'),
                                             (PornFilterTypes.PopularityOrder, 'Video Popularity', 'popular'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'videos'),
                                             ],
                              }
        single_category_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Recent', 'latest-updates'),
                                                  (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                                  (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                                  (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                                  ],
                                   # 'period_filters': ([(PornFilterTypes.AllDate, 'All time', None),
                                   #                     (PornFilterTypes.OneDate, 'Month', 'month'),
                                   #                     (PornFilterTypes.TwoDate, 'Week', 'week'),
                                   #                     (PornFilterTypes.ThreeDate, 'Today', 'today'),
                                   #                     ],
                                   #                    [('sort_order', [PornFilterTypes.RatingOrder])]),
                                   'quality_filters': [(PornFilterTypes.AllQuality, 'All', None),
                                                       (PornFilterTypes.HDQuality, 'HD', '1'),
                                                       ],
                                   }
        video_filters = {'period_filters': ([(PornFilterTypes.AllDate, 'All time', None),
                                             (PornFilterTypes.OneDate, 'Month', 'month'),
                                             (PornFilterTypes.TwoDate, 'Week', 'week'),
                                             (PornFilterTypes.ThreeDate, 'Today', 'today'),
                                             ],
                                            [('sort_order', [PornFilterTypes.RatingOrder,
                                                             PornFilterTypes.PopularityOrder])]),
                         'quality_filters': [(PornFilterTypes.AllQuality, 'All', None),
                                             (PornFilterTypes.HDQuality, 'HD', '1'),
                                             ],
                         }
        single_tag_filters = {'sort_order': single_category_filters['sort_order'],
                              'quality_filters': single_category_filters['quality_filters'],
                              }
        search_filters = {'sort_order': single_category_filters['sort_order'],
                          'quality_filters': single_category_filters['quality_filters'],
                          }
        return {'data_dir': self.fetcher_data_dir,
                'general_args': None,
                'categories_args': categories_filters,
                'tags_args': None,
                'porn_stars_args': None,
                'channels_args': None,
                'single_category_args': single_category_filters,
                'single_tag_args': single_tag_filters,
                'single_porn_star_args': None,
                'single_channel_args': None,
                'video_args': video_filters,
                'search_args': search_filters,
                }

    def __init__(self, source_name='KatesTube', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(KatesTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, './/div[@class="thumbs-list"]/div[@class="thumb"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(channel_data, './/div[@class="thumbs-list"]/div[@class="thumb"]/a',
                                                  PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data, './/div[@class="thumbs-list"]/div[@class="thumb"]/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_base_object(self, object_data, xpath, object_type):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link = category.attrib['href']
            description = category.attrib['title']

            image_data = category.xpath('./span[@class="img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-original'] \
                if 'data-original' in image_data[0].attrib else image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            added_today = category.xpath('./span[@class="img"]/span[@class="added"]')
            additional_data = {'added_today': added_today[0].text} if len(added_today) > 0 else None

            number_of_videos = category.xpath('./span[@class="thumb-info"]/span[@class="vids"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(object_data.url, link),
                                               title=title,
                                               description=description,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               additional_data=additional_data,
                                               object_type=object_type,
                                               super_object=object_data,
                                               ))

        object_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="tags-list"]/div[@class="item"]/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, int(x.xpath('./span')[0].text))
                                                for x in raw_objects])
        return links, titles, number_of_videos

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        request_data = re.findall(r'(?:var flashvars = )({.*?})(?:;)', tmp_request.text, re.DOTALL)
        request_data = prepare_json_from_not_formatted_text(request_data[0])
        res = [VideoSource(link=request_data['video_url'])]
        return VideoNode(video_sources=res)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN,
                                         PornCategories.CHANNEL_MAIN,):
            return 1

        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        if category_data.page_number is not None:
            max_page = max(pages)
            if max_page - category_data.page_number < self._binary_search_page_threshold:
                return max_page

        # We perform binary search
        return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//div[@class="{pg}"]/ul/li/*'.format(pg=self._pagination_class))
                if x.text is not None and x.text.isdigit()]

    def _check_is_available_page(self, page_object, page_request=None):
        """
        In binary search performs test whether the current page is available.
        :param page_object: Page object.
        :param page_request: Page request.
        :return:
        """
        if page_request is None:
            page_request = self.get_object_request(page_object)

        split_url = page_request.url.split('/')
        tree = self.parser.parse(page_request.text)
        if page_object.true_object.object_type == PornCategories.SEARCH_MAIN:
            videos = tree.xpath(self._video_page_videos_xpath)
            return len(videos) > 0

        true_page_number = tree.xpath('.//div[@class="{pg}"]/ul/li/span'.format(pg=self._pagination_class))
        true_page_number = int(true_page_number[0].text) if len(true_page_number) else 1
        if page_object.true_object.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.PORN_STAR_MAIN,
                                                   PornCategories.CHANNEL_MAIN, PornCategories.CATEGORY,
                                                   PornCategories.PORN_STAR, PornCategories.CHANNEL):
            first_not_mandatory_field = self._first_not_mandatory_category_field_index
        else:
            first_not_mandatory_field = self._first_not_mandatory_general_video_field_index
        if len(split_url) > first_not_mandatory_field:
            not_mandatory_fields = split_url[first_not_mandatory_field:]
            fetch_page_number = int(not_mandatory_fields[-2]) \
                if len(not_mandatory_fields) >= 2 and not_mandatory_fields[-2].isdigit() else 1
        else:
            fetch_page_number = 1
        return true_page_number == fetch_page_number

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 2

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath(self._video_page_videos_xpath)
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./span[@class="img"]')
            assert len(image_data) == 1
            video_preview = image_data[0].attrib['data-src']
            image = image_data[0].attrib['data-poster']

            is_hd = video_tree_data.xpath('./span[@class="img"]/span[@class="hd"]')
            is_hd = len(is_hd) == 1 and is_hd[0].text == 'HD'

            video_length = video_tree_data.xpath('./span[@class="img"]/span[@class="info"]/span[@class="length"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            number_of_views = video_tree_data.xpath('./span[@class="img"]/span[@class="info"]/span[@class="views"]')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            title = video_tree_data.xpath('./span[@class="thumb-info"]/b')
            assert len(title) == 1
            title = title[0].text

            rating = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="item-rating"]')
            assert len(rating) == 1
            rating = rating[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  preview_video_link=video_preview,
                                                  is_hd=is_hd,
                                                  duration=self._format_duration(video_length),
                                                  number_of_views=number_of_views,
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Referer': page_data.url,
            # 'Host': urlparse(object_data.url).hostname,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        # sortable videos
        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            split_url.insert(-1, page_filter.sort_order.value)
        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            split_url.insert(-1, page_filter.period.value)
        if page_filter.quality.value is not None:
            params['is_hd'] = [page_filter.quality.value]

        if page_number is not None and page_number != 1:
            split_url.insert(-1, str(page_number))

        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(KatesTube, self)._version_stack + [self.__version]
