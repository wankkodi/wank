# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher, PornFetchUrlError, PornNoVideoError

# Internet tools
from .... import urljoin, quote, urlparse

# Playlist tools
import m3u8

# Regex
import re

# Math
import random
import ctypes

# md5
from hashlib import md5

# JSON
# import json
try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

# requests
# from requests import cookies

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode, VideoTypes
from ....catalogs.porn_catalog import PornCategories


def base_n(num, b, numerals="0123456789abcdefghijklmnopqrstuvwxyz"):
    return ((num == 0) and numerals[0]) or (
            base_n(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])


class PornHDEightK(PornFetcher):
    video_link_request_page_template = 'http://www{sn}.pornhd8k.net/ajax/v2_get_episodes/{v}'
    video_link_request_page2_template = 'http://www{sn}.pornhd8k.net/ajax/get_sources/{v}/{c}?count=1&mobile=false'
    video_host_base_url = 'https://btc.embeddrive.net/hls/'
    _base_url_template = 'http://www{sn}.pornhd8k.net/'
    max_pages = 100

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/category/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/studio/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/porn-hd-videos/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
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
        if len(self.server_number) == 0:
            # We update the server number
            referer = None
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Pragma': 'no-cache',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }
            while 1:
                headers['Host'] = urlparse(self._base_url_template.format(sn=self.server_number)).hostname
                if referer is not None:
                    headers['Referer'] = referer
                page_request = self.session.head(self._base_url_template.format(sn=self.server_number),
                                                 headers=headers)
                if page_request.status_code == 200:
                    break
                else:
                    new_server = re.findall(r'(?:www)(\d+)', page_request.headers['location'])
                    if new_server[0] != self.server_number:
                        referer = (urlparse(self._base_url_template.format(sn=self.server_number)).scheme + '://' +
                                   urlparse(self._base_url_template.format(sn=self.server_number)).hostname)
                        self.server_number = new_server[0]
                    else:
                        raise PornFetchUrlError(page_request)
            self.server_number = re.findall(r'(?:www)(\d+)', page_request.url)
            self.server_number = self.server_number[0] if len(self.server_number) > 0 else ''

        return self._base_url_template.format(sn=self.server_number)

    def __init__(self, source_name='PornHD8K', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        self.server_number = ''
        super(PornHDEightK, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                           session_id)

    def _update_available_categories(self, object_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(object_data, './/div[@class="sub-container cate"]/ul/li/a',
                                                  PornCategories.CHANNEL)

    def _update_available_channels(self, object_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(object_data, './/div[@class="sub-container network"]/ul/li/a',
                                                  PornCategories.CHANNEL)

    def _update_available_base_object(self, object_data, xpath, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        headers = {
            'Accept': '*/*',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        page_request = self.session.get(object_data.url, headers=headers)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=category.attrib['href'],
                                                      url=urljoin(self.base_url, category.attrib['href']),
                                                      title=category.text,
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
        request_data = tmp_tree.xpath('.//input[@type="hidden"]')
        headers = {
            'Accept': '*/*',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Referer': video_data.url,
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        ajax_request_page = self.video_link_request_page_template.format(sn=self.server_number,
                                                                         v=request_data[0].attrib['value'])
        tmp_request = self.session.get(ajax_request_page, headers=headers)
        if tmp_request.text != 'ok':
            err_str = 'Cannot fetch video links from the url {u}, got status {s}'.format(u=tmp_request.url,
                                                                                         s=tmp_request.text)
            error_module = self._prepare_porn_error_module_for_video_page(video_data, tmp_request.url, err_str)
            raise PornNoVideoError(error_module.message, error_module)
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Referer': video_data.url,
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        new_class, new_cookie_name, cookie_value = self._prepare_class(request_data[0].attrib['value'])
        # self.session.cookies.set_cookie(
        #     cookies.create_cookie(domain=self.host_name, name=new_cookie_name, value=cookie_value))
        self.session.cookies.set(domain=self.host_name, name=new_cookie_name, value=cookie_value)
        ajax_request_page = \
            self.video_link_request_page2_template.format(sn=self.server_number,
                                                          v=request_data[0].attrib['value'], c=new_class)
        tmp_request = self.session.get(ajax_request_page, headers=headers)
        raw_data = tmp_request.json()

        # video_links = sorted(((x['file'], x['label']) for x in raw_data['playlist'][0]['sources']),
        #                      key=lambda y: int(re.findall(r'\d+', y[1])[0]), reverse=True)
        # video_links = [x[0] for x in video_links]
        video_links = []
        for video_datum in raw_data['playlist'][0]['sources']:
            if video_datum['type'] == 'video/mp4':
                video_links.append(VideoSource(link=video_datum['file'],
                                               resolution=int(re.findall(r'\d+', video_datum['label'])[0])))
            else:
                req = self.session.get(video_datum['file'])
                video_m3u8 = m3u8.loads(req.text)
                video_links.extend((VideoSource(link=urljoin(self.video_host_base_url, x.uri),
                                                video_type=VideoTypes.VIDEO_SEGMENTS,
                                                quality=x.stream_info.bandwidth,
                                                resolution=x.stream_info.resolution[1],
                                                codec=x.stream_info.codecs)
                                    for x in video_m3u8.playlists)
                                   )
        video_links.sort(key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=video_links)

    @staticmethod
    def _prepare_class(value):
        """
        Prepares the class according to the formula found in fix.js
        :param value: Key value
        :return:
        """
        tmp = 'n1sqcua67bcq9826avrbi6m49vd7shxkn985mhodk06twz87wwxtp3dqiicks2dfyud213k6ygiomq01s94e4tr9' \
              'v0k887bkyud213k6ygiomq01s94e4tr9v0k887bkqocxzw39esdyfhvtkpzq9n4e7at4kc6k8sxom08bl4dukp16h09oplu7zov4m5f8'
        a = PornHDEightK._do_some_magic_1()
        cookie_name = tmp[13:37] + value + tmp[40:64]

        return md5((value + str(a) + '98126avrbi6m49vd7shxkn985').encode()).hexdigest(), cookie_name, a

    @staticmethod
    def _do_some_magic_1():
        d = 1441645250
        e = 666095675
        b = 2
        c = 1
        a = None
        while PornHDEightK._do_some_magic_f(str(c), len(str(c)), 33813) != d:
            a = base_n(int(str(random.random())[2:11]), 36)
            b += 2
            c += 1

        if PornHDEightK._do_some_magic_c(str(b), len(str(b)), 92408) != e:
            pass

        return a

    @staticmethod
    def _do_some_magic_f(a, b, c):
        return PornHDEightK._do_some_magic_bb(a, b, c)

    @staticmethod
    def _do_some_magic_ba(b, c):
        a = c & 0xffff
        d = c - a
        return ctypes.c_int(ctypes.c_int((d * b | 0)).value + ctypes.c_int((a * b | 0)).value | 0).value

    @staticmethod
    def rshift(val, n):
        return val >> n if val >= 0 else (val + 0x100000000) >> n

    @staticmethod
    def _do_some_magic_bb(d, g, j):
        h = 0xcc9e2d51
        i = 0x1b873593
        c = j
        f = g & ~0x3
        for e in range(0, f, 4):
            b = ord(str(d)[e]) & 0xff | (ord(str(d)[e+1]) & 0xff) << 8 | (ord(str(d)[e+2]) & 0xff) << 16 \
                | (ord(str(d)[e+3]) & 0xff) << 24
            b = PornHDEightK._do_some_magic_ba(b, h)
            b = (b & 0x1ffff) << 15 | PornHDEightK.rshift(b, 17)
            b = PornHDEightK._do_some_magic_ba(b, i)
            c ^= b
            c = (c & 0x7ffff) << 13 | PornHDEightK.rshift(c, 19)
            c = c * 5 + 0xe6546b64 | 0

        b = 0
        if (g % 4) == 3:
            b = (ord(str(d)[f+2]) & 0xff) << 16
        elif (g % 4) == 2:
            b |= (ord(str(d)[f+1]) & 0xff) << 8
        elif (g % 4) == 1:
            b |= ord(str(d)[f]) & 0xff
            b = PornHDEightK._do_some_magic_ba(b, h)
            b = (b & 0x1ffff) << 15 | PornHDEightK.rshift(b, 17)
            b = PornHDEightK._do_some_magic_ba(b, i)
            c ^= b

        c ^= g
        c ^= PornHDEightK.rshift(c, 16)
        c = PornHDEightK._do_some_magic_ba(c, 0x85ebca6b)
        c ^= PornHDEightK.rshift(c, 13)
        c = PornHDEightK._do_some_magic_ba(c, 0xc2b2ae35)
        c ^= PornHDEightK.rshift(c, 16)
        return c

    @staticmethod
    def _do_some_magic_c(a, b, c):
        return PornHDEightK._do_some_magic_bb(a, b, c)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.CHANNEL_MAIN):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(re.findall(r'\d+$', x)[0])
                for x in tree.xpath('.//ul[@class="pagination"]/li/a/text()') if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="ml-item"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            url = urljoin(self.base_url, link_data[0].attrib['href'])
            raw_split_title = link_data[0].attrib['title'].split(' / ')
            if len(raw_split_title) == 3:
                subcategory = raw_split_title[0]
                title = raw_split_title[1]
                date = raw_split_title[2]
            elif len(raw_split_title) == 2:
                subcategory = None
                title = raw_split_title[0]
                date = raw_split_title[1]
            else:
                raise RuntimeError('Cannot process the title {t}!'.format(t=link_data[0].attrib['title']))

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['data-original'])

            is_hd = video_tree_data.xpath('./a/span[@class="mli-quality"]')
            is_hd = len(is_hd) > 0 and is_hd[0].text == 'HD'

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=url,
                                                  title=title,
                                                  image_link=image,
                                                  is_hd=is_hd,
                                                  added_before=date,
                                                  additional_data={'subcategory': subcategory},
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
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
        if page_number is not None and page_number != 1:
            if len(split_url[-1]) == 0:
                split_url.pop(-1)
            split_url.append('/page-{p}'.format(p=page_data.page_number))

        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}'.format(q=quote(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(PornHDEightK, self)._version_stack + [self.__version]
