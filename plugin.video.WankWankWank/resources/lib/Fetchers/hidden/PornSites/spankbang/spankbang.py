# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote, parse_qs

# Regex
import re

# Playlist tools
import m3u8

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode, VideoTypes
from ....catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


class SpankBang(PornFetcher):
    _porn_star_pages = 35
    _resolutions = {240: '240p',
                    320: '320p',
                    480: '480p',
                    720: '720p',
                    1080: '1080p',
                    2160: '4k',
                    }
    video_request_json = 'https://spankbang.com/api/videos/stream'

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://spankbang.com/categories',
            PornCategories.PORN_STAR_MAIN: 'https://spankbang.com/pornstars',
            PornCategories.LATEST_VIDEO: 'https://spankbang.com/new_videos/',
            PornCategories.POPULAR_VIDEO: 'https://spankbang.com/most_popular/',
            PornCategories.TRENDING_VIDEO: 'https://spankbang.com/trending_videos/',
            PornCategories.UPCOMING_VIDEO: 'https://spankbang.com/upcoming/',
            PornCategories.TOP_RATED_VIDEO: 'https://spankbang.com/top_rated/',
            PornCategories.LONGEST_VIDEO: 'https://spankbang.com/longest_videos/',
            PornCategories.SEARCH_MAIN: 'https://spankbang.com/s/',
        }

    @property
    def _default_sort_by(self):
        return {PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
                PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
                PornCategories.TRENDING_VIDEO: PornFilterTypes.TrendingOrder,
                PornCategories.UPCOMING_VIDEO: PornFilterTypes.UpcomingOrder,
                PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
                PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
                }

    @property
    def possible_empty_pages(self):
        """
        Defines whether it is possible to have empty pages in the site.
        :return:
        """
        return True

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://spankbang.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', 'straight'),
                                              (PornFilterTypes.GayType, 'Gay', 'gay'),
                                              (PornFilterTypes.ShemaleType, 'Transsexual', 'transexual'),
                                              ],
                          }
        # porn_stars_filters = {'sort_order': ((PornFilterTypes.TrendingOrder, 'Trending Porn Stars', None),
        #                                      (PornFilterTypes.AlphabeticOrder, 'Alphabetic', 'pornstars_alphabet'),
        #                                      ),
        #                       }
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'New', 'order=new'),
                                        (PornFilterTypes.TrendingOrder, 'Trending', 'order=trending'),
                                        (PornFilterTypes.UpcomingOrder, 'Popular videos', 'order=upcoming'),
                                        (PornFilterTypes.PopularityOrder, 'Popular videos', 'order=popular'),
                                        (PornFilterTypes.RatingOrder, 'Most Liked', 'order=rated'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'order=length'),
                                        ),
                         'period_filters': ([(PornFilterTypes.AllDate, 'Any Time', None),
                                             (PornFilterTypes.OneDate, 'Today', 'period=today'),
                                             (PornFilterTypes.TwoDate, 'This Week', 'period=week'),
                                             (PornFilterTypes.ThreeDate, 'This Month', 'period=month'),
                                             (PornFilterTypes.FourDate, 'Three Months', 'period=season'),
                                             (PornFilterTypes.FiveDate, 'Three Year', 'period=year'),
                                             ],
                                            [('sort_order', [PornFilterTypes.PopularityOrder,
                                                             PornFilterTypes.RatingOrder,
                                                             PornFilterTypes.LengthOrder,
                                                             ]),
                                             ]),
                         'length_filters': [(PornFilterTypes.AllLength, 'Any duration', None),
                                            (PornFilterTypes.OneLength, '0-10 min', 'min_length=0&max_length=10'),
                                            (PornFilterTypes.TwoLength, '10-30 min', 'min_length=10&max_length=30'),
                                            (PornFilterTypes.ThreeLength, '30+ min', 'min_length=30'),
                                            ],
                         'quality_filters': [(PornFilterTypes.AllQuality, 'Any Quality', None),
                                             (PornFilterTypes.SDQuality, '720+', '720p=1'),
                                             (PornFilterTypes.HDQuality, '1080+', '1080p=1'),
                                             (PornFilterTypes.UHDQuality, 'Full', '4k=1'),
                                             ],
                         }
        search_filters = {'sort_order': ((PornFilterTypes.RelevanceOrder, 'Relevant videos', 'order=relevance'),
                                         (PornFilterTypes.PopularityOrder, 'Popular videos', 'order=top'),
                                         (PornFilterTypes.DateOrder, 'Latest', 'order=new'),
                                         (PornFilterTypes.RatingOrder, 'Most Liked', 'order=hot'),
                                         ),
                          'period_filters': video_filters['period_filters'][0],
                          'length_filters': video_filters['length_filters'],
                          'quality_filters': video_filters['quality_filters'],
                          }
        single_porn_star_filters = {'sort_order': ((PornFilterTypes.TrendingOrder, 'Trending', 'order=trending'),
                                                   (PornFilterTypes.DateOrder, 'New', 'order=new'),
                                                   (PornFilterTypes.PopularityOrder, 'Popular videos', 'order=popular'),
                                                   (PornFilterTypes.RatingOrder, 'Most Liked', 'order=rated'),
                                                   (PornFilterTypes.LengthOrder, 'Longest', 'order=longest'),
                                                   ),
                                    'period_filters': video_filters['period_filters'],
                                    'length_filters': video_filters['length_filters'],
                                    'quality_filters': video_filters['quality_filters'],

                                    }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter,
                                         # porn_stars_args=porn_stars_filters,
                                         single_category_args=video_filters,
                                         single_porn_star_args=single_porn_star_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='SpankBang', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SpankBang, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="categories"]/a')
        res = []
        for category in categories:
            image = category.xpath('./img/@src')
            assert len(image) == 1

            title = category.xpath('./span/text()')
            assert len(title) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=title[0],
                                                  image_link=urljoin(category_data.url, image[0]),
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@id="pornstars"]/ul[@class="results"]/li/a[@class="image"]')
        res = []
        for category in categories:
            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = urljoin(porn_star_data.url, image_data[0].attrib['src'])
            title = image_data[0].attrib['title'] if 'title' in image_data[0].attrib else image_data[0].attrib['alt']

            views = category.xpath('./span[@class="views"]/*')
            assert len(views) == 1
            additional_data = {'views': self._clear_text(views[0].tail)}

            number_of_videos = category.xpath('./span[@class="videos"]/*')
            assert len(number_of_videos) == 1
            number_of_videos = int(''.join(re.findall(r'\d+', number_of_videos[0].tail)))

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(porn_star_data.url, category.attrib['href']),
                                                  title=title,
                                                  number_of_videos=number_of_videos,
                                                  additional_data=additional_data,
                                                  image_link=image,
                                                  object_type=PornCategories.PORN_STAR,
                                                  super_object=porn_star_data,
                                                  )
            res.append(object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        stream_key = tmp_tree.xpath('.//div[@id="video"]/@data-streamkey')
        video_url = self.video_request_json
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Origin': self.base_url,
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        params = {
            'id': stream_key[0],
            'data': 0,
            'sb_session': self.session.cookies['sb_session'],
        }
        video_request = self.session.post(video_url, headers=headers, data=params)
        video_data = video_request.json()
        video_links = sorted((VideoSource(link=v[0], resolution=int(re.findall(r'\d+', k)[0]),
                                          video_type=VideoTypes.VIDEO_REGULAR)
                              for k, v in video_data.items()
                              if re.findall(r'stream_url.*\d+[kp]', k) and v != '' and len(v) > 0),
                             key=lambda y: y.resolution, reverse=True)

        if len(video_links) == 0:
            # We try to fetch the 'stream_url_m3u8' field
            video_links = []
            for k, v in self._resolutions.items():
                if v in video_data and len(video_data[v]) > 0:
                    video_links.extend([VideoSource(link=x,
                                                    video_type=VideoTypes.VIDEO_REGULAR,
                                                    resolution=k) for x in video_data[v]])
                new_v = 'm3u8_{v}'.format(v=v)
                if new_v in video_data and len(video_data[new_v]) > 0:
                    for x in video_data[new_v]:
                        req3 = self.session.get(x, headers=headers)
                        video_m3u8 = m3u8.loads(req3.text)
                        video_playlists = video_m3u8.playlists
                        if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
                            video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)
                        new_video_links = [VideoSource(link=x.uri,
                                                       video_type=VideoTypes.VIDEO_SEGMENTS,
                                                       quality=x.stream_info.bandwidth,
                                                       resolution=x.stream_info.resolution[1])
                                           for x in video_playlists]
                        video_links.extend(new_video_links)
                        if len(new_video_links) > 0:
                            break
        video_links.sort(key=lambda y: y.resolution, reverse=True)
        return VideoNode(video_sources=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.true_object.object_type == PornCategories.PORN_STAR_MAIN:
            return self._porn_star_pages
        elif category_data.true_object.object_type == PornCategories.CATEGORY_MAIN:
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        if not page_request.ok:
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
        return [int(x) for x in tree.xpath('.//div[@class="pagination"]/ul/li/a/text()') if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = (tree.xpath('.//div[@class="video-list video-rotate video-list-with-ads"]/div[@class="video-item"]') +
                  tree.xpath('.//div[@class="video-list video-rotate "]/div[@class="video-item"]'))
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            img = link_data[0].xpath('./img/@src')
            assert len(img) == 1

            resolution = link_data[0].xpath('./p/span[@class="i-hd"]/text()')

            video_length = link_data[0].xpath('./p/span[@class="i-len"]/text()')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0])

            title_data = video_tree_data.xpath('.//div[@class="inf"]/a')
            title = ''.join(x.text if x.text is not None else '' for x in title_data)
            title_data2 = title_data[0].xpath('./strong')
            if len(title_data2) > 0:
                title += ''.join(''.join((x.text if x.text is not None else '', x.tail if x.tail is not None else ''))
                                 for x in title_data2)

            stats_data = video_tree_data.xpath('.//div[@class="stats"]')
            assert len(stats_data) == 1
            raw_stats = self._clear_text(stats_data[0].text).split(' ')
            number_of_views = raw_stats[0]
            rating = self._clear_text(raw_stats[1])

            added_before = stats_data[0].xpath('./span/text()')
            assert len(added_before) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=urljoin(page_data.url, img[0]),
                                                  is_hd=len(resolution) > 0,
                                                  resolution=resolution[0] if len(resolution) > 0 else '360p',
                                                  number_of_views=number_of_views,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  added_before=added_before[0],
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw duration.
        :return:
        """
        return int(re.findall(r'(\d+)(?:m)', raw_duration)[0]) * 60

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        split_url = fetch_base_url.split('/')
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
        if self.general_filter.current_filters.general.value is not None:
            self.session.cookies.set(name='sex_version',
                                     value=self.general_filter.current_filters.general.value,
                                     domain='.spankbang.com')

        if page_number is not None and page_number != 1:
            if true_object.object_type == PornCategories.PORN_STAR:
                params['page'] = page_number
            else:
                if split_url[-1].isdigit():
                    split_url.pop()
                split_url.append(str(page_number))

        # todo: add condition check for period filters of default type...
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id

        if page_filter.sort_order.value is not None:
            if true_object.object_type not in self._default_sort_by:
                params.update(parse_qs(page_filter.sort_order.value))
        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            params.update(parse_qs(page_filter.period.value))
        if page_filter.length.value is not None:
            params.update(parse_qs(page_filter.length.value))
        if page_filter.quality.value is not None:
            params.update(parse_qs(page_filter.quality.value))

        program_fetch_url = '/'.join(split_url)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
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
        return super(SpankBang, self)._version_stack + [self.__version]
