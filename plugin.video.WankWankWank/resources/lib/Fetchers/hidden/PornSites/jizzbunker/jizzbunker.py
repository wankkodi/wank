# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote_plus

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter


class JizzBunker(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, 'channels'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, 'newest'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, 'popular'),
            PornCategories.TRENDING_VIDEO: urljoin(self.base_url, 'trending'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, 'longest'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, 'search'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.TRENDING_VIDEO: PornFilterTypes.TrendingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://jizzbunker.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        categories_filters = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'alphabetically'),
                                             (PornFilterTypes.PopularityOrder, 'Popular', None),
                                             ],
                              }
        single_category_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', None),
                                                  # (PornFilterTypes.PopularityOrder, 'Top', 'channel'),
                                                  ],
                                   'period_filters': ([(PornFilterTypes.AllDate, 'All time', ''),
                                                       (PornFilterTypes.OneDate, '1 day', '1'),
                                                       (PornFilterTypes.TwoDate, '7 days', '7'),
                                                       (PornFilterTypes.ThreeDate, '30 days', '30'),
                                                       ],
                                                      [('sort_order', (PornFilterTypes.DateOrder, ))]),
                                   }
        video_filters = {'sort_order': [(PornFilterTypes.TrendingOrder, 'Trending', 'trending'),
                                        (PornFilterTypes.DateOrder, 'Recent', 'newest'),
                                        (PornFilterTypes.PopularityOrder, 'Popular', 'popular'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        ],
                         'period_filters': ([(PornFilterTypes.OneDate, '1 day', '1'),
                                             (PornFilterTypes.TwoDate, '7 days', '7'),
                                             (PornFilterTypes.ThreeDate, '30 days', '30'),
                                             (PornFilterTypes.AllDate, 'All time', ''),
                                             ],
                                            [('sort_order', (PornFilterTypes.PopularityOrder, ))]),
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=categories_filters,
                                         single_category_args=single_category_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='JizzBunker', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(JizzBunker, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//ul[@class="gallery category"]/li')
        res = []
        for category in categories:
            link_data = category.xpath('./figure/a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-original']

            number_of_videos = category.xpath('./figcaption/a/span[@class="score"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

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

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        video_data = re.findall(r'(?:sources.push\()({.*})(?:\);)', tmp_request.text)
        video_links = re.findall(r'(?:src: *\')(.*?)(?:\')', video_data[0])
        video_links = [VideoSource(link=x, resolution=re.findall(r'(\d+$)', x)[0]) for x in video_links]
        video_links.sort(key=lambda x: x.resolution)
        return VideoNode(video_sources=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
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
        return [int(x.text) for x in tree.xpath('.//ul[@class="pagination"]/li/a')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//ul[@class="gallery"]/li')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./figure/a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title']
            video_preview = link_data[0].attrib['data-animation'] if 'data-animation' in link_data[0].attrib else None

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-original']

            video_length = video_tree_data.xpath('./figure/figcaption/ul[@class="properties"]/li[@class="dur"]/time')
            assert len(video_length) == 1
            video_length = video_length[0].text

            added_before = video_tree_data.xpath('./figure/figcaption/ul[@class="properties"]/li[@class="pubtime"]')
            assert len(added_before) == 1
            added_before = added_before[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  preview_video_link=video_preview,
                                                  duration=self._format_duration(video_length),
                                                  added_before=added_before,
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

        if true_object.object_type == PornCategories.CATEGORY:
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                split_url[-2] += page_filter.period.value
        elif true_object.object_type == PornCategories.CATEGORY_MAIN:
            if page_filter.sort_order.filter_id != PornFilterTypes.PopularityOrder:
                split_url.append(page_filter.sort_order.value)
        elif (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            # We have default video page
            split_url[-1] += page_filter.period.value
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
        if page_number is not None and page_number != 1:
            if true_object.object_type == PornCategories.SEARCH_MAIN:
                params['page'] = page_number
            else:
                split_url.append(str(page_number))

        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?query={q}'.format(q=quote_plus(query))
