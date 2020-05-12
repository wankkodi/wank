import re
from .... import urljoin, parse_qsl

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .anyporn import AnyPorn
from .pervertsluts import PervertSluts


class PunishBang(PervertSluts):
    # Some of the models we took from AnyPorn module (has thee same structure)
    flip_number = 2

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/videos/?sort_by=post_date'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/videos/?sort_by=video_viewed'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/videos/?sort_by=rating'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/videos/?sort_by=duration'),
            PornCategories.MOST_DISCUSSED_VIDEO: urljoin(self.base_url, '/videos/?sort_by=most_commented'),
            PornCategories.FAVORITE_VIDEO: urljoin(self.base_url, '/videos/?sort_by=most_favourited'),
            PornCategories.RECOMMENDED_VIDEO: urljoin(self.base_url, '/videos/?sort_by=last_time_view_date'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
                PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
                PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
                PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
                PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
                PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
                PornCategories.RECOMMENDED_VIDEO: PornFilterTypes.RecommendedOrder,
                }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.punishbang.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_sort_order = [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                            (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                            (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                            (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                            (PornFilterTypes.FavorOrder, 'Most Favorite', 'most_favourited'),
                            (PornFilterTypes.RecommendedOrder, 'Most Favorite', 'last_time_view_date'),
                            ]
        search_sort_order = [(PornFilterTypes.RelevanceOrder, 'Most Relevant', '')] + video_sort_order
        category_params = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            ],
             }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                                       (PornFilterTypes.FavorOrder, 'Most Favorite', 'most_favourited'),
                                       (PornFilterTypes.RecommendedOrder, 'Most Favorite', 'last_time_view_date'),
                                       ],
                        'period_filters': ([(PornFilterTypes.AllDate, 'All time', ''),
                                            (PornFilterTypes.OneDate, 'This Month', '_month'),
                                            (PornFilterTypes.TwoDate, 'This week', '_week'),
                                            (PornFilterTypes.ThreeDate, 'Today', '_today'),
                                            ],
                                           [('sort_order', [PornFilterTypes.RatingOrder,
                                                            PornFilterTypes.ViewsOrder])]
                                           ),
                        }
        search_params = {'sort_order': search_sort_order,
                         'period_filters': video_params['period_filters']
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_params,
                                         channels_args=category_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         single_porn_star_args=video_params,
                                         single_tag_args=video_params,
                                         video_args=video_params,
                                         search_args=search_params,
                                         )

    def __init__(self, source_name='PunishBang', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PunishBang, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="cards__list"]/'
                                                  'div[@class="cards__item cards__item--small js-item"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="cards__list"]/'
                                                  'div[@class="cards__item cards__item--small js-item"]/a',
                                                  PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        links, titles, numbers_of_videos = self._get_tag_properties(page_request)
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=link,
                                       url=urljoin(self.base_url, link),
                                       title=title,
                                       number_of_videos=number_of_videos,
                                       object_type=PornCategories.PORN_STAR,
                                       super_object=porn_star_data,
                                       )
               for link, title, number_of_videos in zip(links, titles, numbers_of_videos)]
        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_base_object(self, object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span/img')
            image = (image_data[0].attrib['src'] if 'data:image' not in image_data[0].attrib['src']
                     else image_data[0].attrib['data-src']) if len(image_data) == 1 else None
            title = category.attrib['title'].title() \
                if 'title' in category.attrib else image_data[0].attrib['alt'].title()

            tmp_data = category.xpath('./span[@class="card__footer"]/span[@class="card__action"]/'
                                      'span[@class="card__col"]/span[@class="card__text"]')
            if object_type == PornCategories.CATEGORY:
                number_of_videos = int(tmp_data[0].text) if len(tmp_data) > 0 else None
                rating = None
            elif object_type == PornCategories.CHANNEL:
                number_of_videos = None
                rating = tmp_data[0].text if len(tmp_data) > 0 else None
            else:
                raise ValueError('Unsupported type {t}'.format(t=object_type))

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      rating=rating,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        if is_sort:
            res.sort(key=lambda x: x.title)
        object_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//ol[@class="list-column"]/li[@class="list-column__item"]/div/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'],
                                                 x.attrib['title'] if 'title' in x.attrib else x.text,
                                                 x.xpath('./strong')[0].text)
                                                for x in raw_data])
        return links, titles, number_of_videos

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

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
        if category_data.object_type in (PornCategories.CATEGORY_MAIN,):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        elif max(pages) - 1 < self._binary_search_page_threshold:
            return max(pages)
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 4

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        xpath = './/div[@class="pagination"]/ul[@class="pagination__list"]/li/a'
        return ([int(x.attrib['data-parameters'].split(':')[-1]) for x in tree.xpath(xpath)
                if 'data-parameters' in x.attrib and x.attrib['data-parameters'].split(':')[-1].isdigit()
                 and 'class' in x.attrib and 'is-disabled' not in x.attrib['class']] +
                [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0]) for x in tree.xpath(xpath)
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0
                 and 'class' in x.attrib and 'is-disabled' not in x.attrib['class']]
                )

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        # Took from AnyPorn module with somme modifications...
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="cards__list"]/div')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title'] if 'title' in link_data[0].attrib else None

            video_preview = link_data[0].xpath('./span[@class="card__content"]')
            assert len(video_preview) == 1
            video_preview = video_preview[0].attrib['data-preview'] \
                if 'data-preview' in video_preview[0].attrib else None

            image_data = link_data[0].xpath('./span[@class="card__content"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-src']
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, self.flip_number + 1)]
            if title is None and 'alt' in image_data[0].attrib:
                title = image_data[0].attrib['alt']

            is_hd = link_data[0].xpath('./span[@class="card__content"]/span[@class="flag-group"]/'
                                       'span[@class="flag flag--primary"]')
            is_hd = len(is_hd) > 0 and is_hd[0] == 'HD'

            video_length = link_data[0].xpath('./span[@class="card__content"]/span[@class="flag-group"]/'
                                              'span[@class="flag"]')
            video_length = self._format_duration(video_length[0].text)

            if title is None:
                title = link_data[0].xpath('./span[@class="card__footer"]/span[@class="card__title"]')
                if len(title) > 0:
                    title = title[0].attrib['title'] if'title' in title[0].attrib else self._clear_text(title[0].text)
                else:
                    raise ValueError('Cannot find title!')

            video_data = link_data[0].xpath('./span[@class="card__footer"]/span[@class="card__action"]/'
                                            'span[@class="card__col"]/span[@class="card__col"]/'
                                            'span[@class="card__text"]')
            assert len(video_data) == 2

            number_of_views = self._clear_text(video_data[0].text)
            rating = self._clear_text(video_data[1].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  duration=video_length,
                                                  is_hd=is_hd,
                                                  rating=rating,
                                                  number_of_views=number_of_views,
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
        if page_number is None:
            page_number = 1
        params.update({
            'mode': 'async',
            'function': 'get_block',
        })
        if page_filter.length.value is not None:
            params.update(parse_qsl(page_filter.length.value))
        if page_number > 1:
            params['from'] = str(page_number).zfill(2)
        if true_object.object_type == PornCategories.SEARCH_MAIN:
            conditions = self.get_proper_filter(page_data).conditions
            true_sort_filter_id = self._default_sort_by[true_object.object_type] \
                if true_object.object_type in self._default_sort_by \
                else page_filter.sort_order.filter_id

            params['block_id'] = 'list_videos_videos_list_search_result'
            # params['q'] = self._search_query
            # params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

        elif true_object.object_type == PornCategories.LATEST_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = page_filter.sort_order.value
        elif true_object.object_type in (PornCategories.TAG_MAIN, PornCategories.PORN_STAR_MAIN):
            # params['block_id'] = 'list_content_sources_sponsors_list'
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3*',
                'Cache-Control': 'max-age=0',
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }
            page_request = self.session.get(page_data.url, headers=headers)
            return page_request
        else:
            return super(PunishBang, self)._get_page_request_logic(page_data, params, page_number, true_object,
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

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return super(PervertSluts, self)._prepare_new_search_query(query)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(PunishBang, self)._version_stack + [self.__version]
