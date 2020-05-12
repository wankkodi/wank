# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote_plus

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes

# Regex
import re

# Math
import math


class FakingsTV(PornFetcher):
    _quality = {'SD': 360, 'HD': 720, 'UHD': 2160}

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
            PornCategories.CATEGORY_MAIN: 'https://tv.fakings.com/en/categorias.htm',
            PornCategories.CHANNEL_MAIN: 'https://tv.fakings.com/en/series.htm',
            PornCategories.TAG_MAIN: 'https://tv.fakings.com/en/tags.htm',
            PornCategories.LATEST_VIDEO: 'https://tv.fakings.com/en/ultimos-videos.htm',
            PornCategories.TOP_RATED_VIDEO: 'https://tv.fakings.com/en/mas-votados.htm',
            PornCategories.MOST_VIEWED_VIDEO: 'https://tv.fakings.com/en/mas-vistos.htm',
            PornCategories.SEARCH_MAIN: 'https://tv.fakings.com/en/buscar/',
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
        return 'https://palmtube.com/'

    def __init__(self, source_name='FakingsTV', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(FakingsTV, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@id="listado_categorias"]/div')
        res = []
        for category in categories:
            link_data = category.xpath('./div[@class="zona-listado2b redondo"]/div[@class="zonaimagen"]/a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['title']

            number_of_videos = category.xpath('./div[@class="zona-listado2b redondo"]/div[@class="zonatexto"]/'
                                              'div[@class="zonaminif"]/div[@class="mininf"]/p')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        channels = tree.xpath('.//div[@class="item item-serie"]')
        res = []
        for channel in channels:
            link_data = channel.xpath('./div[@class="relative"]/a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            number_of_videos = channel.xpath('./div[@class="relative"]/div[@class="icobottomder"]/div/p')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            title = channel.xpath('./h2[@class="nombre enlinea"]/a')
            assert len(title) == 1
            title = title[0].text

            description = channel.xpath('./a/p[@class="txtmin"]')
            assert len(description) == 1
            description = description[0].text

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               description=description,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ))

        channel_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="zona-listado-chica redondo"]/div[@class="zonatexto"]/h2/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, None) for x in raw_objects])
        return links, titles, number_of_videos

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        videos = tmp_tree.xpath('.//div[@class="video-container"]/iframe')
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            # 'Referer': self.base_url,
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        page_request = self.session.get(videos[0].attrib['src'], headers=headers)
        tmp_tree = self.parser.parse(page_request.text)
        videos = tmp_tree.xpath('.//video/source')
        videos = sorted((VideoSource(link=x.attrib['src'],
                                     quality=self._quality[x.attrib['title']] if 'title' in x.attrib else None)
                         for x in videos),
                        key=lambda x: x.quality, reverse=True)
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type in (PornCategories.TAG_MAIN, ):
            return 1
        start_page = category_data.page_number if category_data.page_number is not None else 1
        page_request = self._get_object_request_no_exception_check(category_data) if fetched_request is None \
            else fetched_request
        if not self._check_is_available_page(category_data, page_request):
            return 1

        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        max_page = max(pages)
        if (max_page - start_page) < self._binary_search_page_threshold:
            return max_page
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 1

    def _binary_search_max_number_of_pages(self, category_data, last_available_number_of_pages):
        """
        Performs binary search in order to find the last available page.
        :param category_data: Category data.
        :param last_available_number_of_pages: Last available number of pages. Will be the pivot for our next search.
        By default is None, which mean the original pivot will be used...
        :return: Page request
        """
        left_page = 1
        right_page = self.max_pages
        page = last_available_number_of_pages if last_available_number_of_pages is not None \
            else int(math.ceil((right_page + left_page) / 2))
        while 1:
            if right_page == left_page:
                return left_page

            page_request = self._get_object_request_no_exception_check(category_data, override_page_number=page)
            if self._check_is_available_page(category_data, page_request):
                tree = self.parser.parse(page_request.text)
                pages = self._get_available_pages_from_tree(tree)
                if len(pages) > 0:
                    # We still have a margin to go...
                    left_page = page + 1
                else:
                    right_page = page
            else:
                # We moved too far...
                right_page = page - 1
            page = int(math.floor((right_page + left_page) / 2))

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        current_url = tree.xpath('.//link[@rel="canonical"]')
        assert len(current_url) == 1
        current_page_number = re.findall(r'(\d+)(?:.htm)', current_url[0].attrib['href'])
        current_page_number = int(current_page_number[0]) if len(current_page_number) > 0 else 1
        is_next_page = len(tree.xpath('.//form[@id="paginacion_scroll"]/input')) > 0
        # next_page = current_page_number + 1 if is_next_page else current_page_number
        return [current_page_number + 1] if is_next_page else []

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="zona-listado2b"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./div[@class="zonaimagen"]/a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt'] if 'alt' in image_data[0].attrib else image_data[0].attrib['title']

            channel_data = video_tree_data.xpath('./div[@class="zonatexto"]/p/a')
            assert len(channel_data) == 1
            additional_info = {'Uploader': channel_data[0].text, 'link': channel_data[0].attrib['href']}

            video_info = video_tree_data.xpath('./div[@class="zonatexto"]/div[@class="zonaminif"]/div/p')
            assert len(video_info) == 2
            number_of_views = video_info[0]
            rating = video_info[1]

            video_length = video_tree_data.xpath('./div[@class="zonaimagen"]/div[@class="icobottomder"]/div/p')
            video_length = self._format_duration(video_length[0].text) if len(video_length) > 0 else None

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_views=number_of_views,
                                                  rating=rating,
                                                  additional_data=additional_info,
                                                  duration=video_length,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            # 'Referer': self.base_url,
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if true_object.object_type == PornCategories.VIDEO:
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request

        suffix_test = re.findall(r'\d+\.html', fetch_base_url)
        if len(suffix_test) == 0:
            fetch_base_url = re.sub(r'\.htm', '/1.htm', fetch_base_url)
        if page_number is not None and page_number != 1:
            fetch_base_url = re.sub(r'\d+\.htm', '{p}.htm'.format(p=page_number), fetch_base_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}.htm'.format(q=quote_plus(query.replace(' ', '-')))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(FakingsTV, self)._version_stack + [self.__version]
