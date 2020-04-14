# -*- coding: UTF-8 -*-
from porn_fetcher import PornFetcher

# Internet tools
from urllib.parse import urljoin

# Regex
import re

# Nodes
from porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode
from porn_catalog import CategoryMain, PornStarMain, LatestVideo, Category, PornStar, Video
from video_catalog import VideoNode

# Generator id
from ..id_generator import IdGenerator


class HDPorn(PornFetcher):
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        return {
            CategoryMain: 'http://www.hdporn.com/categories/',
            PornStarMain: 'http://www.hdporn.com/pornstars/',
            LatestVideo: 'http://www.hdporn.com/movies/',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.hdporn.com/'

    def __init__(self, source_name='HDPorn', source_id=0, store_dir='.', data_dir='../Data'):
        """
        C'tor
        :param source_name: save directory
        """
        super().__init__(source_name, source_id, store_dir, data_dir)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, './/div[@id="categories"]/ul/li/a', Category)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data, './/ul[@id="pornstars"]/li/a', PornStar)

    def _update_available_base_object(self, base_object, xpath, object_type):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self._get_page_request(base_object)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            title = category.xpath('./h3[@class="cat-title"]/span') + category.xpath('./span[@class="name"]')
            assert len(title) == 1
            title = title[0].text

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               object_type=object_type,
                                               super_object=base_object,
                                               ))

        base_object.add_sub_objects(res)
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
        # todo: find a way to get the video
        tmp_request = self.session.get(video_data.url, headers=headers)
        tree = self.parser.parse(tmp_request.text)
        videos = tree.xpath('.//video/source/@src')
        assert len(videos) > 0
        return VideoNode(video_links=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type in (CategoryMain, ):
            return 1
        page_request = self._get_page_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        return max(pages) if len(pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(re.findall(r'(?:finish=)(\d+)', x.attrib['href'])[0])
                for x in tree.xpath('.//div[@class="pagination"]/ul/li/*')
                if 'href' in x.attrib and len(re.findall(r'(?:finish=)(\d+)', x.attrib['href'])) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self._get_page_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//ul[@class="sceneList small"]/li/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            video_length = video_tree_data.xpath('./span[@class="duration"]')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0].text)

            title = video_tree_data.xpath('./div[@class="info"]/span[@class="title"]/span')
            assert len(title) == 1
            title = title[0].text

            added_before = video_tree_data.xpath('./div[@class="info"]/span[@class="date"]')
            assert len(added_before) == 1
            added_before = added_before[0].text

            number_of_views = video_tree_data.xpath('./div[@class="info"]/span[@class="views"]')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  duration=self._format_duration(video_length),
                                                  added_before=added_before,
                                                  number_of_views=number_of_views,
                                                  object_type=Video,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request(self, page_data, override_page_number=None):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :param override_page_number: Override page number.
        :return: Page request
        """
        program_fetch_url = page_data.url.split('?')[0]
        if len(page_data.url.split('?')) > 1:
            params = page_data.url.split('?')[1]
            params = parse_qs(params)
        else:
            params = {}

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
        page_number = page_data.page_number if override_page_number is None else override_page_number
        if page_number is not None and page_number != 1:
            params['display'] = page_number

        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    module = HDPorn()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=False)
