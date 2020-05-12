import re
from .... import urljoin, parse_qsl

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .anyporn import AnyPorn
from .pervertsluts import PervertSluts


class WatchMyExGf(PervertSluts):
    # Some of the models we took from AnyPorn module (has thee same structure)
    flip_number = 11

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/porn/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.watchmyexgf.net/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        channels_params = {'sort_order': [(PornFilterTypes.ViewsOrder, 'Most Viewed', 'avg_videos_popularity'),
                                          (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          ],
                           }
        category_params = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.ViewsOrder, 'Most viewed', 'avg_videos_popularity'),
                                          (PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          ],
                           }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
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
        single_channel_params = {'sort_order': video_params['sort_order']}
        search_params = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Most Relevant', ''),
                                        (PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'video_viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        ],
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_params,
                                         channels_args=channels_params,
                                         single_category_args=single_channel_params,
                                         single_porn_star_args=video_params,
                                         single_tag_args=single_channel_params,
                                         single_channel_args=single_channel_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='WatchMyExGf', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):

        """
        C'tor
        :param source_name: save directory
        """
        super(WatchMyExGf, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                          session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="thumbs"]/div[@class="thumb category"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="thumbs"]/div[@class="thumb sponsor"]/a',
                                                  PornCategories.CHANNEL)

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

            image_data = category.xpath('./div[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None
            title = category.attrib['title'] if 'title' in category.attrib else image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="thumb-container"]/div[@class="thumb-info"]/'
                                              'span[@class="thumb-videos"]/i')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].tail)[0]) if len(number_of_videos) > 0 else None

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        if is_sort:
            res.sort(key=lambda x: x.title)
        object_data.add_sub_objects(res)
        return res

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
        raw_data = tree.xpath('.//div[@class="width-wrap"]/ul/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], self._clear_text(x.xpath('./i')[0].tail), None)
                                                for x in raw_data])
        return links, titles, number_of_videos

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        return self._get_video_links_from_video_data3(video_data)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN):
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
        return ([int(x.attrib['data-parameters'].split(':')[-1])
                for x in tree.xpath('.//ul[@class="paginator"]/li/a')
                if 'data-parameters' in x.attrib and x.attrib['data-parameters'].split(':')[-1].isdigit()] +
                [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0])
                for x in tree.xpath('.//ul[@class="paginator"]/li/a')
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0]
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
        videos = tree.xpath('.//div[@class="thumbs list-videos"]/div[@class="thumb item"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            title = link_data[0].attrib['title'] if 'title' in link_data[0].attrib else None

            image_data = link_data[0].xpath('./div[@class="thumb-container"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'load.gif' in image:
                image = image_data[0].attrib['data-original']
            if title is None:
                title = image_data[0].attrib['alt'] if 'alt' in image_data[0].attrib else None
            flip_images = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                           for i in range(1, self.flip_number + 1)]
            video_preview = image_data[0].attrib['data-preview'] if 'data-preview' in image_data[0].attrib else None
            if title is None:
                title = link_data[0].xpath('./div[@class="thumb-description"]')
                assert len(title) == 1
                title = title[0].text

            info_data = link_data[0].xpath('./div[@class="thumb-container"]/div[@class="thumb-info"]')
            assert len(info_data) == 1
            video_length = info_data[0].xpath('./span[@class="thumb-duration"]/i')
            video_length = self._format_duration(video_length[0].tail)
            number_of_views = info_data[0].xpath('./span[@class="thumb-views"]/i')
            number_of_views = self._clear_text(number_of_views[0].tail)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=re.findall(r'\d+', link_data[0].attrib['href'])[0],
                                                  url=urljoin(self.base_url, link_data[0].attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  duration=video_length,
                                                  number_of_views=number_of_views,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        if true_object.object_type == PornCategories.SEARCH_MAIN:
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

            params['block_id'] = 'list_videos_videos_list_search_result'
            params['q'] = self._search_query
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            return super(WatchMyExGf, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                    page_filter, fetch_base_url)

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return super(AnyPorn, self)._prepare_new_search_query(query)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(WatchMyExGf, self)._version_stack + [self.__version]
