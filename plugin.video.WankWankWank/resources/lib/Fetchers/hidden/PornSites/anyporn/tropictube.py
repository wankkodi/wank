import re
from .... import urljoin, parse_qsl

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .pervertsluts import PervertSluts
from .anyporn import AnyPorn


class TropicTube(PervertSluts):
    # Some of the models we took from AnyPorn module (has thee same structure)
    flip_number = 30

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
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/c/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/sites/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/longest/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.tropictube.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        category_params = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            ],
             }
        porn_stars_params = \
            {'sort_order': [(PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            ],
             }
        search_params = \
            {'sort_order': [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                            (PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                            (PornFilterTypes.ViewsOrder, 'Most Viewed', 'video_viewed'),
                            (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                            (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                            (PornFilterTypes.FavorOrder, 'Most Favourite', 'most_favourited'),
                            ],
             }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_params,
                                         channels_args=category_params,
                                         porn_stars_args=porn_stars_params,
                                         search_args=search_params,
                                         )

    def __init__(self, source_name='TropicTube', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(TropicTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="list-videos"]/div[@class="margin-fix"]/div/a',
                                                  PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="list-videos"]/div[@class="margin-fix"]/div/a',
                                                  PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="list-albums list-models"]/div[@class="margin-fix"]/a')
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None
            title = category.xpath('./div[@class="img"]/div[@class="name"]')[0].text

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      object_type=PornCategories.PORN_STAR,
                                                      super_object=porn_star_data,
                                                      )
            res.append(sub_object_data)
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

            image_data = category.xpath('./span[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None
            title = category.attrib['title'].title() \
                if 'title' in category.attrib else image_data[0].attrib['alt'].title()

            number_of_videos = category.xpath('./span[@class="img"]/span[@class="bottom_info"]/span[@class="title"]/'
                                              'span[@class="videos_count"]')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].text)[0]) if len(number_of_videos) > 0 else None

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

            image_data = link_data[0].xpath('./span[@class="img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, self.flip_number + 1)]
            if title is None:
                title = image_data[0].attrib['alt']

            data_info = link_data[0].xpath('./span[@class="img"]/span[@class="big-info"]')
            assert len(data_info) == 1

            video_length = data_info[0].xpath('./span[@class="video_title"]/span[@class="duration"]')
            assert len(video_length) == 1
            video_length = self._format_duration(self._clear_text(video_length[0].text))

            rating = data_info[0].xpath('./span[@class="video_title"]/span[@class="rating"]')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].text)

            additional_data = data_info[0].xpath('./span[@class="thumb_info"]/em')
            assert len(additional_data) == 3
            number_of_views = int(additional_data[1].text.replace(' ', ''))
            added_before = additional_data[2].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  duration=video_length,
                                                  rating=rating,
                                                  number_of_views=number_of_views,
                                                  added_before=added_before,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
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
            return super(TropicTube, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                   page_filter, fetch_base_url)

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
        return super(TropicTube, self)._version_stack + [self.__version]
