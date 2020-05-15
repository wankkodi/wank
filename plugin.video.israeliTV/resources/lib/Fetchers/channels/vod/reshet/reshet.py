# -*- coding: UTF-8 -*-
from ....fetchers.vod_fetcher import VODFetcher
# Video catalog
from ....catalogs.vod_catalog import VODCatalogNode, VODCategories, VideoNode, VideoSource, VideoTypes

# Brightcove
from ....tools.common_video_host import Brightcove

# Regex
import re

# JSON
import json

# M3U8
import m3u8

# Datetime
from datetime import datetime, timedelta
import time

# Internet tools
from .... import urljoin


class Reshet(VODFetcher):
    # player_js_template = 'https://players.brightcove.net/{aid}/{pid}_default/index.js'
    # video_fetch_url = 'https://secure.brightcove.com/services/mobile/streaming/index/master.m3u8'
    # video_fetch_url2_template = 'https://edge.api.brightcove.com/playback/v1/accounts/{aid}/videos/{vid}'
    # live_video_request_url_template = 'https://edge.api.brightcove.com/playback/v1/accounts/{uid}/videos/{ref}'
    # live_video_params_template = 'https://players.brightcove.net/{uid}/{lpid}_default/index.js'

    brightcove_external_request_url = 'https://13tv.co.il/Services/getVideoItem.php'
    brightcove_external_request_by_id_url = 'https://13tv-api.oplayer.io/api/getlink/getVideoById'
    cast_time_data_url = 'https://13tv.co.il/wp-content/themes/reshet_tv/build/static/js/main.d89ffc8b.js'
    live_video_request_url_template = 'https://13tv-api.oplayer.io/api/getlink/?userId={uid}&' \
                                      'serverType=web&ch=1&cdnName=casttime'
    stored_video_request_url_template = 'https://13tv-api.oplayer.io/api/getlink/getVideoByFileName?userId={uid}&' \
                                        'videoName={vn}&serverType=web&callback=x'

    bref = 'ref%3Astream_reshet_live1_dvr'
    schedule_url = 'https://13tv.co.il/tv-guide/'
    missed_season_suffix_template = 'season-{s}/episodes/'
    missed_season_suffix_regex = r'season-\d\d/episodes/'

    current_season_suffix = u'פרקים מלאים'
    prev_season_suffix = u'עונות קודמות'

    season_prefix = u"עונה"
    episode_prefix = u"פרק"
    page_prefix = u"עמוד"

    @property
    def object_urls(self):
        return {
            VODCategories.CHANNELS_MAIN: 'https://13tv.co.il/vod/',
            VODCategories.LIVE_VIDEO: 'https://13tv.co.il/live/',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://13tv.co.il/'

    def __init__(self, source_name='Reshet', source_id=-3, store_dir='.', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        """
        super(Reshet, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)
        self.available_shows_partitioned = None
        self.brightcove = Brightcove(self.session, self.user_agent)
        self.site_user_id = None

    def _update_base_categories(self, base_object):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        req = self.get_object_request(base_object)
        raw_data = self._find_page_raw_data(req)

        base_object.add_sub_objects([VODCatalogNode(catalog_manager=self.catalog_manager,
                                                    obj_id=x['post_ID'],
                                                    title=x['title'],
                                                    url=urljoin(self.base_url, x['link']),
                                                    super_object=base_object,
                                                    image_link=x['images']['thumb'],
                                                    object_type=VODCategories.SHOW,
                                                    raw_data=x)
                                     for x in raw_data['items'].values() if x['postType'] == 'page'])

        self.available_shows_partitioned = {x['GridTitle']['title']: x for x in raw_data['blocks']
                                            if 'WpQuery' in x and 'GridTitle' in x}
        # with open(self.available_shows_data_filename, 'wb') as fl:
        #     pickle.dump(self.available_categories, fl)

    def fetch_sub_objects(self, element_object):
        """
        Fetches object's sub objects.
        :param element_object: Object element we want to fetch.
        :return:
        """
        if element_object.object_type == VODCategories.CHANNELS_MAIN:
            return self._update_base_categories(element_object)
        elif element_object.object_type == VODCategories.SHOW:
            return self._get_seasons_from_show_object(element_object)
        elif element_object.object_type == VODCategories.SHOW_SEASON:
            return self._get_episodes_from_season_object(element_object)
        else:
            raise ValueError('Wrong additional_type parameter!')

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data (dict).
        :return:
        """
        # We get the data of the page
        req = self.get_object_request(video_data)
        raw_data = self._find_page_raw_data(req)
        channel_id = raw_data['curItem']

        cookies = None
        if self.site_user_id is None:
            self._update_site_user_id()

        raw_m3u8 = self.brightcove.get_video_links(vid=raw_data[u'items'][str(channel_id)][u'video'][u'videoID'],
                                                   secure=True)

        video_m3u8 = m3u8.loads(raw_m3u8)
        video_playlists = video_m3u8.playlists
        if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
            video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)
        res = [VideoSource(link=urljoin(video_data, x.uri), video_type=VideoTypes.VIDEO_SEGMENTS,
                           quality=x.stream_info.bandwidth, codec=x.stream_info.codecs)
               for x in video_playlists]

        if len(res) == 0:
            # We use another method
            raw_data = self._find_page_raw_data(req)
            channel_id = raw_data['curItem']

            tree = self.parser.parse(req.text)
            script = [x for x in tree.xpath('.//script/text()') if 'accountID' in x]
            assert len(script) == 1
            account_id = re.findall(r'(?:accountID: *\')(\d+)(?:\')', script[0])
            player_id = re.findall(r'(?:playerID: *\')([\w\d]+)(?:\')', script[0])

            new_data = \
                self.brightcove.get_video_links_alt(account_id=account_id[0],
                                                    player_id=player_id[0],
                                                    referer=video_data.url,
                                                    video_id=raw_data[u'items'][str(channel_id)][u'video'][u'videoID'])
            if 'sources' in new_data:
                res = sorted(((x['avg_bitrate'], x['src']) for x in new_data['sources']
                              if 'avg_bitrate' in x and 'src' in x),
                             key=lambda y: y[0], reverse=True)
                res = [VideoSource(link=x[1], video_type=VideoTypes.VIDEO_REGULAR, quality=x[0])
                       for x in res]

        if len(res) == 0:
            # We use another method
            video_ref = raw_data[u'items'][str(channel_id)][u'video']['videoRef']
            new_data = self.get_video_links_alt2(vid=video_ref,
                                                 user_id=self.site_user_id,
                                                 external_request_url=self.brightcove_external_request_url,
                                                 external_request_by_id_url=self.brightcove_external_request_by_id_url)
            # Took from channel 10 (same logic)
            headers3 = {
                'Accept': '*/*',
                'Origin': self.base_url,
                'Referer': video_data.url,
                # 'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }
            request_url = (new_data['ProtocolType'] + new_data['ServerAddress'] + new_data['MediaRoot'] +
                           new_data['MediaFile'][:-4] + new_data['Bitrates'] + new_data['MediaFile'][-4:] +
                           new_data['StreamingType'] + new_data['Token'])
            req3 = self.session.get(request_url, headers=headers3)
            assert req3.ok

            video_m3u8 = m3u8.loads(req3.text)
            video_playlists = video_m3u8.playlists
            if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
                video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)
            res = [VideoSource(link=urljoin(request_url, x.uri), video_type=VideoTypes.VIDEO_SEGMENTS,
                               quality=x.stream_info.bandwidth, codec=x.stream_info.codecs)
                   for x in video_playlists]
            cookies = {k: v for k, v in self.session.cookies.items() if k == 'Cookie'}
        if len(res) == 0:
            url = self.stored_video_request_url_template.format(uid=self.site_user_id,
                                                                vn=video_data.raw_data['video']['cst']['videoRef'])
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                'Host': '13tv.co.il',
                'Referer': self.base_url,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'User-Agent': self.user_agent
            }
            req = self.session.get(url, headers=headers)
            assert req.ok

            raw_data = req.json()
            for new_data in raw_data:
                request_url = (new_data['ProtocolType'] + new_data['ServerAddress'] + new_data['MediaRoot'] +
                               new_data['MediaFile'][:-4] + new_data['Bitrates'] + new_data['MediaFile'][-4:] +
                               new_data['StreamingType'] + new_data['Token'])
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                              'q=0.8,application/signed-exchange;v=b3',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'max-age=0',
                    'Origin': self.base_url,
                    'Referer': self.object_urls[VODCategories.LIVE_VIDEO],
                    'Sec-Fetch-Mode': 'cors',
                    'User-Agent': self.user_agent
                }
                req = self.session.get(request_url, headers=headers)
                assert req.ok

                video_m3u8 = m3u8.loads(req.text)
                video_playlists = video_m3u8.playlists
                if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
                    video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)
                res = [VideoSource(link=urljoin(request_url, x.uri), video_type=VideoTypes.VIDEO_SEGMENTS,
                                   quality=x.stream_info.bandwidth, codec=x.stream_info.codecs)
                       for x in video_playlists]

        return VideoNode(video_sources=res, raw_data=raw_data, cookies=cookies)

    def get_video_links_alt2(self, vid, user_id, external_request_url, external_request_by_id_url):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            # 'Referer': self.shows_url,
            'Sec-Fetch-User': '?1',
            'User-Agent': self.user_agent
        }
        params = {u'v': vid}
        new_req = self.session.get(external_request_url, params=params, headers=headers)
        video_data = new_req.json()
        assert video_data['code'] == 200
        new_video_id = video_data['video_obj']['videoID']
        params = {
            'userId': user_id,
            'videoId': new_video_id,
            'serverType': 'web',
            'callback': 'x',
        }
        new_req = self.session.get(external_request_by_id_url, params=params, headers=headers)
        assert new_req.ok
        video_data = new_req.json()
        return video_data[0]

    def _get_show_seasons_from_show_data(self, show_raw_data, show_object):
        """
        Fetches the show seasons from show data.
        :param show_raw_data: Show raw data.
        :return: List of data objects of show seasons.
        """
        seasons_posts = [y for x in show_raw_data['blocks']
                         if 'GridTitle' in x and x['GridTitle'] is not None and
                         self.prev_season_suffix in x['GridTitle']['title']
                         for y in x['Posts']]
        previous_seasons = [v for x, v in show_raw_data['items'].items() if int(x) in seasons_posts]
        assert len(previous_seasons) == len(seasons_posts), 'Could not find info for one of the previous seasons.'
        possible_season = [x for x in show_raw_data['blocks']
                           if 'GridTitle' in x and x['GridTitle'] is not None
                           and self.current_season_suffix in x['GridTitle']['title']]
        if len(possible_season) == 0 and len(previous_seasons) == 0:
            # We don't have special blocks with previous season prefix.
            # Instead, we try to find it with season prefix...
            previous_seasons = [x for x in show_raw_data['blocks']
                                if 'GridTitle' in x and x['GridTitle'] is not None and
                                self.season_prefix in x['GridTitle']['title']]
            seasons = []
            for previous_season in previous_seasons[::-1]:
                season = previous_season['GridTitle'].copy()
                if not re.findall(self.missed_season_suffix_regex, season['link']):
                    # We must manually add the suffix for the last season
                    season['link'] += \
                        self.missed_season_suffix_template.format(s=str(len(previous_seasons)).zfill(2))
                season['post_ID'] = previous_season['block_id']
                season['images'] = {'thumb': season['images']}
                seasons.append(season)

            if len(seasons) == 0:
                # Probably we don't have a seasons, but only one season...
                return self._get_episodes_from_season_object(show_object)

        elif len(possible_season) == 1:
            # We have format of page block that concentrates the previous seasons
            # assert len(possible_season) == 0, 'Cannot retrieve the current season.'
            current_season = possible_season[0]['GridTitle']
            tmp_season = re.findall(r'(?:season-)(\d\d)', current_season['link'])
            assert len(tmp_season) == 1, 'Wrong format of the season in raw data title.'
            if len(previous_seasons) > 0:
                old_title = previous_seasons[0]['title']
                current_season['title'] = re.sub(r'(?:{p} )(\d*)'.format(p=self.season_prefix),
                                                 r'{p} {s}'.format(p=self.season_prefix, s=int(tmp_season[0])),
                                                 old_title)
                current_season['post_ID'] = possible_season[0]['block_id']
                current_season['images'] = {'thumb': previous_seasons[0]['images']['thumb']}
            else:
                current_season['title'] = self.season_prefix + ' 1'
                current_season['post_ID'] = possible_season[0]['block_id']
                current_season['images'] = {'thumb': current_season['images']}
            seasons = sorted(previous_seasons, key=lambda k: k[u'title']) + [current_season]
        elif len(possible_season) > 1:
            # We have all the seasons in the current_season object
            seasons = sorted(previous_seasons, key=lambda k: k[u'title'])
            for x in possible_season:
                current_season = x['GridTitle']
                current_season['post_ID'] = x['block_id']
                current_season['images'] = {'thumb': current_season['images']}
                seasons.append(current_season)
        else:
            raise RuntimeError('You are not suppose to be here...')

        seasons = [VODCatalogNode(catalog_manager=self.catalog_manager,
                                  obj_id=x['post_ID'],
                                  title=x['title'],
                                  url=urljoin(self.base_url, x['link']),
                                  super_object=show_object,
                                  # image_link=x['images']['thumb'],
                                  image_link=show_object.image_link,
                                  object_type=VODCategories.SHOW_SEASON,
                                  raw_data=x,
                                  )
                   for x in seasons[::-1]]

        for season in seasons:
            self._get_episodes_from_season_object(season)

        return seasons

    def _get_episodes_from_season_object(self, season_object):
        """
        Fetches the season objects from season object.
        :param season_object: Season object.
        :return: list of Episode objects.
        """
        def _get_episodes_from_raw_data(block, r_d):
            e_c = block['Posts']
            e = [v for k, v in r_d['items'].items() if int(k) > 0 and int(k) in e_c]
            return e

        # Fetching the page
        req = self.get_object_request(season_object)
        raw_data = self._find_page_raw_data(req)
        raw_episodes = [x for x in raw_data['blocks']
                        if 'GridTitle' in x and x['GridTitle'] is not None and
                        self.current_season_suffix in x['GridTitle']['title']]
        if len(raw_episodes) == 0:
            # We try another format, the current season title
            raw_episodes = [x for x in raw_data['blocks']
                            if 'GridTitle' in x and x['GridTitle'] is not None and
                            season_object.title in x['GridTitle']['title']]

        if (len(raw_episodes) == 0 and len(raw_data['blocks']) == 1 and
                'GridTitle' in raw_data['blocks'][0] and raw_data['blocks'][0]['GridTitle'] is not None and
                len(raw_data['blocks'][0]['GridTitle']['title']) == 0):
            # If we still here and our raw data have only one element we fetch it
            raw_episodes = [x for x in raw_data['blocks']
                            if 'GridTitle' in x and x['GridTitle'] is not None and x['GridTitle']]

        if len(raw_episodes) == 0:
            raw_episodes = [x for x in raw_data['blocks']
                            if 'class' in x and x['class'] == 'grid_content_1']

        assert len(raw_episodes) == 1, 'Fetched more than one element for season episodes. Review the source.'

        episodes = _get_episodes_from_raw_data(raw_episodes[0], raw_data)
        episodes.sort(key=lambda _x: self._get_episode_number_from_episode_video_data(_x))
        episodes = [
            VODCatalogNode(catalog_manager=self.catalog_manager,
                           obj_id=y['post_ID'],
                           title=y['title'],
                           number=(y['title'].split(': ')[0].split(', ')[2]
                                   if (len(y['title'].split(': ')) > 1 and
                                       len(y['title'].split(': ')[0].split(', ')) == 3)
                                   else ''),
                           url=urljoin(self.base_url, y['link']),
                           image_link=y['images']['thumb'],
                           super_object=season_object,
                           description=y['subtitle'],
                           duration=self._format_duration(y['video']['length']),
                           date=y['publishDate'],
                           object_type=VODCategories.VIDEO,
                           raw_data=y,
                           )
            for y in episodes if y['video'] is not None]
        season_object.add_sub_objects(episodes)
        return episodes

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
        show_raw_data = self._find_page_raw_data(req)

        sub_objects = self._get_show_seasons_from_show_data(show_raw_data, show_object)
        # We update some of the fields
        if show_object.title is None:
            show_object.title = show_raw_data['header']['breadCrumbs'][-1]['title']
        if show_object.image_link is None:
            show_object.image_link = show_raw_data['header']['breadCrumbs'][-1]['images']['thumb']
        # Mandatory fields
        show_object.raw_data = show_raw_data
        show_object.add_sub_objects(sub_objects)

        self.show_data[show_object.id] = show_object

        # with open(self.shows_data_filename, 'wb') as fl:
        #     pickle.dump(self.category_data, fl)
        return show_object

    def _get_episode_number_from_episode_video_data(self, episode_video_data):
        """
        Extracts episode name from episode video data.
        :param episode_video_data: Video data object (dict).
        :return:
        """
        res = re.findall(r'{p} \d*'.format(p=self.episode_prefix), episode_video_data['title'])
        if len(res) == 0:
            # warnings.warn('Found no regular info for episode {e}. Returns its original title.'
            #               ''.format(e=episode_video_data['title']))
            res = [episode_video_data['title']]
        int_episode = re.findall(r'(?:{p} )(\d+)'.format(p=self.episode_prefix), res[0])
        res = (int(int_episode[0]) if len(int_episode) == 1 else 1000,
               re.sub(r'[\\/*?:"<>|]', "", res[0]))
        return res

    def _find_page_raw_data(self, page_request):
        """
        Fetches the raw data about the page from the given fetched page object.
        :param page_request: Page request object
        :return: JSON data of the page.
        """
        tree = self.parser.parse(page_request.text)
        scripts = tree.xpath('.//script')
        scripts = [x for x in scripts if x.text is not None and 'data_query' in x.text]
        if len(scripts) > 1:
            raise RuntimeError('Found more than 1 possible script. Revise your code!')
        if len(scripts) == 0:
            raise RuntimeError('Found no possible script. Revise your code!')
        script = scripts[0].text
        raw_data = re.findall(r'(?:data_query = )({.*})', script)
        assert len(raw_data) == 1, 'Wrongly fetched json data.'
        raw_data = json.loads(raw_data[0])
        return raw_data

    @staticmethod
    def _format_duration(raw_duration):
        """
        Formats the duration of the given video.
        :param raw_duration: Raw duration (string with minutes).
        :return: Duration in seconds (int).
        """
        return int(raw_duration) // 1000

    def get_live_stream_info(self):
        """
        Fetches the live stream data.
        :return: CatalogNode object.
        """
        if 'schedule' not in self.live_data:
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                'Host': '13tv.co.il',
                'Referer': self.base_url,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'User-Agent': self.user_agent
            }
            req = self.session.get(self.schedule_url, headers=headers)
            raw_data = self._find_page_raw_data(req)

            self.live_data['schedule'] = raw_data

        now_time = datetime.now()
        daily_schedule = \
            self.live_data['schedule']['Content']['PageGrid'][0]['broadcastWeek']['0']['broadcastDayList']
        day_schedule = [x for x in daily_schedule if datetime.fromtimestamp(x['timestamp']).date() == now_time.date()]
        assert len(day_schedule) == 1
        day_schedule = day_schedule[0]

        prev_day_schedule = [x for x in daily_schedule
                             if datetime.fromtimestamp(x['timestamp']).date() == now_time.date() - timedelta(days=1)]
        if len(prev_day_schedule) == 0:
            # We take the previous day as the last day of the previous week
            prev_week_daily_schedule = \
                self.live_data['schedule']['Content']['PageGrid'][-1]['broadcastWeek']['0']['broadcastDayList']
            prev_day_schedule = prev_week_daily_schedule[-1]
        else:
            prev_day_schedule = prev_day_schedule[0]

        try:
            current_program = [x for x in prev_day_schedule['shows']
                               if x['show_date'] == 0 and
                               datetime.combine(now_time.date(),
                                                datetime.strptime(x['start_time'], '%H:%M').time()) < now_time]
            current_program += [x for x in day_schedule['shows']
                                if x['show_date'] > 0 and
                                datetime.combine(now_time.date(),
                                                 datetime.strptime(x['start_time'], '%H:%M').time()) < now_time]
        except TypeError:
            current_program = [x for x in prev_day_schedule['shows']
                               if x['show_date'] == 0 and x['start_time'] is not None and
                               datetime.combine(now_time.date(),
                                                datetime(*(time.strptime(x['start_time'], '%H:%M')[0:6])).time()) <
                               now_time]
            current_program += [x for x in day_schedule['shows']
                                if x['show_date'] > 0 and x['start_time'] is not None and
                                datetime.combine(now_time.date(),
                                                 datetime(*(time.strptime(x['start_time'], '%H:%M')[0:6])).time()) <
                                now_time]

        if len(current_program) == 0:
            raise RuntimeError('No live shows found!')
        current_program = current_program[-1]
        return VODCatalogNode(catalog_manager=self.catalog_manager,
                              obj_id=('live', current_program['title']),
                              title=current_program['title'],
                              description=current_program['page_category'],
                              image_link=current_program['images']['thumb'],
                              object_type=VODCategories.LIVE_SCHEDULE,
                              )

    def get_live_stream_video_link(self):
        """
        Fetches the live stream video_link.
        :return: VideoNode object.
        """
        if 'raw_data' not in self.live_data:
            self._fetch_live_video_raw_data()

        # video_urls = self.live_data['raw_data']['sources']
        video_urls = self.live_data['raw_data']
        res = []
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Origin': self.base_url,
            'Referer': self.object_urls[VODCategories.LIVE_VIDEO],
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': self.user_agent
        }
        for video_url in video_urls:
            new_req = self.session.get(video_url['Link'], headers=headers)
            video_m3u8 = m3u8.loads(new_req.text)
            video_playlists = video_m3u8.playlists
            if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
                video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)

            res.extend([VideoSource(link=urljoin(video_url['Link'], x.uri), video_type=VideoTypes.VIDEO_SEGMENTS,
                                    quality=x.stream_info.bandwidth, codec=x.stream_info.codecs)
                        for x in video_playlists])
        request_headers = {'Origin': self.base_url,
                           'Referer': self.object_urls[VODCategories.LIVE_VIDEO],
                           'Sec-Fetch-Mode': 'cors',
                           'User-Agent': self.user_agent
                           }

        return VideoNode(video_sources=res, raw_data=self.live_data['raw_data'], headers=request_headers)

    def _fetch_live_video_raw_data(self):
        """
        Fetches live video raw data.
        :return:
        """
        # Old impleentation, now obsolete
        # if 'raw_data' not in self.live_data:
        #     self.live_data['raw_data'] = \
        #         self.brightcove.fetch_live_video_raw_data(live_url=self.object_urls[VODCategories.LIVE_VIDEO],
        #                                                   referer=self.object_urls[VODCategories.CHANNELS_MAIN],
        #                                                   bref=self.bref)
        #
        # if 'sources' not in self.live_data['raw_data'] or len(self.live_data['raw_data']['sources']) == 0:
        #     raise RuntimeError('Wrong format of the live video raw data. Recheck it!')

        if self.site_user_id is None:
            self._update_site_user_id()
        url = self.live_video_request_url_template.format(uid=self.site_user_id)
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Host': '13tv.co.il',
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'User-Agent': self.user_agent
        }
        req = self.session.get(url, headers=headers)
        assert req.ok
        self.live_data['raw_data'] = req.json()

        if len(self.live_data['raw_data']) == 0 or 'Link' not in self.live_data['raw_data'][0]:
            raise RuntimeError('Wrong format of the live video raw data. Recheck it!')

    def get_object_request(self, page_data, override_page_number=None, override_params=None, override_url=None):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :param override_page_number: Override page number.
        :param override_params: Override params.
        :param override_url: Override url.
        :return: Page request
        """
        if page_data.object_type in (VODCategories.VIDEO, VODCategories.SHOW_SEASON, VODCategories.SHOW):
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                # 'Referer': self.shows_url,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'User-Agent': self.user_agent
            }
        else:
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                'Host': '13tv.co.il',
                'Referer': self.base_url,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'User-Agent': self.user_agent
            }

        req = self.session.get(page_data.url, headers=headers)
        return req

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        raise NotImplementedError

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        raise NotImplementedError

    def _update_site_user_id(self):
        """
        Updates site user id.
        :return:
        """
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Host': '13tv.co.il',
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'User-Agent': self.user_agent
        }
        req = self.session.get(self.cast_time_data_url, headers=headers)
        assert req.ok
        self.site_user_id = re.findall(r'(?:"data-ccid":")(.*?)(?:")', req.text)[0]

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Reshet, self)._version_stack + [self.__version]
