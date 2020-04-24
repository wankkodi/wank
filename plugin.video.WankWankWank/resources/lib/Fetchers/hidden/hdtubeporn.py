# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote_plus
from requests import cookies

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# Generator id
from ..id_generator import IdGenerator

# KT fetcher
from ..tools.external_fetchers import KTMoviesFetcher


class HDTubePorn(PornFetcher):
    max_flip_images = 10

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.hdtube.porn/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://www.hdtube.porn/pornstars/',
            PornCategories.CHANNEL_MAIN: 'https://www.hdtube.porn/channels/',
            PornCategories.LATEST_VIDEO: 'https://www.hdtube.porn/videos/latest-updates/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.hdtube.porn/videos/top-rated/',
            PornCategories.LONGEST_VIDEO: 'https://www.hdtube.porn/videos/longest/',
            PornCategories.POPULAR_VIDEO: 'https://www.hdtube.porn/videos/',
            PornCategories.SEARCH_MAIN: 'https://www.hdtube.porn/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.hdtube.porn/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        porn_stars_filters = {'general_filters': [(PornFilterTypes.GirlType, 'Females', '0'),
                                                  (PornFilterTypes.GuyType, 'Males', '1'),
                                                  (PornFilterTypes.AllType, 'All sexes', ''),
                                                  ],
                              'sort_order': [(PornFilterTypes.NumberOfVideosOrder, 'Total videos', None),
                                             (PornFilterTypes.AlphabeticOrder, 'Name', 'title'),
                                             (PornFilterTypes.PopularityOrder, 'Most popular', 'most-popular'),
                                             (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                             (PornFilterTypes.DateOrder, 'Latest update', 'latest-updates'),
                                             ],
                              }
        channels_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most popular', None),
                                           (PornFilterTypes.AlphabeticOrder, 'Name', 'title'),
                                           (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Total videos', 'total-videos'),
                                           ],
                            }
        video_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most popular', None),
                                        (PornFilterTypes.DateOrder, 'Latest', 'latest-updates'),
                                        (PornFilterTypes.RatingOrder, 'Rating', 'top-rated'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        ],
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_category_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         video_args=video_filters,
                                         search_args=video_filters,
                                         )

    def __init__(self, source_name='HDTubePorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HDTubePorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)
        self.kt_fetcher = KTMoviesFetcher(self.session, self.user_agent, self.parser)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@id="list_categories_categories_list_items"]/div/a',
                                                  PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@id="list_models_models_list_items"]/div/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(channel_data,
                                                  './/div[@id="list_content_sources_sponsors_list_items"]/div/a',
                                                  PornCategories.CHANNEL)

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
            title = category.attrib['title']

            content_data = (category.xpath('./div[@class="card__content"]') +
                            category.xpath('./div[@class="card__content card__content--landscape"]')
                            )
            assert len(content_data) == 1
            image_data = content_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] if 'data:image' not in image_data[0].attrib['src'] \
                else image_data[0].attrib['data-original']
            if 'data:image' in image:
                image = None

            number_of_videos_data = content_data[0].xpath('./span[@class="card__flag"]')
            assert len(number_of_videos_data) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos_data[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=object_type,
                                               super_object=object_data,
                                               ))

        object_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        videos, resolutions = self.kt_fetcher.get_video_link(video_data.url)
        video_sources = [VideoSource(link=x, resolution=res) for x, res in zip(videos, resolutions)]
        if not all(x is None for x in resolutions):
            video_sources.sort(key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=video_sources)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type in (PornCategories.CATEGORY_MAIN,):
            return 1
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
        return [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0])
                for x in tree.xpath('.//ul[@class="pagination__list"]/li/*')
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="cards__list "]/div[@class="item cards__item"]/div')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a[@class="card__content"]')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image)
                           for d in range(1, self.max_flip_images + 1)]
            preview_video = link_data[0].attrib['data-preview'] if 'data-preview' in video_tree_data.attrib \
                else None

            video_length = link_data[0].xpath('./span[@class="card__flag"]')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  duration=self._format_duration(video_length),
                                                  flip_images_link=flip_images,
                                                  preview_video_link=preview_video,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')
        last_slash = len(split_url[-1]) == 0
        if last_slash:
            split_url.pop(-1)
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
        if page_filter.general.value is not None:
            new_cookie = cookies.create_cookie(domain=self.host_name, name='gender',
                                               value=page_filter.general.value)
            self.session.cookies.set_cookie(new_cookie)

        if true_object.object_type not in self._default_sort_by and page_filter.sort_order.value is not None:
            split_url.append(page_filter.sort_order.value)
            last_slash = True
        if page_number is not None and page_number != 1:
            split_url.append(str(page_number))
            last_slash = True
        if last_slash is True:
            split_url.append('')
        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query))


class SexVid(HDTubePorn):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.sexvid.xxx/c/',
            PornCategories.PORN_STAR_MAIN: 'https://www.sexvid.xxx/pornstars/',
            PornCategories.CHANNEL_MAIN: 'https://www.sexvid.xxx/sponsor/',
            PornCategories.FAVORITE_VIDEO: 'https://www.sexvid.xxx/p/most-favourited/',
            PornCategories.LATEST_VIDEO: 'https://www.sexvid.xxx/p/date/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.sexvid.xxx/p/rating/',
            PornCategories.LONGEST_VIDEO: 'https://www.sexvid.xxx/p/duration/',
            PornCategories.MOST_DISCUSSED_VIDEO: 'https://www.sexvid.xxx/p/most-commented/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.sexvid.xxx/p/',
            PornCategories.SEARCH_MAIN: 'https://www.sexvid.xxx/s/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.sexvid.xxx/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        porn_stars_filters = {'general_filters': [(PornFilterTypes.GirlType, 'Females', '0'),
                                                  (PornFilterTypes.GuyType, 'Males', '1'),
                                                  (PornFilterTypes.AllType, 'All sexes', ''),
                                                  ],
                              'sort_order': [(PornFilterTypes.NumberOfVideosOrder, 'Total videos', None),
                                             (PornFilterTypes.AlphabeticOrder, 'Name', 'title'),
                                             (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                             (PornFilterTypes.PopularityOrder, 'Popularity', 'popularity'),
                                             ],
                              }
        channels_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most popular', None),
                                           (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sites_ab'),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Total videos', 'total-videos'),
                                           ],
                            }
        video_filters = {'sort_order': [(PornFilterTypes.ViewsOrder, 'Most viewed', None),
                                        (PornFilterTypes.FavorOrder, 'Most favourited', 'most-favourited'),
                                        (PornFilterTypes.DateOrder, 'Latest', 'date'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        (PornFilterTypes.CommentsOrder, 'Most commented', 'most-commented'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                        ],
                         }
        search_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Relevance', None),
                                         (PornFilterTypes.FavorOrder, 'Most favourited', 'most-favourited'),
                                         (PornFilterTypes.DateOrder, 'Latest', 'date'),
                                         (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                         (PornFilterTypes.CommentsOrder, 'Most commented', 'most-commented'),
                                         (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                         ],
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_category_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='SexVid', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SexVid, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumbs"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            title_data = category.xpath('./span[@class="tools"]/span[@class="title_cat"]')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos_data = category.xpath('./span[@class="tools"]/span[@class="video_quantity"]/span')
            assert len(number_of_videos_data) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos_data[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumbs"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span[@class="images_wrapper"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            country = category.xpath('./span[@class="images_wrapper"]/i/img')
            assert len(country) == 1
            additional_data = {'country': country[0].attrib['alt']}

            title_data = category.xpath('./span[@class="tools"]/span[@class="title_thumb"]')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos_data = category.xpath('./span[@class="tools"]/span[@class="rating_holder"]/'
                                                   'span[@class="video_quantity"]/div/span')
            assert len(number_of_videos_data) > 0
            number_of_videos = int(re.findall(r'\d+', number_of_videos_data[0].text)[0])
            number_of_photos = int(re.findall(r'\d+', number_of_videos_data[1].text)[0]) \
                if len(number_of_videos_data) == 2 else None

            rating_data = category.xpath('./span[@class="tools"]/span[@class="rating_holder"]/'
                                         'span[@class="video_rating"]/span')
            assert len(rating_data) == 1
            rating = rating_data[0].text

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               number_of_photos=number_of_photos,
                                               additional_data=additional_data,
                                               rating=rating,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumbs"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            title_data = category.xpath('./span[@class="tools"]/span[@class="title_cat"]')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos_data = category.xpath('./span[@class="tools"]/span[@class="video_quantity"]/div/span')
            assert len(number_of_videos_data) > 0
            number_of_videos = int(re.findall(r'\d+', number_of_videos_data[0].text)[0])
            number_of_photos = int(re.findall(r'\d+', number_of_videos_data[1].text)[0]) \
                if len(number_of_videos_data) == 2 else None

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               number_of_photos=number_of_photos,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ))

        channel_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0])
                for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a')
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumbs"]/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']
            title = video_tree_data.attrib['title']

            image_data = video_tree_data.xpath('./span/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            max_images = len(video_tree_data.xpath('./span/ul[@class="screenshots-list"]/li'))
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, max_images+1)]

            added_before = video_tree_data.xpath('./span[@class="tools"]/span[@class="tools_holder"]/'
                                                 'span[@class="date"]')
            assert len(added_before) == 1
            added_before = self._clear_text(added_before[0].text)

            video_length = video_tree_data.xpath('./span[@class="tools"]/span[@class="tools_holder"]/'
                                                 'span[@class="info"]/span[@class="time"]/span')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0].text)

            number_of_views = video_tree_data.xpath('./span[@class="tools"]/span[@class="tools_holder"]/'
                                                    'span[@class="info"]/span[@class="eye"]/span')
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  duration=self._format_duration(video_length),
                                                  flip_images_link=flip_images,
                                                  added_before=added_before,
                                                  number_of_views=number_of_views,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')
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
        if page_filter.general.value is not None:
            new_cookie = cookies.create_cookie(domain=self.host_name, name='gender',
                                               value=page_filter.general.value)
            self.session.cookies.set_cookie(new_cookie)

        insert_value = None
        insert_index = -1
        if true_object.object_type not in self._default_sort_by:
            insert_value = page_filter.sort_order.value
            if true_object.object_type == PornCategories.SEARCH_MAIN:
                insert_index = -2
        if insert_value is not None:
            split_url.insert(insert_index, insert_value)
        if page_number is not None and page_number != 1:
            split_url.insert(-1, str(page_number))
        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request


class PornID(HDTubePorn):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.pornid.xxx/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://www.pornid.xxx/pornstars/',
            PornCategories.CHANNEL_MAIN: 'https://www.pornid.xxx/channels/',
            PornCategories.LATEST_VIDEO: 'https://www.pornid.xxx/latest/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.pornid.xxx/top-rated/',
            PornCategories.LONGEST_VIDEO: 'https://www.pornid.xxx/longest/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.pornid.xxx/most-viewed/',
            PornCategories.SEARCH_MAIN: 'https://www.pornid.xxx/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornid.xxx/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        porn_stars_filters = {'general_filters': [(PornFilterTypes.GirlType, 'Females', '0'),
                                                  (PornFilterTypes.AllType, 'All sexes', ''),
                                                  (PornFilterTypes.GuyType, 'Males', '1'),
                                                  ],
                              'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Name', None),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Videos', 'videos'),
                                             (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                             (PornFilterTypes.PopularityOrder, 'Popularity', 'popularity'),
                                             ],
                              }
        channels_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most popular', None),
                                           (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sites_ab'),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Total videos', 'total-videos'),
                                           ],
                            }
        video_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', None),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                        ],
                         }
        search_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Relevance', None),
                                         (PornFilterTypes.DateOrder, 'Latest', 'latest'),
                                         (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                         (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                         (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                         ],
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_category_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='PornID', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornID, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumb"]/div/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] if 'src' in image_data[0].attrib else image_data[0].attrib['data-src']
            if 'data:image' in image and 'data-original' in image_data[0].attrib:
                image = image_data[0].attrib['data-original']

            title_data = category.xpath('./span[@class="thumb-info"]/span[@class="info-ctgs"]/span[@class="name-ctg"]')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos_data = category.xpath('./span[@class="thumb-info"]/span[@class="info-ctgs"]/'
                                                   'span[@class="amount-vids"]/span')
            assert len(number_of_videos_data) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos_data[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumb"]/div/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span[@class="preview"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] if 'src' in image_data[0].attrib else image_data[0].attrib['data-src']
            if 'data:image' in image and 'data-original' in image_data[0].attrib:
                image = image_data[0].attrib['data-original']

            title_data = category.xpath('./span[@class="thumb-info"]/span[@class="info-models"]/'
                                        'span[@class="name-model"]')
            assert len(title_data) == 1
            title = title_data[0].text

            rating_data = category.xpath('./span[@class="thumb-info"]/span[@class="info-models"]/'
                                         'span[@class="rating"]/span')
            assert len(rating_data) == 1
            rating = re.findall(r'\d+%', rating_data[0].attrib['style'])[0]

            number_of_videos_data = category.xpath('./span[@class="preview"]/span[@class="duration"]/span')
            assert len(number_of_videos_data) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos_data[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               rating=rating,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumb"]/div/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span[@class="preview"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] if 'src' in image_data[0].attrib else image_data[0].attrib['data-src']
            if 'data:image' in image and 'data-original' in image_data[0].attrib:
                image = image_data[0].attrib['data-original']

            title_data = category.xpath('./span[@class="thumb-info"]/span[@class="info-channel"]/'
                                        'div[@class="channel-name"]')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos_data = category.xpath('./span[@class="thumb-info"]/span[@class="info-channel"]/'
                                                   'div[@class="channel-count"]/span')
            assert len(number_of_videos_data) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos_data[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ))

        channel_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0])
                for x in tree.xpath('.//div[@class="pagination"]/div/a')
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumb"]/div/div')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title']

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] if 'src' in image_data[0].attrib else image_data[0].attrib['data-src']
            max_images = len(video_tree_data.xpath('./a/ul[@class="screenshots-list"]/li'))
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, max_images+1)]

            video_length = video_tree_data.xpath('./a/span[@class="duration"]')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0].text)

            added_before = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="info-bottom"]/'
                                                 'span[@class="added"]')
            assert len(added_before) == 1
            added_before = self._clear_text(added_before[0].text)

            number_of_views = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="info-bottom"]/'
                                                    'span[@class="views"]/span')
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  duration=self._format_duration(video_length),
                                                  flip_images_link=flip_images,
                                                  added_before=added_before,
                                                  number_of_views=number_of_views,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res


class ZBPorn(HDTubePorn):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://zbporn.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://zbporn.com/performers/',
            PornCategories.LATEST_VIDEO: 'https://zbporn.com/latest-updates/',
            PornCategories.TOP_RATED_VIDEO: 'https://zbporn.com/top-rated/',
            PornCategories.POPULAR_VIDEO: 'https://zbporn.com/most-popular/',
            PornCategories.LONGEST_VIDEO: 'https://zbporn.com/longest/',
            PornCategories.SEARCH_MAIN: 'https://zbporn.com/search/',
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
        return 'https://zbporn.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        # general_filter_params = {'general_filters': [(StraightType, 'Straight', None),
        #                                              (GayType, 'Gay', 'gay'),
        #                                              (ShemaleType, 'Shemale', 'shemale'),
        #                                              ],
        #                          }
        categories_filters = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Name', 'title'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                             (PornFilterTypes.ViewsOrder, 'Most Viewed', 'avg_videos_popularity'),
                                             (PornFilterTypes.RatingOrder, 'Top Rated', 'avg_videos_rating'),
                                             ],
                              }
        porn_stars_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Popularity', None),
                                             (PornFilterTypes.AlphabeticOrder, 'Name', 'title'),
                                             (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Videos', 'total-videos'),
                                             (PornFilterTypes.VideosRatingOrder, 'Videos Rating', 'videos-rating'),
                                             (PornFilterTypes.ViewsOrder, 'Most Viewed', 'videos-popularity'),
                                             ],
                              }
        channels_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most popular', None),
                                           (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sites_ab'),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Total videos', 'total-videos'),
                                           ],
                            }
        video_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', None),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                        (PornFilterTypes.PopularityOrder, 'Most Popular', 'most-popular'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        ],
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=categories_filters,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_category_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='ZBPorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(ZBPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumbs"]/div/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="th-image"]/div/img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])

            title_data = category.xpath('./div[@class="th-model"]')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos_data = category.xpath('./div[@class="th-image"]/div/span[@class="th-videos"]/i')
            assert len(number_of_videos_data) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos_data[0].tail)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumbs"]/div/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="th-image th-image-vertical"]/div/img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])

            rating_data = category.xpath('./div[@class="th-image th-image-vertical"]/div/span[@class="th-rating"]/i')
            assert len(rating_data) == 1
            rating = rating_data[0].tail

            title_data = category.xpath('./div[@class="th-model"]')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos_data = category.xpath('./span[@class="added"]')
            assert len(number_of_videos_data) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos_data[0].text)[0])

            number_of_photos_data = category.xpath('./span[@class="rating-tnumb"]')
            assert len(number_of_photos_data) == 1
            number_of_photos = int(re.findall(r'\d+', number_of_photos_data[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               number_of_photos=number_of_photos,
                                               rating=rating,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumb"]/div/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span[@class="preview"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] if 'data:image' not in image_data[0].attrib['src'] \
                else image_data[0].attrib['data-original']

            title_data = category.xpath('./span[@class="thumb-info"]/span[@class="info-channel"]/'
                                        'div[@class="channel-name"]')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos_data = category.xpath('./span[@class="thumb-info"]/span[@class="info-channel"]/'
                                                   'div[@class="channel-count"]/span')
            assert len(number_of_videos_data) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos_data[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ))

        channel_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        search_pattern = r'(\d+)(?:/*$|/*?)'
        return [int(re.findall(search_pattern, x.attrib['href'])[0])
                for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a')
                if 'href' in x.attrib and len(re.findall(search_pattern, x.attrib['href'])) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumbs thumbs-expandable"]/div/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']
            title = video_tree_data.attrib['title']

            image_data = video_tree_data.xpath('./div[@class="th-image"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            max_images = int(re.findall(r'(\d+)(?:\))', image_data[0].attrib['onmouseover'])[0])
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, max_images+1)]

            video_length = video_tree_data.xpath('./div[@class="th-image"]/span[@class="th-duration"]/'
                                                 'span[@class="th-time"]')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0].text)

            rating = video_tree_data.xpath('./div[@class="th-image"]/span[@class="th-rating"]/i')
            rating = rating[0].tail if len(rating) == 1 else None

            is_hd = video_tree_data.xpath('./div[@class="th-image"]/span[@class="th-duration"]/i[@class="th-hd"]')
            is_hd = len(is_hd) > 0

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  duration=self._format_duration(video_length),
                                                  flip_images_link=flip_images,
                                                  rating=rating,
                                                  is_hd=is_hd,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')
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
        if true_object.object_type not in self._default_sort_by:
            if page_filter.sort_order.value is not None:
                if true_object.object_type == PornCategories.CATEGORY_MAIN:
                    params['sort_by'] = page_filter.sort_order.value
                else:
                    split_url.insert(-1, page_filter.sort_order.value)

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


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    # module = HDTubePorn()
    # module = SexVid()
    # module = PornID()
    module = ZBPorn()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=False)
