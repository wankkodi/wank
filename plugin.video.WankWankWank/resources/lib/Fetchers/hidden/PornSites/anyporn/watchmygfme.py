import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogPageNode, PornCatalogVideoPageNode
from ....id_generator import IdGenerator
from .anyporn import AnyPorn


class WatchMyGfMe(AnyPorn):
    max_flip_images = 30
    videos_per_video_page = 56

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/girls/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/new/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/popular/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/rated/'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/longest/'),
            PornCategories.MOST_DISCUSSED_VIDEO: urljoin(self.base_url, '/commented/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_sort_order = [(PornFilterTypes.DateOrder, 'New', 'post_date'),
                            (PornFilterTypes.ViewsOrder, 'Most Viewed', 'video_viewed'),
                            (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                            (PornFilterTypes.FeaturedOrder, 'Recently Featured', 'last_time_view_date'),
                            ]
        video_period = ([(PornFilterTypes.AllDate, 'All time', ''),
                         (PornFilterTypes.OneDate, 'This Month', '_month'),
                         (PornFilterTypes.TwoDate, 'This week', '_week'),
                         (PornFilterTypes.ThreeDate, 'Today', '_today'),
                         ],
                        [('sort_order', [PornFilterTypes.RatingOrder,
                                         PornFilterTypes.ViewsOrder])]
                        )
        video_quality = [(PornFilterTypes.AllQuality, 'All', ''),
                         (PornFilterTypes.HDQuality, 'HD', '1'),
                         ]
        search_sort_order = [(PornFilterTypes.RelevanceOrder, 'Most Relevant', '')] + video_sort_order

        category_params = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.VideosPopularityOrder, 'Popular Categories', 'avg_videos_popularity'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            ],
             }
        porn_stars_params = \
            {'sort_order': [(PornFilterTypes.VideosPopularityOrder, 'Most Popular', 'model_viewed'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.SubscribersOrder, 'Most Subscribed', 'subscribers_count'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            ]
             }
        channel_params = \
            {'sort_order': [(PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'cs_viewed'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            ],
             }

        video_params = {'sort_order': video_sort_order,
                        'period_filters': video_period,
                        'quality_filters': video_quality,
                        }
        search_params = {'sort_order': search_sort_order,
                         'period_filters': video_period,
                         }

        self._video_filters = \
            PornFilter(data_dir=self.fetcher_data_dir,
                       categories_args=category_params if PornCategories.CATEGORY_MAIN in self.object_urls else None,
                       channels_args=channel_params if PornCategories.CHANNEL_MAIN in self.object_urls else None,
                       porn_stars_args=porn_stars_params
                       if PornCategories.PORN_STAR_MAIN in self.object_urls else None,
                       single_category_args=video_params if PornCategories.CATEGORY_MAIN in self.object_urls else None,
                       single_channel_args=video_params if PornCategories.CHANNEL_MAIN in self.object_urls else None,
                       single_porn_star_args=video_params
                       if PornCategories.PORN_STAR_MAIN in self.object_urls else None,
                       single_tag_args=video_params if PornCategories.TAG_MAIN in self.object_urls else None,
                       video_args=video_params,
                       search_args=search_params,
                       )

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.watchmygf.me/'

    @property
    def max_pages(self):
        return 10000

    def __init__(self, source_name='WatchMyGfMe', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):

        """
        C'tor
        :param source_name: save directory
        """
        super(WatchMyGfMe, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                          session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="video-box-body categories item"]/div[@class="video-box-card"]/a')
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="video-box-img more"]/img')
            image = image_data[0].attrib['data-src'] if len(image_data) == 1 else None
            title = image_data[0].attrib['alt'] if len(image_data) == 1 else None

            if title is None:
                title = category.xpath('./div[@class="video-box-img more"]/'
                                       'div[@class="video-box-description second"]/'
                                       'div[@class="video-box-text"]')
                assert len(title) > 0
                title = title[0].text

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      object_type=PornCategories.CATEGORY,
                                                      super_object=category_data,
                                                      )
            res.append(sub_object_data)
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="video-box-body for-client"]/div[@class="video-box-card"]/a')
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="video-box-img"]/img')
            image = image_data[0].attrib['data-src'] if len(image_data) == 1 else None
            title = image_data[0].attrib['alt'] if len(image_data) == 1 else None

            rating = category.xpath('./div[@class="video-box-img"]/div[@class="time"]/span')
            assert len(rating) > 0
            rating = rating[0].text

            number_of_videos = category.xpath('./div[@class="video-box-description"]/div[@class="video-box-likes"]/'
                                              'div/span[@class="like"]')
            assert len(number_of_videos) > 0
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            if title is None:
                title = category.xpath('./div[@class="video-box-description"]/div[@class="video-box-likes"]/'
                                       'div[@class="title-video-box-likes"]')
                assert len(title) > 0
                title = title[0].text

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

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="video-box-card channels-page"]/a')
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="video-box-img channels-page"]/img')
            image = image_data[0].attrib['data-src'] if len(image_data) == 1 else None
            title = image_data[0].attrib['alt'] if len(image_data) == 1 else None

            rating = category.xpath('./div[@class="video-box-img channels-page"]/'
                                    'div[@class="time channels-page"]/span')
            assert len(rating) > 0
            rating = rating[0].text

            number_of_videos = category.xpath('./div[@class="video-box-img channels-page"]/'
                                              'div[@class="video-box-description channels-page"]/'
                                              'div[@class="video-box-likes"]/div/span[@class="like"]')
            assert len(number_of_videos) > 0
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            if title is None:
                title = category.xpath('./div[@class="video-box-img channels-page"]/'
                                       'div[@class="video-box-description channels-page"]/'
                                       'div[@class="video-box-likes"]/div[@class="title-video-box-likes"]')
                assert len(title) > 0
                title = title[0].text

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      rating=rating,
                                                      object_type=PornCategories.CHANNEL,
                                                      super_object=channel_data,
                                                      )
            res.append(sub_object_data)
        channel_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        tag_properties = self._get_tag_properties(page_request)
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=link,
                                       url=urljoin(tag_data.url, link),
                                       title=title,
                                       number_of_videos=number_of_videos,
                                       object_type=PornCategories.TAG,
                                       super_object=tag_data,
                                       )
               for link, title, number_of_videos in zip(*tag_properties)]
        tag_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//ul[@class="channels-list-letter"]/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.xpath('./div')[0].text,
                                                 int(x.xpath('./span')[0].text) if len(x.xpath('./span')) > 0 else None)
                                                for x in raw_data if len(x.attrib['href'].split('/')) > 4])
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
        new_pages = [PornCatalogPageNode(catalog_manager=self.catalog_manager,
                                         obj_id=(IdGenerator.id_to_original_str(tag_data.id), chr(x)),
                                         title='{c} | Letter {p}'.format(c=tag_data.title, p=chr(x)),
                                         url=urljoin(tag_data.url,
                                                     '{x}/'.format(x=chr(x).lower() if chr(x) != '#' else 'symbol')),
                                         additional_data={'letter': chr(x)},
                                         object_type=sub_object_type,
                                         super_object=tag_data,
                                         )
                     for x in (ord('#'),) + tuple(range(ord('A'), ord('Z')+1))]
        tag_data.add_sub_objects(new_pages)

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        return self._get_video_links_from_video_data2(video_data)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        if len(self._get_available_pages_from_tree(tree)) == 0:
            return 1
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//ul[@class="pagination-list"]/li/*/text()') if x.isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 4

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div/div[@class="video-box-card item"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            preview_data = link_data[0].xpath('./div[@class="video-box-img"]')
            assert len(preview_data) == 1
            preview = preview_data[0].attrib['data-preview'] if 'data-preview' in preview_data[0].attrib else None
            image_data = preview_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-src']
            title = image_data[0].attrib['alt'] if 'alt' in image_data[0].attrib else None
            flip_image = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                          for i in range(1, int(image_data[0].attrib['data-cnt']) + 1)]

            video_length = preview_data[0].xpath('./div[@class="time"]')
            assert len(video_length) == 1
            video_length = self._format_duration(video_length[0].text)

            info_data = link_data[0].xpath('./div[@class="video-box-description"]')
            assert len(info_data) == 1
            if title is None:
                title = info_data[0].attrib['title']

            rating = info_data[0].xpath('./div[@class="video-box-likes"]/span[@class="like"]')
            rating = re.findall(r'\d+%', rating[0].text) if len(rating) > 0 else '0'

            number_of_views = info_data[0].xpath('./div[@class="video-box-likes"]/span[@class="eye"]')
            number_of_views = re.findall(r'\d+%', number_of_views[0].text) if len(number_of_views) > 0 else '0'

            uploader = info_data[0].xpath('./div[@class="video-box-info"]/object/a')
            additional_data = {'uploader': uploader[0].text, 'link': uploader[0].attrib['href']} \
                if len(uploader) > 0 else None

            video_data = PornCatalogVideoPageNode(
                catalog_manager=self.catalog_manager,
                obj_id=link,
                title=title,
                url=urljoin(self.base_url, link),
                image_link=image,
                flip_images_link=flip_image,
                preview_video_link=preview,
                duration=video_length,
                rating=rating,
                number_of_views=number_of_views,
                additional_data=additional_data,
                object_type=PornCategories.VIDEO,
                super_object=page_data,
            )
            res.append(video_data)

        # page_filter = self.get_proper_filter(page_data).current_filters
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
        if page_number is None:
            page_number = 1
        params.update({
            'mode': 'async',
            'function': 'get_block',
        })
        if page_filter.quality.value is not None:
            params['is_hd'] = [page_filter.quality.value]
        if page_number > 1:
            params['from'] = str(page_number).zfill(2)

        if true_object.object_type == PornCategories.TAG_MAIN:
            params = {}
        elif true_object.object_type == PornCategories.TAG:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = page_filter.sort_order.value
            params['from'] = str(page_number).zfill(2)
            params['section'] = ''
        elif true_object.object_type == PornCategories.LATEST_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = page_filter.sort_order.value
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            params['block_id'] = 'list_videos_videos_list_search_result'
            params['q'] = self._search_query
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            if 'from' in params:
                params.pop('from')
            params['from_videos'] = str(page_number).zfill(2)
        else:
            return super(WatchMyGfMe, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                    page_filter, fetch_base_url)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw number, i.e. '7m:58s'.
        :return:
        """
        return super(AnyPorn, self)._format_duration(raw_duration)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(WatchMyGfMe, self)._version_stack + [self.__version]
