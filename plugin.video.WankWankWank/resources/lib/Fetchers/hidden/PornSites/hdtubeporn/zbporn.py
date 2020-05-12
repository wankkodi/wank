import re
from .... import urljoin, quote_plus

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .hdtubeporn import HDTubePorn


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

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(ZBPorn, self)._version_stack + [self.__version]
