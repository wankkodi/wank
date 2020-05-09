import re
from .... import urljoin, parse_qsl

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .anyporn import AnyPorn


class WatchMyGfTv(AnyPorn):
    # Some of the models we took from AnyPorn module (has thee same structure)
    flip_number = 11

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, ''),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, ''),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
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
        return 'https://watchmygf.tv/'

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return False

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'New', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most Viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                                       (PornFilterTypes.CommentsOrder, 'Most Favourite', 'most_favourited'),
                                       ],
                        }
        search_params = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'video_viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                                        (PornFilterTypes.FavorOrder, 'Most Favourite', 'most_favourited'),
                                        ]
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=video_params,
                                         search_args=search_params,
                                         # video_args=video_params,
                                         )

    def __init__(self, source_name='WatchMyGfTv', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):

        """
        C'tor
        :param source_name: save directory
        """
        super(WatchMyGfTv, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                          session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="menu-container"]/ul/li/a')
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=category.attrib['href'],
                                       url=urljoin(self.base_url, category.attrib['href']),
                                       title=self._clear_text(category.text),
                                       object_type=PornCategories.CATEGORY,
                                       super_object=category_data,
                                       ) for category in categories
               if category.attrib['href'].split('/')[2].split('.')[1:] == self.base_url.split('/')[2].split('.')]
        category_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        return self._get_video_links_from_video_data3(video_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return ([int(x.attrib['data-parameters'].split(':')[-1])
                for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a')
                if 'data-parameters' in x.attrib and x.attrib['data-parameters'].split(':')[-1].isdigit()] +
                [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0])
                for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a')
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
        videos = tree.xpath('.//div[@class="item-list"]/div[@class="item video"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1

            image_data = link_data[0].xpath('./div[@class="thumb-container"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            title = image_data[0].attrib['alt']
            flip_images = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                           for i in range(1, self.flip_number + 1)]
            video_preview = image_data[0].attrib['data-preview']
            if title is None:
                title = link_data[0].xpath('./div[@class="thumb-container"]/div[@class="name"]')
                assert len(title) == 1
                title = title[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=re.findall(r'\d+', link_data[0].attrib['href'])[0],
                                                  url=urljoin(self.base_url, link_data[0].attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        # New
        headers = {
            'Accept': '*.*',
            'Cache-Control': 'max-age=0',
            'Referer': page_data.url,
            # 'Host': self.host_name,
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
        if page_number > 1:
            params['from'] = str(page_number).zfill(2)
        if true_object.object_type == PornCategories.SEARCH_MAIN:
            params['block_id'] = 'list_videos_videos_list_search_result'
            params['q'] = self._search_query
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            if 'from' in params:
                params.pop('from')
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value
        elif true_object.object_type == PornCategories.CATEGORY_MAIN:
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
            page_request = self.session.get(page_data.url, headers=headers)
            return page_request
        elif true_object.object_type == PornCategories.CATEGORY:
            if page_number is None:
                page_number = 1
                params['from'] = str(page_number).zfill(2)
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = page_filter.sort_order.value
        elif true_object.object_type == PornCategories.LATEST_VIDEO:
            params['block_id'] = 'list_videos_most_recent_videos'
            params['sort_by'] = 'ctr'
        else:
            return super(WatchMyGfTv, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                    page_filter, fetch_base_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return super(AnyPorn, self)._prepare_new_search_query(query)
