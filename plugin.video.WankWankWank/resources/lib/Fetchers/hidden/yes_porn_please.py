# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher
from ..tools.external_fetchers import ExternalFetcher

# Internet tools
from .. import urlparse, urljoin, quote_plus, parse_qsl

# Regex
import re

# Warnings and exceptions
import warnings

# Generator id
from ..id_generator import IdGenerator

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter


class YesPornPlease(PornFetcher):
    max_flip_images = 100

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/'),  # Dummy suffix 'channels'
            PornCategories.HOTTEST_VIDEO: urljoin(self.base_url, '/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/?s=date'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/?s=views&m=3days'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/?s=votes'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.HOTTEST_VIDEO: PornFilterTypes.HottestOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://yespornplease.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': [(PornFilterTypes.HottestOrder, 'Hot Videos', None),
                                        (PornFilterTypes.DateOrder, 'New Videos', 's=date'),
                                        (PornFilterTypes.ViewsOrder, 'Views', 's=views'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 's=votes'),
                                        ],
                         'period_filters': ([(PornFilterTypes.ThreeDate, 'Last 3 Days', 'm=3days'),
                                             (PornFilterTypes.AllDate, 'All time', 'm=all'),
                                             (PornFilterTypes.OneDate, 'This Month', 'm=month'),
                                             (PornFilterTypes.TwoDate, 'This Week', 'm=week'),
                                             (PornFilterTypes.FourDate, 'Yesterday', 'm=yesterday'),
                                             ],
                                            [('sort_order', [PornFilterTypes.ViewsOrder])]),
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='YesPornPlease', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(YesPornPlease, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                            session_id)
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/76.0.3809.100 Safari/537.36'
        self.external_fetchers = ExternalFetcher(session=self.session, user_agent=self.user_agent,
                                                 parser=self.parser)
        self.scroll_json = urljoin(self.base_url, '/ajax/scroll_load')

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="col-sm-4 col-md-3 col-lg-3 m-b-20"]')
        res = []
        for category in categories:
            link = category.xpath('./a')
            assert len(link) == 1

            image = category.xpath('./a/div[@class="thumb-overlay"]/img/@src')
            assert len(image) == 1

            title = category.xpath('./a/div[@class="thumb-overlay"]/div[@class="category-title m-t-5"]/'
                                   'div[@class="pull-left title-truncate"]/text()')
            assert len(title) == 1

            number_of_videos = category.xpath('./a/div[@class="thumb-overlay"]/div[@class="category-title m-t-5"]/'
                                              'div[@class="pull-right"]/span[@class="badge"]/text()')
            assert len(number_of_videos) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  image_link=image[0],
                                                  title=title[0],
                                                  number_of_videos=int(number_of_videos[0]),
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)

        category_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        channels = tree.xpath('.//div[@id="pop-tags"]/a')

        new_pages = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                             obj_id=x.attrib['href'],
                                             title=x.text,
                                             url=urljoin(self.base_url, x.attrib['href']),
                                             object_type=PornCategories.CHANNEL,
                                             super_object=channel_data,
                                             )
                     for x in channels]
        channel_data.add_sub_objects(new_pages)
        return new_pages

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        new_video_url = tmp_tree.xpath('.//iframe/@src')
        assert len(new_video_url) == 1
        hostname = urlparse(new_video_url[0]).hostname
        if hostname == 'vshare.io':
            video_links = [VideoSource(link=x[0], resolution=x[1])
                           for x in self.external_fetchers.get_video_link_from_vshare(urljoin(video_data.url,
                                                                                              new_video_url[0]),
                                                                                      video_data.url)]
        elif hostname == 'fileone.tv':
            video_links = [VideoSource(link=x[0], resolution=x[1])
                           for x in self.external_fetchers.get_video_link_from_fileone(urljoin(video_data.url,
                                                                                               new_video_url[0]),
                                                                                       video_data.url)]
        else:
            warnings.warn('Unknown source {h}...'.format(h=hostname))
            video_links = []

        video_links.sort(key=lambda x: x.resolution, reverse=True)
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'identity;q=1, *;q=0',
            'Range': 'bytes=0-',
            'Referer': new_video_url[0],
            'Sec-Fetch-Mode': 'no-cors',
            # 'Sec-Fetch-Site': 'same-origin',
            # 'Sec-Fetch-User': '?1',
            # 'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        return VideoNode(video_sources=video_links, headers=headers)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.CHANNEL_MAIN):
            return 1
        else:
            page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
            tree = self.parser.parse(page_request.text)
            pages = self._get_available_pages_from_tree(tree)
            return max(pages) if len(pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//ul[@class="pagination"]/li/*/text()') if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = (tree.xpath('.//div[@class="col-sm-6 col-md-4 col-lg-4"]/div[@class="well well-sm"]') +
                  tree.xpath('.//div[@class="col-sm-4 col-md-4 col-lg-3"]/div[@class="well well-sm"]'))
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1

            thumb_tree = [x for x in video_tree_data.xpath('./a/div')
                          if 'class' in x.attrib and 'thumb-overlay' in x.attrib['class']]
            assert len(thumb_tree) == 1
            image_data = thumb_tree[0].xpath('./img/@src')
            assert len(image_data) == 1
            image = image_data[0]
            flip_images = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image) for i in range(1, self.max_flip_images)]
            video_preview = re.sub(r'/.*\.jpg', '/video.mp4', image)

            is_hd = thumb_tree[0].xpath('./div[@class="hd-text-icon"]')
            is_hd = len(is_hd) > 0 and is_hd[0].text == 'HD'

            video_length = thumb_tree[0].xpath('./div[@class="duration"]')
            assert len(video_length) == 1

            title = video_tree_data.xpath('./a/span[@class="video-title title-truncate m-t-5"]')
            assert len(title) == 1

            viewers = video_tree_data.xpath('./div[@class="video-views pull-left"]')
            assert len(viewers) == 1

            added_before = video_tree_data.xpath('./div[@class="video-rating pull-right no-rating"]')
            assert len(added_before) == 1
            added_before = re.sub(r'^[ \r\n]*|[ \r\n]*$', '', added_before[0].text)

            res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                obj_id=video_tree_data.xpath('./a'),
                                                url=urljoin(self.base_url, link[0].attrib['href']),
                                                title=title[0].text,
                                                image_link=image[0],
                                                flip_images_link=flip_images,
                                                preview_video_link=video_preview,
                                                is_hd=is_hd,
                                                duration=self._format_duration(video_length[0].text),
                                                number_of_views=viewers[0].text,
                                                added_before=added_before,
                                                object_type=PornCategories.VIDEO,
                                                super_object=page_data,
                                                ))
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            # 'Referer': self.category_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        conditions = self.get_proper_filter(page_data).conditions
        if page_number is not None and page_number != 1:
            params['p'] = page_data.page_number

        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            params.update(parse_qsl(page_filter.sort_order.value))
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id
        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            params.update(parse_qsl(page_filter.period.value))

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


class SayPornPlease(YesPornPlease):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories'),
            # PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/tags'),
            PornCategories.BEING_WATCHED_VIDEO: urljoin(self.base_url, '/videos?o=bw'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/videos?o=mr'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/videos?o=mv'),
            PornCategories.MOST_DISCUSSED_VIDEO: urljoin(self.base_url, '/videos?o=md'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/videos?o=tr'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/videos?o=lg'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.BEING_WATCHED_VIDEO: PornFilterTypes.BeingWatchedOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.saypornplease.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': [(PornFilterTypes.BeingWatchedOrder, 'Hot Videos', 'o=bw'),
                                        (PornFilterTypes.DateOrder, 'Most Recent', 'o=mr'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'o=mv'),
                                        (PornFilterTypes.CommentsOrder, 'Most Commented', 'o=md'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'o=tr'),
                                        (PornFilterTypes.FavorOrder, 'Most Favorite', 'o=tf'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'o=lg'),
                                        ],
                         'period_filters': ([(PornFilterTypes.ThreeDate, 'Last 3 Days', 'q=3days'),
                                             (PornFilterTypes.AllDate, 'All time', 'q=all'),
                                             (PornFilterTypes.OneDate, 'This Month', 'month'),
                                             (PornFilterTypes.TwoDate, 'This Week', 'week'),
                                             (PornFilterTypes.FourDate, 'Yesterday', 'yesterday'),
                                             ],
                                            [('sort_order', [PornFilterTypes.ViewsOrder])]),
                         'added_before_filters': [(PornFilterTypes.AllAddedBefore, 'Anytime', 't=a'),
                                                  (PornFilterTypes.OneAddedBefore, 'Today', 't=t'),
                                                  (PornFilterTypes.TwoAddedBefore, 'Last Week', 't=w'),
                                                  (PornFilterTypes.ThreeAddedBefore, 'Last Month', 't=m'),
                                                  ],
                         'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', 'q=all'),
                                             (PornFilterTypes.HDQuality, 'HD quality', 'q=hd'),
                                             )
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='SayPornPlease', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SayPornPlease, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                            session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class=" col-sm-6 col-md-4 col-lg-4 col-xl-4 m-b-20"]')
        res = []
        for category in categories:
            link = category.xpath('./a')
            assert len(link) == 1
            link = link[0].attrib['href']

            image = category.xpath('./a/div[@class="thumb-overlay"]/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            title = category.xpath('./a/div[@class="thumb-overlay"]/div[@class="category-title"]/'
                                   'div[@class="float-left title-truncate"]')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            number_of_videos = category.xpath('./a/div[@class="thumb-overlay"]/div[@class="category-title"]/'
                                              'div[@class="float-right"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(self._clear_text(number_of_videos[0].text))

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  image_link=image,
                                                  title=title,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)

        category_data.add_sub_objects(res)
        return res

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = (tree.xpath('.//div[@class=" col-sm-6 col-md-4 col-lg-4 "]') +
                  tree.xpath('.//div[@class=" col-sm-6 col-md-4 col-lg-3 "]'))
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1

            thumb_tree = [x for x in video_tree_data.xpath('./a/div')
                          if 'class' in x.attrib and 'thumb-overlay' in x.attrib['class']]
            assert len(thumb_tree) == 1
            image_data = thumb_tree[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['title'] if 'title' in image_data[0].attrib else None

            if title is None:
                title = video_tree_data.xpath('./div[@class="content-info"]/a/span[@class="content-title"]')
                assert len(title) == 1
                title = title[0].text

            viewers = video_tree_data.xpath('./div[@class="content-info"]/div[@class="content-details"]/'
                                            'span[@class="content-views"]')
            assert len(viewers) == 1
            viewers = self._clear_text(viewers[0].text)

            rating = video_tree_data.xpath('./div[@class="content-info"]/div[@class="content-details"]/'
                                           'span[@class="content-rating"]/span')
            rating = self._clear_text(rating[0].text) if len(rating) == 1 else None

            res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                obj_id=video_tree_data.xpath('./a'),
                                                url=urljoin(self.base_url, link[0].attrib['href']),
                                                title=title,
                                                image_link=image[0],
                                                number_of_views=viewers,
                                                rating=rating,
                                                object_type=PornCategories.VIDEO,
                                                super_object=page_data,
                                                ))
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            # 'Referer': self.category_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        conditions = self.get_proper_filter(page_data).conditions
        if page_number is not None and page_number != 1:
            params['page'] = page_data.page_number

        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            params.update(parse_qsl(page_filter.sort_order.value))
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id
        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            params.update(parse_qsl(page_filter.period.value))
        if page_filter.added_before.value is not None:
            params.update(parse_qsl(page_filter.added_before.value))
        if page_filter.quality.value is not None:
            params.update(parse_qsl(page_filter.quality.value))
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return (self.object_urls[PornCategories.SEARCH_MAIN] +
                '/videos/{q}'.format(q=quote_plus(query.replace(' ', '-'))))


if __name__ == '__main__':
    cat_id = IdGenerator.make_id('/search?q=3some')
    module = YesPornPlease()
    # module.get_available_categories()
    # module.download_object(None, cat_id, verbose=1)
    module.download_category_input_from_user(use_web_server=False)
