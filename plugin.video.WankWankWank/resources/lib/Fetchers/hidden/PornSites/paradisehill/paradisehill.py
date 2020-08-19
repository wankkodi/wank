# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote, parse_qsl

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


class ParadiseHill(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://en.paradisehill.cc/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://en.paradisehill.cc/actors/',
            PornCategories.CHANNEL_MAIN: 'https://en.paradisehill.cc/studios/',
            PornCategories.POPULAR_VIDEO: 'https://en.paradisehill.cc/popular/',
            PornCategories.LATEST_VIDEO: 'https://en.paradisehill.cc/all/?sort=created_at',
            PornCategories.SEARCH_MAIN: 'https://en.paradisehill.cc/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://en.paradisehill.cc/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        categories_filters = {'sort_order': ((PornFilterTypes.AlphabeticOrder, 'From A to Z', 'sort=title_en'),
                                             (PornFilterTypes.RatingOrder, 'By number of Likes', 'sort=by_likes'),
                                             ),
                              }
        porn_stars_filters = {'sort_order': ((PornFilterTypes.RatingOrder, 'By number of Likes', 'sort=by_likes'),
                                             (PornFilterTypes.AlphabeticOrder, 'From A to Z', 'sort=name'),
                                             ),
                              }
        channels_filters = {'sort_order': ((PornFilterTypes.RatingOrder, 'Number of Likes', 'sort=by_likes'),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'sort=by_films'),
                                           (PornFilterTypes.AlphabeticOrder, 'From A to Z', 'sort=title'),
                                           ),
                            }
        single_category_filters = {'sort_order': ((PornFilterTypes.DateAddedOrder, 'By Date Added', 'sort=created_at'),
                                                  (PornFilterTypes.DateOrder, 'By Release Date', 'sort=release'),
                                                  (PornFilterTypes.AlphabeticOrder, 'From A to Z', 'sort=title_en'),
                                                  ),
                                   }
        video_filters = {'sort_order':  ((PornFilterTypes.RatingOrder, 'By number of Likes', 'sort=by_likes'),
                                         (PornFilterTypes.ViewsOrder, 'By number of Views', 'sort=by_views'),
                                         (PornFilterTypes.CommentsOrder, 'By number of Comments', 'sort=by_comment'),
                                         ),
                         'period_filters': ((PornFilterTypes.AllDate, 'All time', 'filter=all'),
                                            (PornFilterTypes.OneDate, 'Last Year', 'filter=year'),
                                            (PornFilterTypes.TwoDate, 'Last Month', 'filter=month'),
                                            (PornFilterTypes.ThreeDate, 'Last Week', 'filter=week'),
                                            (PornFilterTypes.FourDate, 'Last Day', 'filter=day'),
                                            ),
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=categories_filters,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_category_args=single_category_filters,
                                         single_porn_star_args=single_category_filters,
                                         single_channel_args=single_category_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='ParadiseHill', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(ParadiseHill, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                           session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_object(category_data, PornCategories.CATEGORY)

    def _update_available_porn_stars(self, pornstar_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_object(pornstar_data, PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channels.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_object(channel_data, PornCategories.CHANNEL)

    def _update_available_object(self, object_data, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        tags = tree.xpath('.//div[@class="item"]/a')
        res = []
        for tag in tags:
            link = tag.attrib['href']
            title = tag.xpath('./span/div/span')[0].text
            image = urljoin(self.base_url, tag.xpath('./picture/img')[0].attrib['src'])
            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=self._clear_text(title)
                                                      if tag.text is not None else None,
                                                      image_link=image,
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
        videos = tmp_tree.xpath('.//div[@class="fp-playlist"]/a')
        videos = [VideoSource(link=urljoin(self.base_url, x.attrib['href']), title=x.text) for x in videos]
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type == PornCategories.CATEGORY_MAIN:
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
        return [int(x) for x in tree.xpath('.//ul[@class="pagination"]/li/*/@data-page') if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="item list-film-item"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            image = urljoin(self.base_url, link_data[0].xpath('./picture/img')[0].attrib['src'])

            title = link_data[0].xpath('span/div[1]/span')
            assert len(title) == 1
            title = title[0].text

            preview_image = link_data[0].xpath('span/div[2]/picture/img')
            assert len(preview_image) == 1
            flip_images = [urljoin(self.base_url, preview_image[0].attrib['src'])]

            genre = link_data[0].xpath('span/div[3]/span')
            assert len(genre) == 1
            additional_info = {'genre': genre[0].text}

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  additional_data=additional_info,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            params.update(parse_qsl(page_filter.sort_order.value))

        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            if true_object.object_type not in (PornCategories.LATEST_VIDEO, ):
                params.update(parse_qsl(page_filter.period.value))

        if page_number is not None and page_number != 1:
            params['page'] = page_number

        params_sort_order = {'filter': 0, 'sort': 1, 'pattern': 2, 'what': 3, 'page': 4}
        params = sorted(((k, v) for k, v in params.items()), key=lambda x: params_sort_order[x[0]])

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
        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?pattern={q}&what=1'.format(q=quote(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(ParadiseHill, self)._version_stack + [self.__version]
