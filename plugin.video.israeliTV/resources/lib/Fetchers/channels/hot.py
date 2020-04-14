# -*- coding: UTF-8 -*-
from ..fetchers.vod_fetcher import VODFetcher
# Video catalog
from ..catalogs.vod_catalog import VODCatalogNode, VODCategories, VideoNode, VideoSource, VideoTypes

# Regex
import re

# Warnings and exceptions
# import warnings

# # JSON
import json

# M3U8
import m3u8

# ID generator
from ..id_generator import IdGenerator

# Internet tools
from .. import urljoin, parse_qs, urlparse
# from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qs, urlencode


class Hot(VODFetcher):
    episode_request_url_template = 'http://hot.ynet.co.il/Ext/Comp/Hot/TopSeriesPlayer_Hot/' \
                                   'CdaTopSeriesPlayer_VidItems_Hot/0,13031,L-{shid}-{sid}-0-0,00.html'
    video_link_template = 'http://hot.ynet.co.il/home/0,7340,L-{sid}-{vid},00.html'
    season_titles = {u'פרקים מלאים', u'הסרט המלא', u'הצצות', u'מאחורי הקלעים', u'השחקנים'}

    season_prefix = u"עונה"
    episode_prefix = u"פרק"
    dummy_id_key = 'dummy_id'

    @property
    def object_urls(self):
        return {
            VODCategories.CHANNELS_MAIN: 'http://hot.ynet.co.il/home/0,7340,L-7250,00.html',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://hot.ynet.co.il/home/'

    def __init__(self, vod_name='Hot', vod_id=-6, store_dir='.', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        # self.episodes_to_data = {}
        self.season_to_show = {}
        super(Hot, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)
        self.available_shows = [x for x in self.dummy_super_object.sub_objects
                                if x.object_type == VODCategories.CHANNELS_MAIN][0]

    def _update_base_categories(self, base_object):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        req = self.get_object_request(base_object)
        tree = self.parser.parse(req.text)
        xpath = './/div[@id="topSldDiv_Vert"]/table/tbody/tr/td/div/a'
        shows = tree.xpath(xpath)

        res = []
        for show in shows:
            if 'href' not in show.attrib:
                continue

            x = VODCatalogNode(catalog_manager=self.catalog_manager,
                               obj_id=self._get_show_id_from_url(show.attrib['href']),
                               title=show.text,
                               url=urljoin(self.base_url, show.attrib['href']),
                               image_link=None,
                               super_object=base_object,
                               object_type=VODCategories.SHOW,
                               raw_data=None)
            # x = {'link': urljoin(self.base_url, show.attrib['href']),
            #      'title': show.text,
            #      'id': page_id,
            #      }
            res.append(x)

        base_object.add_sub_objects(res)
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
        # elif element_object.object_type == 'season':
        #     return self._get_episodes_from_season_object(element_object)
        else:
            raise ValueError('Wrong additional_type parameter!')

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data (dict).
        :return:
        """
        # We get the data of the page
        # episode_data = self.episodes_to_data[url]
        # link_url = self.video_link_template.format(sid=episode_data.raw_data['show_id'],
        #                                            vid=episode_data.raw_data['id'])
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': self.object_urls[VODCategories.CHANNELS_MAIN],
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'User-Agent': self.user_agent
        }
        req = self.session.get(video_data.url, headers=headers)
        tree = self.parser.parse(req.text)
        scripts = tree.xpath('.//meta[@property="og:video"]/@content')
        assert len(scripts) == 1
        playlist_url = 'http:' + scripts[0]
        playlist_url = json.loads(parse_qs(urlparse(playlist_url).query)['config'][0])
        playlist_url = playlist_url['clip']['url']
        if 'f4m' in playlist_url:
            # # Original:
            # replacePath = function(url, type, isProgresive) {
            #     var newUrl = url;
            #
            #     if(type == 4){
            #
            #             newUrl = url.replace(/ynethd-i.akamaihd.net/g, 'vod.ynet-cdnwiz.com');
            #             newUrl = newUrl.replace(/ynethd-f.akamaihd.net/g, 'vod.ynet-cdnwiz.com');
            #
            #     } else {
            #         newUrl = url.replace(/vod.ynet-cdnwiz.com/g, 'ynethd-i.akamaihd.net');
            #         newUrl = url.replace(/ynethd-f.akamaihd.net\/z/g, 'ynethd-i.akamaihd.net/i');
            #     }
            #
            #     if (newUrl.indexOf('.f4m') > -1) {
            #         newUrl = newUrl.replace(/manifest.f4m/g, 'master.m3u8');
            #         newUrl = newUrl.replace(/z\/cdnwiz/g, 'i/cdnwiz');
            #     }
            #
            #     if(isProgresive && type == 4)
            #         newUrl = newUrl.replace(/vod.ynet/g, 'cdn.ynet');
            #
            #         newUrl = newUrl.replace('http://','https://');
            #
            #    return newUrl
            # };

            playlist_url = re.sub(r'vod.ynet-cdnwiz.com', 'ynethd-i.akamaihd.net', playlist_url)
            playlist_url = re.sub(r'ynethd-f.akamaihd.net/z', 'ynethd-i.akamaihd.net/i', playlist_url)
            playlist_url = re.sub(r'manifest.f4m', 'master.m3u8', playlist_url)
            playlist_url = re.sub(r'/z/', '/i/', playlist_url)
            playlist_url = re.sub(r'vod\.ynet', 'cdn.ynet', playlist_url)
            playlist_url = re.sub(r'http://', 'https://', playlist_url)

        video_m3u8 = self.get_video_m3u8(playlist_url)
        video_playlists = video_m3u8.playlists
        if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
            video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)
        # for video_playlist in video_playlists:
        #     modified_fetch_url = urljoin(video_prefix, video_playlist.uri)
        #     res.append(modified_fetch_url)

        # return VideoNode(video_data=[x.uri for x in video_playlists], raw_data=self.episodes_to_data[url])
        return VideoNode(video_sources=[VideoSource(link=x.uri, video_type=VideoTypes.VIDEO_SEGMENTS,
                                                    quality=x.stream_info.bandwidth, codec=x.stream_info.codecs)
                                        for x in video_playlists])

    def get_video_m3u8(self, video_link):
        """
        Fetches the video m3u8 list.
        :param video_link: Video url.
        :return: Video m3u8 (m3u8 object).
        """
        headers = {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            # 'Referer': 'https://www.mako.co.il/mako-vod?partner=NavBar',
            'Sec-Fetch-Mode': 'cors',
            # 'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        # params.update({'type': 'service', 'device': 'desktop', 'strto': 'desktop'})
        req = self.session.get(video_link, headers=headers)
        # req = self.session.get(video_fetch_url, params=params)
        if req.status_code != 200:
            raise RuntimeError('Wrong download status. Got {s}'.format(s=req.status_code))
        video_m3u8 = m3u8.loads(req.text)

        return video_m3u8

    def _get_seasons_from_show_object(self, show_object):
        """
        Fetches the show seasons from show object.
        :param show_object: Show object.
        :return: list of Season objects.
        """
        if show_object.id in self.show_data:
            return self.show_data[show_object.id]
        show_data = self._fetch_show_data(show_object)

        self.show_data[show_object.id] = show_data
        # with open(self.shows_data_filename, 'wb') as fl:
        #     pickle.dump(self.category_data, fl)
        return show_data

    def _fetch_show_data(self, show_object):
        """
        Fetches the raw data about the page from the given fetched page object.
        :param show_object: Show object which will be updated.
        :return: JSON data of the page.
        """
        req = self.get_object_request(show_object)
        tree = self.parser.parse(req.text)
        res = {}
        # General information
        prescription = tree.xpath('.//meta[@name="description"]/@content')
        assert len(prescription) == 1
        res['prescription'] = prescription[0]

        title = tree.xpath('.//title[@lang="he"]/text()')
        assert len(title) == 1
        title = title[0].split(' - ')
        assert len(title) > 2
        title = ' - '.join(title[2:])
        res['title'] = title

        image = re.findall(r'(?:previewImage_\\\' src=\\\')(.*?)(?:\\\')', req.text)
        assert len(image) == 1
        res['image'] = image[0]

        related_shows = []
        sub_objects = []
        main_sub_objects = []
        season_par = [x for x in tree.xpath('.//tr') if 'id' in x.attrib and re.findall(r'tr_\d', x.attrib['id'])]
        for par in season_par:
            link = par.attrib['onclick']
            if 'window.location' in link:
                season_link = re.findall(r'(?:window.location=\')(.*)(?:\')', link)[0]
                season_type = 'related_show'
                season_id = self._get_show_id_from_url(season_link)
            else:
                season_link = req.url
                season_type = 'season'
                season_id = re.findall(r'(?:topSrsLoadVidItems\()(\d+)(?:\);)', link)
                assert len(season_id) == 1
                season_id = season_id[0]

            season_name = (par.xpath('./td[@class="topSrsMenuItem"]/div/text()') +
                           par.xpath('./td[@class="topSrsMenuItem"]/text()'))
            assert len(season_name) == 1
            season_name = re.sub(r'^ *', '', re.sub(r' *$', '', season_name[0]))
            show_id = re.findall(r'(?:L-)(\d+)(?:,)', season_link)
            assert len(show_id) == 1

            if season_type == 'related_show':
                short_raw_object = {'link': urljoin(self.base_url, season_link),
                                    'season': season_name,
                                    'show_id': show_id[0],
                                    'season_id': season_id,
                                    'season_type': season_type,
                                    }
                related_show = self.search_show(short_raw_object['show_id'])
                # We don't need to recreate the show, unless id doesn't exists
                if len(related_show) == 0:
                    short_show = VODCatalogNode(catalog_manager=self.catalog_manager,
                                                obj_id=short_raw_object['season_id'],
                                                title=short_raw_object['season'],
                                                url=urljoin(self.base_url, short_raw_object['link']),
                                                super_object=self.available_shows,
                                                object_type=VODCategories.SHOW,
                                                raw_data=short_raw_object,
                                                )
                    main_sub_objects.append(short_show)

                related_shows.extend(related_show)
            elif season_type == 'season':
                season_raw_object = {'link': urljoin(self.base_url, season_link),
                                     'season': season_name,
                                     'show_id': show_id[0],
                                     'season_id': season_id,
                                     'season_type': season_type,
                                     }
                self.season_to_show[season_raw_object['link']] = res
                season_obj = VODCatalogNode(catalog_manager=self.catalog_manager,
                                            obj_id=season_raw_object['season_id'],
                                            title=season_raw_object['season'],
                                            url=urljoin(self.base_url, season_raw_object['link']),
                                            super_object=show_object,
                                            raw_data=season_raw_object,
                                            object_type=VODCategories.SHOW_SEASON,
                                            )

                sub_objects.append(season_obj)
                self._fetch_season_data(season_obj)

        show_object.add_sub_objects(sub_objects)
        show_object.add_additional_objects(related_shows)
        self.available_shows.add_sub_objects(main_sub_objects)

        # Update the missed values
        if show_object.title is None:
            show_object.title = res['title']
        if show_object.image_link is None:
            show_object.image_link = res['image']
        if show_object.subtitle is None:
            show_object.subtitle = res['prescription']
        # Mandatory update the new fields
        show_object.raw_data = res

        return show_object

    def _fetch_season_data(self, season_object):
        """
        Fetches season videos.
        :param season_object: Season object.
        :return:
        """
        # Now we fetch the videos on the page
        # Finding the video link.
        # We check if we need to add another hidden videos to our analysis
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            # 'Referer': self.shows_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        request_url = self.episode_request_url_template.format(shid=season_object.raw_data['show_id'],
                                                               sid=season_object.raw_data['season_id'])
        req = self.session.get(request_url, headers=headers)
        tree = self.parser.parse(req.text)
        video_raw_data = [x for x in tree.xpath('.//input[@type="hidden"]')
                          if 'id' in x.attrib and 'vidN_' in x.attrib['id']]

        sub_objects = []
        for video_raw_datum in video_raw_data:
            video_data = {'id': re.findall(r'\d+', video_raw_datum.attrib['id'])[0],
                          'link': self.video_link_template.format(sid=season_object.raw_data['show_id'],
                                                                  vid=season_object.raw_data['season_id'])
                          }
            image_link = tree.xpath('.//img[@id="topSrsImg{vid}"]'.format(vid=video_data['id']))
            assert len(image_link) == 1
            video_data['image_link'] = image_link[0].attrib['src']

            episode_info_data = [x for x in tree.xpath('.//div')
                                 if 'id' in x.attrib and
                                 'topSrsVidTxt{i}'.format(i=video_data['id']) in x.attrib['id']]
            assert len(episode_info_data) == 1
            raw_title = episode_info_data[0].xpath('./font[1]/b/text()')
            assert len(raw_title) == 1
            raw_title = self._clear_text(raw_title[0]).split(' - ')
            episode_number = [x for x in raw_title if self.episode_prefix in x]
            episode_number = episode_number[0] if len(episode_number) > 0 else ''
            episode_name = [x for x in raw_title if self.season_prefix not in x and self.episode_prefix not in x]
            episode_name = ' - '.join(episode_name) if len(episode_name) > 0 else ''
            video_data['season'] = ''
            video_data['episode_title'] = episode_name
            video_data['episode'] = episode_number
            video_data['show_id'] = season_object.raw_data['show_id']
            raw_description = episode_info_data[0].xpath('./font[2]/text()')
            if len(raw_description) == 1:
                raw_description = self._clear_text(raw_description[0])
                video_data['description'] = raw_description
            else:
                video_data['description'] = ''

            video_link_url = self.video_link_template.format(sid=video_data['show_id'],
                                                             vid=video_data['id'])

            episode = VODCatalogNode(catalog_manager=self.catalog_manager,
                                     obj_id=video_data['id'],
                                     title=video_data['episode_title'],
                                     number=video_data['episode'],
                                     # url=urljoin(self.base_url, video_data['link']),
                                     url=urljoin(self.base_url, video_link_url),
                                     super_object=season_object,
                                     image_link=video_data['image_link'],
                                     subtitle=video_data['description'],
                                     raw_data=video_data,
                                     object_type=VODCategories.VIDEO,
                                     )

            sub_objects.append(episode)
            # self.episodes_to_data[episode.url] = episode

        season_object.add_sub_objects(sub_objects)
        return season_object.sub_objects

    @staticmethod
    def _get_show_id_from_url(show_url):
        """
        Parse the show id from it's url.
        :param show_url: Show url
        :return:
        """
        return re.findall(r'(?:L-)(\d+)(?:,)', show_url)[0]

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        raise NotImplemented

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url,
                                override_params=None):
        if override_params is not None:
            params.update(override_params)
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


class HotEight(Hot):
    shows_url = 'http://hot.ynet.co.il/home/0,7340,L-7461,00.html'

    def __init__(self, vod_name='Channel8', vod_id=-7, store_dir='.\\Hot\\', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(HotEight, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)


class HotThree(Hot):
    shows_url = 'http://hot.ynet.co.il/home/0,7340,L-7456,00.html'

    def __init__(self, vod_name='Channel3', vod_id=-8, store_dir='.\\Hot\\', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(HotThree, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)


class HotBidur(Hot):
    shows_url = 'http://hot.ynet.co.il/home/0,7340,L-7261,00.html'

    def __init__(self, vod_name='HotBidur', vod_id=-9, store_dir='.\\Hot\\', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(HotBidur, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)


class HotYoung(Hot):
    shows_url = 'http://hot.ynet.co.il/home/0,7340,L-7449,00.html'

    def __init__(self, vod_name='HotYoung', vod_id=-10, store_dir='.\\Hot\\', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(HotYoung, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)


class HotZoom(Hot):
    shows_url = 'http://hot.ynet.co.il/home/0,7340,L-11527,00.html'

    def __init__(self, vod_name='HotZoom', vod_id=-11, store_dir='.\\Hot\\', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(HotZoom, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)


if __name__ == '__main__':
    # loc_show_id = IdGenerator.make_id('12425')
    # loc_season_id = IdGenerator.make_id('12425')
    loc_show_id = IdGenerator.make_id('26414')
    loc_season_id = IdGenerator.make_id('525')
    hot = HotThree()
    # hot.get_show_object(loc_show_id)
    # hot.get_show_object(loc_show_id, loc_season_id)
    # hot.get_video_links_from_video_data('http://hot.ynet.co.il/home/0,7340,L-26414-340808,00.html')
    # hot.update_available_shows()
    # hot.download_objects(loc_show_id, verbose=1)
    hot.download_category_input_from_user()
