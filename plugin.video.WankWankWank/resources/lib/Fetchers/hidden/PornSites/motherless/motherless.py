# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


class MotherLess(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://motherless.com/',
            PornCategories.LATEST_VIDEO: 'https://motherless.com/videos/recent',
            PornCategories.MOST_VIEWED_VIDEO: 'https://motherless.com/videos/viewed',
            PornCategories.FAVORITE_VIDEO: 'https://motherless.com/videos/favorited',
            PornCategories.POPULAR_VIDEO: 'https://motherless.com/videos/popular',
            PornCategories.MOST_DISCUSSED_VIDEO: 'https://motherless.com/videos/commented',
            PornCategories.SEARCH_MAIN: 'https://motherless.com/term/videos/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://motherless.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        categories_filters = {'general_filters': ((PornFilterTypes.StraightType, 'Straight', 'straight'),
                                                  (PornFilterTypes.GayType, 'Gay', 'gay'),
                                                  (PornFilterTypes.ShemaleType, 'Shemale', 'shemale'),
                                                  (PornFilterTypes.FunnyType, 'Funny', 'funny'),
                                                  (PornFilterTypes.ExtremeType, 'Extreme', 'extreme'),
                                                  ),
                              }
        search_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Relevancy', 'relevance'),
                                         (PornFilterTypes.DateOrder, 'Date', 'date'),
                                         ],
                          'period_filters': [(PornFilterTypes.AllDate, 'All time', '0'),
                                             (PornFilterTypes.OneDate, 'Past 24 Hours', '1'),
                                             (PornFilterTypes.TwoDate, 'Past Week', '2'),
                                             (PornFilterTypes.ThreeDate, 'Past Month', '3'),
                                             (PornFilterTypes.FourDate, 'Older than a Month', '4'),
                                             ],
                          'length_filters': [(PornFilterTypes.AllLength, 'All lengths', '0'),
                                             (PornFilterTypes.OneLength, 'Short Videos', '1'),
                                             (PornFilterTypes.TwoLength, 'Medium Videos', '2'),
                                             (PornFilterTypes.ThreeLength, 'Long Videos', '3'),
                                             (PornFilterTypes.FourLength, 'Extra Long Videos', '4'),
                                             ],
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=categories_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='MotherLess', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(MotherLess, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        main_category = [x for x in tree.xpath('.//div[@class="menu-categories-tab"]')]
        filter_value = self._video_filters[PornCategories.CATEGORY_MAIN].current_filters.general.value
        if filter_value is not None:
            main_category = [x for x in main_category
                             if 'data-orientation' in x.attrib and x.attrib['data-orientation'] == filter_value]
        categories = []
        for x in main_category:
            categories.extend(x.xpath('.//ul[@class="list-unstyled list-inline"]/li/a'))
        res = []
        for category in categories:
            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=category.text,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        script = [x for x in tmp_tree.xpath('.//script/text()') if '__fileurl ' in x]
        video_links = [VideoSource(link=x) for x in re.findall(r'(?:__fileurl = \')(.*)(?:\';)', script[0])]
        return VideoNode(video_sources=video_links)

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
        pages = tree.xpath('.//div[@class="pagination_link awn-ignore"]/*/text()')
        return [int(x) for x in pages if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="content-inner"]//div[@class="thumb-container video"]/div')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            img = video_tree_data.xpath('./a/img[@class="static"]/@src')
            assert len(img) == 1
            img = urljoin(page_data.url, img[0])

            title = (video_tree_data.xpath('./div[@class="captions"]/h2[@class="caption title"]') +
                     video_tree_data.xpath('./div[@class="captions"]/a[@class="caption title pop plain"]'))
            assert len(title) >= 1
            title = title[0].text

            video_length = (video_tree_data.xpath('./div[@class="captions"]/div[@class="caption left"]') +
                            link_data[0].xpath('./span[@class="size"]'))
            assert len(video_length) == 1
            video_length = self._format_duration(video_length[0].text)

            number_of_views = video_tree_data.xpath('./div[@class="captions"]/div[@class="caption right"]')
            if len(number_of_views) >= 1:
                number_of_views = None
            else:
                number_of_views = video_tree_data.xpath('./div[@class="captions"]/div[@class="caption left misc"]/'
                                                        'span[@class="hits"]/i')
                assert len(number_of_views) >= 1
                number_of_views = self._clear_text(number_of_views[0].tail)

            uploader = (video_tree_data.xpath('./div[@class="captions"]/a[@class="caption left"]') +
                        video_tree_data.xpath('./div[@class="captions"]/div[@class="caption left misc"]/a'))
            assert len(uploader) >= 1
            additional_data = {'uploader': {'url': urljoin(self.base_url, uploader[0].attrib['href']),
                                            'name': self._clear_text(uploader[0].text)}}

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=img,
                                                  duration=video_length,
                                                  number_of_views=number_of_views,
                                                  added_before=number_of_views,
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')
        if true_object.object_type in (PornCategories.CATEGORY, ):
            if split_url[-1] != 'videos':
                split_url.append('videos')
        elif true_object.object_type in (PornCategories.SEARCH_MAIN, ):
            params['type'] = ['videos']

        if page_number is not None and page_number != 1:
            params['page'] = [page_data.page_number]

        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            params['sort'] = [page_filter.sort_order.value]
        if page_filter.period.value is not None:
            params['range'] = [page_filter.period.value]
        if page_filter.length.value is not None:
            params['size'] = [page_filter.length.value]

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            # 'Referer': self.base_url,
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
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
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(MotherLess, self)._version_stack + [self.__version]
