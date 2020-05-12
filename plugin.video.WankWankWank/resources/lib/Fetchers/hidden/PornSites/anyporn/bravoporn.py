import re
from .... import urljoin, quote_plus

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .anyporn import AnyPorn


class BravoPorn(AnyPorn):
    more_categories_url = 'https://www.bravoporn.com/v/devbmg_desktop_categories_helper.php?sort_by=sort_id'

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.bravoporn.com/c/',
            PornCategories.TAG_MAIN: 'https://www.bravoporn.com/c/',
            PornCategories.PORN_STAR_MAIN: 'https://www.bravoporn.com/models/',
            PornCategories.LATEST_VIDEO: 'https://www.bravoporn.com/latest-updates/',
            PornCategories.POPULAR_VIDEO: 'https://www.bravoporn.com/most-popular/',
            PornCategories.SEARCH_MAIN: 'https://www.bravoporn.com/s/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.bravoporn.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        category_params = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          (PornFilterTypes.VideosPopularityOrder, 'Videos Popularity',
                                           'avg_videos_popularity'),
                                          (PornFilterTypes.VideosRatingOrder, 'Videos Rating', 'avg_videos_rating'),
                                          ],
                           }
        single_category_params = {'sort_order': [(PornFilterTypes.ViewsOrder, 'Most Viewed First', None),
                                                 (PornFilterTypes.RecommendedOrder, 'Recommended first', 'recommended'),
                                                 (PornFilterTypes.VideosRatingOrder, 'Top Rated first', 'top-rated'),
                                                 (PornFilterTypes.DateOrder, 'Recent first', 'latest'),
                                                 ],
                                  }
        model_params = {'sort_order': [(PornFilterTypes.VideosPopularityOrder, 'Videos Popularity',
                                        'avg_videos_popularity'),
                                       (PornFilterTypes.VideosRatingOrder, 'Videos rating', 'avg_videos_rating'),
                                       (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                       (PornFilterTypes.PopularityOrder, 'Popularity', 'model_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                       (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                       ],
                        }
        video_params = {'period_filters': ([(PornFilterTypes.ThreeDate, 'Today', 'today'),
                                            (PornFilterTypes.TwoDate, 'This week', 'week'),
                                            (PornFilterTypes.OneDate, 'This Month', 'month'),
                                            (PornFilterTypes.AllDate, 'All time', 'alltime'),
                                            ],
                                           [('sort_order', [PornFilterTypes.PopularityOrder])]
                                           ),
                        }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_params,
                                         single_category_args=single_category_params,
                                         # single_tag_args=single_category_params,
                                         porn_stars_args=model_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='BravoPorn', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(BravoPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories1 = tree.xpath('.//div[@class="th-wrap"]/a')

        headers = {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        page_request2 = self.session.get(self.more_categories_url, headers=headers)
        tree2 = self.parser.parse(page_request2.text)
        categories2 = tree2.xpath('./body/a')

        categories = categories1 + categories2
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="in-mod"]/strong/span')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].tail)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))
        res.sort(key=lambda x: x.title)
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="th-wrap"]/a')

        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="in-mod"]/strong/span')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].tail)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="list-tags"]/ul/li/a')
        links = [x.attrib['href'] for x in raw_objects]
        titles = [x.text for x in raw_objects]
        number_of_videos = [None] * len(titles)
        assert len(titles) == len(links)
        # assert len(titles) == len(number_of_videos)

        return links, titles, number_of_videos

    def _add_tag_sub_pages(self, tag_data, sub_object_type):
        """
        Adds sub pages to the tags according to the first letter of the title. Stores all the tags to the proper pages.
        Notice that the current method contradicts with the _get_tag_properties method, thus you must use either of
        them, according to the way you want to implement the parsing (Use the _make_tag_pages_by_letter property to
        indicate which of the methods you are about to use...)
        :param tag_data: Tag data.
        :param sub_object_type: Object types of the sub pages (either Page or VideoPage).
        :return:
        """
        return super(AnyPorn, self)._add_tag_sub_pages(tag_data, sub_object_type)

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
        return [int(x.text) for x in tree.xpath('.//div[@class="pager"]/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="th-wrap"]/div[@class="video_block"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])
            title = image_data[0].attrib['alt']
            if 'onmouseover' in image_data[0].attrib:
                max_flip_images = int(re.findall(r'(\d+)(?:\)$)', image_data[0].attrib['onmouseover'])[0])
                flix_image = [re.sub(r'\d.jpg$', '{d}.jpg'.format(d=d), image) for d in range(1, max_flip_images+1)]
            else:
                flix_image = None
            is_hd = video_tree_data.xpath('./div[@class="hd"]')
            is_hd = len(is_hd) == 1

            video_length = video_tree_data.xpath('./div[@class="on"]/span')
            assert len(video_length) == 1
            video_length = video_length[0].text

            rating = video_tree_data.xpath('./em')
            assert len(rating) == 1
            rating = rating[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  is_hd=is_hd,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id
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

        if true_object.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.PORN_STAR_MAIN,):
            params['sort_by'] = page_filter.sort_order.value
        if true_object.object_type in (PornCategories.CATEGORY, PornCategories.TAG):
            if page_filter.sort_order.value is not None:
                fetch_base_url += page_filter.sort_order.value + '/'
        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            fetch_base_url += page_filter.period.value + '/'
        if page_number is not None and page_number != 1:
            fetch_base_url = re.sub(r'/*\d*/$', '/{d}/'.format(d=page_number), fetch_base_url)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(BravoPorn, self)._version_stack + [self.__version]
