# -*- coding: UTF-8 -*-
from porn_fetcher import PornFetcher

# Internet tools
from urllib.parse import urljoin

# Regex
import re

# Nodes
from porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode
from porn_catalog import CategoryMain, TopRatedVideo, LatestVideo, MostViewedVideo, MostDiscussedVideo, LongestVideo, \
    Category, Video
from video_catalog import VideoNode

# Generator id
from ..id_generator import IdGenerator


class HypnoTube(PornFetcher):
    @property
    def max_pages(self):
        return 1000

    @property
    def object_urls(self):
        return {
            CategoryMain: 'https://hypnotube.com/channels/',
            LatestVideo: 'https://hypnotube.com/videos/',
            TopRatedVideo: 'https://hypnotube.com/top-rated/',
            MostViewedVideo: 'https://hypnotube.com/most-viewed/',
            MostDiscussedVideo: 'https://hypnotube.com/most-discussed/',
            LongestVideo: 'https://hypnotube.com/longest/',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://hypnotube.com/'

    def __init__(self, source_name='HypnoTube', source_id=0, store_dir='.', data_dir='../Data'):
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
        page_request = self._get_page_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="inner-box-container"]/div[@class="row"]/div/div/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            title = category.attrib['title']

            image_data = category.xpath('./span[@class="image"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(category_data.url, link),
                                               title=title,
                                               image_link=image,
                                               object_type=Category,
                                               super_object=category_data,
                                               ))

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

        videos = [urljoin(video_data.url, x) for x in tmp_tree.xpath('.//video/source/@src')]
        assert len(videos) > 0
        return VideoNode(video_links=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (CategoryMain, ):
            return 1

        page_request = self._get_page_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        if category_data.page_number is not None:
            max_page = max(pages)
            if max_page - category_data.page_number < self._binary_search_page_threshold:
                return max_page

        # We perform binary search
        return self._binary_search_max_number_of_pages(category_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//div[@class="pagination-inner-col inner-col"]/a')
                if x.text is not None and x.text.isdigit()]

    def _binary_search_check_is_available_page(self, page_request):
        """
        In binary search performs test whether the current page is available.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        return len(pages) > 0

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 10

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self._get_page_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="inner-box-container"]/div[@class="row"]/div[@class="item-col col "]/'
                            '/div[@class="item-inner-col inner-col"]/a[1]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']
            title = video_tree_data.attrib['title']

            image_data = video_tree_data.xpath('./span[@class="image"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image)
                           for d in range(1, int(image_data[0].attrib['data-opt-limit']) + 1)]

            video_length = video_tree_data.xpath('./span[@class="image"]/span[@class="time"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            is_hd = video_tree_data.xpath('./span[@class="image"]/span[@class="quality"]/'
                                          'span[@class="quality-icon q-hd"]')
            is_hd = len(is_hd) > 0

            rating = video_tree_data.xpath('./span[@class="item-info"]/span[@class="item-stats"]/'
                                           'span[@class="s-elem s-e-rate"]/span[@class="sub-desc"]')
            assert len(rating) == 1
            rating = rating[0].text

            number_of_views = video_tree_data.xpath('./span[@class="item-info"]/span[@class="item-stats"]/'
                                                    'span[@class="s-elem s-e-views"]/span[@class="sub-desc"]')
            assert len(number_of_views) >= 1
            if len(number_of_views) > 1 and number_of_views[1].text == 'Private':
                # We have a private video...
                continue
            number_of_views = number_of_views[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  duration=self._format_duration(video_length),
                                                  is_hd=is_hd,
                                                  rating=rating,
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
            'Referer': page_data.url,
            # 'Host': urlparse(object_data.url).hostname,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        page_number = page_data.page_number if override_page_number is None else override_page_number
        if page_number is not None and page_number != 1:
            program_fetch_url = re.sub(r'/(page\d+.html)*$', '', program_fetch_url)
            program_fetch_url += '/page{d}.html'.format(d=page_number)

        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    module = HypnoTube()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
