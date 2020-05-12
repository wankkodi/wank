import re
from .... import urljoin, parse_qs

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .upornia import UPornia


class Shemalez(UPornia):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://shemalez.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://shemalez.com/models/',
            PornCategories.TOP_RATED_VIDEO: 'https://shemalez.com/top-rated/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://shemalez.com/most-popular/',
            PornCategories.LATEST_VIDEO: 'https://shemalez.com/latest-updates/',
            PornCategories.LONGEST_VIDEO: 'https://shemalez.com/latest-updates/?sort_by=duration',
            PornCategories.MOST_DISCUSSED_VIDEO: 'https://shemalez.com/latest-updates/?sort_by=most_commented',
            PornCategories.FAVORITE_VIDEO: 'https://shemalez.com/latest-updates/?sort_by=most_favourited',
            PornCategories.SEARCH_MAIN: 'https://shemalez.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
            PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://shemalez.com/'

    def _prepare_filters(self):
        _, video_filters, video_filters, categories_filters, porn_stars_filters, _ = \
            super(Shemalez, self)._prepare_filters()
        general_filters = {'general_filters': [(PornFilterTypes.ShemaleType, 'Shemale', None),
                                               ],
                           }
        channels_filters = \
            {'sort_order': ((PornFilterTypes.VideosRatingOrder, 'Top Rated', 'sort_by=avg_videos_rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sort_by=title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'sort_by=total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'sort_by=avg_videos_popularity'),
                            ),
             }
        video_filters['quality_filters'] = ((PornFilterTypes.AllQuality, 'All quality', None),
                                            (PornFilterTypes.HDQuality, 'HD quality', 'is_hd=1'),
                                            )
        search_filters = {'length_filters': video_filters['length_filters']}
        return general_filters, video_filters, search_filters, categories_filters, porn_stars_filters, channels_filters

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        _, video_filters, search_filter, categories_filters, porn_stars_filters, channels_filters = \
            self._prepare_filters()

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=categories_filters,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filter,
                                         )

    def __init__(self, source_name='Shemalez', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Shemalez, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@id="list_categories_list"]//'
                                                  'div[@class="thumb-category"]',
                                                  PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@id="list_models_list_items"]//'
                                                  'div[@class="thumb-model"]',
                                                  PornCategories.PORN_STAR)

    def _update_available_base_object(self, object_data, xpath, object_type):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            rating = category.xpath('./span[@class="thumb__rating rating"]/i')
            rating = self._clear_text(rating[0].tail) if len(rating) == 1 else None

            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = category.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = (category.xpath('./span[@class="thumb__amount amount"]/i') +
                                category.xpath('./a/span[@class="thumb__amount amount"]/i') +
                                category.xpath('./span[@class="thumb__amount"]/i') +
                                category.xpath('./a/span[@class="thumb__amount"]/i'))
            assert len(number_of_videos) == 1
            number_of_videos = int(''.join(re.findall(r'\d+', number_of_videos[0].tail)))

            number_of_views = category.xpath('./div[@class="thumb__info"]/div[@class="thumb__row"]/'
                                             'span[@class="thumb__view"]/i')
            number_of_views = int(''.join(re.findall(r'\d+', number_of_views[0].tail))) \
                if len(number_of_views) == 1 else None

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               number_of_views=number_of_views,
                                               rating=rating,
                                               object_type=object_type,
                                               super_object=object_data,
                                               ))

        object_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(self._clear_text(x.text).replace(' ', ''))
                for x in tree.xpath('.//ul[@class="pagination__list"]/li/*')
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
            re.findall(r'(?:\[)(\d+)(?:\])(?:.*?)(https://[\w./-]*/videos)', page_request.text))
        videos = (tree.xpath('.//div[@id="list_videos_list_items"]/div[@class="thumb"]') +
                  tree.xpath('.//div[@id="list_videos_videos_items"]/div[@class="thumb"]'))
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a[@class="thumb__link"]')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = video_tree_data.xpath('./a/img')
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

            video_length = video_tree_data.xpath('./a/span[@class="thumb__duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            title = video_tree_data.xpath('./div[@class="thumb__info"]/a')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            rating = video_tree_data.xpath('./div[@class="thumb__info"]//div[@class="thumb__row"]/'
                                           'span[@class="thumb__rating"]/i')
            rating = self._clear_text(rating[0].tail) if len(rating) == 1 else None

            number_of_views = video_tree_data.xpath('./div[@class="thumb__info"]//div[@class="thumb__row"]/'
                                                    'span[@class="thumb__view"]/i')
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

        # if self.general_filter.current_filters.general.value is not None:
        #     self.session.cookies.set(name='category_group_id',
        #                              value=self.general_filter.current_filters.general.value,
        #                              domain=urlparse(self.base_url).netloc,
        #                              )

        if page_number is None:
            page_number = 1
        conditions = self.get_proper_filter(page_data).conditions
        sort_filter_type = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id
        params.update(parse_qs(self.get_proper_filter(page_data).filters.sort_order[sort_filter_type].value))

        if split_url[-2].isdigit():
            split_url.pop(-2)
        if page_number > 1:
            split_url.insert(-1, str(page_number))

        if true_object.object_type in (PornCategories.CATEGORY, PornCategories.PORN_STAR,
                                       PornCategories.CHANNEL, PornCategories.SEARCH_MAIN):
            params.update({
                'mode': 'async',
                'action': 'get_block',
                'from': str(page_number).zfill(2)
            })

            if true_object.object_type == PornCategories.SEARCH_MAIN:
                params['block_id'] = ['list_videos_list']
                params.pop('from')
                params['from_videos'] = str(page_number).zfill(2)
            elif true_object.object_type == PornCategories.CATEGORY:
                params['block_id'] = ['list_videos_list']
                params['category'] = split_url[4]
            elif true_object.object_type == PornCategories.CHANNEL:
                params['block_id'] = ['list_videos_videos']
                params['cs'] = split_url[4]
            elif true_object.object_type == PornCategories.PORN_STAR:
                params['block_id'] = ['list_videos_videos']
                params['model'] = split_url[4]

        if page_filter.period.value is not None and sort_filter_type in conditions.period.sort_order:
            params['sort_by'][0] += ('_' + page_filter.period.value)
        if page_filter.quality.value is not None:
            params.update(parse_qs(page_filter.quality.value))
        if page_filter.length.value is not None:
            params.update(parse_qs(page_filter.length.value))

        program_fetch_url = '/'.join(split_url)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Shemalez, self)._version_stack + [self.__version]
