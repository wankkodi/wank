# -*- coding: UTF-8 -*-
from ....tools.external_fetchers import ExternalFetcher

# Internet tools
from .... import urlparse, urljoin, quote_plus, parse_qsl

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

from .yespornplease import YesPornPlease


class YesPornPleaseX(YesPornPlease):
    max_flip_images = 100

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, ''),
        }

    @property
    def _default_sort_by(self):
        return {}

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://yespornpleasex.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'filter=latest'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'filter=most-viewed'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'filter=longest'),
                                        (PornFilterTypes.PopularityOrder, 'Popular', 'filter=popular'),
                                        (PornFilterTypes.RandomOrder, 'Random', 'filter=random'),
                                        ],
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=video_filters,
                                         search_args=video_filters,
                                         )

    def __init__(self, source_name='YesPornPleaseX', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(YesPornPleaseX, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                             session_id)
        # self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
        #                   'Chrome/76.0.3809.100 Safari/537.36'
        self.external_fetchers = ExternalFetcher(session=self.session, user_agent=self.user_agent,
                                                 parser=self.parser)
        # self.scroll_json = urljoin(self.base_url, '/ajax/scroll_load')

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = [x for x in tree.xpath('.//article') if 'id' in x.attrib]
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title'] if 'title' in link_data[0].attrib \
                else link_data[0].attrib['data-title']

            image_data = link_data[0].xpath('./div[@class="post-thumbnail"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  image_link=image,
                                                  title=title,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)

        category_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//main/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text,
                                                 int(re.findall(r'(\d+)(?: item)', x.attrib['aria-label'])[0]))
                                                for x in raw_data])
        return links, titles, number_of_videos

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN):
            return 1
        else:
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
        return [int(x) for x in tree.xpath('.//div[@class="pagination"]/ul/li/*/text()') if x.isdigit()]

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        new_video_url = tmp_tree.xpath('.//video/source')
        if len(new_video_url) > 0 and urlparse(new_video_url[0].attrib['src']).hostname == self.host_name:
            video_links = [VideoSource(link=x.attrib['src']) for x in new_video_url]
        else:
            return super(YesPornPleaseX, self)._get_video_links_from_video_data_no_exception_check(video_data)

        video_links.sort(key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=video_links)

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        categories = [x for x in tree.xpath('.//article') if 'id' in x.attrib]
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title'] if 'title' in link_data[0].attrib \
                else link_data[0].attrib['data-title']

            image_section_data = link_data[0].xpath('./div[@class="post-thumbnail "]')
            if len(image_section_data) == 1:
                image_data = image_section_data[0].xpath('.//img')
                assert len(image_data) == 1
                image = image_data[0].attrib['src'] \
                    if 'src' in image_data[0].attrib and 'data:image' not in image_data[0].attrib['src'] \
                    else image_data[0].attrib['data-src']
                video_preview = None
            else:
                image_section_data = link_data[0].xpath('./div[@class="post-thumbnail video-with-trailer"]')
                image_data = image_section_data[0].xpath('./video')
                image = image_data[0].attrib['poster']
                video_preview_data = image_data[0].xpath('./source')
                assert len(video_preview_data) == 1
                video_preview = video_preview_data[0].attrib['src']

            is_hd = image_section_data[0].xpath('./span[@class="hd-video-left"]')
            is_hd = len(is_hd) == 1 and is_hd[0].text == 'HD'

            video_length = image_section_data[0].xpath('./span[@class="duration"]/i')
            assert len(video_length) == 1
            video_length = self._format_duration(video_length[0].tail)

            res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                obj_id=link,
                                                url=urljoin(self.base_url, link),
                                                title=title,
                                                image_link=image,
                                                preview_video_link=video_preview,
                                                is_hd=is_hd,
                                                duration=video_length,
                                                object_type=PornCategories.VIDEO,
                                                super_object=page_data,
                                                ))
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
            'Host': self.host_name,
            # 'Referer': self.category_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_number is not None and page_number != 1:
            split_url.insert(-1, 'page')
            split_url.insert(-1, str(page_data.page_number))

        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            params.update(parse_qsl(page_filter.sort_order.value))
        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?s={q}'.format(q=quote_plus(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(YesPornPleaseX, self)._version_stack + [self.__version]
