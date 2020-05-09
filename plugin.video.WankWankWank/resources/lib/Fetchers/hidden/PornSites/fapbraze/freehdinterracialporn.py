import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .fapbraze import FapBraze


class FreeHDInterracialPorn(FapBraze):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://freehdinterracialporn.in/'

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/videos/rated/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/videos/recent/'),
            # PornCategories.POPULAR_VIDEO: urljoin(self.base_url, '/videos/popular/'),
            PornCategories.MOST_DISCUSSED_VIDEO: urljoin(self.base_url, '/videos/discussed/'),
            PornCategories.MOST_DOWNLOADED_VIDEO: urljoin(self.base_url, '/videos/downloaded/'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/videos/longest/'),
            PornCategories.MOST_WATCHED_VIDEO: urljoin(self.base_url, '/videos/watched/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/video/'),
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        period_filters = ([(PornFilterTypes.AllDate, 'All time', None),
                           (PornFilterTypes.OneDate, 'Today', 'today'),
                           (PornFilterTypes.ThreeDate, 'This Week', 'week'),
                           (PornFilterTypes.FourDate, 'This Month', 'month'),
                           (PornFilterTypes.FiveDate, 'This Year', 'year'),
                           ],
                          [('sort_order', [PornFilterTypes.RatingOrder,
                                           PornFilterTypes.ViewsOrder,
                                           ])]
                          )
        porn_stars_filter = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most Popular', None),
                                            (PornFilterTypes.DateOrder, 'Most Recent', 'recent'),
                                            (PornFilterTypes.ViewsOrder, 'Most Viewed', 'viewed'),
                                            (PornFilterTypes.AlphabeticOrder, 'Alphabetical', 'alphabetical'),
                                            (PornFilterTypes.SubscribersOrder, 'Most Subscribed', 'subscribed'),
                                            (PornFilterTypes.NumberOfVideosOrder, 'Number of videos', 'videos'),
                                            ],
                             }
        categories_filter = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Name', 'alphabetical'),
                                            (PornFilterTypes.PopularityOrder, 'Popular', 'popular'),
                                            (PornFilterTypes.NumberOfVideosOrder, 'Number of videos', 'videos'),
                                            (PornFilterTypes.FeaturedOrder, 'Featured', 'featured'),
                                            ],
                             }
        single_porn_stars_filter = {'sort_order': [(PornFilterTypes.DateOrder, 'Recent', 'recent'),
                                                   (PornFilterTypes.ViewsOrder, 'Most Viewed', 'viewed'),
                                                   (PornFilterTypes.PopularityOrder, 'Most Popular', 'popular'),
                                                   (PornFilterTypes.RatingOrder, 'Top rated', 'rated'),
                                                   (PornFilterTypes.BeingWatchedOrder, 'Recently Watched', 'watched'),
                                                   (PornFilterTypes.FeaturedOrder, 'Recently Featured', 'featured'),
                                                   ],
                                    }
        video_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Recent', None),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'viewed'),
                                        (PornFilterTypes.CommentsOrder, 'Most Discussed', 'discussed'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'rated'),
                                        (PornFilterTypes.FavorOrder, 'Most Favorite', 'favorite'),
                                        (PornFilterTypes.DownloadsOrder, 'Most Downloads', 'downloaded'),
                                        (PornFilterTypes.BeingWatchedOrder, 'Recently watched', 'watched'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        (PornFilterTypes.FeaturedOrder, 'Recently Featured', 'Featured'),
                                        ],
                         'period_filters': period_filters,
                         }

        search_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Most relevant', None),
                                         (PornFilterTypes.DateOrder, 'Most Recent', 'recent'),
                                         (PornFilterTypes.ViewsOrder, 'Most Viewed', 'viewed'),
                                         (PornFilterTypes.RatingOrder, 'Top Rated', 'rated'),
                                         (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                         ],
                          'period_filters': period_filters,
                          'length_filters': [(PornFilterTypes.AllLength, 'All durations', None),
                                             (PornFilterTypes.OneLength, 'Short (<=5 mins)', 'short'),
                                             (PornFilterTypes.TwoLength, 'Medium (5-20 mins)', 'medium'),
                                             (PornFilterTypes.ThreeLength, 'Long (>=20 mins)', 'long'),
                                             ],
                          'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', None),
                                              (PornFilterTypes.HDQuality, 'HD quality', 'tes'),
                                              ],
                          }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=categories_filter,
                                         porn_stars_args=porn_stars_filter,
                                         single_category_args=video_filters,
                                         single_porn_star_args=single_porn_stars_filter,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='FreeHDInterracialPorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(FreeHDInterracialPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type,
                                                    use_web_server, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="cell category"]/div[@class="category-thumb"]',
                                                  PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@class="cell model"]/div[@class="model-thumb"]',
                                                  PornCategories.PORN_STAR)

    def _update_available_base_object(self, object_data, xpath, object_type):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        xpath_keyword = re.findall(r'(?:cell )(\w+)', xpath)[0]
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])
            title = link_data[0].attrib['title'] if 'title' in link_data[0].attrib else image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="{kw}-info {kw}-videos"]/i'.format(kw=xpath_keyword))
            number_of_videos = int(self._clear_text(number_of_videos[0].tail)) if len(number_of_videos) == 1 else None

            number_of_views = category.xpath('./div[@class="{kw}-info {kw}-views"]/i'.format(kw=xpath_keyword))
            number_of_views = self._format_number_of_viewers(number_of_views[0].tail) \
                if len(number_of_views) == 1 else None

            ranking = category.xpath('./div[@class="{kw}-info {kw}-rank"]'.format(kw=xpath_keyword))
            ranking = int(ranking[0].text[1:]) if len(ranking) == 1 else None

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               number_of_views=number_of_views,
                                               rating=ranking,
                                               object_type=object_type,
                                               super_object=object_data,
                                               ))

        object_data.add_sub_objects(res)
        return res

    def _format_number_of_viewers(self, raw_number):
        ranking = self._clear_text(raw_number)
        if not ranking[-1].isdigit():
            ranking_suffix = ranking[-1]
            ranking = int(float(ranking[:-1]) * (1000 if ranking_suffix == 'k' else 1000000))
        else:
            ranking = int(ranking)
        return ranking

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//ul[@class="pagination pagination-lg justify-content-center"]/li/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="grid mx-auto videos"]/div[@class="cell video"]/'
                            'div[@class="video-thumb video-preview"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = urljoin(page_request.url, image_data[0].attrib['src'])
            flip_images = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                           for i in range(int(image_data[0].attrib['data-thumbs']) + 1)]
            preview = re.sub(r'\d+.jpg', 'preview.mp4', image)

            # title = video_tree_data.xpath('./span[@class="video-title"]')
            # assert len(title) == 1
            # title = title[0].text

            video_length = video_tree_data.xpath('./div[@class="video-info video-duration"]/i')
            assert len(video_length) == 1
            video_length = self._format_duration(self._clear_text(video_length[0].tail))

            rating = (video_tree_data.xpath('./div[@class="video-info video-rating up"]/i') +
                      video_tree_data.xpath('./div[@class="video-info video-rating down"]/i'))
            rating = self._clear_text(rating[0].tail) if len(rating) == 1 else None

            number_of_views = video_tree_data.xpath('./div[@class="video-info video-views"]/i')
            number_of_views = self._format_number_of_viewers(number_of_views[0].tail) \
                if len(number_of_views) == 1 else None

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=preview,
                                                  duration=video_length,
                                                  rating=rating,
                                                  number_of_views=number_of_views,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        if true_object.object_type not in (PornCategories.PORN_STAR, PornCategories.PORN_STAR_MAIN,
                                           PornCategories.CATEGORY_MAIN, PornCategories.SEARCH_MAIN):
            return super(FreeHDInterracialPorn, self)._get_page_request_logic(page_data, params, page_number,
                                                                              true_object, page_filter, fetch_base_url)
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
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        if page_number is not None and page_number != 1:
            params['page'] = [page_number]
        if true_object.object_type in (PornCategories.PORN_STAR, PornCategories.CATEGORY_MAIN):
            if page_filter.sort_order.value is not None:
                params['order'] = [page_filter.sort_order.value]
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            if page_filter.sort_order.value is not None:
                params['o'] = [page_filter.sort_order.value]
            if page_filter.length.value is not None:
                params['d'] = [page_filter.length.value]
            if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['t'] = [page_filter.period.value]
        else:
            if true_object.object_type not in self._default_sort_by:
                if page_filter.sort_order.value is not None:
                    fetch_base_url += page_filter.sort_order.value + '/'
            if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                if page_filter.period.value is not None:
                    fetch_base_url += page_filter.period.value + '/'

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request
