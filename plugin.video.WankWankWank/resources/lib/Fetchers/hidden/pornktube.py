# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError
from ..tools.external_fetchers import ExternalFetcher

# Internet tools
from .. import urljoin, quote_plus, parse_qs

# Regex
import re

# Playlist tools
import m3u8

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode, VideoTypes
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# Generator id
from ..id_generator import IdGenerator


class PornKTube(PornFetcher):
    # Many similarities with rushporn module
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornktube.porn/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters, single_category_filters, _, _, _, _ = self._prepare_filters()
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=single_category_filters,
                                         video_args=video_filters,
                                         )

    @staticmethod
    def _prepare_filters():
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Recent', 'latest-updates'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                        (PornFilterTypes.PopularityOrder, 'Most Popular', 'most-popular'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        ),
                         'period_filters': ([(PornFilterTypes.AllDate, 'All time', None),
                                             (PornFilterTypes.TwoDate, 'Week', 'week'),
                                             (PornFilterTypes.OneDate, 'Month', 'month'),
                                             (PornFilterTypes.ThreeDate, 'Today', 'today'),
                                             ],
                                            [('sort_order', [PornFilterTypes.RatingOrder,
                                                             PornFilterTypes.PopularityOrder])]),
                         }
        single_category_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Recent', None),
                                                  (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                                  (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                                  (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                                  ),
                                   }
        single_porn_star_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Recent', None),
                                                   (PornFilterTypes.RatingOrder, 'Top Rated', 'voted'),
                                                   (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                                                   (PornFilterTypes.LengthOrder, 'Longest', 'long'),
                                                   ),
                                    }
        categories_filters = {'sort_order': ((PornFilterTypes.AlphabeticOrder, 'Alphabetically', None),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Videos', 'sort_by=total_videos'),
                                             (PornFilterTypes.VideosRatingOrder, 'Videos Rating',
                                              'sort_by=avg_videos_rating'),
                                             (PornFilterTypes.VideosPopularityOrder, 'Videos Popularity',
                                              'sort_by=avg_videos_popularity'),
                                             ),
                              }
        porn_stars_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Recent', None),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'count'),
                                             (PornFilterTypes.RatingOrder, 'Rated', 'rated'),
                                             (PornFilterTypes.ViewsOrder, 'Views', 'views'),
                                             ),
                              }
        channels_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Popular', None),
                                           (PornFilterTypes.RatingOrder, 'Rated', 'rated'),
                                           (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                                           (PornFilterTypes.DateOrder, 'New', 'recent'),
                                           ),
                            }
        return (video_filters, single_category_filters, single_porn_star_filters, categories_filters,
                porn_stars_filters, channels_filters)

    def __init__(self, source_name='PornKTube', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornKTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)
        # self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
        #                   'Chrome/76.0.3809.100 Safari/537.36'
        self.external_fetchers = ExternalFetcher(session=self.session, user_agent=self.user_agent,
                                                 parser=self.parser)

    def _update_available_base_category(self, base_data, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="cat"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            description = link_data[0].attrib['title'] if 'title' in link_data[0].attrib else None

            image_data = category.xpath('./a/img')
            assert len(image_data) == 1
            image = urljoin(base_data.url, image_data[0].attrib['src'])

            text_data = category.xpath('./h2/a')
            assert len(text_data) == 1
            title = re.findall(r'(\w+)(?: \(\d+\))', text_data[0].text)
            title = title[0] if len(title) > 0 else text_data[0].text
            number_of_videos = re.findall(r'(?:\w+ \()(\d+)(?:\))', text_data[0].text)
            number_of_videos = int(number_of_videos[0]) if len(number_of_videos) else None

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(base_data.url, link),
                                                  image_link=image,
                                                  title=title,
                                                  description=description,
                                                  number_of_videos=number_of_videos,
                                                  object_type=object_type,
                                                  super_object=base_data,
                                                  )
            res.append(object_data)
        base_data.add_sub_objects(res)
        return res

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_category(category_data, PornCategories.CATEGORY)

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """

        video_raw_data = self.external_fetchers.get_video_link_from_fapmedia(video_data.url)
        video_links = sorted((VideoSource(link=x[0], resolution=x[1]) for x in video_raw_data),
                             key=lambda x: x.resolution, reverse=True)
        headers = {
            'Accept-Encoding': 'identity;q=1, *;q=0',
            'Range': 'bytes=0-',
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
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1
        try:
            page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        except PornFetchUrlError:
            return 1
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//div[@class="pagination"]/div[@class="block_content"]/*/text()')
                if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="pornkvideos"]/div[@class="wrap"]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./div[@class="vid_info"]/a')
            assert len(link) == 1

            image_data = video_tree_data.xpath('./div[@class="vid_info"]/a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'onmouseover' in image_data[0].attrib:
                _, flip_url, flip_range = re.findall(r'(?:\()(.*)(?:\))',
                                                     image_data[0].attrib['onmouseover'])[0].split(', ')
                flip_image = ['{u}{i}.jpg'.format(u=flip_url, i=i) for i in range(int(flip_range)+1)]
            else:
                flip_image = None

            video_length = video_tree_data.xpath('./div[@class="vid_info"]/div[@class="vlength"]')
            assert len(video_length) == 1

            pos_rating = video_tree_data.xpath('./div[@class="vid_info"]/div[@class="likes"]')
            assert len(pos_rating) == 1
            neg_rating = video_tree_data.xpath('./div[@class="vid_info"]/div[@class="dislikes"]')
            assert len(neg_rating) == 1
            try:
                rating = \
                    str(int(int(pos_rating[0].text)/(int(pos_rating[0].text) + int(neg_rating[0].text))*100)) + '%'
            except ZeroDivisionError:
                rating = 0

            title = video_tree_data.xpath('./h2/a')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=re.findall(r'\d+', link[0].attrib['href'])[0],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_image,
                                                  duration=self._format_duration(video_length[0].text),
                                                  rating=rating,
                                                  pos_rating=pos_rating,
                                                  neg_rating=neg_rating,
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
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        conditions = self.get_proper_filter(page_data).conditions
        fetch_base_url = self._prepare_request(page_number, true_object, page_filter, fetch_base_url, True, conditions)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        if not page_request.ok:
            # Sometimes we try another fetch
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_request(self, page_number, true_object, page_filter, fetch_base_url, use_last_slash, conditions):
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id
        split_url = fetch_base_url.split('/')
        if len(split_url[-1]) == 0:
            # We remove the last slash
            split_url.pop()
        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            split_url.append(page_filter.sort_order.value)
        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            split_url.append(page_filter.period.value)
        if page_number is not None and page_number != 1:
            split_url.append(str(page_number))

        if use_last_slash is True:
            split_url.append('')

        fetch_base_url = '/'.join(split_url)
        return fetch_base_url

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


class PornKy(PornKTube):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornky.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters, single_category_filters, _, categories_filters, _, _ = self._prepare_filters()
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=categories_filters,
                                         single_category_args=single_category_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='PornKy', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornKy, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)

        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="block_content"]/div[@class="item"]')
        res = []
        for category in categories:
            link = category.xpath('./div[@class="image"]/a')
            assert len(link) == 1

            image = category.xpath('./div[@class="image"]/a/img')
            assert len(image) == 1

            title = category.xpath('./h2/a')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            number_of_videos = category.xpath('./h2/a/span[@class="info"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=title,
                                                  image_link=image[0].attrib['src'],
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        video_raw_data = self.external_fetchers.get_video_link_from_fapmedia(video_data.url)
        video_links = sorted((VideoSource(link=x[0], resolution=x[1]) for x in video_raw_data),
                             key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=video_links)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//div[@class="pages"]/*/text()') if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="video_content"]/div[@class="video"]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./div[@class="image "]/a')
            assert len(link) == 1

            image_data = video_tree_data.xpath('./div[@class="image "]/a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            number_of_flip_images = int(re.findall(r'(\d+)(?:\))', image_data[0].attrib['onmouseover'])[0])
            flip_image = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                          for i in range(1, number_of_flip_images+1)]

            video_length = video_tree_data.xpath('./div[@class="image "]/div[@class="duration"]')
            assert len(video_length) == 1

            rating = video_tree_data.xpath('./div[@class="image "]/div[@class="thumbsup"]')
            assert len(rating) == 1

            title = video_tree_data.xpath('./div[@class="info"]/h2/a')
            assert len(title) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=title[0].attrib['title'],
                                                  image_link=image,
                                                  flip_images_link=flip_image,
                                                  duration=self._format_duration(video_length[0].text),
                                                  rating=rating[0].text,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        if true_object.object_type not in (PornCategories.CATEGORY_MAIN, ):
            return super(PornKy, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                               page_filter, fetch_base_url)

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_filter.sort_order.value is not None:
            params.update(parse_qs(page_filter.sort_order.value))
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        if not page_request.ok:
            # Sometimes we try another fetch
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request


class RushPorn(PornKTube):
    # Many similarities with ponktube module
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/pornstars'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/recent-videos'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-viewed'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/longest'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.rushporn.xxx/'

    @staticmethod
    def _prepare_filters():
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Newest', 'recent-videos'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        ),
                         'period_filters': ([(PornFilterTypes.AllDate, 'All time', None),
                                             (PornFilterTypes.TwoDate, 'Week', 'week'),
                                             (PornFilterTypes.OneDate, 'Month', 'month'),
                                             (PornFilterTypes.ThreeDate, 'Today', 'today'),
                                             ],
                                            [('sort_order', [PornFilterTypes.ViewsOrder])]),
                         }
        single_category_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Recent', None),
                                                  (PornFilterTypes.RatingOrder, 'Top Rated', 'rated'),
                                                  (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                                                  (PornFilterTypes.LengthOrder, 'Longest', 'long'),
                                                  ),
                                   }

        (_, _, single_porn_star_filters, categories_filters,
         porn_stars_filters, channels_filters) = PornKTube._prepare_filters()

        return (video_filters, single_category_filters, single_porn_star_filters, categories_filters,
                porn_stars_filters, channels_filters)

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters, single_category_filters, single_porn_star_filters, _, porn_stars_filters, channels_filters = \
            self._prepare_filters()
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_category_args=single_category_filters,
                                         single_porn_star_args=single_porn_star_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='RushPorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(RushPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_category(channel_data, PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="pornstar"]/div[@class="wrap"]/div[@class="pornstars"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            description = link_data[0].attrib['title'] if 'title' in link_data[0].attrib else None

            image_data = category.xpath('./a/img')
            assert len(image_data) == 1
            image = urljoin(porn_star_data.url, image_data[0].attrib['src'])
            title = image_data[0].attrib['alt']

            additional_data = {}
            likes = category.xpath('./div[@class="likes"]/text()')
            additional_data['likes'] = int(likes[0]) if len(likes) > 0 else None
            dislikes = category.xpath('./div[@class="dislikes"]/text()')
            additional_data['dislikes'] = int(dislikes[0]) if len(dislikes) > 0 else None
            rating = category.xpath('./div[@class="vsaw"]/text()')
            additional_data['rating'] = int(rating[0]) if len(rating) > 0 else None

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(porn_star_data.url, link),
                                                  image_link=image,
                                                  title=title,
                                                  description=description,
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.PORN_STAR,
                                                  super_object=porn_star_data,
                                                  )
            res.append(object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        org_request = self.get_object_request(video_data)
        org_tree = self.parser.parse(org_request.text)
        tmp_url = org_tree.xpath('.//video[@id="main_video"]/source')
        videos = sorted((VideoSource(link=x.attrib['src'],  quality=int(re.findall(r'\d+', x.attrib['title'])[0]))
                         for x in tmp_url),
                        key=lambda x: x.quality, reverse=True)

        if len(videos) == 0:
            # Probably we have video from xvideos source. In such case we copy the code from their module.
            video_embed_url = re.findall(r'(?:video_embed_url *= *\')(.*?)(?:\')', org_request.text)
            if len(video_embed_url) == 1:
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                              'q=0.8,application/signed-exchange;v=b3*',
                    'Cache-Control': 'max-age=0',
                    'Referer': video_data.url,
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': self.user_agent
                }
                xvideo_req = self.session.get(video_embed_url[0], headers=headers)
                request_data = re.findall(r'(?:html5player.setVideoHLS\(\')(.*?)(?:\'\);)', xvideo_req.text)
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                              'q=0.8,application/signed-exchange;v=b3*',
                    'Cache-Control': 'max-age=0',
                    'Referer': video_data.url,
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': self.user_agent
                }
                m3u8_req = self.session.get(request_data[0], headers=headers)
                video_m3u8 = m3u8.loads(m3u8_req.text)
                video_playlists = video_m3u8.playlists
                if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
                    video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)
                videos = sorted((VideoSource(link=urljoin(request_data[0], x.uri),
                                             video_type=VideoTypes.VIDEO_SEGMENTS,
                                             quality=x.stream_info.bandwidth,
                                             resolution=x.stream_info.resolution[1],
                                             codec=x.stream_info.codecs)
                                 for x in video_playlists),
                                key=lambda x: x.quality, reverse=True)

        return VideoNode(video_sources=videos)

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        conditions = self.get_proper_filter(page_data).conditions
        if true_object.object_type in (PornCategories.CATEGORY, PornCategories.SEARCH_MAIN, PornCategories.VIDEO):
            last_slash = True
        else:
            last_slash = False
        fetch_base_url = self._prepare_request(page_number, true_object, page_filter, fetch_base_url, last_slash,
                                               conditions)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        if not page_request.ok:
            # Sometimes we try another fetch
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_request(self, page_number, true_object, page_filter, fetch_base_url, use_last_slash, conditions):
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id
        split_url = fetch_base_url.split('/')
        if len(split_url[-1]) == 0:
            # We remove the last slash
            split_url.pop()
        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            tmp_value = page_filter.sort_order.value
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                tmp_value = page_filter.period.value + '-' + tmp_value

            split_url.append(tmp_value)

        if page_number is not None and page_number != 1:
            split_url.append(str(page_number))

        if use_last_slash is True:
            split_url.append('')

        fetch_base_url = '/'.join(split_url)
        return fetch_base_url

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


class TubeXXPorn(PornKTube):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.tubxporn.com/'

    def __init__(self, source_name='TubeXXPorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(TubeXXPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters, single_category_filters, _, _, _, _ = self._prepare_filters()
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=single_category_filters,
                                         video_args=video_filters,
                                         )

    def _update_available_categories(self, category_data):
        """
        Fetches all the available category.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="list_categories"]//div[@class="item"]')
        res = []
        for category in categories:
            link_data = category.xpath('./div[@class="image"]/a')
            assert len(link_data) == 1

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1

            info_data = category.xpath('./h2/a')
            assert len(info_data) == 1
            title = re.findall(r'(\w+?)(?: *\(\d+\))', info_data[0].text)[0]
            number_of_videos = int(re.findall(r'(?:\()(\d+)(?:\))', info_data[0].text)[0])

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(category_data.url, link_data[0].attrib['href']),
                                                  image_link=image_data[0].attrib['src'],
                                                  title=title,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)

        category_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in (tree.xpath('.//div[@class="pagination"]/div[@class="block_content"]/*/text()') +
                                 tree.xpath('.//div[@class="pagination"]/div[@class="block_content"]/*/*/text()'))
                if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="block_content"]/div[@class="item"]/div[@class="inner"]')
        res = []
        for video_tree_data in videos:
            # We skip vip title
            link = video_tree_data.xpath('./div[@class="image "]/a')
            assert len(link) == 1

            image_data = video_tree_data.xpath('./div[@class="image "]/a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            number_of_flip_images = int(re.findall(r'(\d+)(?:\))', image_data[0].attrib['onmouseover'])[0])
            flip_image = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                          for i in range(1, number_of_flip_images + 1)]

            video_length = video_tree_data.xpath('./div[@class="image "]/div[@class="length"]/text()')
            assert len(video_length) == 1

            video_likes = video_tree_data.xpath('./div[@class="image "]/div[@class="likes"]/text()')
            assert len(video_likes) == 1

            video_dislikes = video_tree_data.xpath('./div[@class="image "]/div[@class="dislikes"]/text()')
            assert len(video_dislikes) == 1

            title = video_tree_data.xpath('./div[@class="info"]/a/@title')
            assert len(title) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=re.findall(r'\d+', link[0].attrib['href'])[0],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=title[0],
                                                  image_link=image,
                                                  flip_images_link=flip_image,
                                                  duration=self._format_duration(video_length[0]),
                                                  pos_rating=video_likes[0],
                                                  neg_rating=video_dislikes[0],
                                                  rating=str(int(video_likes[0]) /
                                                             (int(video_likes[0]) + int(video_dislikes[0]))),
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornktube.porn/categories/amateur-porn-videos/')
    module = PornKTube()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
