import re
from .... import urljoin, unquote

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogVideoPageNode
from .porntrex import PornTrex


class JAVBangers(PornTrex):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.javbangers.com/'

    @property
    def object_urls(self):
        res = super(JAVBangers, self).object_urls
        res.pop(PornCategories.TAG_MAIN)
        return res

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        category_filters = {'sort_order': ((PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                           (PornFilterTypes.RatingOrder, 'Top Rated', 'avg_videos_rating'),
                                           ),
                            }
        porn_stars_filters = {'sort_order': ((PornFilterTypes.RatingOrder, 'Top Rated', 'avg_videos_rating'),
                                             (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                             (PornFilterTypes.ViewsOrder, 'Most Viewed', 'avg_videos_popularity'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                             ),
                              }
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Latest', ('post_date', None)),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', ('video_viewed', 'most-popular')),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', ('rating', 'top-rated')),
                                        (PornFilterTypes.LengthOrder, 'Longest', ('duration', 'longest')),
                                        (PornFilterTypes.CommentsOrder, 'Most Commented',
                                         ('most-commented', 'most-commented')),
                                        (PornFilterTypes.FavorOrder, 'Most Favorite',
                                         ('most_favourited', 'most-favourited')),
                                        ),
                         'period_filters': ([(PornFilterTypes.AllDate, 'All time', ('', None)),
                                             (PornFilterTypes.TwoDate, 'Week', ('_week', 'weekly')),
                                             (PornFilterTypes.OneDate, 'Month', ('_month', 'monthly')),
                                             (PornFilterTypes.ThreeDate, 'Today', ('_today', 'daily')),
                                             ],
                                            [('sort_order', [PornFilterTypes.RatingOrder,
                                                             PornFilterTypes.ViewsOrder,
                                                             ]),
                                             ]),
                         }
        search_filters = {'sort_order': ((PornFilterTypes.RelevanceOrder, 'Relevant', ('', None)),
                                         (PornFilterTypes.DateOrder, 'Latest', ('post_date', 'latest-updates')),
                                         (PornFilterTypes.RatingOrder, 'Top Rated', ('rating', 'top-rated')),
                                         (PornFilterTypes.LengthOrder, 'Longest', ('duration', 'longest')),
                                         (PornFilterTypes.CommentsOrder, 'Most Commented',
                                          ('most-commented', 'most-commented')),
                                         (PornFilterTypes.FavorOrder, 'Most Favorite',
                                          ('most_favourited', 'most-favourited')),
                                         ),
                          'period_filters': video_filters['period_filters'],
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_filters,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=porn_stars_filters,
                                         single_category_args=video_filters,
                                         single_channel_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         single_tag_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='JAVBangers', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(JAVBangers, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//div[@class="list-tags"]/div[@class="margin-fix"]/ul/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, None) for x in raw_data])
        return links, titles, number_of_videos

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return ([int(x) for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/span/text()') if x.isdigit()] +
                [int(re.findall(r'(?:/)(\d+)(?:/)', x)[0])
                 for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a/@href')
                 if len(re.findall(r'(?:/)(\d+)(?:/)', x))] +
                [int(re.findall(r'(?:from.*:)(\d+)', x)[0])
                 for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a/@data-parameters')
                 if len(re.findall(r'(?:from.*:)(\d+)', x)) > 0]
                )

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="video-item   "]')
        # todo: add support for private videos
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a/@href')
            assert len(link) == 1

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            image = urljoin(page_request.url, image)

            num_screenshots = video_tree_data.xpath('./a/img/@data-cnt')
            assert len(num_screenshots) == 1
            flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                           for d in range(1, int(num_screenshots[0])+1)]

            is_hd = len(video_tree_data.xpath('./div[@class="hd-text-icon"]')) > 0

            viewers = video_tree_data.xpath('./div[@class="viewsthumb"]/text()')
            assert len(viewers) == 1

            video_length = video_tree_data.xpath('./div[@class="durations"]/i')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0].tail)

            title = video_tree_data.xpath('.//p[@class="inf"]/a/text()')
            assert len(title) == 1
            title = self._clear_text(title[0])

            added_before_data = video_tree_data.xpath('.//ul[@class="list-unstyled"]/li')
            assert len(added_before_data) == 2
            added_before = None
            rating = None
            for data in added_before_data:
                if 'class' not in data.attrib:
                    added_before = data.text
                elif data.attrib['class'] == 'pull-right':
                    rating = self._clear_text(data.xpath('./i')[0].tail)
                else:
                    raise RuntimeError('Additional information available. Check the html.')

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.xpath('./span/@data-fav-video-id')[0],
                                                  url=urljoin(self.base_url, link[0]),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  is_hd=is_hd,
                                                  duration=self._format_duration(video_length),
                                                  added_before=added_before,
                                                  number_of_views=viewers[0],
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        Slightly changed from above...
        :param page_data: Page data.
        :return: Page request
        """
        split_url = fetch_base_url.split('/')
        query = unquote(split_url[-2])
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
        if true_object.object_type == PornCategories.VIDEO:
            return self.session.get(fetch_base_url, headers=headers, params=params)

        conditions = self.get_proper_filter(page_data).conditions

        from_key = 'from'
        if true_object.object_type == PornCategories.PORN_STAR_MAIN:
            block_id = 'list_models_models_list'
            sort_by = page_filter.sort_order.value
        elif true_object.object_type == PornCategories.CHANNEL_MAIN:
            block_id = 'list_dvds_channels_list'
            sort_by = page_filter.sort_order.value
        elif true_object.object_type == PornCategories.TAG_MAIN:
            block_id = 'list_tags_tags_list'
            sort_by = 'tag'
        elif true_object.object_type == PornCategories.CATEGORY_MAIN:
            block_id = 'list_categories_categories_list'
            sort_by = page_filter.sort_order.value
        else:
            # We have video pages...
            if true_object.object_type in self._default_sort_by:
                suffix = split_url.pop(-2)
                true_sort_filter_id = self._default_sort_by[true_object.object_type]
                sort_by = self.get_proper_filter(page_data).filters.sort_order[true_sort_filter_id].value[0]
            else:
                suffix = None
                true_sort_filter_id = page_filter.sort_order.filter_id
                sort_by = page_filter.sort_order.value[0]

            if suffix is not None:
                split_url.insert(-1, suffix)

            if conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order:
                sort_by += page_filter.period.value[0]

            if page_filter.length.value is not None:
                split_url.insert(-1, page_filter.length.value)

            if true_object.object_type == PornCategories.PORN_STAR:
                block_id = 'list_videos_common_videos_list'
            elif true_object.object_type == PornCategories.CHANNEL:
                block_id = 'list_videos_common_videos_list'
            elif true_object.object_type == PornCategories.LATEST_VIDEO:
                block_id = 'list_videos_latest_videos_list'
            elif true_object.object_type == PornCategories.TOP_RATED_VIDEO:
                block_id = 'list_videos_common_videos_list'
            elif true_object.object_type == PornCategories.MOST_VIEWED_VIDEO:
                block_id = 'list_videos_common_videos_list'
            elif true_object.object_type == PornCategories.CATEGORY:
                block_id = 'list_videos_common_videos_list'
            elif true_object.object_type == PornCategories.TAG:
                block_id = 'list_videos_common_videos_list'
            elif true_object.object_type == PornCategories.SEARCH_MAIN:
                block_id = 'list_videos_videos_list_search_result'
                from_key = 'from_videos'
            else:
                raise RuntimeError('Unknown suffix {u}'.format(u=page_data.url))

        params.update({
            'mode': 'async',
            'function': 'get_block',
            'block_id': block_id,
            'sort_by': sort_by,
            from_key: str(page_number).zfill(2) if page_number is not None else '01',
        })

        if true_object.object_type == PornCategories.SEARCH_MAIN:
            # special case...
            params.update({
                'q': query,
                'from_albums': str(page_number).zfill(2) if page_number is not None else '01',
            })

        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(JAVBangers, self)._version_stack + [self.__version]
