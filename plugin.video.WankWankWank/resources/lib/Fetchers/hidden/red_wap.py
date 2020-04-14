# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError

# Internet tools
from .. import urlparse, urljoin, quote

# Generator id
from ..id_generator import IdGenerator

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories


class RedWap(PornFetcher):
    category_url = 'https://www.redwap2.com/'
    host_name = urlparse(category_url).hostname

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.redwap2.com/',
            PornCategories.LATEST_VIDEO: 'https://www.redwap2.com/latest/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.redwap2.com/most-viewed/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.redwap2.com/top-rated/',
            PornCategories.SEARCH_MAIN: 'https://www.redwap2.com/to/',
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
        return 'https://www.redwap2.com/'

    def __init__(self, source_name='RedWap', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(RedWap, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@id="menul"]/a')
        res = []
        for category in categories:
            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=(self._clear_text(category.text)
                                                         if category.text is not None else None),
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_data.url, headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)
        # new_video_data = json.loads([x for x in tmp_tree.xpath('.//script/text()') if 'gvideo' in x][0])
        # video_suffix = video_suffix = urlparse(tmp_data['contentUrl']).path

        videos = [VideoSource(link=x) for x in tmp_tree.xpath('.//source/@src')]
        assert len(videos) > 0
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        try:
            page_request = self.get_object_request(category_data, send_error=False) if fetched_request is None \
                else fetched_request
        except PornFetchUrlError:
            return 1
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return ([int(x) for x in tree.xpath('.//div[@class="pagination"]/div[@class="block_content"]/span/a/text()')
                if x.isdigit()] +
                [int(x) for x in tree.xpath('.//div[@class="pagination"]/div[@class="block_content"]/span/text()')
                 if x.isdigit()]
                )

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="item"]/div[@class="inner"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./div[@class="image"]/a')
            assert len(link_data) == 1

            image = video_tree_data.xpath('./div[@class="image"]/a/img/@src')
            assert len(image) == 1

            video_length = video_tree_data.xpath('./div[@class="image"]/div[@class="length"]/text()')
            assert len(video_length) == 1

            pos_rating = video_tree_data.xpath('./div[@class="image"]/div[@class="likes"]/text()')
            assert len(pos_rating) == 1
            neg_rating = video_tree_data.xpath('./div[@class="image"]/div[@class="dislikes"]/text()')
            assert len(neg_rating) == 1

            title = video_tree_data.xpath('./div[@class="info"]/a/text()')
            assert len(title) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(self.base_url, link_data[0].attrib['href']),
                                                  title=title[0],
                                                  image_link=image[0],
                                                  duration=self._format_duration(video_length[0]),
                                                  pos_rating=pos_rating[0],
                                                  neg_rating=neg_rating[0],
                                                  rating=int(pos_rating[0]) / int(neg_rating[0]),
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
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
        if page_data.page_number is not None and page_data.page_number != 1:
            params['page'] = page_data.page_number

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote(query.replace('-', '').
                                                                                    replace(' ', '-')))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('/to/amateur/')
    module = RedWap()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
