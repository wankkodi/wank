# -*- coding: UTF-8 -*-
from ....fetchers.vod_fetcher import VODFetcher
# Video catalog
from ....catalogs.vod_catalog import VODCatalogNode, VODCategories, VideoNode, VideoSource, VideoTypes

# Regex
import re

# System
from os import path
import pickle

# # JSON
import json

# M3U8
# import m3u8


class One(VODFetcher):
    qualities = {
        'URLStreamHD': {'quality': 1080, 'codec': ''},
        'URLStreamSD': {'quality': 360, 'codec': 'H264'},
        'URLStreamMobile': {'quality': 480, 'codec': 'H264'},
        'URLStreamFailover': {'quality': 480, 'codec': 'H264'},
    }
    video_category_url = 'https://www.one.co.il/Cat/Video/Default.aspx/GetVideos?vod={c}&page={p}'

    dummy_id_key = 'dummy_id'

    @property
    def object_urls(self):
        return {
            VODCategories.CHANNELS_MAIN: 'https://www.one.co.il/VOD/',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.one.co.il/'

    def __init__(self, vod_name='One', vod_id=-14, store_dir='.', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(One, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)

        self.episodes_to_data_filename = path.join(self.fetcher_data_dir, 'one_episodes_to_data.dat')
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
        else:
            return self._get_items_from_show_object(element_object)

    def _update_base_categories(self, base_object):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
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
            'User-Agent': self.user_agent
        }

        req = self.session.get(base_object.url, headers=headers)
        tree = self.parser.parse(req.text)
        xpath = './/ul[@id="one-vod-categories"]/li/a'
        shows = tree.xpath(xpath)

        sub_objects = []
        for show in shows:
            show_data = show.xpath('./span')[0]
            show_image = show.xpath('./img')[0]
            category_id = re.findall(r'\d*$', show_data.attrib['class'])[0]
            x = VODCatalogNode(catalog_manager=self.catalog_manager,
                               obj_id=show_data.attrib['class'],
                               title=show_data.text,
                               url=self.video_category_url.format(c=category_id, p=1),
                               image_link=show_image.attrib['src'],
                               super_object=base_object,
                               object_type=VODCategories.SHOW,
                               raw_data=None)
            sub_objects.append(x)
        base_object.add_sub_objects(sub_objects)

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data (dict).
        :return:
        """
        # We get the data of the page
        object_ids = self.episodes_to_data[video_data.url]
        episode_object = self.get_show_object(*object_ids)

        res = []
        for x in ('URLStreamHD', 'URLStreamSD', 'URLStreamMobile', 'URLStreamFailover'):
            if episode_object.raw_data[x] is not None and len(episode_object.raw_data[x]) > 0:
                params = {'link': episode_object.raw_data[x], 'video_type': VideoTypes.VIDEO_SEGMENTS}
                params.update(self.qualities[x])
                res.append(VideoSource(**params))
        return VideoNode(video_sources=res, raw_data=episode_object.raw_data)

    def _get_items_from_show_object(self, show_object):
        """
        Fetches the show seasons from show object.
        :param show_object: Show object.
        :return: list of Season objects.
        """
        # In case we have it in our db, we fetch it from, there
        if show_object.id in self.show_data:
            return self.show_data[show_object.id]

        req = self.get_object_request(show_object)
        show_raw_data = json.loads(req.text)
        show_raw_data = json.loads(show_raw_data['d'])
        # At first we add the additional objects
        number_of_pages = self._get_number_of_sub_pages(show_object, req)
        if show_object.object_type is not VODCategories.PAGE and number_of_pages > 1:
            self._add_category_sub_pages(show_object, VODCategories.PAGE, req)
            show_object = show_object.sub_objects[0]

        # Now we add the sub objects
        items = json.loads(show_raw_data['Items'])
        show_object.add_sub_objects([VODCatalogNode(catalog_manager=self.catalog_manager,
                                                    obj_id=x['ID'],
                                                    title=x['Title'],
                                                    subtitle=x['TitleSeconadry'],
                                                    url=x['URLPermanent'],
                                                    image_link=x['ImageURL'],
                                                    super_object=show_object,
                                                    date=x['Date'],
                                                    object_type=VODCategories.VIDEO,
                                                    raw_data=x)
                                     for x in items])

        save_flag = False
        if show_object.sub_objects is not None:
            for x in show_object.sub_objects:
                ids = []
                tmp_object = x
                while 1:
                    ids.append(tmp_object.id)
                    if tmp_object.super_object is None:
                        break
                    tmp_object = tmp_object.super_object

                ids = tuple(ids[1::-1])
                if x.url not in self.episodes_to_data or self.episodes_to_data[x.url] != ids:
                    self.episodes_to_data[x.url] = ids
                    save_flag = True
            if save_flag is True:
                with open(self.episodes_to_data_filename, 'wb') as fl:
                    pickle.dump(self.episodes_to_data, fl)

        return show_object

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
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=utf-8',
            'Host': self.host_name,
            # 'Referer': self.shows_url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        req = self.session.get(page_data.url, headers=headers)
        return req

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        raise NotImplementedError

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        if fetched_request is None:
            fetched_request = self.get_object_request(category_data)
        show_raw_data = json.loads(fetched_request.text)
        show_raw_data = json.loads(show_raw_data['d'])
        return show_raw_data['NumOfPages']

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(One, self)._version_stack + [self.__version]
