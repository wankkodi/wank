# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError
from ..tools.external_fetchers import ExternalFetcher

# Internet tools
from .. import urlparse, urljoin, quote_plus

# Regex
import re

# Warnings and exceptions
import warnings

# Base 64
import base64

# Generator id
from ..id_generator import IdGenerator

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories


class UltraHorny(PornFetcher):
    number_of_flip_images = 20

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://ultrahorny.com/channels/',
            PornCategories.LATEST_VIDEO: 'https://ultrahorny.com/latest-video/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://ultrahorny.com/most-viewed/',
            PornCategories.TOP_RATED_VIDEO: 'https://ultrahorny.com/top-rated/',
            PornCategories.LONGEST_VIDEO: 'https://ultrahorny.com/longest/',
            PornCategories.MOST_DISCUSSED_VIDEO: 'https://ultrahorny.com/most-comment/',
            PornCategories.SEARCH_MAIN: 'https://ultrahorny.com/search/',
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
        return 'https://ultrahorny.com/'

    def __init__(self, source_name='UltraHorny', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(UltraHorny, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)
        self.external_fetchers = ExternalFetcher(session=self.session, user_agent=self.user_agent,
                                                 parser=self.parser)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        # todo: to change from category to channel...
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//article[@class="post channel"]/a')
        res = []
        for category in categories:
            title = category.xpath('./header/h2[@class="entry-title"]')
            assert len(title) == 1
            title = re.sub(r'[ \r\n]*$|^[ \r\n]*', '', title[0].text)

            number_of_videos = category.xpath('./header/span[@class="videos fa-video"]/span')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.sub(r'[ \r\n]*$|^[ \r\n]*', '', number_of_videos[0].text))

            image = category.xpath('./div/figure/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
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
        video_url = video_data.url
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        # Was taken from pornktube module (have the same engine.
        tmp_request = self.session.get(video_url, headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)
        outsource_link = tmp_tree.xpath('.//div[@class="video videocc"]/iframe')
        assert len(outsource_link) == 1
        hostname = urlparse(outsource_link[0].attrib['src']).hostname
        if hostname == 'ultrahorny.com':
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3*',
                'Cache-Control': 'max-age=0',
                # 'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }
            tmp_request = self.session.get(outsource_link[0].attrib['src'], headers=headers)
            raw_code = re.findall(r'(?:atob\(")(.*?)(?:"\))', tmp_request.text)
            assert len(raw_code) == 1
            raw_code = ''.join(chr(int(x, 16)) for x in raw_code[0].split('\\x')[1:])
            raw_code = base64.b64decode(raw_code.encode("utf-8")).decode('utf-8')
            files = re.findall(r'(?:file: *")(.*?)(?:")', raw_code)
            resolutions = [int(re.findall(r'\d+', x)[0]) for x in re.findall(r'(?:label: *")(.*?)(?:")', raw_code)]
            assert len(files) == len(resolutions) and len(files) > 0
            # video_links = list(zip(files, resolutions))
            video_links = sorted((VideoSource(link=link, resolution=res) for link, res in zip(files, resolutions)),
                                 key=lambda x: x.resolution, reverse=True)
        elif hostname == 'stream.ksplayer.com':
            video_links = sorted((VideoSource(link=x[0], resolution=x[1])
                                  for x in self.external_fetchers.
                                 get_video_link_from_ksplayer(outsource_link[0].attrib['src'])),
                                 key=lambda x: x.resolution, reverse=True)
        else:
            warnings.warn('The fetch module for hostname {h} is not implemented yet.'.format(h=hostname))
            video_links = []

        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'identity;q=1, *;q=0',
            'Cache-Control': 'max-age=0',
            'Referer': video_url,
            'Range': 'bytes=0-',
            'Sec-Fetch-Mode': 'no-cors',
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
        return [int(x) for x in tree.xpath('.//nav[@class="navigation pagination"]/div/a/text()')
                if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//article[@class="post"]/a')
        res = []
        for video_tree_data in videos:
            video_preview = video_tree_data.xpath('./div[@class="post-thumbnail or1"]/figure[@class="image-articles"]')
            assert len(video_preview) == 1

            image = video_tree_data.xpath('./div[@class="post-thumbnail or1"]/figure[@class="image-articles"]/img')
            assert len(image) == 1

            # video_length = video_tree_data.xpath('./div[@class="post-thumbnail or1"]/span[@class="duration"]')
            # assert len(video_length) == 1

            is_hd = video_tree_data.xpath('./div[@class="post-thumbnail or1"]/span[@class="quality"]')

            number_of_views = video_tree_data.xpath('./div[@class="post-thumbnail or1"]/'
                                                    'span[@class="views fa-eye far"]/span')
            assert len(number_of_views) == 1

            res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                obj_id=video_tree_data.attrib['href'],
                                                url=urljoin(self.base_url, video_tree_data.attrib['href']),
                                                title=video_tree_data.attrib['title'],
                                                image_link=image[0].attrib['src'],
                                                preview_video_link=video_preview[0].attrib['data-url'],
                                                is_hd=len(is_hd) == 1 and is_hd[0].text == 'HD',
                                                # duration=self._format_duration(video_length[0].text),
                                                number_of_views=number_of_views[0].text,
                                                object_type=PornCategories.VIDEO,
                                                super_object=page_data,
                                                ))
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        split_url = fetch_base_url.split('/')
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
            # program_fetch_url = re.sub(r'/*$|\.html$', '', program_fetch_url)
            # program_fetch_url += '/page/{p}/'.format(p=page_data.page_number)
            if len(split_url[-1]) != 0:
                # We add slash at the end of the request
                split_url.append('')
            if split_url[-3] != 'page':
                # We add the format of the page
                split_url.insert(-1, 'page')
                split_url.insert(-1, str(page_number))
            else:
                # We override the existing page
                split_url[-2] = str(page_number)
        program_fetch_url = '/'.join(split_url)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}'.format(q=quote_plus(query))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://ultrahorny.com/channels/blacked/')
    module = UltraHorny()
    # module.get_available_categories()
    # module.download_object(None, category_id, verbose=1)
    module.download_category_input_from_user(use_web_server=False)
