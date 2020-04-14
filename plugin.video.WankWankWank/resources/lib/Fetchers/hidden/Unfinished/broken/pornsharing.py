# -*- coding: UTF-8 -*-
from porn_fetcher import PornFetcher

# Internet tools
from urllib.parse import urljoin

# Generator id
from ..id_generator import IdGenerator

# Nodes
from porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode
from porn_catalog import CategoryMain, PornStarMain, ChannelMain, LatestVideo, TopRatedVideo, PopularVideo, InterestingVideo, \
    Category, PornStar, Video
from video_catalog import VideoNode


class PornSharing(PornFetcher):
    @property
    def object_urls(self):
        return {
            CategoryMain: 'https://pornsharing.com/categories',
            PornStarMain: 'https://pornsharing.com/models',
            ChannelMain: 'https://pornsharing.com/sites',
            LatestVideo: 'https://sexu.com/new',
            TopRatedVideo: 'https://sexu.com/all',
            PopularVideo: 'https://sexu.com/trending',
            InterestingVideo: 'https://sexu.com/engaging',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://sexu.com/'

    def __init__(self, source_name='SexU', source_id=0, store_dir='.', data_dir='../Data'):
        """
        C'tor
        :param source_name: save directory
        """
        super().__init__(source_name, source_id, store_dir, data_dir)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, Category)

    def _update_available_porn_stars(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, PornStar)

    def _update_available_base_object(self, base_object_data, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self._get_page_request(base_object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//ul[@class="grid"]/li[@class="grid__item"]/a')
        res = []
        for category in categories:
            image = category.xpath('./div[@class="item__main"]/div[@class="item__image"]/img')
            assert len(image) == 1
            image = image[0].attrib['data-src'] \
                if 'data-src' in image[0].attrib else image[0].attrib['src']

            number_of_videos = category.xpath('./div[@class="item__main"]/div[@class="item__counter"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=category.attrib['title'],
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  object_type=object_type,
                                                  super_object=base_object_data,
                                                  )
            res.append(object_data)
        base_object_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """

        video_url = video_data.url
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
        tmp_request = self.session.get(video_url, headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)

        videos = tmp_tree.xpath('.//div[@class="player-block__item"]/video/source')
        assert len(videos) > 0
        video_links = sorted(((urljoin(video_url, x.attrib['src']), x.attrib['title']) for x in videos),
                             key=lambda y: int(y[1][:-1]), reverse=True)
        video_links = [x[0] for x in video_links]
        return VideoNode(video_links=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        page_request = self._get_page_request(category_data) if fetched_request is None else fetched_request
        if not page_request.ok:
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
        return ([int(x) for x in tree.xpath('.//div[@class="pagination__list"]/a/text()') if x.isdigit()] +
                [int(x) for x in tree.xpath('.//div[@class="pagination__list"]/a/span/text()') if x.isdigit()])

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self._get_page_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//ul[@class="grid"]/li[@class="grid__item"]/div')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1

            image = video_tree_data.xpath('./a/div[@class="item__image"]/img')
            assert len(image) == 1
            image = image[0].attrib['data-src'] \
                if 'data-src' in image[0].attrib else image[0].attrib['src']

            video_length = video_tree_data.xpath('./a/div[@class="item__counter"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            special_emojis = video_tree_data.xpath('./a/div[@class="item__reactions emoji emoji--sm"]/'
                                                   '/div[@class="emoji__item"]/div[@class="emoji__title"]')
            additional_data = {'special_descriptions': [x.text for x in special_emojis]}

            rating = video_tree_data.xpath('./div[@class="item__description"]/div[@class="item__line"]/'
                                           'div[@class="item__rate"]/span')
            rating = int(rating[0].text) if len(rating) == 1 else 0

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=link[0].attrib['title'],
                                                  image_link=image,
                                                  rating=rating,
                                                  duration=self._format_duration(video_length),
                                                  additional_data=additional_data,
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
        :param override_page_number: Overrides page number.
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
        page_number = override_page_number if override_page_number is not None else page_data.page_number
        if page_number is not None and page_number != 1:
            program_fetch_url += '/{p}'.format(p=page_number)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request


if __name__ == '__main__':
    # category_id = IdGenerator.make_id('/tag/mom')
    category_id = IdGenerator.make_id('/tag/wife')
    porn_star_id = IdGenerator.make_id('/pornstar/asa+akira')
    module = SexU()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['porn_stars']['obj'], (porn_star_id, ), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
