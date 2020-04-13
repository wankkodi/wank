# -*- coding: UTF-8 -*-
from ..fetchers.vod_fetcher import VODFetcher
# Video catalog
from ..catalogs.vod_catalog import VODCatalogNode, VODCategories, VideoNode, VideoSource, VideoTypes

# Internet tools
# from urllib.parse import urljoin
# from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qs, urlencode

# System
from os import path
import pickle

# Regex
# import re

# math
import math

# Random
import random

# Warnings and exceptions
import warnings

# Hash
import hashlib
import uuid

# datetime
from datetime import datetime
import time

# # JSON
import json

# M3U8
import m3u8

# ID generator
from ..id_generator import IdGenerator

# Internet tools
from .. import urljoin


class IBA(VODFetcher):
    main_url = 'http://admin.applicaster.com/'
    account_url_template = main_url + 'v{api_version}/accounts/{account_id}.json'
    category_url_template = main_url + 'v{api_version}/accounts/{account_id}/broadcasters/{broadcaster_id}/' \
                                       'categories/{category_id}.json'
    video_url_template = main_url + 'v{api_version}/accounts/{account_id}/broadcasters/{broadcaster_id}/' \
                                    'vod_items/{source_id}.json'
    uuid_url_template = 'https://ais-api.applicaster.com/api/v1/buckets/{bucket_id}/devices.json'

    time_format = '%Y/%m/%d %H:%M:%S +0000'
    dummy_id_key = 'dummy_id'

    items_per_page = 100

    @property
    def object_urls(self):
        return {
            VODCategories.CHANNELS_MAIN: 'http://admin.applicaster.com/',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://admin.applicaster.com/'

    def __init__(self, vod_name='IBA', vod_id=-19, store_dir='.', data_dir='../../Data', source_type='VOD',
                 session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        self.episodes_to_data = {}
        super(IBA, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, session_id)

        self._properties = {
            'p_key': '9f220835e4cf51b79de811d271',
            'account_id': '120',
            'broadcaster_id': '132',
            'bundle': 'com.applicaster.il.ch1',
            'bucket_id': '5491890569702d45789dc204',
            'app_id': '104442',
        }

        self._default_params = {
            'bundle': 'com.applicaster.il.ch1android',
            'bver': '1.0',
            'device_model': 'Nexus 7',
            'os_type': 'android',
            'os_version': '19',
            'ver': '1.2',
        }
        self._dynamic_keys = {'token', 'uuid'}

        self.episodes_to_data_filename = path.join(self.fetcher_data_dir, 'used_data.dat')
        if not path.isfile(self.episodes_to_data_filename):
            for k in self._dynamic_keys:
                self._default_params[k] = None
        else:
            with open(self.episodes_to_data_filename, 'rb') as fl:
                load_data = pickle.load(fl)
                if not all(k in load_data for k in self._dynamic_keys):
                    warnings.warn('Not all the dynamic keys are found in the loaded data! Creating new ones...')
                    for k in self._dynamic_keys:
                        self._default_params[k] = None
                else:
                    for k in self._dynamic_keys:
                        self._default_params[k] = load_data[k]

        if any((k not in self._default_params or self._default_params[k] is None) for k in self._dynamic_keys):
            # We need to create new values for the dynamic keys...
            self._update_dynamic_values()

    def fetch_sub_objects(self, element_object):
        """
        Fetches object's sub objects.
        :param element_object: Object element we want to fetch.
        :return:
        """
        if element_object.object_type == VODCategories.CHANNELS_MAIN:
            return self._update_base_categories(element_object)
        else:
            return self._get_seasons_from_show_object(element_object)

    def _update_base_categories(self, base_object):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        headers = {
            'Accept': 'application/json, text/plain, */*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            # 'Referer': self.base_url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        url = self.account_url_template.format(api_version='12',
                                               account_id=self._properties['account_id'],
                                               )
        params = self._prepare_request_params(url)
        req = self.session.get(url, headers=headers, params=params)
        raw_data = json.loads(req.content.decode('utf-8-sig'))
        try:
            category_id = raw_data["account"]["broadcasters"][0]['broadcaster']['content_category_id']
        except ValueError:
            category_id = None

        if category_id is not None:
            if category_id != 16512:
                url = self.category_url_template.format(api_version='12',
                                                        account_id=self._properties['account_id'],
                                                        broadcaster_id=self._properties['broadcaster_id'],
                                                        category_id=category_id)
                req = self.session.get(url, headers=headers, params=params)
                raw_data2 = json.loads(req.content.decode('utf-8-sig'))
                program_id = [x for x in raw_data2['category']['children'] if x['name'] == 'תוכניות']
                if len(program_id) == 0:
                    raise ValueError
                program_id = program_id[0]
            else:
                # We know the preset value...
                program_id = 16898

            url = self.category_url_template.format(api_version='12',
                                                    account_id=self._properties['account_id'],
                                                    broadcaster_id=self._properties['broadcaster_id'],
                                                    category_id=program_id)
            req = self.session.get(url, headers=headers, params=params)
            raw_data3 = json.loads(req.content.decode('utf-8-sig'))
            sub_objects = [self._prepare_middle_object_from_category_raw_data(x, base_object)
                           for x in raw_data3['category']['children']]
            base_object.add_sub_objects(sub_objects)

    def _prepare_middle_object_from_category_raw_data(self, category_raw_data, super_object):
        """
        Prepares object from raw data.
        :param category_raw_data: Category raw data (dict).
        :param super_object: Super object (CatalogManager).
        :return: New object (CatalogManager).
        """
        image_links = json.loads(category_raw_data['images_json'])
        try:
            format_duration = datetime.strptime(category_raw_data['order_date'], self.time_format)
        except TypeError:
            format_duration = datetime(*(time.strptime(category_raw_data['order_date'], self.time_format)[0:6]))
        return VODCatalogNode(catalog_manager=self.catalog_manager,
                              obj_id=category_raw_data['id'],
                              title=category_raw_data['name'],
                              description=category_raw_data['description']
                              if len(category_raw_data['description']) > 0 else None,
                              image_link=image_links['image_base']
                              if len(image_links['image_base']) > 0 or 'image_2' not in image_links else
                              image_links['image_2'],
                              url=self.category_url_template.format(api_version='12',
                                                                    account_id=self._properties['account_id'],
                                                                    broadcaster_id=self._properties['broadcaster_id'],
                                                                    category_id=category_raw_data['id']),
                              date=format_duration,
                              super_object=super_object,
                              object_type=VODCategories.SHOW,
                              raw_data=category_raw_data,)

    def _prepare_final_object_from_category_raw_data(self, category_raw_data, super_object):
        """
        Prepares object from raw data.
        :param category_raw_data: Category raw data (dict).
        :param super_object: Super object (CatalogManager).
        :return: New object (CatalogManager).
        """
        image_links = json.loads(category_raw_data['images_json'])
        try:
            format_duration = datetime.strptime(category_raw_data['order_date'], self.time_format)
        except TypeError:
            format_duration = datetime(*(time.strptime(category_raw_data['order_date'], self.time_format)[0:6]))
        return VODCatalogNode(catalog_manager=self.catalog_manager,
                              obj_id=category_raw_data['id'],
                              title=category_raw_data['title'],
                              description=category_raw_data['summary']
                              if len(category_raw_data['summary']) > 0 else None,
                              image_link=image_links['image_base']
                              if len(image_links['image_base']) > 0 or 'image_2' not in image_links else
                              image_links['image_2'],
                              url=self.video_url_template.format(api_version='12',
                                                                 account_id=self._properties['account_id'],
                                                                 broadcaster_id=self._properties['broadcaster_id'],
                                                                 source_id=category_raw_data['id']),
                              date=format_duration,
                              super_object=super_object,
                              object_type=VODCategories.VIDEO,
                              raw_data=category_raw_data, )

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data (dict).
        :return:
        """
        # We get the data of the page
        headers = {
            # 'Accept': 'application/json, text/plain, */*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Cache-Control': 'max-age=0',
            # 'Referer': self.base_url,
            # 'Sec-Fetch-Mode': 'cors',
            # 'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'android'
        }
        params = self._prepare_request_params(video_data.url)

        # # For debug purpose
        # tmp_url = url + '?api[bundle]=' + params['api[bundle]']
        # tmp_url += '&api[bver]=' + params['api[bver]']
        # tmp_url += '&api[device_model]=' + params['api[device_model]']
        # tmp_url += '&api[os_type]=' + params['api[os_type]']
        # tmp_url += '&api[os_version]=' + params['api[os_version]']
        # tmp_url += '&api[sig]=' + request_sign
        # tmp_url += '&api[timestamp]=' + str(params['api[timestamp]'])
        # tmp_url += '&api[token]=' + params['api[token]']
        # tmp_url += '&api[uuid]=' + params['api[uuid]']
        # tmp_url += '&api[ver]=' + params['api[ver]']
        # req = self.session.get(tmp_url, headers=headers)
        # tmp_url2 = url + '?' + '&'.join('='.join((k, v)) for k, v in sorted(params.items(), key=lambda x: x[0]))

        params = sorted(((k, v) for k, v in params.items()), key=lambda y: y[0])
        req = self.session.get(video_data.url, headers=headers, params=params)
        if not req.ok:
            raise RuntimeError('Wrong download status. Got {s}'.format(s=req.status_code))
        raw_video_data = req.json()
        video_url = raw_video_data['vod_item']['stream_url']

        video_req = self.session.get(video_url, headers=headers)
        video_m3u8 = m3u8.loads(video_req.text)

        video_playlists = video_m3u8.playlists
        if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
            video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)

        video_objects = [VideoSource(link=urljoin(video_url, x.uri), video_type=VideoTypes.VIDEO_SEGMENTS,
                                     quality=x.stream_info.bandwidth, codec=x.stream_info.codecs)
                         for x in video_playlists]
        return VideoNode(video_sources=video_objects, raw_data=raw_video_data)

    def _get_seasons_from_show_object(self, show_object):
        """
        Fetches the show seasons from show object.
        :param show_object: Show object.
        :return: list of Season objects.
        """
        # In case we have it in our db, we fetch it from, there
        params = self._prepare_request_params(show_object.url)
        req = self.get_object_request(show_object, override_params=params)
        raw_data = json.loads(req.content.decode('utf-8-sig'))
        if (
                'children' in raw_data['category'] and
                len(raw_data['category']['children']) == 1 and
                raw_data['category']['children'][0]['nature'] == 'Season' and
                raw_data['category']['nature'] == 'Show'
        ):
            # We have only one season, so we skip the middle object
            url = self.category_url_template.format(api_version='12',
                                                    account_id=self._properties['account_id'],
                                                    broadcaster_id=self._properties['broadcaster_id'],
                                                    category_id=raw_data['category']['children'][0]['id'])
            req = self.get_object_request(show_object, override_params=params, override_url=url)
            raw_data = json.loads(req.content.decode('utf-8-sig'))

        if 'children' in raw_data['category']:
            sub_key = 'children'
            sub_function = self._prepare_middle_object_from_category_raw_data

        else:
            sub_key = 'vod_items'
            sub_function = self._prepare_final_object_from_category_raw_data

        if len(raw_data['category'][sub_key]) > self.items_per_page:
            # We prepare additional pages
            sub_objects = []
            for i in range(int(math.ceil(len(raw_data['category'][sub_key])) / self.items_per_page)):
                additional_page = VODCatalogNode(catalog_manager=self.catalog_manager,
                                                 obj_id=(show_object.id, i + 1),
                                                 title=show_object.title,
                                                 description=show_object.description,
                                                 image_link=show_object.image_link,
                                                 url=show_object.url,
                                                 page_number=i + 1,
                                                 date=show_object.date,
                                                 super_object=show_object.super_object,
                                                 object_type=VODCategories.SHOW_SEASON,
                                                 raw_data=show_object.raw_data, )
                additional_page_sub_pages = \
                    [sub_function(x, show_object)
                     for x in raw_data['category'][sub_key][self.items_per_page * i:self.items_per_page * (i + 1)]]
                additional_page.add_sub_objects(additional_page_sub_pages)
                sub_objects.append(additional_page)

        else:
            sub_objects = [sub_function(x, show_object) for x in raw_data['category'][sub_key]]

        show_object.add_sub_objects(sub_objects)

        return show_object

    def _update_dynamic_values(self):
        """
        Updates the values for the keys stored in self._dynamic_keys.
        :return:
        """
        if self._default_params['token'] is None:
            rand1 = int((random.random() * 8999) + 1000)
            rand2 = int((random.random() * 8999) + 1000)
            rand3 = int((random.random() * 8999) + 1000)

            device_id = 'd12' + str(rand1) + str(rand2) + str(rand3)
            self._default_params['token'] = device_id
            # # For debug purpose...
            # self._default_params['token'] = 'd12340352978677'

            # hash_device_id = hashlib.sha1()
            # hash_device_id.update((device_id + self._properties['bundle'] + 'android').encode('utf-8'))
            # device_id_seed = hash_device_id.hexdigest()

        # UUID

        # url = self.uuid_url_template.format(bucket_id=self._properties['bucket_id'])
        # params = {
        #     'device[device_model]': self._default_params['device_model'],
        #     'device[os_type]': self._default_params['os_type'],
        #     'device[os_version]': self._default_params['os_version'],
        #     'device[bundle_id]': self._default_params['bundle'],
        #     'device[bundle_version]': self._default_params['bver'],
        #     'device[app]': self._default_params['ver'],
        #     # 'device[app]': 'IBA',
        #     'device[app_id]': self._properties['app_id'],
        #     'device[uuid]': device_id_seed,
        # }
        # headers = {
        #     'Accept': '*/*',
        #     'Content-Type': 'application/json; charset=UTF-8',
        #     'User-Agent': 'android',
        #     'X-Requested-With': 'XMLHttpRequest',
        # }
        # raw_uuid = self.session.post(url, headers=headers, params=params)

        # url += '?device[device_model]=' + quote_plus(self._default_params['device_model'])
        # url += '&device[os_type]=android'
        # url += '&device[os_version]=' + self._default_params['os_type']
        # url += '&device[os_version]=' + self._default_params['os_version']
        # url += '&device[bundle_id]=' + self._default_params['bundle']
        # url += '&device[bundle_version]=' + self._default_params['bver']
        # url += '&device[app_id]=104442'
        # raw_uuid = self.session.post(url, headers=header)

        full_token = uuid.uuid4().hex
        self._default_params['uuid'] = full_token[:24]
        # # For debug purpose...
        # self._default_params['uuid'] = '59d19e58e1b91d46d91795e4'

        data = {k: self._default_params[k] for k in self._dynamic_keys}
        with open(self.episodes_to_data_filename, 'wb') as fl:
            pickle.dump(data, fl)

    def _prepare_request_params(self, url):
        """
        Prepares parameter sign for the given request.
        :param url: Request url.
        :return: Request sign (string).
        """
        # # sig:
        #         localStringBuilder = self.pKey + paramString + self.prepareUrlParams(localParamMap, False) + self.pKey
        #         signedValue = MD5(localStringBuilder)

        timestamp = str(int(time.time()))

        # # For debug purpose...
        # timestamp = '1571524000'

        params = {'api[{k}]'.format(k=k): v for k, v in self._default_params.items() if v is not None}
        params['api[timestamp]'] = timestamp

        # # For debug purpose
        # params = {
        #     'api[bundle]': self._default_params['bundle'],
        #     'api[bver]': self._default_params['bver'],
        #     'api[device_model]': self._default_params['device_model'],
        #     'api[os_type]': self._default_params['os_type'],
        #     'api[os_version]': self._default_params['os_version'],
        #     'api[timestamp]': timestamp,
        #     'api[token]': self._default_params['token'],
        #     'api[uuid]': self._default_params['uuid'],
        #     'api[ver]': self._default_params['ver'],
        # }

        coded_params = '&'.join('='.join((k, v)) for k, v in sorted(params.items(), key=lambda x: x[0]))
        signed_value = self._properties['p_key'] + url + coded_params + self._properties['p_key']
        hash_signed_value = hashlib.md5()
        hash_signed_value.update(signed_value.encode('utf-8'))
        request_sign = hash_signed_value.hexdigest()
        params['api[sig]'] = request_sign

        # params = {'api[{k}]'.format(k=k): v for k, v in self._default_params.items() if v is not None}
        # params['api[timestamp]'] = timestamp
        # params['api[sig]'] = request_sign
        return params

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        raise NotImplementedError

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'User-Agent': self.user_agent
        }
        req = self.session.get(fetch_base_url, headers=headers, params=params)

        return req


if __name__ == '__main__':
    loc_show_id = IdGenerator.make_id('16523')  # מבט
    loc_season_id = IdGenerator.make_id('16524')  # מהדורות מלאות
    # loc_show_id = IdGenerator.make_id('137678')  # 'היום זה אנחנו'
    # loc_season_id = IdGenerator.make_id('4937532')
    kan = IBA(store_dir='D:\\')
    # kan.get_show_object(loc_show_id, loc_season_id)
    # kan.get_video_links_from_video_data('http://admin.applicaster.com/v12/accounts/120/broadcasters/132/vod_items/'
    #                                      '4937532.json')
    # kan.get_seasons(loc_show_id)
    # kan.get_episodes(loc_show_id, loc_season_id)
    # kan.fetch_video_from_episode_url('https://13tv.co.il/item/entertainment/the-voice/season-02/'
    #                                   'episodes/episode1-25/')
    # kan.update_available_shows()
    # kan.download_objects(loc_show_id, verbose=1)
    # kan.download_objects(cat_id, episode_id, episode_id=, verbose=1)
    # kan._get_video_links_from_episode_url('https://www.kan.org.il/program/?catid=1464', verbose=1)
    kan.download_category_input_from_user()
