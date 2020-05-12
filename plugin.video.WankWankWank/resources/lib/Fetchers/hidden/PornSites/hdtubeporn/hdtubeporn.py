# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote_plus

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# KT fetcher
from ....tools.external_fetchers import KTMoviesFetcher


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
            self.session.cookies.set(domain=self.host_name, name='gender',
                                     value=page_filter.general.value)

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

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(HDTubePorn, self)._version_stack + [self.__version]
