# -*- coding: UTF-8 -*-
# Regex
import re

# Internet tools
from .. import urljoin, quote_plus
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter
# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ..fetchers.porn_fetcher import PornFetcher
# Generator id
from ..id_generator import IdGenerator
# JSON
from ..tools.text_json_manioulations import prepare_json_from_not_formatted_text


class KatesTube(PornFetcher):
    _pagination_class = 'holder'
    _video_page_videos_xpath = './/div[@class="thumbs-list"]/div/a'

    @property
    def max_pages(self):
        return 8000

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
                'search_args': single_tag_filters,
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

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        request_data = re.findall(r'(?:var flashvars = )({.*?})(?:;)', tmp_request.text, re.DOTALL)
        assert len(request_data) == 1
        request_data = prepare_json_from_not_formatted_text(request_data[0])
        assert len(request_data) > 0
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

    def _check_is_available_page(self, page_request):
        """
        In binary search performs test whether the current page is available.
        :param page_request: Page request.
        :return:
        """
        split_url = page_request.url.split('/')
        tree = self.parser.parse(page_request.text)
        true_page_number = tree.xpath('.//div[@class="{pg}"]/ul/li/span'.format(pg=self._pagination_class))
        true_page_number = int(true_page_number[0].text) if len(true_page_number) else 1
        if len(split_url) >= 4:
            fetch_page_number = int(split_url[len(split_url)-2]) if split_url[len(split_url)-2].isdigit() else 1
        else:
            fetch_page_number = 1
        if split_url[3] == 'search':
            videos = tree.xpath(self._video_page_videos_xpath)
            return len(videos) > 0
        else:
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


class PervClips(KatesTube):
    _pagination_class = 'pagination'
    _video_page_videos_xpath = './/div[@class="thumbs-holder"]/div/div/a'
    max_flip_images = 5

    @property
    def max_pages(self):
        return 8000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.pervclips.com/tube/categories/',
            # VideoCategories.CHANNEL_MAIN: 'https://www.pervclips.com/tube/channels/',
            PornCategories.TAG_MAIN: 'https://www.pervclips.com/tube/tags/',
            PornCategories.LATEST_VIDEO: 'https://www.pervclips.com/tube/latest-updates/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.pervclips.com/tube/top-rated/',
            PornCategories.POPULAR_VIDEO: 'https://www.pervclips.com/tube/most-popular/',
            PornCategories.LONGEST_VIDEO: 'https://www.pervclips.com/tube/longest/',
            PornCategories.MOST_DISCUSSED_VIDEO: 'https://www.pervclips.com/tube/commented/',
            PornCategories.SEARCH_MAIN: 'https://www.pervclips.com/tube/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pervclips.com/'

    def _prepare_filters(self):
        filters = super(PervClips, self)._prepare_filters()
        filters['single_category_args']['sort_order'].append((PornFilterTypes.CommentsOrder, 'Commented', 'commented'))
        filters['single_category_args']['sort_order'][0] = (PornFilterTypes.DateOrder, 'Recent', 'latest')
        filters['channels_args'] = None
        return filters

    def __init__(self, source_name='PervClips', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PervClips, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="items-list new_cat"]/div[@class="item"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            description = category.attrib['title']

            image_data = category.xpath('./div[@class="img-holder"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-original'] \
                if 'data-original' in image_data[0].attrib else image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="title-holder"]/div[@class="quantity-videos"]/'
                                              'span[@class="quantity"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(category_data.url, link),
                                               title=title,
                                               description=description,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="list-tags"]/div[@class="item"]/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.attrib['title'], int(x.xpath('./span')[0].text))
                                                for x in raw_objects])
        return links, titles, number_of_videos

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
            video_preview = video_tree_data.attrib['data-src']
            image = video_tree_data.attrib['data-poster']
            flip_images = [re.sub(r'\d+.jpg', '{p}.jpg'.format(p=p), image)
                           for p in range(1, self.max_flip_images + 1)]

            is_hd = video_tree_data.xpath('./div[@class="img-holder"]/div[@class="hd-holder"]')
            is_hd = len(is_hd) == 1

            video_length = video_tree_data.xpath('./div[@class="img-holder"]/div[@class="time-holder"]')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0].text)

            number_of_views = video_tree_data.xpath('./div[@class="title-item"]/div[@class="item-info"]/'
                                                    'span[@class="views-info"]/i')
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].tail)

            added_before = video_tree_data.xpath('./div[@class="title-item"]/div[@class="item-info"]/'
                                                 'meta[@itemprop="datePublished"]')
            assert len(added_before) == 1
            added_before = added_before[0].attrib['content']

            rating = video_tree_data.xpath('./div[@class="title-item"]/div[@class="item-info"]/'
                                           'span[@class="rating-info"]/span[@class="rating"]/i')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].tail)

            title = video_tree_data.xpath('./div[@class="title-item"]/p')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  is_hd=is_hd,
                                                  duration=self._format_duration(video_length),
                                                  number_of_views=number_of_views,
                                                  added_before=added_before,
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res


class PornWhite(KatesTube):
    _pagination_class = 'pager'
    _video_page_videos_xpath = './/div[@class="thumbs-list"]/div/a'
    max_flip_images = 5

    @property
    def max_pages(self):
        return 8000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.pornwhite.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://www.pornwhite.com/models/',
            # VideoCategories.CHANNEL_MAIN: 'https://www.pornwhite.com/channels/',
            PornCategories.TAG_MAIN: 'https://www.pornwhite.com/tags/',
            PornCategories.LATEST_VIDEO: 'https://www.pornwhite.com/latest-updates/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.pornwhite.com/top-rated/',
            PornCategories.POPULAR_VIDEO: 'https://www.pornwhite.com/most-popular/',
            PornCategories.SEARCH_MAIN: 'https://www.pornwhite.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornwhite.com/'

    def _prepare_filters(self):
        filters = super(PornWhite, self)._prepare_filters()
        filters['single_category_args']['sort_order'].append((PornFilterTypes.CommentsOrder, 'Commented', 'commented'))
        filters['channels_args'] = None
        filters['categories_args'] = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', None),
                            (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'total_videos'),
                            (PornFilterTypes.VideosRatingOrder, 'Video Rating', 'avg_videos_rating'),
                            (PornFilterTypes.VideosPopularityOrder, 'Video Popularity', 'avg_videos_popularity'),
                            ],
             }
        filters['porn_stars_args'] = \
            {'sort_order': [(PornFilterTypes.RatingOrder, 'Video Rating', 'rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.PopularityOrder, 'Popularity', 'model_viewed'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'total_videos'),
                            (PornFilterTypes.VideosRatingOrder, 'Video Rating', 'avg_videos_rating'),
                            (PornFilterTypes.VideosPopularityOrder, 'Video Popularity', 'avg_videos_popularity'),
                            ],
             }
        filters['single_porn_star_args'] = filters['single_category_args']

        return filters

    # def _set_video_filter(self):
    #     """
    #     Sets the video filters and the default values of the current filters
    #     :return:
    #     """
    #     ret super(PornWhite, self)._set_video_filter()

    def __init__(self, source_name='PornWhite', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornWhite, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

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

            image_data = category.xpath('./span[@class="img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-original'] \
                if 'data-original' in image_data[0].attrib else image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('.//span[@class="vids"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(object_data.url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
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
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.attrib['title'],
                                                 int(re.findall(r'\d+', x.xpath('./b')[0].tail)[0]))
                                                for x in raw_objects])
        return links, titles, number_of_videos

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
            flip_images = [re.sub(r'\d+.jpg', '{p}.jpg'.format(p=p), image)
                           for p in range(1, self.max_flip_images + 1)]

            is_hd = video_tree_data.xpath('./span[@class="img"]/span[@class="hd"]')
            is_hd = len(is_hd) == 1 and is_hd[0].text == 'HD'

            video_length = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="info-holder"]/'
                                                 'span[@class="length"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            number_of_views = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="info-holder"]/'
                                                    'span[@class="views"]')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            title = video_tree_data.xpath('./span[@class="thumb-info"]/b')
            assert len(title) == 1
            title = title[0].text

            rating = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="info-holder"]/'
                                           'span[@class="item-rating"]')
            assert len(rating) == 1
            rating = rating[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
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

        if true_object.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.PORN_STAR_MAIN):
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
            if page_filter.sort_order.value is not None:
                params['sort_by'] = [page_filter.sort_order.value]
            fetch_base_url = '/'.join(split_url)
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            return super(PornWhite, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                  page_filter, fetch_base_url)


class SleazyNEasy(PornWhite):
    _video_page_videos_xpath = './/div[@class="thumbs-list"]/div/a'

    @property
    def max_pages(self):
        return 8000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.sleazyneasy.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://www.sleazyneasy.com/models/',
            # VideoCategories.CHANNEL_MAIN: 'https://www.sleazyneasy.com/channels/',
            PornCategories.TAG_MAIN: 'https://www.sleazyneasy.com/tags/',
            PornCategories.LATEST_VIDEO: 'https://www.sleazyneasy.com/latest-updates/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.sleazyneasy.com/top-rated/',
            PornCategories.POPULAR_VIDEO: 'https://www.sleazyneasy.com/most-popular/',
            PornCategories.SEARCH_MAIN: 'https://www.sleazyneasy.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.sleazyneasy.com/'

    def __init__(self, source_name='SleazyNEasy', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SleazyNEasy, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                          session_id)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="wrap-th category"]/div/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            # title = category.attrib['title']

            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-original'] \
                if 'data-original' in image_data[0].attrib else image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./i[@class="mov"]/em')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].tail)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(porn_star_data.url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

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
            flip_images = [re.sub(r'\d+.jpg', '{p}.jpg'.format(p=p), image)
                           for p in range(1, self.max_flip_images + 1)]

            is_hd = video_tree_data.xpath('./span[@class="img"]/span[@itemprop="duration"]/span[@class="hd"]')
            is_hd = len(is_hd) == 1 and is_hd[0].text == 'HD'

            video_length = video_tree_data.xpath('./span[@class="img"]/span[@itemprop="duration"]/i')
            assert len(video_length) == 1
            video_length = video_length[0].text

            number_of_views = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="views"]')
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
                                                  flip_images_link=flip_images,
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


class VikiPorn(PornWhite):
    _pagination_class = 'paging-area'
    _video_page_videos_xpath = './/div[@class="thumbs-list"]/div/a'
    max_flip_images = 5

    @property
    def max_pages(self):
        return 8000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.vikiporn.com/categories/',
            PornCategories.TAG_MAIN: 'https://www.vikiporn.com/tags/',
            PornCategories.LATEST_VIDEO: 'https://www.vikiporn.com/latest-updates/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.vikiporn.com/top-rated/',
            PornCategories.POPULAR_VIDEO: 'https://www.vikiporn.com/most-popular/',
            PornCategories.SEARCH_MAIN: 'https://www.vikiporn.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.vikiporn.com/'

    def __init__(self, source_name='VikiPorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(VikiPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="categories-thumbs"]/div/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            # title = category.attrib['title']

            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-original'] \
                if 'data-original' in image_data[0].attrib else image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./i')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(category_data.url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="tags-list"]/div[@class="item"]/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.attrib['title'],
                                                 int(re.findall(r'\d', x.xpath('./span')[0].text)[0]))
                                                for x in raw_objects])
        return links, titles, number_of_videos

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
            flip_images = [re.sub(r'\d+.jpg', '{p}.jpg'.format(p=p), image)
                           for p in range(1, self.max_flip_images + 1)]

            is_hd = video_tree_data.xpath('./span[@class="img"]/span[@class="hd"]')
            is_hd = len(is_hd) == 1 and is_hd[0].text == 'HD'

            video_length = video_tree_data.xpath('./span[@class="img"]/span[@itemprop="duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            number_of_views = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="views"]/span')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            title = video_tree_data.xpath('./span[@class="thumb-info"]/b')
            assert len(title) == 1
            title = title[0].text

            rating = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="item-rating"]/span')
            assert len(rating) == 1
            rating = rating[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
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


class WankOz(PornWhite):
    max_flip_images = 5
    _video_page_videos_xpath = './/div[@class="thumbs-list"]/div/a'

    @property
    def max_pages(self):
        return 8000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.wankoz.com/categories/',
            PornCategories.TAG_MAIN: 'https://www.wankoz.com/tags/',
            PornCategories.LATEST_VIDEO: 'https://www.wankoz.com/latest-updates/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.wankoz.com/top-rated/',
            PornCategories.POPULAR_VIDEO: 'https://www.wankoz.com/most-popular/',
            PornCategories.SEARCH_MAIN: 'https://www.wankoz.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.wankoz.com/'

    def _prepare_filters(self):
        filters = super(WankOz, self)._prepare_filters()
        filters['single_category_args']['sort_order'][0] = (PornFilterTypes.DateOrder, 'Recent', 'latest')
        return filters

    def __init__(self, source_name='WankOz', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(WankOz, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

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
            flip_images = [re.sub(r'\d+.jpg', '{p}.jpg'.format(p=p), image)
                           for p in range(1, self.max_flip_images + 1)]

            is_hd = video_tree_data.xpath('./span[@class="img"]/span[@class="hd"]')
            is_hd = len(is_hd) == 1 and is_hd[0].text == 'HD'

            video_length = video_tree_data.xpath('./span[@class="img"]/span[@itemprop="duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            number_of_views = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="views"]')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            title = video_tree_data.xpath('./span[@class="thumb-info"]/b')
            assert len(title) == 1
            title = title[0].text

            rating = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="item-rating"]/i')
            assert len(rating) == 1
            rating = rating[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
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


class PorniCom(PornWhite):
    _pagination_class = 'pagination'
    _video_page_videos_xpath = './/div[@class="items-list"]/div/div'
    max_flip_images = 5

    @property
    def max_pages(self):
        return 8000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    def _prepare_filters(self):
        filters = super(PorniCom, self)._prepare_filters()
        filters['porn_stars_args'] = None
        filters['single_porn_star_args'] = None
        return filters

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornicom.com/'

    def __init__(self, source_name='PorniCom', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PorniCom, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="items-list"]/div/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            # title = category.attrib['title']

            image_data = category.xpath('./div[@class="img-holder"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-original'] \
                if 'data-original' in image_data[0].attrib else image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="title-holder"]/div[@class="quantity-videos"]/'
                                              'span[@class="quantity"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(category_data.url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="list-tags"]/div[@class="item"]/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], self._clear_text(x.text),
                                                 int(x.xpath('./span')[0].text[1:-1]))
                                                for x in raw_objects])
        return links, titles, number_of_videos

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
            image_data = video_tree_data.xpath('./div[@class="img-holder image"]')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-poster']
            video_preview = image_data[0].attrib['data-src'] if 'data-src' in image_data[0].attrib else None
            flip_images = [re.sub(r'\d+.jpg', '{p}.jpg'.format(p=p), image)
                           for p in range(1, self.max_flip_images + 1)]

            is_hd = image_data[0].xpath('./div[@class="hd-holder"]/span')
            is_hd = len(is_hd) == 1 and 'class' in is_hd[0].attrib and is_hd[0].attrib['class'] == 'hd'

            video_length = image_data[0].xpath('./div[@class="time-holder"]/span[@class="time"]/meta')
            assert len(video_length) == 1
            video_length = self._format_duration(video_length[0].attrib['content'])

            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            title = link_data[0].xpath('./p')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            added_before = link_data[0].xpath('./meta')
            assert len(added_before) == 1
            added_before = added_before[0].attrib['content']

            info_data = link_data[0].xpath('./div[@class="item-info"]')
            assert len(info_data) == 1

            rating = info_data[0].xpath('./span[@class="rating-info"]/span[@class="rating"]/i')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].tail)

            number_of_views = info_data[0].xpath('./span[@class="views-info"]/i')
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].tail)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  is_hd=is_hd,
                                                  added_before=added_before,
                                                  duration=video_length,
                                                  number_of_views=number_of_views,
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res


class FetishShrine(PornWhite):
    _pagination_class = 'paging-area'
    _video_page_videos_xpath = './/div[@class="thumbs-list"]/div/a'
    max_flip_images = 5

    @property
    def max_pages(self):
        return 8000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    def _prepare_filters(self):
        filters = super(FetishShrine, self)._prepare_filters()
        filters['categories_args']['sort_order'][0] = (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title')
        filters['porn_stars_args'] = None
        filters['single_porn_star_args'] = None
        filters['single_category_args']['sort_order'][0] = (PornFilterTypes.DateOrder, 'Recent', 'latest')
        return filters

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.fetishshrine.com/'

    def __init__(self, source_name='FetishShrine', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(FetishShrine, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                           session_id)

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
            flip_images = [re.sub(r'\d+.jpg', '{p}.jpg'.format(p=p), image)
                           for p in range(1, self.max_flip_images + 1)]

            video_length = video_tree_data.xpath('./span[@class="img"]/span[@itemprop="duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            number_of_views = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="views"]')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            title = video_tree_data.xpath('./span[@class="thumb-info"]/b')
            assert len(title) == 1
            title = title[0].text

            rating = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="item-rating"]/span')
            assert len(rating) == 1
            rating = rating[0].text

            added_before = video_tree_data.xpath('./span[@class="thumb-info"]/meta[@itemprop="datePublished"]')
            assert len(added_before) == 1
            added_before = added_before[0].attrib['content']

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  duration=self._format_duration(video_length),
                                                  number_of_views=number_of_views,
                                                  rating=rating,
                                                  added_before=added_before,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res


class SheShaft(PornWhite):
    # todo: to change the general object type to shemale...
    _pagination_class = 'pagination'
    _video_page_videos_xpath = './/div[@class="thumbs-list"]/div/a'
    max_flip_images = 5

    @property
    def max_pages(self):
        return 8000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    def _prepare_filters(self):
        filters = super(SheShaft, self)._prepare_filters()
        filters['porn_stars_args'] = None
        filters['single_porn_star_args'] = None
        return filters

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.sheshaft.com/'

    def __init__(self, source_name='SheShaft', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SheShaft, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

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
            flip_images = [re.sub(r'\d+.jpg', '{p}.jpg'.format(p=p), image)
                           for p in range(1, self.max_flip_images + 1)]
            is_hd = image_data[0].xpath('./span[@class="hd"]')
            is_hd = len(is_hd) == 1 and is_hd[0].text == 'hd'

            video_length = video_tree_data.xpath('./span[@class="img"]/span[@itemprop="duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            number_of_views = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="views"]')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            title = video_tree_data.xpath('./span[@class="thumb-info"]/b')
            assert len(title) == 1
            title = title[0].text

            rating = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="rating-holder"]/'
                                           'span[@class="item-rating"]')
            assert len(rating) == 1
            rating = rating[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  is_hd=is_hd,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  duration=self._format_duration(video_length),
                                                  number_of_views=number_of_views,
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    # module = KatesTube()
    # module = PervClips()
    # module = PornWhite()
    # module = SleazyNEasy()
    # module = VikiPorn()
    module = WankOz()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
