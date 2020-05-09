# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote_plus

# Regex
import re

# KT fetcher
from ....tools.external_fetchers import KTMoviesFetcher

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


class ThreeMovs(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.3movs.com/categories/',
            PornCategories.TAG_MAIN: 'https://www.3movs.com/tags/',
            PornCategories.PORN_STAR_MAIN: 'https://www.3movs.com/pornstars/',
            PornCategories.RECOMMENDED_VIDEO: 'https://www.3movs.com/videos/',
            PornCategories.LATEST_VIDEO: 'https://www.3movs.com/latest-updates/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.3movs.com/most-viewed/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.3movs.com/top-rated/',
            PornCategories.LONGEST_VIDEO: 'https://www.3movs.com/longest/',
            PornCategories.SEARCH_MAIN: 'https://www.3movs.com/search_videos/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.RECOMMENDED_VIDEO: PornFilterTypes.FeaturedOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.3movs.com'

    @property
    def possible_empty_pages(self):
        """
        Defines whether it is possible to have empty pages in the site.
        :return:
        """
        return True

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        category_filters = {'sort_order': ((PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Videos', 'total_videos'),
                                           (PornFilterTypes.VideosRatingOrder, 'Videos Rating', 'avg_videos_rating'),
                                           (PornFilterTypes.VideosPopularityOrder, 'Videos Views',
                                            'avg_videos_popularity'),
                                           ),
                            }
        porn_star_filters = {'sort_order': ((PornFilterTypes.RatingOrder, 'Rating', 'top-rated'),
                                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                            (PornFilterTypes.ViewsOrder, 'Views', 'most-viewed'),
                                            (PornFilterTypes.NumberOfVideosOrder, 'Videos', 'videos'),
                                            (PornFilterTypes.VideosRatingOrder, 'Videos Rating', 'videos-rating'),
                                            (PornFilterTypes.VideosPopularityOrder, 'Videos Views', 'videos-views'),
                                            (PornFilterTypes.SubscribersOrder, 'Subscribers', 'subscribers'),
                                            ),
                             }
        video_filters = {'sort_order': ((PornFilterTypes.FeaturedOrder, 'Recently Featured', None),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        (PornFilterTypes.DateOrder, 'Newest', 'latest-updates'),
                                        ),
                         'period_filters': ([(PornFilterTypes.AllDate, 'All Time', 'all-time'),
                                             (PornFilterTypes.OneDate, 'Today', 'today'),
                                             (PornFilterTypes.TwoDate, 'This Week', 'week'),
                                             (PornFilterTypes.ThreeDate, 'This Month', 'month'),
                                             ],
                                            [('sort_order', [PornFilterTypes.ViewsOrder,
                                                             PornFilterTypes.RatingOrder,
                                                             ]),
                                             ]),
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_filters,
                                         porn_stars_args=porn_star_filters,
                                         single_category_args=video_filters,
                                         single_tag_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         video_args=video_filters,
                                         search_args=video_filters,
                                         )

    def __init__(self, source_name='3Movs', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(ThreeMovs, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/76.0.3809.100 Safari/537.36'
        self.kt_fetcher = KTMoviesFetcher(self.session, self.user_agent, self.parser)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, './/div[@class="list_thumbs"]/div[@class="item"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data, './/div[@class="big_thumbs"]/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_base_object(self, base_object, xpath, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:

            image_data = category.xpath('./span[@class="image-holder"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] if 'data:image' not in image_data[0].attrib['src'] \
                else (image_data[0].attrib['data-src'] if 'data-src' in image_data[0].attrib
                      else image_data[0].attrib['data-original'])

            title_data = (category.xpath('./span[@class="info"]/strong/text()') +
                          category.xpath('./div[@class="info"]/h2/text()'))
            assert len(title_data) >= 1
            if len(title_data) > 1:
                title_data = [''.join(title_data)]
            title = re.findall(r'(^[\w ]+)(?: \([\d, ]+\)*$)', title_data[0])
            title = title[0] if len(title) > 0 else title_data[0]
            number_of_videos = re.findall(r'(?:\()([\d,]+)(?: *\)*$)', title_data[0])
            if len(number_of_videos) > 0:
                number_of_videos = int(re.sub(',', '', number_of_videos[0]))
            else:
                number_of_videos = None

            left_info_data = category.xpath('./div[@class="info"]/span[@class="left"]/text()')
            rating = None
            if len(left_info_data) > 1:
                if 'rating' in left_info_data[0]:
                    rating = left_info_data[1]

            right_info_data = category.xpath('./div[@class="info"]/span[@class="left"]/text()')
            if number_of_videos is None and len(right_info_data) > 1:
                if 'movies' in right_info_data[0]:
                    number_of_videos = int(right_info_data[1])

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(base_object.url, category.attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  rating=rating,
                                                  number_of_videos=number_of_videos,
                                                  object_type=object_type,
                                                  super_object=base_object,
                                                  )
            res.append(object_data)
        base_object.add_sub_objects(res)
        return res

    # def _add_category_sub_pages(self, category_data, sub_object_type, page_request=None):
    #     """
    #     Adds category sub pages.
    #     :param page_request:
    #     :param category_data: Category data object (PornCatalogCategoryNode).
    #     :param sub_object_type: Sub object type.
    #     :return:
    #     """
    #     if category_data.object_type == PornCategories.PORN_STAR_MAIN:
    #         category_data.clear_sub_objects()
    #         return self._add_porn_star_sub_pages(category_data, sub_object_type, page_request)
    #     else:
    #         return super(ThreeMovs, self)._add_category_sub_pages(category_data, sub_object_type, page_request)

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="list-tags"]/ul[@class="item"]/li/a')
        links = [x.attrib['href'] for x in raw_objects]
        titles = [re.findall(r'([\w()+]+)(?: *\(\d+\)$)', x.text)[0] for x in raw_objects]
        number_of_videos = [int(re.findall(r'(?:[\w()+]+ *\()(\d+)(?:\)$)', x.text)[0]) for x in raw_objects]
        assert len(titles) == len(links)
        assert len(titles) == len(number_of_videos)

        return links, titles, number_of_videos

    # def _add_porn_star_sub_pages(self, porn_star_data, sub_object_type, fetched_request=None):
    #     page_request = self.get_object_request(porn_star_data) if fetched_request is None else fetched_request
    #     tree = self.parser.parse(page_request.text)
    #     porn_star_page_links = tree.xpath('.//div[@class="block_sub_header p-ig"]')
    #     porn_star_page_links = porn_star_page_links[0].xpath('./a')
    #     new_pages = [PornCatalogPageNode(catalog_manager=self.catalog_manager,
    #                                      obj_id=(IdGenerator.id_to_original_str(porn_star_data.id), link.text),
    #                                      title='{c} | Letter {p}'.format(c=porn_star_data.title, p=link.text),
    #                                      url=urljoin(porn_star_data.url, link.attrib['href']),
    #                                      raw_data=porn_star_data.raw_data,
    #                                      object_type=sub_object_type,
    #                                      super_object=porn_star_data,
    #                                      )
    #                  for i, link in enumerate(porn_star_page_links)]
    #     porn_star_data.add_sub_objects(new_pages)

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
        page_request = self._get_object_request_no_exception_check(category_data) if fetched_request is None \
            else fetched_request
        if not self._check_is_available_page(category_data, page_request):
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
        return [int(x) for x in tree.xpath('.//div[@class="block_sub_header p-ig"]/*/text()')
                if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list_videos"]/div[@class="item"]/a')
        res = []
        for video_tree_data in videos:
            img = video_tree_data.xpath('./span[@class="image-holder"]/img')
            assert len(img) == 1
            image = img[0].attrib['src']
            if 'data:image' in image:
                image = img[0].attrib['data-src']

            rating = video_tree_data.xpath('./span[@class="info"]/span[@class="item_rating"]/text()')
            assert len(rating) == 1

            added_before = video_tree_data.xpath('./span[@class="info"]/span[@class="added"]/text()')
            assert len(added_before) > 0

            number_of_views = video_tree_data.xpath('./span[@class="info"]/span[@class="added"]/span[@class="views"]/'
                                                    'text()')
            assert len(number_of_views) == 1

            video_length = video_tree_data.xpath('./span[@class="info"]/span[@class="added"]/span[@class="time"]/'
                                                 'text()')
            assert len(video_length) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['href'],
                                                  url=urljoin(self.base_url, video_tree_data.attrib['href']),
                                                  title=video_tree_data.attrib['title'],
                                                  image_link=image,
                                                  duration=self._format_duration(video_length[0]),
                                                  rating=rating[0],
                                                  added_before=re.findall(r'([\w\d ]+)(?: | $)', added_before[0])[0],
                                                  number_of_views=number_of_views[0],
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        split_url = fetch_base_url.split('/')
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
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id

        if page_filter.sort_order.value is not None:
            if true_object.object_type == PornCategories.CATEGORY_MAIN:
                params.update({
                    'mode': 'async',
                    'action': 'get_block',
                    'block_id': 'list_categories_categories_list',
                    'sort_by': page_filter.sort_order.value,
                })
            elif true_object.object_type not in self._default_sort_by:
                if split_url[-2].isdigit():
                    split_url.pop(-2)
                split_url.insert(-1, page_filter.sort_order.value)

        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            split_url.insert(-1, page_filter.period.value)

        if page_number is not None and page_number != 1:
            split_url.insert(-1, str(page_number))

        program_fetch_url = '/'.join(split_url)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))
