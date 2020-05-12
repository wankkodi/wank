import re
from .... import urljoin, parse_qsl

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornCatalogCategoryNode, PornCatalogVideoPageNode
from .pornbimbo import PornBimbo


class Porn7(PornBimbo):
    max_flip_images = 10
    videos_per_video_page = 40

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/studios/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/pornstars/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.RECOMMENDED_VIDEO: urljoin(self.base_url, '/featured/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/new/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/popular/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/rated/'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/longest/'),
            PornCategories.MOST_DISCUSSED_VIDEO: urljoin(self.base_url, '/featured/?sort_by=most_commented'),
            PornCategories.FAVORITE_VIDEO: urljoin(self.base_url, '/featured/?sort_by=most_favourited'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.RECOMMENDED_VIDEO: PornFilterTypes.RecommendedOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
            PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
        }

    def _prepare_filters(self):
        """
        Prepares the filters
        :return:
        """
        video_sort_order = [(PornFilterTypes.RecommendedOrder, 'Featured', 'ctr'),
                            (PornFilterTypes.DateOrder, 'New', 'post_date'),
                            (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                            (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                            (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                            (PornFilterTypes.FavorOrder, 'Most Favorite', 'most_favourited'),
                            ]
        video_period = ([(PornFilterTypes.AllDate, 'All time', ''),
                         (PornFilterTypes.OneDate, 'This Month', '_month'),
                         (PornFilterTypes.TwoDate, 'This week', '_week'),
                         (PornFilterTypes.ThreeDate, 'Today', '_today'),
                         ],
                        [('sort_order', [PornFilterTypes.RatingOrder,
                                         PornFilterTypes.ViewsOrder])]
                        )
        search_sort_order = [(PornFilterTypes.RelevanceOrder, 'Most Relevant', '')] + video_sort_order

        category_params = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.PopularityOrder, 'Popular', 'max_videos_ctr'),
                            (PornFilterTypes.DateOrder, 'Last Update', 'today_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            ],
             }
        porn_stars_params = \
            {'sort_order': [(PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.DateOrder, 'Last Update', 'today_videos'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            ]
             }
        actress_params = None
        channel_params = porn_stars_params
        tag_params = None
        video_params = {'sort_order': video_sort_order,
                        'period_filters': video_period,
                        }
        search_params = {'sort_order': search_sort_order,
                         'period_filters': video_period,
                         }

        return (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
                search_params)

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.porn7.xxx/'

    @property
    def max_pages(self):
        return 2000

    def __init__(self, source_name='Porn7', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Porn7, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                    session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="list-categories"]/div[@class="margin-fix"]/div')
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = link_data[0].xpath('div[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None

            number_of_videos = category.xpath('./div[@class="wrap"]/div[@class="views"]')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].text)[0]) if len(number_of_videos) > 0 else None
            number_of_photos = category.xpath('./div[@class="wrap"]/div[@class="added"]/*')
            number_of_photos = \
                int(re.findall(r'\d+', number_of_photos[0].text)[0]) if len(number_of_photos) > 0 else None

            rating = link_data[0].xpath('./strong[@class="title"]/*')
            rating = self._clear_text(rating[0].text) if len(rating) == 1 else None

            title = category.xpath('./strong[@class="title"]/*')
            assert len(title) == 1
            title = self._clear_text(title[0].text)
            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      number_of_photos=number_of_photos,
                                                      rating=rating,
                                                      object_type=PornCategories.CATEGORY,
                                                      super_object=category_data,
                                                      )
            res.append(sub_object_data)
        category_data.add_sub_objects(res)

    def _update_available_channels(self, channel_data):
        res = []
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="list-sponsors"]/div[@class="margin-fix"]/a')
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('div[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None

            number_of_videos = category.xpath('./div[@class="wrap pr-first"]/div[@class="rating"]')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].text)[0]) if len(number_of_videos) > 0 else None
            if number_of_videos is None or number_of_videos == 0:
                continue
            title = category.xpath('./strong[@class="title"]')
            assert len(title) == 1
            title = self._clear_text(title[0].text)
            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      object_type=PornCategories.CHANNEL,
                                                      super_object=channel_data,
                                                      )
            res.append(sub_object_data)
        channel_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        res = []
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="list-models"]/div[@class="margin-fix"]/a')
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('div[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None

            number_of_videos = category.xpath('./div[@class="wrap pr-first"]/div[@class="rating"]')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].text)[0]) if len(number_of_videos) > 0 else None

            rating = category.xpath('./strong[@class="title"]/*')
            rating = self._clear_text(rating[0].text) if len(rating) == 1 else None

            title = category.xpath('./strong[@class="title"]')
            assert len(title) == 1
            title = self._clear_text(title[0].text)
            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      rating=rating,
                                                      object_type=PornCategories.PORN_STAR,
                                                      super_object=porn_star_data,
                                                      )
            res.append(sub_object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN, ):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        if category_data.object_type == PornCategories.SEARCH_MAIN:
            return max(pages)
        else:
            if max(pages) - 1 < self._binary_search_page_threshold:
                return max(pages)
            else:
                return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        res = ([int(x.attrib['data-parameters'].split(':')[-1])
                for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a')
                if 'data-parameters' in x.attrib and x.attrib['data-parameters'].split(':')[-1].isdigit()] +
               [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0])
                for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a')
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0]
               )
        if len(res) == 0:
            xpath = './/div[@class="link_show_more"]/a'
            res = [int(re.findall(r'(?:from.*?:)(\d+)', x.attrib['data-parameters'])[0])
                   for x in tree.xpath(xpath)
                   if 'data-parameters' in x.attrib and
                   len(re.findall(r'(?:from.*?:)(\d+)', x.attrib['data-parameters'])) > 0]
        return res

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        # Took from AnyPorn module with somme modifications...
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div[@class="margin-fix"]/div[@class="item  "]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title'] if 'title' in link_data[0].attrib else None
            preview = link_data[0].attrib['data-mp4'] if 'data-mp4' in link_data[0].attrib else None

            image_data = link_data[0].xpath('./div[@class="img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, self.flip_number + 1)]
            if title is None:
                title = image_data[0].attrib['alt']

            video_length = video_tree_data.xpath('./div[@class="wrap pr-first"]/div[@class="duration"]')
            assert len(video_length) == 1
            video_length = self._format_duration(self._clear_text(video_length[0].text))

            if title is None:
                title = self._clear_text(link_data[0].xpath('./p[@class="title"]')[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=preview,
                                                  duration=video_length,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        headers = {
            'Accept': '*.*',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        if page_number is None:
            page_number = 1
        params.update({
            'mode': 'async',
            'function': 'get_block',
        })
        if page_filter.length.value is not None:
            params.update(parse_qsl(page_filter.length.value))
        params['from'] = str(page_number).zfill(2)

        if true_object.object_type == PornCategories.SEARCH_MAIN:
            conditions = self.get_proper_filter(page_data).conditions
            true_sort_filter_id = self._default_sort_by[true_object.object_type] \
                if true_object.object_type in self._default_sort_by \
                else page_filter.sort_order.filter_id

            params['block_id'] = 'list_videos_videos_list_search_result'
            params['sort_by'] = page_filter.sort_order.value
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value
            params.pop('from')
            params['from2'] = str(page_number).zfill(2)
        elif true_object.object_type == PornCategories.CHANNEL_MAIN:
            params['block_id'] = 'list_content_sources_sponsors_list'
            params['sort_by'] = page_filter.sort_order.value
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

        else:
            return super(Porn7, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                              page_filter, fetch_base_url)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Porn7, self)._version_stack + [self.__version]
