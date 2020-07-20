# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter


class CumLouder(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.cumlouder.com/categories/',
            PornCategories.CHANNEL_MAIN: 'https://www.cumlouder.com/channels/',
            PornCategories.PORN_STAR_MAIN: 'https://www.cumlouder.com/girls/',
            PornCategories.LATEST_VIDEO: 'https://www.cumlouder.com/porn/',
            PornCategories.SEARCH_MAIN: 'https://www.cumlouder.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
        }

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 5000

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.cumlouder.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        channel_params = {'sort_order': [(PornFilterTypes.RatingOrder, 'Rate', 'r'),
                                         (PornFilterTypes.NumberOfVideosOrder, 'Scenes', 's'),
                                         ],
                          }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         channels_args=channel_params,
                                         porn_stars_args=channel_params,
                                         )

    def __init__(self, source_name='CumLouder', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(CumLouder, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/76.0.3809.100 Safari/537.36'
        self.session.headers['User-Agent'] = self.user_agent

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        xpath = './/div[@class="medida"]/a[@class="muestra-escena muestra-categoria show-tag"]'
        return self._update_available_base_object(category_data, xpath, PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        xpath = './/div[@class="medida"]/a[@class="muestra-escena muestra-canales show-channel"]'
        return self._update_available_base_object(channel_data, xpath, PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        xpath = './/div[@class="medida"]/a[@class="muestra-escena muestra-pornostar show-girl"]'
        return self._update_available_base_object(porn_star_data, xpath, PornCategories.PORN_STAR)

    def _update_available_base_object(self, object_data, xpath, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)

        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] \
                if (image_data[0].attrib['src'] != "/css/css-cumlouder/images/loading-placeholder.gif" and
                    'data:image' not in image_data[0].attrib['src']) \
                else image_data[0].attrib['data-src']
            image = urljoin(self.base_url, image)

            title = category.xpath('./h2/span[@class="ico-h2 sprite"]')
            if len(title) == 1:
                title = self._clear_text(title[0].tail)
            else:
                title = category.xpath('./h2/span[@class="categoria"]')
                assert len(title) == 1
                title = self._clear_text(title[0].text)

            number_of_videos = category.xpath('./span[@class="box-fecha-mins"]/span[@class="videos"]/'
                                              'span[@class="ico-videos sprite"]')
            if len(number_of_videos) == 1:
                number_of_videos = self._clear_text(number_of_videos[0].tail)
                number_of_videos = re.findall(r'\d+', number_of_videos)[0]
            else:
                number_of_videos = category.xpath('./h2/span[@class="cantidad"]')
                number_of_videos = self._clear_text(number_of_videos[0].text)
                number_of_videos = re.findall(r'\d+', number_of_videos)[0]

            rating = category.xpath('./span[@class="box-fecha-mins"]/span[@class="puntaje"]/'
                                    'span[@class="ico-videos sprite"]')
            rating = self._clear_text(number_of_videos[0].tail) if len(rating) == 1 else None

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=category.attrib['href'],
                                                      url=urljoin(object_data.url, category.attrib['href']),
                                                      image_link=image,
                                                      title=title,
                                                      rating=rating,
                                                      number_of_videos=int(number_of_videos),
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
        raw_links = [x for x in tmp_tree.xpath('.//script/text()') if 'flashPlayerEvents' in x]
        video_links = [VideoSource(link=urljoin(video_data.url, re.sub(r'&amp;', '&', x)))
                       for x in re.findall(r'(?:var urlVideo = \')(.*)(?:\';)', raw_links[0])]
        request_headers = {
            'Accept-Encoding': 'identity;q=1, *;q=0',
            'Range': 'bytes=0-',
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'no-cors',
            'User-Agent': self.user_agent
        }
        return VideoNode(video_sources=video_links, headers=request_headers)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # At first we try to check whether we have max page from the initial page.
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        if category_data.page_number is not None:
            max_page = max(pages)
            if max_page - category_data.page_number < self._binary_search_page_threshold:
                return max_page

        # We perform binary search
        return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//ul[@class="pagination"]/li/*/text()') if x.isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 7

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)

        tree = self.parser.parse(page_request.text)
        videos = (tree.xpath('.//body/div[@class="listado-escenas"]/div[@class="medida"]/a[@class="muestra-escena"]') +
                  tree.xpath('.//body/div[@class="listado-escenas listado-busqueda"]/div[@class="medida"]/'
                             'a[@class="muestra-escena"]')
                  )
        res = []
        for video_tree_data in videos:

            image_data = video_tree_data.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] \
                if (image_data[0].attrib['src'] != "/css/css-cumlouder/images/loading-placeholder.gif" and
                    'data:image' not in image_data[0].attrib['src']) \
                else image_data[0].attrib['data-src']
            image = urljoin(self.base_url, image)
            title = image_data[0].attrib['alt']

            number_of_views = video_tree_data.xpath('./span[@class="box-fecha-mins"]/span[@class="vistas"]/'
                                                    'span[@class="ico-vistas sprite"]')
            number_of_views = self._clear_text(number_of_views[0].tail) if len(number_of_views) == 1 else None

            added_before = video_tree_data.xpath('./span[@class="box-fecha-mins"]/span[@class="fecha"]/'
                                                 'span[@class="ico-fecha sprite"]')
            added_before = self._clear_text(added_before[0].tail) if len(added_before) == 1 else None

            video_length = video_tree_data.xpath('./span[@class="minutos"]/span[@class="ico-minutos sprite"]')
            video_length = self._clear_text(video_length[0].tail) if len(video_length) == 1 else None

            is_hd = video_tree_data.xpath('./span[@class="hd sprite"]')
            is_hd = len(is_hd) > 0

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['href'],
                                                  url=urljoin(self.base_url, video_tree_data.attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_views=number_of_views,
                                                  added_before=added_before,
                                                  duration=self._format_duration(video_length),
                                                  is_hd=is_hd,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw number, i.e. '7m:58s'.
        :return:
        """
        raw_duration, suffix = raw_duration.split(' ')
        split_duration = [int(x) for x in raw_duration.split(':')]
        assert len(split_duration) == 2
        if suffix == 'h':
            return split_duration[0] * 3600 + split_duration[1] * 60
        elif suffix in ('m', 'min'):
            return split_duration[0] * 60 + split_duration[1]
        else:
            raise RuntimeError('Unknown time suffix {s}!'.format(s=suffix))

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        if true_object.object_type in (PornCategories.CHANNEL_MAIN, PornCategories.PORN_STAR_MAIN):
            if page_number is None:
                page_number = 1
            fetch_base_url += '{p}/'.format(p=page_number)
            params['orderBy'] = [page_filter.sort_order.value]
        else:
            if page_number is not None and page_number > 1:
                if true_object.object_type == PornCategories.LATEST_VIDEO:
                    fetch_base_url = self.base_url + '{p}/'.format(p=page_number)
                elif true_object.object_type == PornCategories.SEARCH_MAIN:
                    fetch_base_url += '{p}'.format(p=page_number)
                else:
                    fetch_base_url += '{p}/'.format(p=page_number)

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            # 'Referer': self.base_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)

        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote(query))

    @property
    def __version(self):
        return 1

    @property
    def _version_stack(self):
        return super(CumLouder, self)._version_stack + [self.__version]
