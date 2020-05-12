import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .sex3 import Sex3


class CrocoTube(Sex3):
    flip_number = 5

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 5000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://crocotube.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://crocotube.com/pornstars/',
            PornCategories.TOP_RATED_VIDEO: 'https://crocotube.com/top-rated/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://crocotube.com/most-popular/',
            PornCategories.LONGEST_VIDEO: 'https://crocotube.com/longest/',
            PornCategories.LATEST_VIDEO: 'https://crocotube.com/',
            PornCategories.SEARCH_MAIN: 'https://crocotube.com/search/',
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
        return 'https://crocotube.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        model_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Last Added', ''),
                                       (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-popular'),
                                       (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                       ],
                        }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=model_params,
                                         single_porn_star_args=model_params,
                                         )

    def __init__(self, source_name='CrocoTube', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(CrocoTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        # page_request = self.get_object_request(category_data)
        # tree = self.parser.parse(page_request.text)
        # categories = tree.xpath('.//div[@class="smovies-list categories-list"]/ul/li/a')
        # res = []
        # for category in categories:
        #     link = category.attrib['href']
        #
        #     image_data = category.xpath('./span[@class="img-shadow"]/img')
        #     assert len(image_data) == 1
        #     image = image_data[0].attrib['src']
        #     title = image_data[0].attrib['alt']
        #
        #     number_of_videos = category.xpath('./strong/em')
        #     assert len(number_of_videos) == 1
        #     number_of_videos = int(self._clear_text(number_of_videos[0].text))
        #
        #     res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
        #                                        obj_id=link,
        #                                        url=urljoin(self.base_url, link),
        #                                        image_link=image,
        #                                        title=title,
        #                                        number_of_videos=number_of_videos,
        #                                        object_type=Category,
        #                                        super_object=category_data,
        #                                        ))
        #
        # category_data.add_sub_objects(res)
        # return res
        return self._update_available_base_object(category_data, None, PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        # page_request = self.get_object_request(porn_star_data)
        # tree = self.parser.parse(page_request.text)
        # porn_stars = tree.xpath('.//div[@class="models-block"]/ul/li/a')
        # res = []
        # for porn_star in porn_stars:
        #     link = porn_star.attrib['href']
        #
        #     image_data = porn_star.xpath('./img')
        #     assert len(image_data) == 1
        #     image = image_data[0].attrib['src']
        #
        #     title_data = porn_star.xpath('./span[@class="model-name"]')
        #     assert len(title_data) == 1
        #     title = title_data[0].text
        #
        #     number_of_videos = porn_star.xpath('./span[@class="count"]')
        #     assert len(number_of_videos) == 1
        #     number_of_videos = int(self._clear_text(number_of_videos[0].text))
        #
        #     res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
        #                                        obj_id=link,
        #                                        url=urljoin(self.base_url, link),
        #                                        image_link=image,
        #                                        title=title,
        #                                        number_of_videos=number_of_videos,
        #                                        object_type=PornStar,
        #                                        super_object=porn_star_data,
        #                                        ))
        #
        # porn_star_data.add_sub_objects(res)
        # return res
        return self._update_available_base_object(porn_star_data, None, PornCategories.PORN_STAR)

    def _update_available_base_object(self, base_object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//a[@class="ct-az-list-item"]')
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=category.attrib['href'],
                                       url=urljoin(self.base_url, category.attrib['href']),
                                       title=category.text,
                                       object_type=object_type,
                                       super_object=base_object_data,
                                       ) for category in categories]
        base_object_data.add_sub_objects(res)
        return res

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
        if len(pages) == 0:
            return 1
        return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//div[@class="ct-pagination"]/a')
                if x.text is not None and x.text.isdigit()]

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
        videos = tree.xpath('.//div[@class="ct-videos-list"]/div[@class="thumb"]/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_general_data = video_tree_data.xpath('./div[@class="ct-video-thumb-image img"]')
            assert len(image_general_data) == 1
            image_data = image_general_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']
            video_data = image_general_data[0].xpath('./video')
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, self.flip_number + 1)]
            preview_link = video_data[0].attrib['src'] if len(video_data) == 1 else None

            is_hd = image_general_data[0].xpath('./div[@class="ct-video-thumb-icons"]/'
                                                'div[@class="ct-video-thumb-hd-icon"]')
            is_hd = len(is_hd) > 0

            video_length = image_general_data[0].xpath('./div[@class="ct-video-thumb-icons"]/'
                                                       'div[@class="ct-video-thumb-duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            footer_data = video_tree_data.xpath('./div[@class="ct-video-thumb-stats"]')
            assert len(footer_data) == 1
            rating = footer_data[0].xpath('./div[@class="ct-video-thumb-rating"]/em')
            assert len(rating) == 1
            rating = rating[0].text

            number_of_views = footer_data[0].xpath('./div[@class="ct-video-thumb-views"]/em')
            assert len(number_of_views) == 1
            number_of_views = int(number_of_views[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=preview_link,
                                                  is_hd=is_hd,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  number_of_views=number_of_views,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
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

        if true_object.object_type in (PornCategories.CATEGORY, PornCategories.PORN_STAR):
            if page_filter.sort_order.filter_id != PornFilterTypes.DateOrder:
                fetch_base_url += page_filter.sort_order.value + '/'

        if page_number is not None and page_number != 1:
            fetch_base_url += '{d}/'.format(d=page_number)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(CrocoTube, self)._version_stack + [self.__version]
