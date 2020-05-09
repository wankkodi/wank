# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher
from ....tools.external_fetchers import ExternalFetcher

# Internet tools
from .... import urljoin

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ....catalogs.porn_catalog import PornCategories


class JoysPorn(PornFetcher):
    number_of_flip_images = 20

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.joysporn.com/categories.html',
            PornCategories.LATEST_VIDEO: 'https://www.joysporn.com/latest-updates/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.joysporn.com/most-popular/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.joysporn.com/top-rated/',
            PornCategories.SEARCH_MAIN: 'https://www.joysporn.com/',
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
        return 'https://www.joysporn.com/'

    def __init__(self, source_name='JoysPorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(JoysPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)
        self.external_fetchers = ExternalFetcher(session=self.session, user_agent=self.user_agent,
                                                 parser=self.parser)
        self.search_data = {}
        self._first_run = True

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="porncategories"]/a')
        res = []
        for category in categories:
            image = category.xpath('./img')
            assert len(image) == 1

            title = category.xpath('./h2')
            assert len(title) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=self._clear_text(title[0].text),
                                                  image_link=image[0].attrib['src'],
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
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
        video_raw_data = self.external_fetchers.get_video_link_from_fapmedia(video_data.url)
        # video_raw_data = self.external_fetchers.get_video_link_from_cdna(video_url)
        video_links = sorted((VideoSource(link=x[0], resolution=x[1]) for x in video_raw_data),
                             key=lambda x: x.resolution, reverse=True)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Cache-Control': 'max-age=0',
            'Referer': video_data.url,
            'Sec-Fetch-Desy': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': 'none',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        return VideoNode(video_sources=video_links, headers=headers)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        Finds the number of pages for the given parsed object.
        :param tree: Page tree.
        :return: number of pages (int).
        """
        pages = tree.xpath('.//div[@class="navigation"]/*')
        pages = [int(x.text) for x in pages if x.text.isdigit()]
        return pages

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@id="video_preview"]/div[@class="video_c"]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1

            image_data = video_tree_data.xpath('./div[@class="vidimage"]/a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            flip_images = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                           for i in range(1, self.number_of_flip_images+1)]

            video_length = video_tree_data.xpath('./div[@class="vidimage"]/div[@class="vidduration"]')
            assert len(video_length) == 1

            rating = video_tree_data.xpath('./div[@class="vidimage"]/div[@class="like"]')
            assert len(rating) == 1

            number_of_views = video_tree_data.xpath('./div[@class="vidimage"]/div[@class="views"]')
            assert len(number_of_views) == 1

            title = video_tree_data.xpath('./a/h2')
            assert len(title) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=title[0].text,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  duration=self._format_duration(video_length[0].text),
                                                  rating=rating[0].text,
                                                  number_of_views=number_of_views[0].text,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        if true_object.object_type == PornCategories.SEARCH_MAIN:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;'
                          'q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Cache-Control': 'max-age=0',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': self.host_name,
                'Origin': page_data.url,
                'Referer': page_data.url,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }
            data = self.search_data
            page_request = self.session.post(fetch_base_url, headers=headers, params=params, data=data)
        else:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3',
                'Cache-Control': 'max-age=0',
                'Host': self.host_name,
                'Referer': page_data.url,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }
            if self._first_run is True:
                self.session.get(self.base_url, headers=headers, params=params)
                self._first_run = False

            split_url = fetch_base_url.split('/')
            if page_number is not None and page_number != 1:
                split_url.insert(-1, 'page')
                split_url.insert(-1, str(page_number))
            fetch_base_url = '/'.join(split_url)
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self.search_data = {'story': [query],
                            'do': 'search',
                            'subaction': 'search',
                            }
        return self.object_urls[PornCategories.SEARCH_MAIN]
