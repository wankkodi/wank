# -*- coding: UTF-8 -*-
from ....fetchers.vod_fetcher import VODFetcher
# Video catalog
from ....catalogs.vod_catalog import VODCatalogNode, VODCategories, VideoNode, VideoSource, VideoTypes

# Playlist tools
import m3u8

# Warnings and exceptions
# import warnings

# Datetime
from datetime import datetime, timedelta
import time

# Internet tools
from .... import urljoin, urlparse, unquote_plus, quote

# Abstract
from abc import abstractmethod, ABCMeta


class Base(VODFetcher):
    metaclass = ABCMeta

    time_format = '%H:%M:%S'
    time_format_2 = '%M:%S'
    video_fetch_url = 'https://www.mako.co.il/AjaxPage'
    video_token_url = 'https://mass.mako.co.il/ClicksStatistics/entitlementsServicesV2.jsp'
    video_vod_prefixes = {'AKAMAI': 'https://makostore-vh.akamaihd.net',
                          'CASTTIME': 'https://makostore-hd.ctedgecdn.net'}
    video_live_prefixes = {'AKAMAI': 'https://keshethlslive-i.akamaihd.net',
                           'CASTTIME': 'https://makostore-hdl.ctedgecdn.net'
                           }

    season_prefix = u"עונה"
    episode_prefix = u"פרק"

    max_search_results_per_page = 50

    israel_time_timedelta = timedelta(seconds=3*3600)

    @property
    def object_urls(self):
        return {
            VODCategories.CHANNELS_MAIN: 'https://www.mako.co.il/mako-vod-index',
            VODCategories.LIVE_VIDEO: 'https://www.mako.co.il/AjaxPage',
            VODCategories.SEARCH_MAIN: 'https://www.mako.co.il/autocomplete/vodAutocompletion.ashx',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.mako.co.il/'

    def __init__(self, vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id):
        """
        C'tor
        :param vod_name: save directory
        """
        super(Base, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)

    @abstractmethod
    def _update_base_categories(self, base_object):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        raise NotImplementedError

    def fetch_sub_objects(self, element_object):
        """
        Fetches object's sub objects.
        :param element_object: Object element we want to fetch.
        :return:
        """
        if element_object.object_type == VODCategories.CHANNELS_MAIN:
            return self._update_base_categories(element_object)
        elif element_object.object_type in (VODCategories.SHOW_SEASON, VODCategories.SHOW, ):
            return self._get_show_from_show_object(element_object)
        elif element_object.object_type in (VODCategories.SEARCH_MAIN,):
            return self._get_search_objects(element_object)
        elif element_object.object_type in (VODCategories.LIVE_VIDEO,):
            return self.get_live_stream_video_link()
        # elif element_object.object_type == 'episodes':
        #     return self._get_episodes_show_object(element_object)
        else:
            raise ValueError('Wrong additional_type parameter!')

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data (dict).
        :return:
        """
        # We get the data of the page
        params = dict((x.split('=') for x in video_data.url.split('?')[1].split('&'))) \
            if len(video_data.url.split('?')) > 0 else {}
        # params = dict((x.split('=') for x in parse_url.query.split('&')))
        params['type'] = 'service'
        params['device'] = 'desktop'
        new_url = video_data.url.split('?')[0]
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'User-Agent': self.user_agent
        }
        req = self.session.get(new_url, params=params, headers=headers)
        video_data = req.json()
        channel_id = video_data['root']['video']['chId']
        gallery_channel_id = video_data['root']['video']['galleryChId']
        guid = video_data['root']['video']['guid']
        video_links = self._fetch_best_video_links_from_channel_data(channel_id, gallery_channel_id, guid)
        return VideoNode(video_sources=video_links, raw_data=video_data)

    def _fetch_best_video_links_from_channel_data(self, channel_id, gallery_channel_id, guid):
        """
        Fetches the video from a given parameters.
        :param channel_id: Channel id.
        :param gallery_channel_id:  Gallery id.
        :param guid: GUID.
        :return: Video link.
        """
        # if video_source_indicator == 'vod':
        #     video_source_prefix = self.video_vod_prefixes
        # elif video_source_indicator == 'live':
        #     video_source_prefix = self.video_live_prefixes
        # else:
        #     raise ValueError('The \'video_source_indicator\' variable can be either \'vod\' or \'live\'. '
        #                      'Got {v} instead!'.format(v=video_source_indicator))

        video_data = self.get_video_data_for_channel(channel_id, gallery_channel_id, guid)
        # extra_params = (dict(y.split('=') for y in video_data['videoDetails']['extraParams'].split(','))
        #                 if 'videoDetails' in video_data and 'extraParams' in video_data['videoDetails'] else {})
        video_data = sorted(video_data['media'], key=lambda k: k['cdn'])
        res = []
        for x in video_data:
            request_video_link = x['url']
            request_video_type = x['cdn']
            video_token = self.get_token_for_playlist(request_video_link, request_video_type, gallery_channel_id)
            assert video_token['caseId'] == '1', 'Cannot fetch video token for video {v}'.format(v=request_video_link)

            # video_prefix = video_source_prefix[video_token['tickets'][0]['vendor']]
            url = x['url']
            # url += '&' if len(url.split('?')) > 1 else '?'
            # url += '&'.join('='.join((k, v)) for k, v in extra_params.items())

            video_url = urljoin(request_video_link, unquote_plus(url))
            video_m3u8 = self.get_video_m3u8(video_url, video_token)
            video_playlists = video_m3u8.playlists
            if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
                video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)
            for video_playlist in video_playlists:
                res.append(VideoSource(link=urljoin(request_video_link, video_playlist.uri),
                                       video_type=VideoTypes.VIDEO_SEGMENTS,
                                       quality=video_playlist.stream_info.bandwidth,
                                       codec=video_playlist.stream_info.codecs))

        return res

    def get_more_videos_for_the_same_channel(self, channel_id):
        """
        Fetches the data witht hte links to the rest of the series of the same channel.
        :param channel_id: Channel id.
        :return: Video page data (JSON).
        """
        video_fetch_url = self.video_fetch_url
        params = {
            'jspName': 'FlashVODMoreOnChannel.jsp',
            'type': 'service',
            'channelId': channel_id,
            'device': 'desktop',
            'strto': True,
        }
        req = self.session.get(video_fetch_url, params=params)
        res = req.json()
        return res

    def get_video_data_for_channel(self, video_channel_id, gallery_channel_id, vcm_id):
        """
        Fetches the video page data.
        :param video_channel_id: Channel id.
        :param gallery_channel_id: Gallery channel id.
        :param vcm_id: Video channel mannager id.
        :return: Video page data (JSON).
        """
        video_fetch_url = self.video_fetch_url
        params = {
            'jspName': 'playlist.jsp',
            'vcmid': vcm_id,
            'videoChannelId': video_channel_id,
            'galleryChannelId': gallery_channel_id,
            'isGallery': False,
            'consumer': 'web_html5',
            'encryption': 'no',
        }
        req = self.session.get(video_fetch_url, params=params)
        res = req.json()
        return res

    def get_token_for_playlist(self, video_url, video_type, gallery_channel_id):
        """
        Fetches token for the given video url.
        :param video_url: Video url.
        :param video_type: Video type.
        :param gallery_channel_id: Gallery channel id.
        :return: Video page data (JSON).
        """
        video_fetch_url = self.video_token_url
        params = {
            'et': 'ngt',
            'lp': self._get_playlist_request_url_suffix(video_url),
            'rv': video_type,
            'dv': gallery_channel_id,
            # 'dac': '4CD25596-EF6F-4E88-97FD-B92B1B2432FE',
            # 'du': 'WEFCE6A122493-9D83-16D8-9490AFDE229B',
        }
        req = self.session.post(video_fetch_url, params=params)
        res = req.json()
        return res

    @staticmethod
    def _get_playlist_request_url_suffix(video_url):
        """
        Prepares the playlist link for the given video url
        :param video_url: Video url.
        :return: Playlist url.
        """
        return urlparse(video_url).path

    def get_video_m3u8(self, video_link, video_token):
        """
        Fetches the video m3u8 list.
        :param video_link: Video url.
        :param video_token: Video token.
        :return: Video m3u8 (m3u8 object).
        """
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            # 'Referer': 'https://www.mako.co.il/mako-vod?partner=NavBar',
            'Sec-Fetch-Mode': 'cors',
            # 'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        params = self._get_request_params_from_token(video_token)

        req = self.session.get(video_link, params=params, headers=headers)
        if not req.ok:
            # new_video_link = video_link + u'?' + u'&'.join(u'='.join(z.decode('utf-8') for z in (x, y))
            #                                                for x, y in list(params.items())[::-1])
            new_video_link = video_link + u'?'
            if u'btoken' in params:
                ordered_params = (u'btoken', u'str', u'exp')
            elif u'ctoken' in params:
                ordered_params = (u'ctoken', u'str', u'exp')
            elif u'hdnea' in params:
                ordered_params = params.keys()
            else:
                raise RuntimeError('Unknown type of params. Recheck the algorithm...')
            for x in ordered_params:
                new_video_link += x + u'=' + quote(params[x]) + u'&'
            new_video_link = new_video_link[:-1]
            req = self.session.get(new_video_link, headers=headers)

        if req.status_code != 200:
            raise RuntimeError('Wrong download status. Got {s}'.format(s=req.status_code))
        video_m3u8 = m3u8.loads(req.text)

        return video_m3u8

    def search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        if self._previous_search_query == query:
            return self.objects[VODCategories.SEARCH_MAIN]

        self._previous_search_query = query
        search_element = self.objects[VODCategories.SEARCH_MAIN]
        search_element.clear_additional_objects()
        search_element.clear_sub_objects()
        search_element.additional_data = \
            {'params': {'query': [query],
                        '&max': [self.max_search_results_per_page],
                        'id': ['query', '123'],
                        'type': ['mobile_vod_rich'],
                        }
             }

        # request = self.get_object_request(search_element)

        return search_element

    def _prepare_new_search_query(self, query):
        raise NotImplemented

    def _get_search_objects(self, search_element):
        # req = self.session.get(self.search_url, headers=headers, params=params)
        req = self.get_object_request(search_element, override_params=search_element.additional_data['params'])

        assert req.ok
        raw_res = req.json()
        res = []
        for x in raw_res['data']:
            if len(x['guid']) > 0:
                # We have a page link
                if self.catalog_manager.is_node(x['guid']):
                    res.append(self.catalog_manager.get_node(x['guid']))
                else:
                    res.append(VODCatalogNode(catalog_manager=self.catalog_manager,
                                              obj_id=x['guid'],
                                              title=x['label'],
                                              url=urljoin(self.base_url, x['url']),
                                              image_link=x['picB'],
                                              super_object=self.objects[VODCategories.SEARCH_MAIN],
                                              description=x['subtitle'],
                                              object_type=VODCategories.SHOW,
                                              raw_data=x))
            else:
                # We have a video link
                if self.catalog_manager.is_node(x['vcmId']):
                    res.append(self.catalog_manager.get_node(x['vcmId']))
                else:
                    res.append(VODCatalogNode(catalog_manager=self.catalog_manager,
                                              obj_id=x['vcmId'],
                                              title=x['label'],
                                              url=urljoin(self.base_url, x['url']),
                                              image_link=x['picB'],
                                              super_object=self.objects[VODCategories.SEARCH_MAIN],
                                              description=x['subtitle'],
                                              duration=(self._format_duration(x['duration'])
                                                        if x['duration'] is not None else None),
                                              date=x['date'],
                                              object_type=VODCategories.VIDEO,
                                              raw_data=x))
        self.objects[VODCategories.SEARCH_MAIN].add_sub_objects(res)
        return self.objects[VODCategories.SEARCH_MAIN]

    @staticmethod
    def _get_request_params_from_token(request_token):
        """
        Returns request params from the request token.
        :param request_token: Request token
        :return: Request params (dict).
        """
        raw_data = request_token['tickets'][0]['ticket'].split('&')
        raw_data = {unquote_plus(x.split('=')[0]): unquote_plus(x.split('=')[1]) for x in raw_data}
        return raw_data

    def _get_show_from_show_object(self, show_object):
        """
        Fetches the show seasons from show object.
        :param show_object: Show object.
        :return: list of Season objects.
        """
        # In case we have it in our db, we fetch it from, there
        if show_object.id in self.show_data:
            return self.show_data[show_object.id]

        params = {
            'type': 'service',
            'device': 'desktop',
            'strto': True,
        }
        # req = self.session.get(show_object.url, headers=headers, params=params)
        req = self.get_object_request(show_object, override_params=params)

        show_raw_data = req.json()
        # Update the missed values
        if show_object.title is None:
            show_object.title = show_raw_data['root']['programData']['title']
        if show_object.image_link is None:
            show_object.image_link = show_raw_data['root']['programData']['picVOD'] \
                if len(show_raw_data['root']['programData']['picVOD']) > 0 \
                else show_raw_data['root']['programData']['logoPicE4']
        # Mandatory update the new fields
        show_object.raw_data = show_raw_data
        show_sub_objects = []

        for x in show_raw_data['root']['programData']['seasons']:
            season = VODCatalogNode(catalog_manager=self.catalog_manager,
                                    obj_id=x['id'],
                                    title=x['name'],
                                    url=urljoin(self.base_url, x['url']),
                                    image_link=show_object.image_link,
                                    super_object=show_object,
                                    sub_objects=[],
                                    subtitle=x['shortSubtitle'],
                                    description=x['brief'],
                                    object_type=VODCategories.SHOW_SEASON,
                                    raw_data=x,
                                    )
            season_sub_objects = []
            for y in x['vods'][::-1]:
                episode = VODCatalogNode(catalog_manager=self.catalog_manager,
                                         obj_id=y['guid'],
                                         title=y['title'],
                                         number=(y['title'].split(' - ')[0]
                                                 if len(y['title'].split(' - ')) > 1 else ''),
                                         url=urljoin(self.base_url, y['link']),
                                         image_link=y['picUrl'],
                                         super_object=season,
                                         subtitle=y['shortSubtitle'],
                                         description=y['subtitle'],
                                         duration=self._format_duration(y['duration'])
                                         if y['duration'] is not None and len(y['duration']) > 0 else None,
                                         date=y['date'],
                                         object_type=VODCategories.VIDEO,
                                         raw_data=y,
                                         )
                season_sub_objects.append(episode)

            season.add_sub_objects(season_sub_objects)
            show_sub_objects.append(season)

        show_object.add_sub_objects(show_sub_objects)
        self.show_data[show_object.id] = show_object
        # with open(self.shows_data_filename, 'wb') as fl:
        #     pickle.dump(self.category_data, fl)
        return show_object

    def _format_duration(self, raw_duration):
        """
        Formats the duration of the given video.
        :param raw_duration: Raw duration of the form HH:MM:SS (i.e. u'00:58:28').
        :return: Duration in seconds (int).
        """
        if len(raw_duration.split(':')) == 2:
            time_format = self.time_format_2
        elif len(raw_duration.split(':')) == 3:
            time_format = self.time_format
        else:
            raise ValueError('Wrong time format!')

        try:
            format_duration = datetime.strptime(raw_duration, time_format)
        except TypeError:
            format_duration = datetime(*(time.strptime(raw_duration, time_format)[0:6]))

        return format_duration.hour * 3600 + format_duration.minute * 60 + format_duration.second

    def get_live_stream_info(self):
        """
        Fetches the live stream data.
        :return: CatalogNode object.
        """
        if 'raw_data' not in self.live_data:
            # We update the live page
            self._update_live_page_data()

        self._update_live_schedule_data()

        now_time = datetime.now()
        current_program = [x for x in self.live_data['live_schedule']['programs']
                           if datetime.utcfromtimestamp(x['StartTimeUTC']/1000) + self.israel_time_timedelta <
                           now_time]

        if len(current_program) == 0:
            raise RuntimeError('No live shows found!')
        current_program = current_program[-1]

        res = VODCatalogNode(catalog_manager=self.catalog_manager,
                             obj_id=current_program['ProgramCode'],
                             title=current_program['ProgramName'],
                             description=current_program['EventDescription'],
                             image_link=current_program['Picture'],
                             object_type=VODCategories.LIVE_SCHEDULE,
                             )
        return res

    def get_live_stream_video_link(self):
        """
        Fetches the live stream video_link.
        :return: VideoNode object.
        """
        if 'live_show_data' not in self.live_data:
            self._update_live_show_data()

        channel_id = self.live_data['live_show_data']['chId']
        gallery_channel_id = self.live_data['live_show_data']['galleryChId']
        guid = (self.live_data['live_show_data']['guid'] if 'guid' in self.live_data['live_show_data']
                else self.live_data['live_show_data']['Guid'])
        video_links = self._fetch_best_video_links_from_channel_data(channel_id, gallery_channel_id, guid)
        return VideoNode(video_sources=video_links, raw_data=self.live_data['live_show_data'])

    @abstractmethod
    def _update_live_page_data(self):
        """
        Updates the live page data.
        :return:
        """
        raise NotImplementedError

    def _update_live_schedule_data(self):
        """
        Updates the live schedule data.
        :return:
        """
        video_fetch_url = self.video_fetch_url
        params = {
            'jspName': 'EPGPlayerResponse.jsp',
        }
        req = self.session.get(video_fetch_url, params=params)
        res = req.json()
        self.live_data['live_schedule'] = res
        if 'programs' not in self.live_data['live_schedule'] or len(self.live_data['live_schedule']['programs']) == 0:
            raise RuntimeError('The structure of the live page has changed. Recheck the code!')

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        raise NotImplementedError

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
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
        url = page_data.url
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.mako.co.il/mako-vod?partner=NavBar',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        params = {
            'type': 'service',
            'device': 'desktop',
        }
        if override_params is not None:
            params.update(override_params)
        req = self.session.get(url, headers=headers, params=params)
        return req

    @abstractmethod
    def _update_live_show_data(self):
        """
        Updates the live page data.
        :return:
        """
        raise NotImplementedError

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Base, self)._version_stack + [self.__version]
