# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote_plus

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ....catalogs.porn_catalog import PornCategories


class EroProfile(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.eroprofile.com/m/videos/home',
            PornCategories.LATEST_VIDEO: 'https://www.eroprofile.com/m/videos/search?niche=all-sf',
            PornCategories.POPULAR_VIDEO: 'https://www.eroprofile.com/m/videos/popular',
            PornCategories.SEARCH_MAIN: 'https://www.eroprofile.com/m/videos/search',
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
        return 'https://www.eroprofile.com/'

    def __init__(self, source_name='EroProfile', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(EroProfile, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@id="divVideoListNiches"]/div[@class="formGroup"]/a')
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=category.attrib['href'],
                                       url=urljoin(self.base_url, category.attrib['href']),
                                       title=category.text,
                                       object_type=PornCategories.CATEGORY,
                                       super_object=category_data,
                                       ) for category in categories]
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
        videos = tmp_tree.xpath('.//video/source/@src')
        videos = [VideoSource(link=urljoin(video_data.url, x)) for x in videos]
        return VideoNode(video_sources=videos)

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
        return max(pages) if len(pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(re.findall(r'(?:pnum=)(\d+)', x)[0])
                for x in tree.xpath('.//div[@id="divVideoListPageNav"]/div/a/@href')
                if len(re.findall(r'(?:pnum=)(\d+)', x)) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="videoGrid"]/div[@class="video"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./div[@class="videoCnt"]/a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = video_tree_data.xpath('./div[@class="videoCnt"]/a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            video_length = video_tree_data.xpath('./div[@class="videoCnt"]/a/div[@class="videoDur"]/text()')
            assert len(video_length) == 1

            title = video_tree_data.xpath('./div[@class="videoTtl"]')
            assert len(title) == 1
            title = title[0].attrib['title'] if 'title' in title[0].attrib else title[0].text

            category = video_tree_data.xpath('./div[@class="videoNiche"]/a')
            assert len(category) == 1

            added_before = video_tree_data.xpath('./div[@class="videoNiche fsSmall"]/text()')
            assert len(added_before) == 1

            uploader = video_tree_data.xpath('./div[@class="videoNiche fsSmall"]/a')
            assert len(uploader) == 1
            additional_data = {'category': category[0].text,
                               'category_url': urljoin(page_data.url, category[0].attrib['href']),
                               'uploader': uploader[0].text,
                               'uploader_url': urljoin(page_data.url, uploader[0].attrib['href'])}

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  duration=self._format_duration(video_length[0]),
                                                  added_before=added_before[0],
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
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
        if page_number is not None and page_number != 1:
            params['pnum'] = page_number
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?niche=&text={q}/'.format(q=quote_plus(query))
