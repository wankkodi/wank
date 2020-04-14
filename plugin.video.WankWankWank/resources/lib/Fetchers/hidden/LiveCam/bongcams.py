# -*- coding: UTF-8 -*-
from porn_fetcher import PornFetcher

# Internet tools
from urllib.parse import urljoin, quote_plus

# from requests import cookies

# Regex
import re

# Nodes
from video_catalog import GeneralMainDummy
from porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode
from porn_catalog import CategoryMain, TopRatedVideo, FavoriteVideo, MostViewedVideo, JustLoggedInVideo, \
    NewModelVideo, Category, Video
from video_catalog import VideoNode

# # json
# import json

# m3u8
import m3u8

# Math
import math

# Generator id
from ..id_generator import IdGenerator


class BongCams(PornFetcher):
    number_of_videos_per_page = 18
    page_request_json_url = 'https://en.bongacams.com/tools/listing_v3.php'
    video_request_json_url = 'https://en.bongacams.com/tools/amf.php'
    playlist_template = 'https:{srv}/hls/stream_{usr}/playlist.m3u8'

    @property
    def object_urls(self):
        return {
            CategoryMain: 'https://en.bongacams.com/',
            MostViewedVideo: 'https://en.bongacams.com/',
            TopRatedVideo: 'https://en.bongacams.com/',
            FavoriteVideo: 'https://en.bongacams.com/',
            JustLoggedInVideo: 'https://en.bongacams.com/',
        }

    @property
    def request_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://en.bongacams.com/tools/listing_v3.php?livetab={ps}&online_only=true&offset=0' \
               ''.format(ps=self.preferred_sex)

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://en.bongacams.com/'

    def __init__(self, source_name='BongCams', source_id=0, store_dir='.', data_dir='../../Data',
                 preferred_sex='female'):
        """
        C'tor
        :param source_name: save directory
        """
        self.preferred_sex = preferred_sex
        super().__init__(source_name, source_id, store_dir, data_dir)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self._get_page_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//ul[@class="hbd_list js-spa_categories"]/li/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            title = self._clear_text(category.text)
            number_of_videos = category.xpath('./span[@class="hbd_s_live"]/text()')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0])[0])
            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=Category,
                                               super_object=category_data,
                                               ))

        # js = json.loads(tree.xpath('.//script[@id="listingConfiguration"]/text()')[0])
        # res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
        #                                obj_id=x['code'],
        #                                url=urljoin(self.base_url, '/{c}'.format(c=x['code'])),
        #                                title=x['title'],
        #                                object_type=Category,
        #                                super_object=category_data,
        #                                ) for x in js['initData']['tagTitles']]
        #

        category_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        params = [('method', ['getRoomData']), ('args[]', [video_data.raw_data['username'], 'false'])]
        page_request = self.session.post(self.video_request_json_url, headers=headers, data=params)
        raw_data = page_request.json()
        playlist = self.playlist_template.format(srv=raw_data['localData']['videoServerUrl'],
                                                 usr=raw_data['performerData']['username'])

        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            # 'Referer': video_data.url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': self.user_agent,
        }
        req = self.session.get(playlist, headers=headers)
        video_m3u8 = m3u8.loads(req.text)
        video_playlists = video_m3u8.playlists
        if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
            video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)
        res = [urljoin(playlist, video_playlist.uri) for video_playlist in video_playlists]

        return VideoNode(video_links=res, raw_data=req.text, video_type='segments')

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (CategoryMain, ):
            return 1

        page_request = self._get_page_request(category_data) if fetched_request is None else fetched_request
        raw_data = page_request.json()

        return math.ceil(raw_data['online_count'] / self.number_of_videos_per_page)

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self._get_page_request(page_data)
        videos = page_request.json()
        res = [PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                        obj_id=x['chat_url'],
                                        url=urljoin(self.base_url, x['chat_url']),
                                        title=x['display_name'],
                                        image_link=x['thumb_image'],
                                        number_of_views=x['viewers'],
                                        raw_data=x,
                                        object_type=Video,
                                        super_object=page_data,
                                        ) for x in videos['models']]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request(self, page_data):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        if page_data.super_object.object_type == CategoryMain:
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
            page_request = self.session.get(page_data.url, headers=headers)
            return page_request

        # Here we are preparing the true request
        if page_data.super_object.object_type == TopRatedVideo:
            raw_cookie = '{{"sorting":"camscore","th_type":"live","limit":{npp},"c_limit":12}}' \
                         ''.format(npp=self.number_of_videos_per_page)
        elif page_data.super_object.object_type == MostViewedVideo:
            raw_cookie = '{{"sorting":"popular","th_type":"live","limit":{npp},"c_limit":12}}' \
                         ''.format(npp=self.number_of_videos_per_page)
        elif page_data.super_object.object_type == FavoriteVideo:
            raw_cookie = '{{"sorting":"lovers","th_type":"live","limit":{npp},"c_limit":12}}' \
                         ''.format(npp=self.number_of_videos_per_page)
        elif page_data.super_object.object_type == JustLoggedInVideo:
            raw_cookie = '{{"sorting":"logged","th_type":"live","limit":{npp},"c_limit":12}}' \
                         ''.format(npp=self.number_of_videos_per_page)
        elif page_data.super_object.object_type == NewModelVideo:
            raw_cookie = '{{"sorting":"new","th_type":"live","limit":{npp},"c_limit":12}}' \
                         ''.format(npp=self.number_of_videos_per_page)
        elif page_data.super_object.object_type == GeneralMainDummy:
            # Regular request
            raw_cookie = '{{"sorting":"popular","th_type":"live","limit":{npp},"c_limit":12}}' \
                         ''.format(npp=self.number_of_videos_per_page)
        else:
            raise RuntimeError('Unknown object type {ot}'.format(ot=page_data.super_object.object_type))

        if len(page_data.url.split('?')) > 1:
            params = page_data.url.split('?')[1]
            params = parse_qs(params)
        else:
            params = {}

        # new_cookie = cookies.create_cookie(name='ls01',
        #                                    value=quote_plus(raw_cookie),
        #                                    domain='.bongacams.com'
        #                                    )
        self.session.cookies.set(name='ls01', value=quote_plus(raw_cookie), domain='.bongacams.com')
        self.session.cookies.set(name='warning18', value=quote_plus('["en_GB"]'), domain='.bongacams.com')
        self.session.cookies.set(name='reg_ver2', value='3', domain='.bongacams.com')
        self.session.cookies.set(name='ts_type2', value='1', domain='.bongacams.com')
        # self.session.cookies.set(name='bonga20120608', value='e77cd0f91bb0e9453742957b5f7a11af',
        #                          domain='.bongacams.com')
        # self.session.cookies.set(name='sg', value=695, domain='.bongacams.com')

        page_number = page_data.page_number if page_data.page_number is not None else 1
        params['offset'] = self.number_of_videos_per_page * (page_number - 1)
        params['livetab'] = self.preferred_sex
        params['online_only'] = 'true'

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        page_request = self.session.get(self.page_request_json_url, headers=headers, params=params)
        return page_request


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    module = BongCams()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=False)
