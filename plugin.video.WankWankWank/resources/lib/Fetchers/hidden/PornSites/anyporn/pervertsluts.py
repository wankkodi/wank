# import re

# Internet tools
from .... import urljoin, quote_plus, parse_qsl

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

from .anyporn import AnyPorn


class PervertSluts(AnyPorn):
    # Some of the models we took from AnyPorn module (has thee same structure)
    flip_number = 11

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://pervertslut.com/categories/',
            PornCategories.TAG_MAIN: 'https://pervertslut.com/tags/',
            PornCategories.CHANNEL_MAIN: 'https://pervertslut.com/channels/',
            PornCategories.LATEST_VIDEO: 'https://pervertslut.com/latest-updates/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://pervertslut.com/most-popular/',
            PornCategories.TOP_RATED_VIDEO: 'https://pervertslut.com/top-rated/',
            PornCategories.SEARCH_MAIN: 'https://pervertslut.com/search/',
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
        return 'https://pervertslut.com/'

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
        general_filter_params = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', ''),
                                                     (PornFilterTypes.GayType, 'Gay', 'gay'),
                                                     (PornFilterTypes.ShemaleType, 'Shemale', 'shemale'),
                                                     ],
                                 }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       ],
                        }
        search_params = video_params.copy()
        search_params['sort_order'] = [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                                       (PornFilterTypes.DateOrder, 'Recent videos', 'most-recent'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                       (PornFilterTypes.LengthOrder, 'By duration', 'long-movies'),
                                       ]

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='PervertSluts', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PervertSluts, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                           session_id)

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available channels.
        :return: Object of all available shows (JSON).
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        page_request = self.session.get(tag_data.url, headers=headers)
        tree = self.parser.parse(page_request.text)
        tags = tree.xpath('.//div[@class="list-tags"]/div[@class="margin-fix"]/ul/li/a')
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x.attrib['href'],
                                       url=urljoin(self.base_url, x.attrib['href']),
                                       title=x.text,
                                       object_type=PornCategories.TAG,
                                       super_object=tag_data,
                                       ) for x in tags]
        tag_data.add_sub_objects(res)
        return res

    def _add_tag_sub_pages(self, tag_data, sub_object_type):
        """
        Adds sub pages to the tags according to the first letter of the title. Stores all the tags to the proper pages.
        Notice that the current method contradicts with the _get_tag_properties method, thus you must use either of
        them, according to the way you want to implement the parsing (Use the _make_tag_pages_by_letter property to
        indicate which of the methods you are about to use...)
        :param tag_data: Tag data.
        :param sub_object_type: Object types of the sub pages (either Page or VideoPage).
        :return:
        """
        return super(AnyPorn, self)._add_tag_sub_pages(tag_data, sub_object_type)

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
        """
        return self._get_video_links_from_video_data2(video_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        xpath = './/div[@class="pagination-holder"]/ul/li/a'
        return ([int(x.attrib['data-parameters'].split(':')[-1])
                for x in tree.xpath(xpath)
                if 'data-parameters' in x.attrib and x.attrib['data-parameters'].split(':')[-1].isdigit()] +
                [int(re.findall(r'(?:from.*?:)(\d+)', x.attrib['href'])[0])
                for x in tree.xpath(xpath)
                if 'href' in x.attrib and len(re.findall(r'(?:from.*?:)(\d+)', x.attrib['href'])) > 0]
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
        videos = tree.xpath('.//div[@class="list-videos"]/div[@class="margin-fix"]/div[@class="item  "]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1

            image = video_tree_data.xpath('./a/div[@class="img"]/img')
            assert len(image) == 1

            is_hd = video_tree_data.xpath('./a/div[@class="img"]/div[@class="hdpng"]')

            video_length = video_tree_data.xpath('./a/div[@class="img"]/div[@class="duration-overlay"]')
            assert len(video_length) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=re.findall(r'\d+', link[0].attrib['href'])[0],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=image[0].attrib['alt'],
                                                  image_link=urljoin(self.base_url, image[0].attrib['src']),
                                                  duration=self._format_duration(video_length[0].text),
                                                  is_hd=len(is_hd) > 0,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        if true_object.object_type in (PornCategories.TAG, PornCategories.SEARCH_MAIN):
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
            params['from'] = str(page_number).zfill(2)

            if true_object.object_type == PornCategories.TAG:
                params['block_id'] = 'list_videos_common_videos_list'
            elif true_object.object_type == PornCategories.SEARCH_MAIN:
                params['block_id'] = 'list_videos_videos_list_search_result'
                params['category_ids'] = ''
                params['sort_by'] = page_filter.sort_order.value
                if 'from' in params:
                    params.pop('from')
                params['from_videos'] = str(page_number).zfill(2)
                params['from_albums'] = str(page_number).zfill(2)
                params['q'] = self._search_query if true_object.object_type == PornCategories.SEARCH_MAIN \
                    else fetch_base_url.split('/')[-2]

            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            return super(PervertSluts, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                     page_filter, fetch_base_url)

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query))
