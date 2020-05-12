# -*- coding: UTF-8 -*-
from ....fetchers.vod_fetcher import VODFetcher
# Video catalog
from ....catalogs.vod_catalog import VODCatalogNode, VODCategories, VideoNode, VideoSource, VideoTypes

# Regex
import re

# datetime
from datetime import datetime

# M3U8
import m3u8

# Internet tools
from .... import urljoin


class Knesset(VODFetcher):
    number_of_shows_per_page = 50
    video_data_request_url = 'https://www.knesset.tv/umbraco/Surface/Lobby/GetAllVodLobby?lobbyNodeId=19526'
    video_data_live_tv = 'https://w1.013.gostreaming.tv/Knesset/myStream/playlist.m3u8'

    @property
    def object_urls(self):
        return {
            VODCategories.CHANNELS_MAIN: 'https://www.knesset.tv/vod/',
            VODCategories.LIVE_VIDEO: 'https://www.knesset.tv/live/',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.knesset.tv/'

    def __init__(self, vod_name='Knesset', vod_id=-21, store_dir='.', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(Knesset, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)

    def fetch_sub_objects(self, element_object):
        """
        Fetches object's sub objects.
        :param element_object: Object element we want to fetch.
        :return:
        """
        if element_object.object_type == VODCategories.CHANNELS_MAIN:
            return self._update_base_categories(element_object)
        else:
            raise RuntimeError('You not suppose to be here...')

    def _update_base_categories(self, base_object):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        # Doesn't work as additional capthca must be entered
        req = self.get_object_request(base_object)
        raw_data = req.json()
        main_objects = []
        for show_category in raw_data['CategoriesTree']:
            show_category_object = VODCatalogNode(catalog_manager=self.catalog_manager,
                                                  obj_id=show_category['CurrentCategory']['Id'],
                                                  title=show_category['CurrentCategory']['Label'],
                                                  url=None,
                                                  super_object=base_object,
                                                  object_type=VODCategories.GENERAL_CHANNEL_SUB_CATEGORY,
                                                  raw_data=show_category['CurrentCategory'])
            main_objects.append(show_category_object)
            show_category_sub_objects = []
            for show in show_category['SubCategories']:
                show_object = VODCatalogNode(catalog_manager=self.catalog_manager,
                                             obj_id=show['Id'],
                                             title=show['Label'],
                                             url=None,
                                             super_object=show_category_object,
                                             object_type=VODCategories.GENERAL_CHANNEL_SUB_CATEGORY,
                                             raw_data=show)

                show_object = self._prepare_sub_objects_from_main_object(show_object, raw_data['Videos'])
                show_category_sub_objects.append(show_object)
            show_category_object.add_sub_objects(show_category_sub_objects)
            self._prepare_sub_objects_from_main_object(show_category_object, raw_data['Videos'])

        base_object.add_sub_objects(main_objects)

    def _prepare_sub_objects_from_main_object(self, show_object, videos):
        """
        Prepares sub objects (pages of video objects) for the given show.
        The analysis is based on the structure of the JSON object of the site...
        :param show_object: Show raw object.
        :param videos: Videos raw data.
        :return:
        """
        show_objects = [x for x in videos if x['SubCategoryId'] == show_object.raw_data['Id']]
        show_videos_chunks = [show_objects[i:i + self.number_of_shows_per_page]
                              for i in range(0, len(show_objects), self.number_of_shows_per_page)]
        show_pages = []
        for i, chunk in enumerate(show_videos_chunks):
            show_page = VODCatalogNode(catalog_manager=self.catalog_manager,
                                       obj_id=(show_object.id, i),
                                       title='{t} | Page {p}'.format(t=show_object.title, p=i + 1),
                                       url=show_object.url,
                                       object_type=VODCategories.PAGE,
                                       super_object=show_object)
            show_pages.append(show_page)
            show_page_videos = [VODCatalogNode(catalog_manager=self.catalog_manager,
                                               obj_id=x['Url'],
                                               title=x['Title'],
                                               url=urljoin(self.base_url, x['Url']),
                                               image_link=urljoin(self.base_url, x['PicUrl']),
                                               object_type=VODCategories.VIDEO,
                                               date=datetime.fromtimestamp(
                                                   int(re.findall(r'(?:Date\()(\d+)(?:\))',
                                                                  x['PublishedDate'])[0]) // 1000),
                                               raw_data=x,
                                               super_object=show_page) for x in chunk]
            show_page.add_sub_objects(show_page_videos)
        show_object.add_sub_objects(show_pages)
        return show_object

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data (dict).
        :return:
        """
        # We get the data of the page
        headers = {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': video_data.url,
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        if video_data.object_type == VODCategories.VIDEO:
            video_url = video_data.raw_data['VideoUrl']
        elif video_data.object_type in (VODCategories.LIVE_VIDEO, VODCategories.LIVE_SCHEDULE):
            video_url = self.video_data_live_tv
        else:
            raise ValueError('Unknown object type {ot}'.format(ot=video_data.object_type))
        req = self.session.get(video_url, headers=headers)
        new_data = m3u8.loads(req.text)
        video_playlists = new_data.playlists
        if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
            video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)
        res = [VideoSource(link=urljoin(video_url, x.uri), video_type=VideoTypes.VIDEO_SEGMENTS,
                           quality=x.stream_info.bandwidth, codec=x.stream_info.codecs)
               for x in video_playlists]
        return VideoNode(video_sources=res, raw_data=new_data)

    def get_object_request(self, page_data, override_page_number=None, override_params=None, override_url=None):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :param override_page_number: Override page number.
        :param override_params: Override params.
        :param override_url: Override url.
        :return: Page request
        """
        if page_data.object_type in (VODCategories.CHANNELS_MAIN, ):
            headers = {
                'Accept': 'text/html, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                'Referer': page_data.super_object.url,
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
            url = self.video_data_request_url
        else:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                'Referer': self.base_url,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
            }
            url = page_data.url
        req = self.session.get(url, headers=headers)
        tmp_tree = self.parser.parse(req.text)
        tmp_script = [x.attrib['src'] for x in tmp_tree.xpath('.//script')
                      if 'src' in x.attrib and '_Incapsula_Resource' in x.attrib['src']]
        if len(tmp_script) > 0:
            raise RuntimeError('Incapsula avoids getting true page :(')
            # tmp_req = self.session.get(urljoin(self.base_url, tmp_script[0]), headers=headers)
            # tmp_script = self.decrypt_initial_script(tmp_req.text)
        return req

    def get_live_stream_info(self):
        """
        Fetches the live stream data.
        :return: CatalogNode object.
        """
        return VODCatalogNode(catalog_manager=self.catalog_manager,
                              obj_id=-1,
                              title=u'שידור חי - ערוץ הכנסת',
                              url=self.object_urls[VODCategories.LIVE_VIDEO],
                              object_type=VODCategories.LIVE_SCHEDULE
                              )

    def get_live_stream_video_link(self):
        """
        Fetches the live stream video_link.
        :return: VideoNode object.
        """
        return self.get_video_links_from_video_data(self.get_live_stream_info())

    @staticmethod
    def decrypt_initial_script(raw_script):
        z = ''
        a = re.findall(r'(?:b=")(.*?)(?:")', raw_script, re.DOTALL)
        assert len(a) == 1
        a = a[0]
        for i in range(0, len(a), 2):
            z += chr(int(a[i:i + 2], 16))
        z = re.sub(r'\\x[0-9a-f]{2}', lambda x: chr(int(x[0][2:], 16)), z)
        # z = re.sub(r'var _0x[0-9a-f]+', lambda x: 'var ' + ''.join(chr(int(x[0][i:i+2], 16))
        #                                                            for i in range(7, len(x[0]), 2)), z)
        return z

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        raise NotImplementedError

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        return NotImplemented

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Knesset, self)._version_stack + [self.__version]
