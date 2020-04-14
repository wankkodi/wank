# -*- coding: UTF-8 -*-
from porn_fetcher import PornFetcher

# Internet tools
from urllib.parse import urljoin

# Regex
import re

# Nodes
from porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, PornCatalogPageNode
from porn_catalog import CategoryMain, TagMain, TopRatedVideo, LatestVideo, LongestVideo, \
    MostDiscussedVideo, MostViewedVideo, Category, Tag, Video
from video_catalog import VideoNode

# Generator id
from ..id_generator import IdGenerator


class HandJobHub(PornFetcher):
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
            CategoryMain: 'https://handjobhub.com/channels/',
            TagMain: 'https://handjobhub.com/tags/',
            LatestVideo: 'https://handjobhub.com/videos/',
            TopRatedVideo: 'https://handjobhub.com/top-rated/',
            LongestVideo: 'https://handjobhub.com/longest/',
            MostDiscussedVideo: 'https://handjobhub.com/most-discussed/',
            MostViewedVideo: 'https://handjobhub.com/most-viewed/',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://handjobhub.com/'

    def __init__(self, source_name='HandJobHub', source_id=0, store_dir='.', data_dir='../Data'):
        """
        C'tor
        :param source_name: save directory
        """
        super(HandJobHub, self).__init__(source_name, source_id, store_dir, data_dir)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self._get_page_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="item-col item--channel col"]/div[@class="item-inner-col inner-col"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            title = category.attrib['title']

            image_data = category.xpath('./span[@class="image"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               object_type=Category,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self._get_page_request(tag_data)
        links, titles, numbers_of_videos = self._get_tag_properties(page_request)
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=link,
                                       url=urljoin(self.base_url, link),
                                       title=title,
                                       number_of_videos=number_of_videos,
                                       object_type=Tag,
                                       super_object=tag_data,
                                       ) for link, title, number_of_videos in zip(links, titles, numbers_of_videos)]
        tag_data.add_sub_objects(res)
        return res

    def _add_tag_sub_pages(self, tag_data, sub_object_type):
        """
        Adds sub pages to the tags according to the first letter of the title. Stores all the tags to the proper pages.
        Notice that the current method contradicts with the _get_tag_properties method, thus you must use either of
        them, according to the way you want to implement the parsing (Use the _make_tag_pages_by_letter property to
        indicate which of the methods you are about to use...)
        :param tag_data: Tag data.
        :param sub_object_type: Object types of the sub pages (either Page or VideoPage).
        :return:
        """
        page_request = self._get_page_request(tag_data)
        tree = self.parser.parse(page_request.text)
        pages = tree.xpath('.//div[@class="alphabet-col col col-full"]/div[@class="alphabet-inner-col inner-col"]/a')
        new_pages = [PornCatalogPageNode(catalog_manager=self.catalog_manager,
                                         obj_id=(IdGenerator.id_to_original_str(tag_data.id), p.text),
                                         title='{c} | Letter {p}'.format(c=tag_data.title, p=p.text),
                                         url=urljoin(tag_data.url, p.attrib['href']),
                                         raw_data=tag_data.raw_data,
                                         additional_data={'letter': p.text},
                                         object_type=sub_object_type,
                                         super_object=tag_data,
                                         ) for p in pages[1:]]
        tag_data.add_sub_objects(new_pages)

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="textpage-inner-col inner-col"]/'
                                 'div[@style="width: 25%; min-width: 250px; float: left;"]/a')
        raw_numbers = tree.xpath('.//div[@class="textpage-inner-col inner-col"]/'
                                 'div[@style="width: 25%; min-width: 250px; float: left;"]/span')
        assert len(raw_objects) == len(raw_numbers)
        links, titles, number_of_videos = \
            zip(*[(x.attrib['href'], x.text, int(re.findall(r'\d+', y.text)[0]))
                  for x, y in zip(raw_objects, raw_numbers)])
        return links, titles, number_of_videos

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
        our_page = category_data.page_number if category_data.page_number is not None else 1
        if len(pages) == 0:
            return 1
        if (max(pages) - our_page) < self._binary_search_page_threshold:
            return max(pages)
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _binary_search_check_is_available_page(self, page_request):
        """
        In binary search performs test whether the current page is available.
        :param page_request: Page request.
        :return:
        """
        return page_request.ok

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 10

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//div[@class="pagination-inner-col inner-col"]/*')
                if x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self._get_page_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//main[@class="main-col"]//div[@class="item-col col"]/'
                            'div[@class="item-inner-col inner-col"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a[1]')
            assert len(link_data)
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title']

            image_data = video_tree_data.xpath('./a/span[@class="image"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            video_length = video_tree_data.xpath('./a/span[@class="image"]/span[@class="time"]')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0].text)
            if 'Photos' in video_length:
                # We have a gallery instead!
                continue

            rating = video_tree_data.xpath('./a/span[@class="item-info"]/span[@class="item-stats"]/'
                                           'span[@class="s-elem s-e-rate"]/span[@class="sub-desc"]')
            assert len(rating) == 1
            rating = rating[0].text

            number_of_views = video_tree_data.xpath('./a/span[@class="item-info"]/span[@class="item-stats"]/'
                                                    'span[@class="s-elem s-e-views"]/span[@class="sub-desc"]')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  duration=self._format_duration(video_length),
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
            program_fetch_url = \
                re.sub(r'(page\d*\.html)*$', 'page{d}.html'.format(d=page_number), program_fetch_url)

        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    module = HandJobHub()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
