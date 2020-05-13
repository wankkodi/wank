# -*- coding: UTF-8 -*-
from ....fetchers.vod_fetcher import VODFetcher
# Video catalog
from ....catalogs.vod_catalog import VODCatalogNode, VODCategories, VideoNode, VideoSource, VideoTypes

# System
from os import path
import pickle

# JSON
import json

# M3U8
import m3u8


class Sport5(VODFetcher):
    video_fetch_url = 'https://vod.sport5.co.il/HTML/External/VodCentertDS.txt'
    video_category_url = 'https://vod.sport5.co.il/ajax/GetAllCategories.aspx/GettMessage'

    dummy_id_key = 'dummy_id'

    @property
    def object_urls(self):
        return {
            VODCategories.CHANNELS_MAIN: 'https://vod.sport5.co.il/',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://vod.sport5.co.il/'

    def __init__(self, source_name='Sport5', source_id=-13, store_dir='.', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(Sport5, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)
        self.episodes_to_data_filename = path.join(self.fetcher_data_dir, 'sport5_episodes_to_data.dat')
        if not path.isfile(self.episodes_to_data_filename):
            self.episodes_to_data = {}
        else:
            with open(self.episodes_to_data_filename, 'rb') as fl:
                self.episodes_to_data = pickle.load(fl)

    def fetch_sub_objects(self, element_object):
        """
        Fetches object's sub objects.
        :param element_object: Object element we want to fetch.
        :return:
        """
        if element_object.object_type == VODCategories.CHANNELS_MAIN:
            return self._update_base_categories(element_object)
        elif element_object.object_type == VODCategories.GENERAL_CHANNEL_SUB_CATEGORY:
            return self._get_seasons_from_show_object(element_object)
        else:
            raise RuntimeError('Unsupported object type {ot}'.format(ot=element_object.object_type))

    def _update_base_categories(self, base_object):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        headers = {
            'Accept': 'application/json, text/plain, */*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }

        req = self.session.get(self.video_fetch_url, headers=headers)
        raw_data = json.loads(req.content.decode('utf-8-sig'))
        self._add_categories_recursively(base_object, raw_data['Category']['Category'])

        # with open(self.available_shows_data_filename, 'wb') as fl:
        #     pickle.dump(self.available_categories, fl)

    def _update_sub_categories(self, update_object=None):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        headers = {
            'Accept': 'application/json, text/plain, */*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }

        req = self.session.get(update_object.url, headers=headers)
        raw_data = json.loads(req.content.decode('utf-8-sig'))
        self._add_categories_recursively(update_object, raw_data['Category']['Category'])

        # with open(self.available_shows_data_filename, 'wb') as fl:
        #     pickle.dump(self.available_categories, fl)

    def _add_categories_recursively(self, category_object, raw_subcategories):
        """
        Creates the Elements for the given values and append them in the category object sub categories.
        :param category_object: Category object.
        :param raw_subcategories: List of raw subcategories.
        :return:
        """
        sub_objects = []
        for raw_subcategory in raw_subcategories:
            new_object = VODCatalogNode(catalog_manager=self.catalog_manager,
                                        obj_id=raw_subcategory['ID'],
                                        title=raw_subcategory['Name'],
                                        url=self.video_category_url,
                                        super_object=category_object,
                                        object_type=VODCategories.GENERAL_CHANNEL_SUB_CATEGORY,
                                        raw_data=raw_subcategory)
            sub_objects.append(new_object)
            if 'Category' in raw_subcategory:
                if type(raw_subcategory['Category']) == list:
                    self._add_categories_recursively(new_object, raw_subcategory['Category'])
                elif type(raw_subcategory['Category']) == dict:
                    self._add_categories_recursively(new_object, [raw_subcategory['Category']])
                else:
                    raise ValueError('Wrong type of input for subcategories of the title {t}.'
                                     ''.format(t=new_object.title))

        category_object.add_sub_objects(sub_objects)

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data (dict).
        :return:
        """
        # We get the data of the page
        episode_object = self.episodes_to_data[video_data.url]

        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            # 'Referer': 'https://www.mako.co.il/mako-vod?partner=NavBar',
            'Sec-Fetch-Mode': 'cors',
            # 'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        req = self.session.get(episode_object.raw_data['stream_url'], headers=headers)
        if req.status_code != 200:
            raise RuntimeError('Wrong download status. Got {s}'.format(s=req.status_code))
        video_m3u8 = m3u8.loads(req.text)

        video_playlists = video_m3u8.playlists
        if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
            video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)
        video_objects = [VideoSource(link=x.uri, video_type=VideoTypes.VIDEO_SEGMENTS,
                                     quality=x.stream_info.bandwidth, codec=x.stream_info.codecs)
                         for x in video_playlists]

        return VideoNode(video_sources=video_objects, raw_data=episode_object.raw_data)

    def _get_seasons_from_show_object(self, show_object):
        """
        Fetches the show seasons from show object.
        :param show_object: Show object.
        :return: list of Season objects.
        """
        # In case we have it in our db, we fetch it from, there
        if show_object.id in self.show_data:
            return self.show_data[show_object.id]
        req = self.get_object_request(show_object)
        sub_objects = []
        show_raw_data = json.loads(req.content.decode('utf-8-sig'))
        if type(show_raw_data['Category']['Category']['Items']['Item']) is list:
            shows = show_raw_data['Category']['Category']['Items']['Item']
        else:
            shows = [show_raw_data['Category']['Category']['Items']['Item']]
        for x in shows:
            new_episode = VODCatalogNode(catalog_manager=self.catalog_manager,
                                         obj_id=x['doc_id'],
                                         title=x['title'],
                                         url=x['url'],
                                         image_link=x['img_upload'],
                                         super_object=show_object,
                                         date=x['video_date'],
                                         object_type=VODCategories.VIDEO,
                                         raw_data=x)
            sub_objects.append(new_episode)
            self.episodes_to_data[new_episode.url] = new_episode
        show_object.add_sub_objects(sub_objects)

        if len(show_raw_data['Category']['Category']['Items']['Item']) > 0:
            with open(self.episodes_to_data_filename, 'wb') as fl:
                pickle.dump(self.episodes_to_data, fl)

        return show_object

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Get number of pages from category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        raise NotImplementedError

    def get_object_request(self, page_data, override_page_number=None, override_params=None, override_url=None):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :param override_page_number: Override page number.
        :param override_params: Override params.
        :param override_url: Override url.
        :return: Page request
        """
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        params = {
            'catID': page_data.raw_data['ID'],
        }
        req = self.session.get(page_data.url, headers=headers, params=params)
        return req

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        raise NotImplementedError

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Sport5, self)._version_stack + [self.__version]
