from .... import urljoin, parse_qsl, quote_plus

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .yespornplease import YesPornPlease


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
            image = urljoin(self.base_url, image[0].attrib['src'])

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
                                                image_link=image,
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

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(SayPornPlease, self)._version_stack + [self.__version]
