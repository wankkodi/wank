import re
from .... import urljoin, urlparse, parse_qs, quote

from ....catalogs.base_catalog import VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .txxx import Txxx


class UPornia(Txxx):
    number_of_flip_images = 15

    @property
    def video_data_request_url(self):
        """
        Most viewed videos page url.
        :return:
        """
        return urljoin(self.base_url, '/sn4diyux.php')

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/longest/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://upornia.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filters, video_filters, search_filter, categories_filters, porn_stars_filters, channels_filters = \
            self._prepare_filters()

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filters,
                                         categories_args=categories_filters,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filter,
                                         )

    def _prepare_filters(self):
        general_filters = {'general_filters': ((PornFilterTypes.StraightType, 'Heterosexual', '1'),
                                               (PornFilterTypes.GayType, 'Gay', '2'),
                                               (PornFilterTypes.ShemaleType, 'Transgender', '3'),
                                               ),
                           }
        video_filters = \
            {'sort_order': ((PornFilterTypes.DateOrder, 'Latest', 'sort_by=post_date'),
                            (PornFilterTypes.ViewsOrder, 'Most Viewed', 'sort_by=video_viewed'),
                            (PornFilterTypes.RatingOrder, 'Top Rated', 'sort_by=rating'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'sort_by=duration'),
                            (PornFilterTypes.CommentsOrder, 'Most Commented', 'sort_by=most_commented'),
                            (PornFilterTypes.FavorOrder, 'Most Favorite', 'sort_by=most_favourited'),
                            ),
             'period_filters': (((PornFilterTypes.AllDate, 'All time', None),
                                 (PornFilterTypes.TwoDate, 'Week', 'week'),
                                 (PornFilterTypes.OneDate, 'Month', 'month'),
                                 (PornFilterTypes.ThreeDate, 'Today', 'day'),
                                 ),
                                (('sort_order', [PornFilterTypes.ViewsOrder,
                                                 PornFilterTypes.RatingOrder]),
                                 ),
                                ),
             'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', None),
                                 (PornFilterTypes.HDQuality, 'HD quality', 'show_only_hd=1'),
                                 ),
             'length_filters': ((PornFilterTypes.AllLength, 'Any duration', None),
                                (PornFilterTypes.OneLength, '0-8 min', 'duration_from=&duration_to=480'),
                                (PornFilterTypes.TwoLength, '10-40 min.', 'duration_from=481&duration_to=1200'),
                                (PornFilterTypes.ThreeLength, '40+ min.', 'duration_from=1200&duration_to=1201'),
                                ),
             }
        categories_filters = \
            {'sort_order': ((PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sort_by=title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Video Count', 'sort_by=total_videos'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'sort_by=avg_videos_rating'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'sort_by=avg_videos_popularity'),
                            ),
             }
        porn_stars_filters = \
            {'sort_order': ((PornFilterTypes.VideosRatingOrder, 'Top Rated', 'sort_by=avg_videos_rating'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'sort_by=avg_videos_popularity'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Total Videos', 'sort_by=total_videos'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sort_by=title'),
                            (PornFilterTypes.SubscribersOrder, 'Most Subscribers', 'sort_by=subscribers_count'),
                            ),
             }
        channels_filters = \
            {'sort_order': ((PornFilterTypes.VideosRatingOrder, 'Top Rated', 'sort_by=avg_videos_rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sort_by=title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Video Count', 'sort_by=total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'sort_by=avg_videos_popularity'),
                            (PornFilterTypes.DateOrder, 'Recently Updated', 'sort_by=last_content_date'),
                            ),
             }
        return general_filters, video_filters, video_filters, categories_filters, porn_stars_filters, channels_filters

    def __init__(self, source_name='UPornia', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(UPornia, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@id="list_categories_categories_list_items"]/article/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="thumbnail__label"]/i')
            assert len(number_of_videos) == 1
            number_of_videos = int(''.join(re.findall(r'\d+', number_of_videos[0].tail)))

            rating = category.xpath('./div[@class="thumbnail__info"]/span[@class="thumbnail__info__right"]/i')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].tail)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               rating=rating,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channels.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        channels = tree.xpath('.//div[@id="list_content_sources2_sponsors_list_items"]/article/a')
        res = []
        for channel in channels:
            link = channel.attrib['href']

            image_data = channel.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = channel.xpath('./div[@class="thumbnail__info"]/span[@class="thumbnail__info__right"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

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

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = tree.xpath('.//div[@id="list_models_sphinx_models_list_items"]/article/a')
        res = []
        for porn_star in porn_stars:
            link = porn_star.attrib['href']

            image_data = porn_star.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = porn_star.xpath('./div[@class="thumbnail__label"]/i')
            assert len(number_of_videos) == 1
            number_of_videos = int(''.join(re.findall(r'\d+', number_of_videos[0].tail)))

            country = porn_star.xpath('./div[@class="thumbnail__label thumbnail__label thumbnail__label--left"]/i')
            additional_info = {'country': re.findall(r'(?:flag-)(\w*$)',
                                                     country[0].attrib['class'])[0]} if len(country) == 1 else None

            rating = porn_star.xpath('./div[@class="thumbnail__info thumbnail__info--transparent"]/'
                                     'span[@class="thumbnail__info__right"]/i')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].tail)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               additional_data=additional_info,
                                               rating=rating,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tree = self.parser.parse(tmp_request.text)
        raw_script = [x for x in tree.xpath('.//script') if x.text is not None and 'pC3' in x.text]
        video_id = re.findall(r'(?:"*video_id"*: *)(\d+)', raw_script[0].text)[0]
        pc3 = re.findall(r'(?:"*pC3"*: *\'*)([\d|,]*)', raw_script[0].text)[0]
        params = {'param': video_id + ',' + pc3}

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Cache-Control': 'max-age=0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': video_data.url,
            'Origin': self.base_url[:-1],
            'Sec-Fetch-Mode': 'nested-navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        request = self.session.post(self.video_data_request_url, headers=headers, data=params)
        video_url = re.findall(r'(?:"*video_url"*: *")(.*?)(?:")', request.text)[0]
        video_url = re.sub(r'\\u\d{3}[a-e0-9]', lambda x: x.group(0).encode('utf-8').decode('unicode-escape'),
                           video_url)
        true_video_url = self._get_video_url_from_raw_url(video_url)
        video_url = [VideoSource(link=true_video_url)]

        return VideoNode(video_sources=video_url)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        return max(pages) if len(pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(self._clear_text(x.text).replace(' ', '')) for x in tree.xpath('.//ul[@id="pagination-list"]/li/*')
                if x.text is not None and self._clear_text(x.text).replace(' ', '').isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        video_preview_url = dict(
            re.findall(r'(?:\[)(\d+)(?:\])(?:.*?)(https://cdn\d+.ahacdn.me/c\d+/videos)', page_request.text))
        videos = (tree.xpath('.//div[@id="list_videos2_common_videos_list_items"]/article/a') +
                  tree.xpath('.//div[@id="sphinx_list_cat_videos_videos_list_items"]/article/a') +
                  tree.xpath('.//div[@id="list_videos_videos_list_search_result_items"]/article/a'))
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./img')
            assert len(image_data) == 1
            video_id = image_data[0].attrib['data-video-id']
            image = image_data[0].attrib['src']
            flix_image = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                          for d in range(1, self.number_of_flip_images + 1)]
            video_source = image_data[0].attrib['data-sgid'].split(':')[-1]
            preview_link = (video_preview_url[video_source] +
                            '/{vid_prefix}/{vid}/{vid}_tr.mp4'
                            ''.format(vid_prefix=video_id[:-3]+'000', vid=video_id)) \
                if video_source in video_preview_url else None
            additional_info = {'video_id': video_id}

            video_length = video_tree_data.xpath('./div[@class="thumbnail__info"]/'
                                                 'div[@class="thumbnail__info__right"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            title = video_tree_data.xpath('./div[@class="thumbnail__info"]/div[@class="thumbnail__info__left"]/h5')
            assert len(title) == 1
            title = title[0].text

            rating = video_tree_data.xpath('./div[@class="thumbnail__info__left"]/i')
            rating = self._clear_text(rating[0].tail) if len(rating) == 1 else None

            number_of_views = video_tree_data.xpath('./div[@class="thumbnail__info thumbnail__info--hover"]/'
                                                    'div[@class="thumbnail__info__right"]/i')
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].tail)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  preview_video_link=preview_link,
                                                  additional_data=additional_info,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  number_of_views=number_of_views,
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
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request

        if self.general_filter.current_filters.general.value is not None:
            self.session.cookies.set(name='category_group_id',
                                     value=self.general_filter.current_filters.general.value,
                                     domain=urlparse(self.base_url).netloc,
                                     )

        if page_number is None:
            page_number = 1
        conditions = self.get_proper_filter(page_data).conditions
        sort_filter_type = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id
        params.update({
            'mode': 'async',
            'action': 'get_block',
            'from': str(page_number).zfill(2)
        })
        if self.get_proper_filter(page_data).filters.sort_order[sort_filter_type].value is not None:
            params.update(parse_qs(self.get_proper_filter(page_data).filters.sort_order[sort_filter_type].value))

        if split_url[-2].isdigit():
            split_url.pop(-2)
        if page_number > 1:
            split_url.insert(-1, str(page_number))

        if true_object.object_type == PornCategories.CATEGORY_MAIN:
            params['block_id'] = ['list_categories_categories_list']
            params.pop('from')
        elif true_object.object_type == PornCategories.TAG_MAIN:
            params = None
            page_request = self.session.post(fetch_base_url, headers=headers, data=params)
            return page_request
        elif true_object.object_type == PornCategories.PORN_STAR_MAIN:
            params['block_id'] = ['list_models_sphinx_models_list']
        elif true_object.object_type == PornCategories.CHANNEL_MAIN:
            params['block_id'] = ['list_content_sources2_sponsors_list']
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            params['block_id'] = ['list_videos_videos_list_search_result']
            params.pop('from')
            params['from_videos'] = str(page_number).zfill(2)
        elif true_object.object_type in (PornCategories.CATEGORY, PornCategories.TAG):
            params['block_id'] = ['sphinx_list_cat_videos_videos_list']
            params['category'] = split_url[4]
        else:
            params['block_id'] = ['list_videos2_common_videos_list']

        if page_filter.period.value is not None and sort_filter_type in conditions.period.sort_order:
            params['sort_by'][0] += ('_' + page_filter.period.value)
        if page_filter.quality.value is not None:
            params.update(parse_qs(page_filter.quality.value))
        if page_filter.length.value is not None:
            params.update(parse_qs(page_filter.length.value))

        program_fetch_url = '/'.join(split_url)
        page_request = self.session.post(program_fetch_url, headers=headers, data=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(UPornia, self)._version_stack + [self.__version]
