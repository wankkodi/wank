# -*- coding: UTF-8 -*-
# Video catalog
from ....catalogs.vod_catalog import VODCatalogNode, VODCategories, VideoNode, VideoSource, VideoTypes
from ....fetchers.vod_fetcher import VODFetcher

# Playlist tools
import m3u8

# Regex
import re

# JSON
import json

# Warnings and exceptions
# import warnings

# OS
from os import path

# Datetime
from datetime import datetime
# import time

# Math
import math

# Internet tools
from .... import urljoin, urlparse, parse_qs


class Channel10(VODFetcher):
    vod_json_url = 'http://common.nana10.co.il/SectionVOD/GetSectionVOD.ashx'
    video_request_url_template1 = 'http://10tv.nana10.co.il/Video/?VideoID={vid}&TypeID=13&SectionID={sid}&' \
                                  'CategoryID={cid}&pid=48&AutoPlay=1'
    video_request_url2 = 'http://vod.ch10.cloudvideoplatform.com/api/getlink/getflash'
    image_link_template = 'http://f.nanafiles.co.il/upload/mediastock/img/693/0/{im_pr}/{im}.jpg'

    results_per_requests = 150

    @property
    def object_urls(self):
        return {
            VODCategories.CHANNELS_MAIN: 'http://10tv.nana.co.il/',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://10tv.nana.co.il/'

    def __init__(self, source_name='Channel10', source_id=-18, store_dir='.', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        # self.episodes_to_data = {}
        super(Channel10, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)
        self.show_names_filename = path.join(self.fetcher_data_dir, 'show_names.json.py')
        with open(self.show_names_filename, 'rb') as fl:
            self.show_names = json.load(fl)

    def fetch_sub_objects(self, element_object):
        """
        Fetches object's sub objects.
        :param element_object: Object element we want to fetch.
        :return:
        """
        if element_object.object_type == VODCategories.CHANNELS_MAIN:
            return self._update_base_categories(element_object)
        elif element_object.object_type == VODCategories.SHOW:
            return self._update_show_subcategories(element_object)
        elif element_object.object_type == VODCategories.SHOW_SEASON:
            return self._get_episodes_show_object(element_object)
        else:
            raise ValueError('Wrong additional_type parameter!')

    def _update_base_categories(self, base_object):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        req = self.get_object_request(base_object)
        tree = self.parser.parse(req.content.decode('utf-8'))
        categories_trees = tree.xpath('.//div[@id="t1677_tab1"]//div[@class="t1677_Menu"]')
        main_categories = []
        for category_tree in categories_trees:
            category_url = re.findall(r'(?:href=\')(.*)(?:\')', category_tree.attrib['onclick'])[0]
            # category_params = parse_qs(urlparse(category_url).query)
            image_link = urljoin(base_object.url, category_tree.xpath('./img/@src')[0])
            description = category_tree.xpath('./div[@class="t1677_menuitem_title"]/text()')[0]
            main_category = VODCatalogNode(catalog_manager=self.catalog_manager,
                                           obj_id=category_url,
                                           title=self.show_names[category_url],
                                           url=category_url,
                                           image_link=image_link,
                                           description=description,
                                           super_object=base_object,
                                           object_type=VODCategories.SHOW,
                                           raw_data=category_tree)
            main_categories.append(main_category)

        base_object.add_sub_objects(main_categories)

        # with open(self.available_shows_data_filename, 'wb') as fl:
        #     pickle.dump(self.available_categories, fl)

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data (dict).
        :return:
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate',
            'Host': self.host_name,
            # 'Referer': self.base_url,
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        req = self.session.get(video_data.url, headers=headers)
        assert req.ok

        video_id = re.findall(r'(?:"MediaStockVideoItemGroupID",")(\d+)(?:")', req.text)[0]
        user_id = re.findall(r'(?:UserID=)(.+?)(?:;)', req.text)[0]
        headers2 = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': self.base_url,
            'Referer': video_data.url,
            # 'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        params2 = {
            'showid': video_id,
            'userid': user_id
        }
        req2 = self.session.get(self.video_request_url2, headers=headers2, params=params2)
        assert req2.ok

        raw_data = json.loads(req2.text[1:-1])
        headers3 = {
            # 'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': self.base_url,
            'Referer': video_data.url,
            # 'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        request_url3 = (raw_data['ProtocolType'] + raw_data['ServerAddress'] + raw_data['MediaRoot'] +
                        raw_data['MediaFile'][:-4] + raw_data['Bitrates'] + raw_data['MediaFile'][-4:] +
                        raw_data['StreamingType'] + raw_data['Params'])

        req3 = self.session.get(request_url3, headers=headers3)
        assert req3.ok

        video_m3u8 = m3u8.loads(req3.text)
        video_playlists = video_m3u8.playlists
        if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
            video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)
        res = [urljoin(request_url3, video_playlist.uri) for video_playlist in video_playlists]

        video_objects = [VideoSource(link=x, video_type=VideoTypes.VIDEO_REGULAR) for x in res]
        return VideoNode(video_sources=video_objects)

    def _update_show_subcategories(self, show_object):
        """
        Fetches the show subcategories.
        :param show_object: Show object.
        :return: list of Season objects.
        """
        # In case we have it in our db, we fetch it from, there
        req = self.get_object_request(show_object)
        tree = self.parser.parse(req.content.decode('utf-8'))
        sub_trees = tree.xpath('.//div[@id="t1672_tabs"]/a')
        sub_categories = [VODCatalogNode(catalog_manager=self.catalog_manager,
                                         obj_id=x.attrib['href'],
                                         title=x.text,
                                         url=x.attrib['href'],
                                         image_link=show_object.image_link,
                                         super_object=show_object,
                                         object_type=VODCategories.VIDEO,
                                         raw_data=x)
                          for x in sub_trees]
        show_object.add_sub_objects(sub_categories)
        return sub_categories

    def _get_episodes_show_object(self, show_object):
        """
        Fetches the show seasons from show object.
        :param show_object: Show object.
        :return: list of Season objects.
        """
        # In case we have it in our db, we fetch it from, there
        # if show_object.id in self.show_data:
        #     return self.show_data[show_object.id]

        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Cache-Control': 'max-age=0',
            # 'Host': urlparse(self.base_url).hostname,
            'Referer': show_object.super_object.url,
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        url_params = parse_qs(urlparse(show_object.url).query)
        super_url_params = parse_qs(urlparse(show_object.super_object.url).query)

        params = {
            'PageSize': self.results_per_requests,
            'FetchVideo': 1,
            'PageNumber': 1 if show_object.page_number is None else show_object.page_number,
            'SectionID': url_params['SectionId'],
            # 'callback': 'jQuery1720531467264828591_1571195720238',
        }
        req = self.session.get(self.vod_json_url, headers=headers, params=params)
        assert req.ok
        raw_data = json.loads(req.text[1:-1])

        # Additional objects
        if show_object.object_type is not VODCategories.PAGE and show_object.sub_objects is None:
            number_of_additional_pages = int(math.ceil(raw_data['TotalResults'] / float(self.results_per_requests)))
            if number_of_additional_pages > 1:
                additional_objects = [VODCatalogNode(catalog_manager=self.catalog_manager,
                                                     obj_id=(show_object.id, i+1),
                                                     title=show_object.title,
                                                     url=show_object.url,
                                                     image_link=show_object.image_link,
                                                     super_object=show_object,
                                                     page_number=i+1,
                                                     object_type=VODCategories.PAGE,
                                                     )
                                      for i in range(number_of_additional_pages)]
                assert len(additional_objects) > 0
                show_object.add_sub_objects(additional_objects)

            self.show_data[show_object.id] = show_object
            if show_object.sub_objects is not None:
                show_object = show_object.sub_objects[0]

        # Sub objects
        episodes = [VODCatalogNode(catalog_manager=self.catalog_manager,
                                   obj_id=x['ArticleID'],
                                   title=x['Title'],
                                   description=x['SubTitle'],
                                   url=self.video_request_url_template1.format(vid=x['VideoID'],
                                                                               sid=url_params['SectionId'][0],
                                                                               cid=super_url_params['CategoryID'][0],
                                                                               ),
                                   image_link=self.image_link_template.format(im_pr=str(x['MediaStockImageID'])[:3],
                                                                              im=str(x['MediaStockImageID'])),
                                   super_object=show_object,
                                   date=datetime.utcfromtimestamp(int(re.findall(r'\d+', x['CreateDate'])[0])/1000),
                                   object_type=VODCategories.VIDEO,
                                   raw_data=x) for x in raw_data['HeadlineList']]

        show_object.add_sub_objects(episodes)

        self.show_data[show_object.id] = show_object
        # with open(self.shows_data_filename, 'wb') as fl:
        #     pickle.dump(self.category_data, fl)
        return show_object

    def get_live_stream_video_link(self):
        """
        Fetches the live stream video_link.
        :return: VideoNode object.
        """
        raise NotImplementedError

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        return NotImplemented

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        if page_data.object_type in (VODCategories.SHOW_SEASON, VODCategories.PAGE):
            params = {
                'PageSize': self.results_per_requests,
                'FetchVideo': 1,
                'PageNumber': 1 if page_data.page_number is None else page_data.page_number,
                'SectionID': params['SectionId'],
                # 'callback': 'jQuery1720531467264828591_1571195720238',
            }

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        req = self.session.get(fetch_base_url, headers=headers, params=params)
        return req

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Channel10, self)._version_stack + [self.__version]
