# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornNoVideoError, PornErrorModule
from ..tools.external_fetchers import ExternalFetcher

# Internet tools
from .. import urlparse, urljoin

# Regex
import re

# Warnings and exceptions
import warnings

# JSON
import json

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ..catalogs.porn_catalog import PornCategories

# Generator id
from ..id_generator import IdGenerator


class Likuoo(PornFetcher):
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 3000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.likuoo.video/all-channels/',
            PornCategories.TAG_MAIN: 'https://www.likuoo.video/',
            PornCategories.PORN_STAR_MAIN: 'https://www.likuoo.video/pornstars/',
            PornCategories.LATEST_VIDEO: 'https://www.likuoo.video/',
            PornCategories.SEARCH_MAIN: 'https://www.likuoo.video/search/',
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
        return 'https://www.likuoo.video/'

    def __init__(self, source_name='Likuoo', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Likuoo, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)
        # self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
        #                   'Chrome/76.0.3809.100 Safari/537.36'
        self.external_fetchers = ExternalFetcher(session=self.session, user_agent=self.user_agent, parser=self.parser)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_objects(category_data, './/div[@class="item_p"]/a',
                                                   PornCategories.CATEGORY)

    def _update_available_porn_stars(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_objects(category_data, './/div[@class="item_p"]/a',
                                                   PornCategories.PORN_STAR)

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//ul[@class="category"]/li/a')
        links = [x.attrib['href'] for x in raw_objects]
        titles = [x.text for x in raw_objects]
        number_of_videos = [None] * len(links)
        assert len(titles) == len(links)
        # assert len(titles) == len(number_of_videos)

        return links, titles, number_of_videos

    def _update_available_base_objects(self, base_object_data, sub_object_xpath, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(sub_object_xpath)
        res = []
        for category in categories:
            image = category.xpath('./img/@src')
            assert len(image) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=category.attrib['title'],
                                                  image_link=urljoin(self.base_url, image[0]),
                                                  object_type=object_type,
                                                  super_object=base_object_data
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
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)

        request_data = [x for x in tmp_tree.xpath('.//script/text()') if 'ext' in x and 'ajax' in x]
        assert len(request_data) > 0
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cache-Control': 'max-age=0',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            # 'Host': self.host_name,
            'Origin': self.base_url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }

        videos = []
        for request_datum in request_data:
            req_suffix = re.findall(r'(?:url: *\')(.*?)(?:\')', request_datum)
            assert len(req_suffix) == 1
            req_data = re.findall(r'(?:data: *\')(.*?)(?:\')', request_datum)
            assert len(req_data) == 1
            req = self.session.post(urljoin(self.base_url, req_suffix[0]), headers=headers,
                                    data=dict([req_data[0].split('=')]))
            assert req.ok
            if not self._check_is_available_page(req):
                server_data = PornErrorModule(self.data_server, self.source_name, video_data.url,
                                              'Cannot fetch video links from the url {u}'.format(u=req.url),
                                              None, None)
                raise PornNoVideoError('No Video link for url {u}'.format(u=req.url), server_data)

            raw_data = req.json()
            tmp_new_tree = self.parser.parse(raw_data['i'])
            new_source = tmp_new_tree.xpath('.//iframe/@src')
            if len(new_source) > 0:
                if urlparse(new_source[0]).hostname == 'verystream.com':
                    # Not available anymore...
                    # videos.extend(self.external_fetchers.get_video_link_from_verystream(new_source[0]))
                    continue
                elif urlparse(new_source[0]).hostname == 'oload.stream':
                    videos.extend(self.external_fetchers.get_video_link_from_openload(new_source[0]))
                    continue
                elif urlparse(new_source[0]).hostname == 'mixdrop.co':
                    videos.extend(self.external_fetchers.get_video_link_from_mixdrop(new_source[0]))
                    continue
                elif urlparse(new_source[0]).hostname == 'gounlimited.to':
                    videos.extend(self.external_fetchers.get_video_link_from_gotounlimited(new_source[0]))
                    continue
                else:
                    warnings.warn('Unknown source {h}...'.format(h=urlparse(new_source[0]).hostname))

            # We have multiple sources
            new_source = re.findall(r'(?:setup\()({.*})(?:\);)', raw_data['i'])
            if len(new_source) > 0:
                new_source = re.sub(r'\'', '"', new_source[0])
                new_source = re.sub(r'\w+(?=:)(?!:[/\d])', lambda x: '"' + x.group(0) + '"', new_source)
                new_source = re.sub(r', *[}\]]', lambda x: x.group(0)[-1], new_source)
                new_source = json.loads(new_source)
                videos.extend(((x['file'], int(re.findall(r'\d+', x['label'])[0])) for x in new_source['sources']))
                continue

            # If we are here we have some unknown pattern...
            server_data = PornErrorModule(self.data_server, self.source_name, video_data.url,
                                          'Unknown pattern for the page {u}'.format(u=req.url),
                                          None, None)
            raise PornNoVideoError('Unknown pattern for the page {u}'.format(u=req.url), server_data)

        videos = sorted((VideoSource(link=x[0], resolution=x[1]) for x in videos),
                        key=lambda x: x.resolution, reverse=True)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        return VideoNode(video_sources=videos, headers=headers)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        start_page = category_data.page_number if category_data.page_number is not None else 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        max_page = max(pages)
        if (max_page - start_page) < self._binary_search_page_threshold:
            return max_page
        else:
            return self._binary_search_max_number_of_pages(category_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        pages = [int(x) for x in tree.xpath('.//div[@class="pagination"]/*/text()') if x.isdigit()]
        return pages

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 2

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="item"]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1

            img = video_tree_data.xpath('./a/img/@src')
            assert len(img) == 1

            video_length = video_tree_data.xpath('./div[@class="runtime"]')
            assert len(video_length) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=link[0].attrib['title'],
                                                  image_link=urljoin(self.base_url, img[0]),
                                                  duration=self._format_duration(video_length[0].text),
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw duration.
        :return:
        """
        if len(raw_duration.split(':')) > 1:
            minutes, seconds = raw_duration.split(':')
        else:
            # We have format of \d h \d m \d s
            minutes, seconds = re.findall(r'\d+', raw_duration)
        return minutes * 60 + seconds

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')

        if page_number is not None and page_number != 1:
            if split_url[-2].isdigit():
                split_url.pop(-2)
            if fetch_base_url == self.base_url:
                split_url.insert(-1, 'new')
            split_url.insert(-1, str(page_number))
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

        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        true_query = re.sub(r'[^A-Za-z0-9 ]', '', query)
        true_query = re.sub(r'\s{2}\s*', ' ', true_query)
        true_query = re.sub(r'\s', '- ', true_query)
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=true_query)


if __name__ == '__main__':
    category_id = IdGenerator.make_id('/channels/hd-full-1080p')
    tag_id = IdGenerator.make_id('/topic/at-work')
    pornstar_id = IdGenerator.make_id('/pornstar/peta-jensen/')
    module = Likuoo()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['porn_stars']['obj'], (pornstar_id, ), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
