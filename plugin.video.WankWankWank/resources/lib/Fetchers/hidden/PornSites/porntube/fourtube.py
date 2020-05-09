import re
from .... import urljoin, quote_plus

from ....catalogs.base_catalog import VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from ....fetchers.porn_fetcher import PornNoVideoError
from .porntube import PornTube


class FourTube(PornTube):
    video_request_format = 'https://token.4tube.com/{id}/desktop/{formats}'

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        res = super(FourTube, self).object_urls
        res.pop(PornCategories.TAG_MAIN)
        return res
        # return {
        #     PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/tags'),
        #     PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels'),
        #     PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/pornstars'),
        #     PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/videos?sort=date'),
        #     PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/videos?sort=views&time=month'),
        #     PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/videos?sort=rating&time=month'),
        #     PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search'),
        # }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.4tube.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filters = {'general_filters': ((PornFilterTypes.StraightType, 'Straight', None),
                                               (PornFilterTypes.GayType, 'Gay', 'gay'),
                                               (PornFilterTypes.ShemaleType, 'Shemale', 'shemale'),
                                               ),
                           }
        category_filters = {'sort_order': ((PornFilterTypes.AlphabeticOrder, 'Alphabetically', None),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'qty'),
                                           (PornFilterTypes.DateOrder, 'Date added', 'date'),
                                           ),
                            }
        # todo: add filter breast size...
        porn_stars_filters = {'general_filters': ((PornFilterTypes.AllType, 'All', None),
                                                  (PornFilterTypes.GirlType, 'Female', 'female'),
                                                  (PornFilterTypes.GuyType, 'Male', 'male'),
                                                  ),
                              'sort_order': ((PornFilterTypes.PopularityOrder, 'Popularity', None),
                                             (PornFilterTypes.SubscribersOrder, 'Most Subscribers', 'subscribers'),
                                             (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'name'),
                                             (PornFilterTypes.TwitterFollowersOrder, 'Twitter Followers', 'twitter'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'videos'),
                                             (PornFilterTypes.DateOrder, 'Date added', 'date'),
                                             (PornFilterTypes.FavorOrder, 'Likes', 'likes'),
                                             ),
                              }
        channels_filters = {'sort_order': ((PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', None),
                                           (PornFilterTypes.AlphabeticOrder, 'Name', 'name'),
                                           (PornFilterTypes.DateOrder, 'Date added', 'date'),
                                           (PornFilterTypes.SubscribersOrder, 'Most Subscribers', 'subscribers'),
                                           (PornFilterTypes.FavorOrder, 'Likes', 'likes'),
                                           ),
                            }
        video_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Most Popular', None),
                                        (PornFilterTypes.DateOrder, 'Latest', 'date'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                                        ),
                         'added_before_filters': [(PornFilterTypes.AllAddedBefore, 'All time', None),
                                                  (PornFilterTypes.OneAddedBefore, '24 Hours', '24h'),
                                                  (PornFilterTypes.TwoAddedBefore, 'This week', 'week'),
                                                  (PornFilterTypes.ThreeAddedBefore, 'This month', 'month'),
                                                  (PornFilterTypes.FourAddedBefore, 'This Year', 'year'),
                                                  ],
                         'length_filters': [(PornFilterTypes.AllLength, 'Any duration', None),
                                            (PornFilterTypes.OneLength, 'Short (0-5 min.)', 'short'),
                                            (PornFilterTypes.TwoLength, 'Medium (5-20 min.)', 'medium'),
                                            (PornFilterTypes.ThreeLength, 'Long (20+ min.)', 'long'),
                                            ],
                         'quality_filters': [(PornFilterTypes.AllQuality, 'Any quality', None),
                                             (PornFilterTypes.HDQuality, 'HD quality', 'hd'),
                                             ],
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filters,
                                         categories_args=category_filters,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_category_args=video_filters,
                                         single_channel_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         single_tag_args=video_filters,
                                         video_args=video_filters,
                                         search_args=video_filters,
                                         )

    def __init__(self, source_name='4Tube', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(FourTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_general_category(category_data, PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_general_category(channel_data, PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_general_category(porn_star_data, PornCategories.PORN_STAR)

    def _update_available_general_category(self, object_data, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = (tree.xpath('.//div[@class="grid-col4 mb1"]//div[@class="col"]/a') +
                      tree.xpath('.//div[@class="grid-col4 mb1"]//div[@class="col thumb_video"]/a') +
                      tree.xpath('.//div[@class="grid-col4"]//div[@class="col"]/a') +
                      tree.xpath('.//div[@class="grid-col4"]//div[@class="col thumb_video"]/a')
                      )
        res = []
        for category in categories:
            assert 'href' in category.attrib
            title = category.attrib['title']

            number_of_videos = category.xpath('./div[@class="bottom"]//i[@class="icon icon-video"]')
            assert len(number_of_videos) == 1

            image_data = category.xpath('./div[@class="thumb"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-original'] if 'data-original' in image_data[0].attrib \
                else image_data[0].attrib['src']

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=category.attrib['href'],
                                                      url=urljoin(object_data.url, category.attrib['href']),
                                                      image_link=image,
                                                      title=title,
                                                      number_of_videos=int(re.sub(r'[(),]', '',
                                                                                  str(number_of_videos[0].tail))),
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        object_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        page_id = tmp_tree.xpath('.//div[@class="links-list inline text-center"]//button/@data-id')
        if any(x != page_id[0] for x in page_id):
            error_module = self._prepare_porn_error_module_for_video_page(
                video_data, tmp_request.url, 'Inconsistent page id in url {u}'.format(u=tmp_request.url))
            raise PornNoVideoError(error_module.message, error_module)
        page_id = page_id[0].zfill(16)
        formats = sorted((int(x.attrib['data-quality']) for x in tmp_tree.xpath('.//button')
                          if 'data-quality' in x.attrib), reverse=True)
        video_request_page = self.video_request_format.format(id=page_id, formats='+'.join(str(x) for x in formats))
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Origin': self.base_url,
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'cors',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        raw_video = self.session.post(video_request_page, headers=headers)
        videos = raw_video.json()

        video_links = sorted((VideoSource(resolution=int(k), link=v['token'])
                              for k, v in videos.items() if v['status'] == 'success'),
                             key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Get number of pages from category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _check_is_available_page(self, page_object, page_request=None):
        """
        In binary search performs test whether the current page is available.
        :param page_request: Page request.
        :return:
        """
        if page_request is None:
            page_request = self.get_object_request(page_object)
        tree = self.parser.parse(page_request.text)
        error_message = tree.xpath('.//div[@class="col-xs-12 text-center"]/h1/strong')
        return not (len(error_message) == 1 and error_message[0].text == 'Oops!' and
                    error_message[0].tail == ' Not Found')

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(self._clear_text(x)) for x in tree.xpath('.//ul[@class="pagination"]/li/a/text()')
                if self._clear_text(x).isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 4

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@id="video_list_column"]//div[@class="col thumb_video"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1

            img = video_tree_data.xpath('./a/div[@class="thumb"]/img/@src')
            assert len(img) == 1

            mini_slide = video_tree_data.xpath('./a/ul//li/@data-src')
            assert len(mini_slide) > 0

            star_info = video_tree_data.xpath('./ul[@class="thumb-info_top"]/li[@class="master-pornstar"]/a')

            is_hd = video_tree_data.xpath('./ul[@class="thumb-info_top"]/li[@class="topHD"]/text()')

            video_length = video_tree_data.xpath('./ul[@class="thumb-info_top"]/li[@class="duration-top"]/text()')
            assert len(video_length) == 1

            title = video_tree_data.xpath('./div[@class="bottom"]/p[@class="thumb-title"]/text()')
            assert len(title) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(self.base_url, link_data[0].attrib['href']),
                                                  image_link=img[0],
                                                  additional_data={'name': star_info[0].text,
                                                                   'url': star_info[0].attrib['href']}
                                                  if len(star_info) > 0 else None,
                                                  is_hd=len(is_hd) > 0 and is_hd[0] == 'HD',
                                                  flip_images_link=mini_slide,
                                                  title=title[0],
                                                  duration=self._format_duration(video_length[0]),
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
        if self.general_filter.current_filters.general.value is not None:
            if len(split_url) <= 3 or split_url[3] != self.general_filter.current_filters.general.value:
                split_url.insert(3, self.general_filter.current_filters.general.value)
        original_params = params

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
        params = {}
        if page_filter.sort_order.value is not None:
            params['sort'] = page_filter.sort_order.value
        if page_filter.quality.value is not None:
            params['quality'] = page_filter.sort_order.value
        if page_filter.length.value is not None:
            params['duration'] = page_filter.length.value
        if page_filter.added_before.value is not None:
            params['time'] = page_filter.added_before.value
        if page_number is not None and page_number > 1:
            params['p'] = page_number
        params.update(original_params)
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
