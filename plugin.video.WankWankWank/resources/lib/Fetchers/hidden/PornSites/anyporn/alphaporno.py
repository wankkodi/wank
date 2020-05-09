import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .hellporno import HellPorno


class AlphaPorno(HellPorno):
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.alphaporno.com/categories/',
            PornCategories.CHANNEL_MAIN: 'https://www.alphaporno.com/channels/',
            PornCategories.PORN_STAR_MAIN: 'https://www.alphaporno.com/pornstars/',
            PornCategories.TAG_MAIN: 'https://www.alphaporno.com/tags/',
            PornCategories.LATEST_VIDEO: 'https://www.alphaporno.com/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.alphaporno.com/most-popular/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.alphaporno.com/top-rated/',
            PornCategories.LONGEST_VIDEO: 'https://www.alphaporno.com/longest/',
            PornCategories.SEARCH_MAIN: 'https://www.alphaporno.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        porn_stars_params = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Popularity', 'popularity'),
                                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'name'),
                                            (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total-videos'),
                                            ],
                             }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       ],
                        'period_filters': [(PornFilterTypes.AllDate, 'All time', ''),
                                           (PornFilterTypes.OneDate, 'This Month', '_month'),
                                           (PornFilterTypes.TwoDate, 'This week', '_week'),
                                           (PornFilterTypes.ThreeDate, 'Today', '_today'),
                                           ],
                        }
        search_params = video_params.copy()
        search_params['sort_order'] = [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                                       (PornFilterTypes.DateOrder, 'Recent videos', 'most-recent'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                       (PornFilterTypes.LengthOrder, 'By duration', 'long-movies'),
                                       ]

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.alphaporno.com/'

    def __init__(self, source_name='AlphaPorno', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(AlphaPorno, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="movies-block"]/ul/li')
        res = []
        for category in categories:
            link = category.xpath('./a')
            assert len(link) == 1
            link = link[0].attrib['href']

            image = category.xpath('./a/img')
            assert len(image) == 1
            image = urljoin(self.base_url, image[0].attrib['src'])

            title_data = category.xpath('./a/span[@class="cat-title"]')
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].text)

            number_of_videos = category.xpath('./a/span[@class="cat-title"]/em')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(category_data.url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        channels = tree.xpath('.//div[@class="movies-block"]/ul/li')
        res = []
        for channel in channels:
            link_data = channel.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']

            image = channel.xpath('./a/img')
            assert len(image) == 1
            image = urljoin(self.base_url, image[0].attrib['src'])

            title_data = channel.xpath('./a/b')
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].text)

            number_of_videos = channel.xpath('./em')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            related_categories = channel.xpath('./span/a')

            additional_data = {'site_link': link_data[-1].attrib['href'],
                               'related_categories': {x.attrib['title']: x.attrib['href'] for x in related_categories}}

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(channel_data.url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               additional_data=additional_data,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ))

        channel_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = tree.xpath('.//div[@class="models-block"]/ul/li')
        res = []
        for porn_star in porn_stars:
            link_data = porn_star.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']

            image = porn_star.xpath('./a/img')
            assert len(image) == 1
            image = urljoin(self.base_url, image[0].attrib['src'])

            title_data = porn_star.xpath('./a/span')
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].text)

            number_of_videos = porn_star.xpath('./span[@class="count"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(porn_star_data.url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        tree = self.parser.parse(page_request.text)
        tags = tree.xpath('.//div[@class="wrap"]/ul/li')
        res = []
        for tag in tags:
            link_data = tag.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']

            title_data = tag.xpath('./a/em')
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].text)

            number_of_videos = tag.xpath('./a/span')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(tag_data.url, link),
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.TAG,
                                               super_object=tag_data,
                                               ))

        tag_data.add_sub_objects(res)
        return res

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return False

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN,):
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
        return [int(x.text) for x in tree.xpath('.//ul[@class="pagination-list"]/li/a')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//ul[@class="movies-list"]/li[@class="thumb"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']
            max_flip_images = int(re.findall(r'(\d+)(?:\)$)', image_data[0].attrib['onmouseover'])[0])
            flix_image = [re.sub(r'\d.jpg$', '{d}.jpg'.format(d=d), image) for d in range(1, max_flip_images+1)]

            added_before = video_tree_data.xpath('./meta[@itemprop="datePublished"]')
            assert len(added_before) == 1
            added_before = added_before[0].attrib['content']

            video_length = video_tree_data.xpath('./span[@class="duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  added_before=added_before,
                                                  duration=self._format_duration(video_length),
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
        if true_object.object_type in (PornCategories.TOP_RATED_VIDEO, PornCategories.MOST_VIEWED_VIDEO,):
            if page_filter.period.filter_id != PornFilterTypes.AllDate:
                fetch_base_url += page_filter.period.value + '/'
        if true_object.object_type == PornCategories.PORN_STAR_MAIN:
            if page_filter.sort_order.filter_id != PornFilterTypes.DateOrder:
                fetch_base_url += page_filter.sort_order.value + '/'

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Referer': page_data.url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        if page_number is not None and page_number != 1:
            if fetch_base_url == self.base_url:
                fetch_base_url += 'latest-updates/'
            fetch_base_url += '{d}/'.format(d=page_number)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request
