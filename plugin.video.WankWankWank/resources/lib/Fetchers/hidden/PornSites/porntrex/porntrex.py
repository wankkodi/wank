# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote, unquote

# JSON
from ....tools.text_json_manioulations import prepare_json_from_not_formatted_text

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


class PornTrex(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.porntrex.com/'

    @property
    def possible_empty_pages(self):
        """
        Defines whether it is possible to have empty pages in the site.
        :return:
        """
        return True

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
                         'length_filters': [(PornFilterTypes.AllLength, 'Any duration', None),
                                            (PornFilterTypes.OneLength, '0-10 min', 'ten-min'),
                                            (PornFilterTypes.TwoLength, '10-30 min.', 'ten-thirty-min'),
                                            (PornFilterTypes.ThreeLength, '30+ min.', 'thirty-all-min'),
                                            ],
                         'quality_filters': [(PornFilterTypes.AllQuality, 'Any quality', None),
                                             (PornFilterTypes.HDQuality, 'HD quality', 'hd'),
                                             ],
                         }
        search_filters = {'sort_order': ((PornFilterTypes.RelevanceOrder, 'Relevant', ('relevance', None)),
                                         (PornFilterTypes.DateOrder, 'Latest', ('post_date', 'latest-updates')),
                                         (PornFilterTypes.RatingOrder, 'Top Rated', ('rating', 'top-rated')),
                                         (PornFilterTypes.LengthOrder, 'Longest', ('duration', 'longest')),
                                         (PornFilterTypes.CommentsOrder, 'Most Commented',
                                          ('most-commented', 'most-commented')),
                                         (PornFilterTypes.FavorOrder, 'Most Favorite',
                                          ('most_favourited', 'most-favourited')),
                                         ),
                          'period_filters': video_filters['period_filters'],
                          'length_filters': video_filters['length_filters'],
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

    def __init__(self, source_name='PornTRex', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornTrex, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_category(category_data, PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_category(porn_star_data, PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        channels = tree.xpath('.//div[@class="video-item   "]')
        res = []
        for channel in channels:
            link_data = channel.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            # title = link_data[0].attrib['title']

            image_data = channel.xpath('./a/img/@src')
            assert len(image_data) == 1
            image = urljoin(channel_data.url, image_data[0])

            title = channel.xpath('./p/a/text()')
            assert len(title) == 1
            title = self._clear_text(title[0])

            number_of_videos = channel.xpath('./ul[@class="list-unstyled"]/li[1]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            rating = channel.xpath('./ul[@class="list-unstyled"]/li[@class="pull-right"]/i')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].tail)

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(channel_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  rating=rating,
                                                  object_type=PornCategories.CHANNEL,
                                                  super_object=channel_data,
                                                  )
            res.append(object_data)
        channel_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available tags.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        tree = self.parser.parse(page_request.text)
        tags = tree.xpath('.//div[@class="margin-fix"]/ul/li/a')
        res = []
        for tag in tags:
            assert 'href' in tag.attrib
            title = self._clear_text(tag.text)

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=tag.attrib['href'],
                                                  url=urljoin(tag_data.url, tag.attrib['href']),
                                                  title=title,
                                                  object_type=PornCategories.TAG,
                                                  super_object=tag_data,
                                                  )
            res.append(object_data)
        tag_data.add_sub_objects(res)
        return res

    def _update_available_base_category(self, base_object_data, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object_data)
        tree = self.parser.parse(page_request.text)
        general_objects = tree.xpath('.//div[@class="margin-fix"]/a')
        res = []
        for general_object in general_objects:
            assert 'href' in general_object.attrib
            title = self._clear_text(general_object.attrib['title'])

            image_data = general_object.xpath('./div[@class="img"]/img/@src')
            assert len(image_data) == 1
            image = urljoin(base_object_data.url, image_data[0])

            # title = porn_star.xpath('./p/text()')
            # assert len(title) == 1

            num_of_videos = general_object.xpath('./div[@class="wrap"]/div[@class="videos"]/text()')
            assert len(num_of_videos) == 1
            number_of_videos = int(re.findall(r'(\d+)(?: *\w*)', str(num_of_videos[0]))[0])

            rating = (general_object.xpath('./div[@class="wrap"]/div[@class="rating positive"]/text()') +
                      general_object.xpath('./div[@class="wrap"]/div[@class="rating negative"]/text()'))
            assert len(rating) == 1
            rating = self._clear_text(rating[0])

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=general_object.attrib['href'],
                                                  url=urljoin(base_object_data.url, general_object.attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  rating=rating,
                                                  object_type=object_type,
                                                  super_object=base_object_data,
                                                  )
            res.append(object_data)
        base_object_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        request_data = re.findall(r'(?:var flashvars = )({.*?})(?:;)', tmp_request.text, re.DOTALL)
        request_data = prepare_json_from_not_formatted_text(request_data[0])
        videos = [VideoSource(link=re.findall(r'http.*$', request_data['video_url'])[0],
                              resolution=re.findall(r'\d+', request_data['video_url_text'])[0])]
        i = 1
        while 1:
            new_video_field = 'video_alt_url{i}'.format(i=i if i != 1 else '')
            new_text_field = 'video_alt_url{i}_text'.format(i=i if i != 1 else '')
            if new_video_field in request_data:
                videos.append(VideoSource(link=re.findall(r'http.*$', request_data[new_video_field])[0],
                                          resolution=re.findall(r'\d+', request_data[new_text_field])[0]))
                i += 1
            else:
                break

        videos.sort(key=lambda x: x.resolution, reverse=True)

        return VideoNode(video_sources=videos)

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
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        if not self._check_is_available_page(category_data, page_request):
            return 1
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return ([int(x) for x in tree.xpath('.//div[@class="pagination-holder "]/ul/li/span/text()') if x.isdigit()] +
                [int(re.findall(r'(?:/)(\d+)(?:/)', x)[0])
                 for x in tree.xpath('.//div[@class="pagination-holder "]/ul/li/a/@href')
                 if len(re.findall(r'(?:/)(\d+)(?:/)', x))] +
                [int(re.findall(r'(?:from.*:)(\d+)', x)[0])
                 for x in tree.xpath('.//div[@class="pagination-holder "]/ul/li/a/@data-parameters')
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
        videos = tree.xpath('.//div[@class="video-preview-screen video-item thumb-item  "]')
        # todo: add support for private videos
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a/@href')
            assert len(link) == 1

            image_data = video_tree_data.xpath('./a/img/@data-src')
            assert len(image_data) == 1
            image = urljoin(page_data.url, image_data[0])

            screenshots = video_tree_data.xpath('./a/ul[@class="screenshots-list"]/li/@data-src')
            assert len(screenshots) > 0
            flip_images = [urljoin(page_data.url, x) for x in screenshots]

            resolution = video_tree_data.xpath('./div[@class="hd-text-icon text video-item-submitted k4"]/'
                                               'span[@class="quality"]/text()')
            resolution = resolution[0] if len(resolution) > 0 else ''

            viewers = video_tree_data.xpath('./div[@class="viewsthumb"]/text()')
            assert len(viewers) == 1

            video_length = video_tree_data.xpath('./div[@class="durations"]/i')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0].tail)

            title = video_tree_data.xpath('.//p[@class="inf"]/a/text()')
            assert len(title) == 1

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
                                                  obj_id=video_tree_data.attrib['data-item-id'],
                                                  url=urljoin(self.base_url, link[0]),
                                                  title=title[0],
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  resolution=resolution,
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

        from_key = 'from4'
        if true_object.object_type == PornCategories.PORN_STAR_MAIN:
            block_id = 'list_models_models_list'
            sort_by = page_filter.sort_order.value
            from_key = 'from'
        elif true_object.object_type == PornCategories.CHANNEL_MAIN:
            block_id = 'list_dvds_channels_list'
            sort_by = page_filter.sort_order.value
        elif true_object.object_type == PornCategories.TAG_MAIN:
            block_id = 'list_tags_tags_list'
            sort_by = 'tag'
            from_key = 'from'
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

            if page_filter.quality.value is not None:
                split_url.insert(-1, page_filter.quality.value)

            if suffix is not None:
                split_url.insert(-1, suffix)
            elif page_filter.sort_order.value[1] is not None:
                split_url.insert(-1, page_filter.sort_order.value[1])

            if conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order:
                if page_filter.period.value[1] is not None:
                    split_url.insert(-1, page_filter.period.value[1])
                sort_by += page_filter.period.value[0]

            if page_filter.length.value is not None:
                split_url.insert(-1, page_filter.length.value)

            if true_object.object_type == PornCategories.PORN_STAR:
                block_id = 'list_videos_common_videos_list_norm'
            elif true_object.object_type == PornCategories.CHANNEL:
                block_id = 'list_videos_common_videos_list_norm'
            elif true_object.object_type == PornCategories.LATEST_VIDEO:
                block_id = 'list_videos_latest_videos_list_norm'
                from_key = 'from'
            elif true_object.object_type == PornCategories.TOP_RATED_VIDEO:
                block_id = 'list_videos_common_videos_list_norm'
            elif true_object.object_type == PornCategories.MOST_VIEWED_VIDEO:
                block_id = 'list_videos_common_videos_list_norm'
            elif true_object.object_type == PornCategories.CATEGORY:
                block_id = 'list_videos_common_videos_list_norm'
            elif true_object.object_type == PornCategories.TAG:
                block_id = 'list_videos_common_videos_list_norm'
            elif true_object.object_type == PornCategories.SEARCH_MAIN:
                block_id = 'list_videos_videos'
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

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(PornTrex, self)._version_stack + [self.__version]
