# -*- coding: UTF-8 -*-
from ..fetchers.vod_fetcher import VODFetcher
# Video catalog
from ..catalogs.vod_catalog import VODCatalogNode, VODCategories, VideoNode, VideoSource, VideoTypes

# Regex
import re

# Warnings and exceptions
import warnings

# JSON
import json

# # System
# from os import path
# import pickle

# Datetime
from datetime import datetime
import time

# M3U8
import m3u8

# Math
import math

# ID generator
from ..id_generator import IdGenerator

# Internet tools
from .. import urljoin, urlparse, parse_qs


class Kan(VODFetcher):
    # video_fetch_url = 'https://secure.brightcove.com/services/mobile/streaming/index/master.m3u8'
    # live_tv_url = 'https://www.kan.org.il/live/tv.aspx?stationid=2'
    schedule_url = 'https://www.kan.org.il/tv-guide/tv_guidePrograms.ashx'
    additional_content_page = 'https://www.kan.org.il/program/getMoreProgram.aspx'

    # search_url = 'https://cse.google.com/cse/element/v1'
    # search_params_url = 'https://cse.google.com/cse.js'
    number_of_results_per_page = 6
    # search_default_params = {
    #     'rsz': 'filtered_cse',
    #     'num': number_of_results_per_page,
    #     'hl': 'iw',
    #     'source': 'gcsc',
    #     'gss': '.il',
    #     'cselibv': None,
    #     'cx': None,
    #     'safe': 'off',
    #     'cse_tok': None,
    #     'sort': '',
    #     'exp': 'csqr,cc',
    #     'gs_l': 'artner-generic.3...17065.18940.0.19283.7.7.0.0.0.0.131.784.1j6.7.0.gsnos,'
    #             'n=13...0.2758j1804806j9...1.34.partner-generic..3.4.511.r1WkKWB6Qio',
    #     'callback': 'google.search.cse.api14287'
    #
    # }

    youtube_hostname = ('www.youtube.com', 'www.google.com')
    kan_hostname = ('www.kan.co.il', 'kanapi.media.kan.org.il')
    kan_raw_hostname = ('www.kan.org.il', )
    kan_download_hostname = ('kanvod.media.kan.org.il', 'kanapi.media.kan.org.il')

    schedule_index = 1
    schedule_date_format = '%d/%m/%Y'
    season_prefix = u"עונה"
    episode_prefix = u"פרק"
    dummy_id_key = 'dummy_id'

    @property
    def object_urls(self):
        return {
            VODCategories.CHANNELS_MAIN: 'https://www.kan.org.il/page.aspx?landingPageId=1039',
            VODCategories.LIVE_VIDEO: 'https://www.kan.org.il/live/tv.aspx?stationid=2',
            VODCategories.SEARCH_MAIN: 'https://cogito3.com/kansearch/',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.kan.org.il/'

    def __init__(self, vod_name='Kan', vod_id=-4, store_dir='.', data_dir='../../Data', source_type='VOD',
                 session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        # self.season_to_show = {}
        self.special_show_parsing = {
            'https://www.kan.org.il/page.aspx?landingpageid=1135': self._fetch_show_data_1135,
            'https://www.kan.org.il/page.aspx?landingPageId=1135': self._fetch_show_data_1135,
            'https://www.kan.org.il/program/?catId=1274': self._fetch_show_data_1135,
            'https://www.kan.org.il/page.aspx?landingPageId=1274': self._fetch_show_data_1135,
        }
        super(Kan, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, session_id)

    def fetch_sub_objects(self, element_object):
        """
        Fetches object's sub objects.
        :param element_object: Object element we want to fetch.
        :return:
        """
        if element_object.object_type == VODCategories.CHANNELS_MAIN:
            return self._update_base_categories(element_object)
        if element_object.object_type == VODCategories.SHOW:
            return self._fetch_show_data(element_object)
        if element_object.object_type == VODCategories.SHOW_SEASON:
            return self._fetch_season_objects(element_object)
        if element_object.object_type == VODCategories.SEARCH_MAIN:
            return self._get_search_from_show_object(element_object)
        if element_object.object_type == VODCategories.SEARCH_PAGE:
            return self._get_search_sub_objects_from_search_object(element_object)
        elif element_object.object_type == VODCategories.LIVE_VIDEO:
            return self.get_live_stream_info()
        else:
            raise ValueError('Wrong additional_type parameter!')

    def _update_base_categories(self, base_object):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        req = self.get_object_request(base_object)
        tree = self.parser.parse(req.text)
        xpath = './/div[@class="sm_it_fullsection spacing"]/div[@class="component_sm_item news"]/' \
                'a[@class="component_news_biglink black w-inline-block"]'
        shows = tree.xpath(xpath)

        base_object.add_sub_objects(self._get_show_objects_from_show_news_trees(shows, base_object))
        # with open(self.available_shows_data_filename, 'wb') as fl:
        #     pickle.dump(self.available_categories, fl)

    def _get_show_objects_from_show_news_trees(self, show_trees, super_object):
        """
        Parses the show objects from the given show_trees.
        :param show_trees: Show trees of the show nodes (as they implemented in the Kan site).
        :param super_object: Super object of the created show objects.
        :return: List of CatalogNode objects.
        """
        res = []
        for show in show_trees:
            if 'href' not in show.attrib:
                continue
            title = show.xpath('./div/@title')[0]
            title = self._clear_text(title)
            subtitle = show.xpath('./div[@class="news_up_group hiddenDescDiv"]/div[@class="news_up_txt"]')[0]
            subtitle = self._clear_text(subtitle.text) if subtitle.text is not None else None
            image_link = re.findall(r'(?:url\(\')(.*)(?:\')', show.xpath('./div/@style')[0])[0]
            try:
                page_id = self._get_page_id_from_page_url(show.attrib['href'])
            except ValueError:
                if urlparse(show.attrib['href']).hostname == 'www.youtube.com':
                    # We have a single episode show
                    x = VODCatalogNode(catalog_manager=self.catalog_manager,
                                       obj_id=show.attrib['href'],
                                       title=title,
                                       url=show.attrib['href'],
                                       image_link=image_link,
                                       description=subtitle,
                                       object_type=VODCategories.VIDEO,
                                       super_object=super_object)
                    res.append(x)
                    continue
                else:
                    warnings.warn('Wrong format of the link for the title {t}!'.format(t=title))
                    continue
            x = VODCatalogNode(catalog_manager=self.catalog_manager,
                               obj_id=page_id,
                               title=title,
                               url=urljoin(self.base_url, show.attrib['href']),
                               image_link=image_link,
                               description=subtitle,
                               object_type=VODCategories.SHOW,
                               super_object=super_object)
            res.append(x)
        return res

    def _get_show_objects_from_show_magazine_trees(self, show_trees, super_object):
        """
        Parses the show objects from the given show_trees.
        :param show_trees: Show trees of the show nodes (as they implemented in the Kan site).
        :param super_object: Super object of the created show objects.
        """
        res = []
        for show in show_trees:
            if 'href' not in show.attrib:
                continue
            title = show.xpath('./div[@class="magazine_info_group"]/h2[@class="magazine_info_title"]')[0]
            title = self._clear_text(title.text)
            subtitle = show.xpath('./div[@class="magazine_info_group"]/div[@class="magazine_txt_inner "]/'
                                  'div[@class="magazine_info_txt"]')[0]
            subtitle = self._clear_text(subtitle.text)
            image_link = re.findall(r'(?:url\(\')(.*)(?:\')', show.xpath('./div/@style')[0])[0]
            try:
                page_id = self._get_page_id_from_page_url(show.attrib['href'])
            except ValueError:
                if urlparse(show.attrib['href']).hostname == 'www.youtube.com':
                    # We have a single episode show
                    x = VODCatalogNode(catalog_manager=self.catalog_manager,
                                       obj_id=show.attrib['href'],
                                       title=title,
                                       url=show.attrib['href'],
                                       image_link=image_link,
                                       description=subtitle,
                                       object_type=VODCategories.VIDEO,
                                       super_object=super_object)
                    res.append(x)
                    continue
                else:
                    warnings.warn('Wrong format of the link for the title {t}!'.format(t=title))
                    continue
            x = VODCatalogNode(catalog_manager=self.catalog_manager,
                               obj_id=page_id,
                               title=title,
                               url=urljoin(self.base_url, show.attrib['href']),
                               image_link=image_link,
                               description=subtitle,
                               object_type=VODCategories.SHOW,
                               super_object=super_object)
            res.append(x)
        return res

    def _get_show_objects_from_show_main_component_trees(self, show_trees, super_object):
        """
        Parses the show objects from the given show_trees.
        :param show_trees: Show trees of the show nodes (as they implemented in the Kan site).
        :param super_object: Super object of the created show objects.
        :return: List of VODCatalogNode objects.
        """
        res = []
        for show in show_trees:
            if 'href' not in show.attrib:
                continue
            title = show.xpath('.//div[@class="component_big_infogroup"]/'
                               'h1[@class="component_big_title news "]')[0]
            title = self._clear_text(title.text)
            subtitle = show.xpath('.//div[@class="component_big_infogroup"]/p')[0]
            subtitle = self._clear_text(subtitle.text)
            image_link = re.findall(r'(?:url\(\')(.*)(?:\')', show.xpath('./div/@style')[0])[0]
            try:
                page_id = self._get_page_id_from_page_url(show.attrib['href'])
            except ValueError:
                warnings.warn('Wrong format of the link for the title {t}!'.format(t=title))
                continue
            x = VODCatalogNode(catalog_manager=self.catalog_manager,
                               obj_id=page_id,
                               title=title,
                               url=urljoin(self.base_url, show.attrib['href']),
                               image_link=image_link,
                               description=subtitle,
                               object_type=VODCategories.SHOW,
                               super_object=super_object)
            res.append(x)
        return res

    def _get_show_objects_from_show_small_component_trees(self, show_trees, super_object):
        """
        Parses the show objects from the given show_trees.
        :param show_trees: Show trees of the show nodes (as they implemented in the Kan site).
        :param super_object: Super object of the created show objects.
        :return: List of VODCatalogNode objects.
        """
        res = []
        for show in show_trees:
            if 'href' not in show.attrib:
                continue
            title = show.xpath('./h3[@class="component sm_il_videotitle"]/text()')[0]
            title = self._clear_text(title)
            subtitle = show.xpath('./p/text()')[0]
            subtitle = self._clear_text(subtitle)
            try:
                page_id = self._get_page_id_from_page_url(show.attrib['href'])
            except ValueError:
                warnings.warn('Wrong format of the link for the title {t}!'.format(t=title))
                continue
            image_link = re.findall(r'(?:url\(\')(.*)(?:\')', show.xpath('./div/@style')[0])[0]
            x = VODCatalogNode(catalog_manager=self.catalog_manager,
                               obj_id=page_id,
                               title=title,
                               url=urljoin(self.base_url, show.attrib['href']),
                               image_link=image_link,
                               description=subtitle,
                               object_type=VODCategories.SHOW,
                               super_object=super_object)
            res.append(x)
        return res

    def _get_show_objects_from_it_small_component_trees(self, show_trees, super_object):
        """
        Parses the show objects from the given show_trees.
        :param show_trees: Show trees of the show nodes (as they implemented in the Kan site).
        :param super_object: Super object of the created show objects.
        :return: List of VODCatalogNode objects.
        """
        res = []
        for show in show_trees:
            image_link = urljoin(self.base_url, re.findall(r'(?:url\(\')(.*)(?:\'\);)', show.attrib['style'])[0])
            title = show.attrib['alt']
            url = urljoin(self.base_url, show.xpath('./a')[0].attrib['href'])
            try:
                page_id = self._get_page_id_from_page_url(url)
            except ValueError:
                warnings.warn('Wrong format of the link for the title {t}!'.format(t=title))
                continue
            x = VODCatalogNode(catalog_manager=self.catalog_manager,
                               obj_id=page_id,
                               title=title,
                               url=url,
                               image_link=image_link,
                               object_type=VODCategories.SHOW,
                               super_object=super_object)
            res.append(x)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data (dict).
        :return:
        """
        if urlparse(video_data.url).hostname in self.youtube_hostname:
            # We try to fetch the KAN video from search option
            if video_data.additional_data is not None and 'id' in video_data.additional_data:
                dummy_object = VODCatalogNode(catalog_manager=self.catalog_manager,
                                              obj_id=(video_data.id, 1),
                                              title='',
                                              url=self.object_urls[VODCategories.SEARCH_MAIN],
                                              additional_data={'params': {'q': video_data.additional_data['id'],
                                                                          'start': 0}
                                                               }
                                              )
                search_raw_results, req = self._get_raw_search_data(dummy_object)
                if len(search_raw_results['items']) == 1:
                    video_data.url = search_raw_results['items'][0]['url']

        return self._get_video_links_from_video_url(video_data.url)

    def _get_video_links_from_video_url(self, url):
        """
        Fetches the video property from the given page.
        :param url: video url.
        The dummy parameter is used to find the proper episode by its id.
        :return: VideoNode object.
        """
        # We get the data of the page
        split_url = urlparse(url)
        if split_url.hostname in self.youtube_hostname:
            video_objects = [VideoSource(link=url, video_type=VideoTypes.VIDEO_YOUTUBE)]
        elif split_url.hostname in self.kan_hostname:
            video_objects = self._get_playlist_of_kan_source(url)
        elif split_url.hostname in self.kan_raw_hostname:
            video_objects = self._get_playlist_of_kan_raw_source(url)
        else:
            raise RuntimeError('Wrong video hostname {h}.'.format(h=split_url.hostname))
        return VideoNode(video_sources=video_objects)

    @staticmethod
    def _get_page_id_from_page_url(page_url):
        """
        Parses the page id from page ur.
        :param page_url: Page url
        :return:
        """
        page_id = parse_qs(urlparse(page_url.lower()).query)
        if 'landingpageid' in page_id:
            # todo: to make private case. have different page structure!
            page_id = page_id['landingpageid'][0]
        elif 'catid' in page_id:
            if 'subcatid' in page_id:
                page_id = (page_id['catid'][0], page_id['subcatid'][0])
            else:
                page_id = page_id['catid'][0]
        elif 'itemid' in page_id:
            page_id = page_id['itemid'][0]
        else:
            raise ValueError
        return page_id

    def _get_playlist_of_kan_source(self, url):
        """
        Returns the playlist of Kan source
        :param url: video URL.
        :return: list of links to video, sorted by bandwidth.
        """
        headers = {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            # 'Referer': self.shows_url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            # 'Sec-Fetch-User': '?1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest'
        }
        req = self.session.get(url, headers=headers)
        playlist_url = re.findall(r'(?:let objModel = )({.*})', req.text)
        assert len(playlist_url) == 1
        playlist_url = json.loads(playlist_url[0])
        # We have inner KAN video link
        req = self.session.get(playlist_url['UrlRedirector'], headers=headers)

        video_m3u8 = m3u8.loads(req.text)
        video_playlists = video_m3u8.playlists
        if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
            video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)
        video_objects = [VideoSource(link=x.uri, video_type=VideoTypes.VIDEO_SEGMENTS,
                                     quality=x.stream_info.bandwidth, codec=x.stream_info.codecs)
                         for x in video_playlists]
        return video_objects

    def _get_playlist_of_kan_raw_source(self, url):
        """
        Returns the playlist of Kan source
        :param url: video URL.
        :return: list of links to video, sorted by bandwidth.
        """
        headers = {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            # 'Referer': self.shows_url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            # 'Sec-Fetch-User': '?1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest'
        }
        req = self.session.get(url, headers=headers)
        # We have external YouTube video link
        res = re.findall(r'(?:<iframe.*src=\\")(.*?)(?:\\")', req.text)
        if any(urlparse(x).hostname in self.kan_hostname for x in res):
            res = self._get_playlist_of_kan_source(res[0])

        if len(res) == 0:
            # We use another format
            episode_tree = self.parser.parse(req.text)
            res = episode_tree.xpath('.//div/iframe/@src')
            assert len(res) > 0
            if len(res) == 1 and urlparse(res[0]).hostname in self.youtube_hostname:
                return [VideoSource(link=res[0], video_type=VideoTypes.VIDEO_YOUTUBE)]
            else:
                return [VideoSource(link=x, video_type=VideoTypes.VIDEO_SEGMENTS) for x in res]

        return res

    def _fetch_show_data(self, show_object):
        """
        Fetches the raw data about the page from the given fetched page object.
        :param show_object: Show object.
        :return: JSON data of the page.
        """
        page_request = self.get_object_request(show_object)
        if page_request.url in self.special_show_parsing:
            # return self._fetch_show_data_1135(show_object)
            return self.special_show_parsing[page_request.url](show_object)
        tree = self.parser.parse(page_request.text)

        title_prescriptions = []
        prescription_par = (tree.xpath('.//div[@class="program_top_txt"]') +
                            tree.xpath('.//div[@class="program_top_txt"]/p'))
        for par in prescription_par:
            sub_prescription = ' '.join(par.xpath('./text()'))
            sub_prescription += ' '.join(par.xpath('./*/text()'))
            if len(sub_prescription) > 0:
                title_prescriptions.append(sub_prescription)
        show_object.description = title_prescriptions

        season_par = (tree.xpath('.//div[@class="program_top_txt"]/p/strong/a') +
                      tree.xpath('.//ul[@class="con_menu_list w-list-unstyled"]/li/a'))
        season_par = [x for x in season_par if 'subcat' in urlparse(x.attrib['href']).query]
        show_sub_objects = [VODCatalogNode(catalog_manager=self.catalog_manager,
                                           obj_id=self._get_page_id_from_page_url(par.attrib['href']),
                                           title=par.text,
                                           number=par.text,
                                           url=urljoin(self.base_url, par.attrib['href']),
                                           image_link=show_object.image_link,
                                           super_object=show_object,
                                           object_type=VODCategories.SHOW_SEASON,
                                           raw_data=par,
                                           ) for par in season_par]
        show_object.add_sub_objects(show_sub_objects)
        if len(show_sub_objects) == 0:
            show_sub_objects = self._fetch_season_objects(show_object)

        return show_sub_objects

    def _fetch_show_data_1135(self, show_object):
        """
        Fetches the raw data about the page https://www.kan.org.il/page.aspx?landingpageid=1135.
        :param show_object: Show object
        :return: JSON data of the page.
        """
        show_url = urljoin(self.base_url, show_object.url)
        # if show_object.id in self.show_data:
        #     return self.show_data[show_object.id]
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
        page_request = self.session.get(show_url, headers=headers)
        tree = self.parser.parse(page_request.text)
        name = [x for x in tree.xpath('.//title/text()')]
        assert len(name) == 1
        name = ' | '.join(name[0].split(' | ')[:-1]).split(' - ')[0]
        name = self._clear_text(name)
        # res['title'] = name

        title_prescriptions = []
        previous_seasons = []
        prescription_par = tree.xpath('.//div[@class="txt_info_center"]/p')
        for par in prescription_par:
            sub_prescription = ' '.join(par.xpath('./text()'))
            if len(sub_prescription) > 0:
                title_prescriptions.append(sub_prescription)
            sub_prescription = par.xpath('./strong/a')
            if len(sub_prescription) > 0:
                previous_seasons.extend(x.attrib['href'] for x in sub_prescription)
        show_object.description = '\n'.join(title_prescriptions)

        season_urls = [page_request.url] + previous_seasons
        season_urls = season_urls[::-1]
        season_numbers = ['{p} {i}'.format(p=self.season_prefix, i=i+1) for i, _ in enumerate(season_urls)]
        replace_title = [x for x in season_numbers if x in name]
        show_sub_objects = []
        for seasons_url, season_number in zip(season_urls, season_numbers):
            new_season_title = name.replace(replace_title[0], season_number) \
                if len(replace_title) > 0 else season_number
            season_object = VODCatalogNode(catalog_manager=self.catalog_manager,
                                           obj_id=self._get_page_id_from_page_url(seasons_url),
                                           title=new_season_title,
                                           number=season_number,
                                           url=urljoin(self.base_url, seasons_url),
                                           image_link=show_object.image_link,
                                           super_object=show_object,
                                           object_type=VODCategories.SHOW_SEASON,
                                           raw_data=tree,
                                           )
            season_episodes = self._fetch_season_data_1135(season_object)
            season_object.add_sub_objects(season_episodes)
            show_sub_objects.append(season_object)

        show_object.add_sub_objects(show_sub_objects)
        return show_sub_objects

    def _fetch_season_data_1135(self, season_object):
        """
        Extract episode data for page episodes on page https://www.kan.org.il/page.aspx?landingpageid=1135.
        :param season_object: Season object.
        :return: List of season episode data.
        """
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
        req = self.session.get(season_object.url, headers=headers)
        tree = self.parser.parse(req.text)
        videos = []
        # At first we update the image url
        new_image_link = tree.xpath('.//div[@class="big_it_pict"]/img/@src')
        if len(new_image_link) == 0:
            new_image_link = tree.xpath('.//div[@class="big_it_pict"]/img/@data-cfsrc')
        assert len(new_image_link) > 0
        season_object.image_link = urljoin(self.base_url, new_image_link[0])

        season_episode_page_urls = [urljoin(self.base_url, x)
                                    for x in tree.xpath('.//div[@class="news_phlah small news_phlah"]/../../../@href')]
        season_episode_images = [urljoin(self.base_url, re.findall(r'(?:url\(\')(.*)(?:\'\))', x)[0])
                                 for x in tree.xpath('.//div[@class="news_phlah small news_phlah"]/../../@style')]
        season_episode_info_tree = tree.xpath('.//div[@class="news_phlah small news_phlah"]/../../../'
                                              'div[@class="magazine_info_group"]')
        season_episode_episode_number_tree = tree.xpath('.//div[@class="news_phlah small news_phlah"]/text()')

        assert len(season_episode_page_urls) == len(season_episode_images)
        for i, (url, image_url, info_tree, episode_number) in enumerate(zip(season_episode_page_urls,
                                                                            season_episode_images,
                                                                            season_episode_info_tree,
                                                                            season_episode_episode_number_tree)):
            # episode_req = self.session.get(url, headers=headers)
            # episode_tree = self.parser.parse(episode_req.text)

            # Fetching id
            episode_id = self._get_page_id_from_page_url(url)

            # Fetching link
            # Old implementation.
            # link = episode_tree.xpath('.//script[@type="application/json"]/text()')
            # assert len(link) == 1
            # link = re.findall(r'(?:<iframe src=\\")(.*?)(?:\\")', link[0])
            # assert len(link) == 1
            # episode_link = link[0]
            # New implementation
            episode_link = urljoin(season_object.url, url)

            # Fetching title
            episode_title = info_tree.xpath('./h2[@class="magazine_info_title"]/text()')
            assert len(episode_title) == 1
            episode_title = info_tree.xpath('./h2[@class="magazine_info_title"]/text()')[0]

            # episode_number, episode_title = self._parse_episode_title_and_season(title[0], i)

            # Fetching description
            episode_description = info_tree.xpath('./div[@class="magazine_txt_inner "]/'
                                                  'div[@class="magazine_info_txt"]/text()')
            assert len(episode_description) == 1
            episode_description = self._clear_text(episode_description[0])

            if episode_number not in episode_title:
                episode_title = '{p} - {t}'.format(p=episode_number, t=episode_title)

            episode_data = VODCatalogNode(catalog_manager=self.catalog_manager,
                                          obj_id=episode_id,
                                          title=episode_title,
                                          # title=episode_title,
                                          number=episode_number,
                                          url=episode_link,
                                          image_link=image_url,
                                          super_object=season_object,
                                          description=episode_description,
                                          object_type=VODCategories.VIDEO,
                                          raw_data=None,
                                          )

            videos.append(episode_data)

        return videos

    def _fetch_season_objects(self, season_object):
        """
        Fetches season Episodes.
        :param season_object: Season object.
        :return:
        """
        # We fetch the season title
        # show_title = show_data['title']
        # Now we fetch the videos on the page
        # Finding the video link.
        episodes = []
        episodes_raw_data = []
        # We check if we need to add another hidden videos to our analysis
        count = 1
        split_url = urlparse(season_object.url)
        args = parse_qs(split_url.query)
        video_ids = set()
        while 1:
            args['count'] = [str(count)]
            req = self.get_object_request(season_object, override_params=args)
            tmp_tree = self.parser.parse(req.text)
            optional_page = tmp_tree.xpath('.//li[@class="program_list_item w-clearfix"]')
            page_video_ids = {x.xpath('./div/div/iframe/@id')[0] for x in optional_page}
            if len(optional_page) == 0 or page_video_ids <= video_ids:
                break
            episodes_raw_data.extend(optional_page)
            video_ids.update(page_video_ids)
            count += 1

        for video_raw_datum in episodes_raw_data:
            episode_image = video_raw_datum.xpath('./div[@class="program_list_videoblock"]//'
                                                  'div[@class="program video_screen_full grayScaleImg"]/@style')
            episode_image = urljoin(self.base_url, re.findall(r'(?:url\(\')(.*)(?:\'\))', episode_image[0])[0])

            episode_video_data = video_raw_datum.xpath('./div[@class="program_list_videoblock"]//'
                                                       'div[@class="program video_screen_full grayScaleImg"]/'
                                                       'iframe')
            if len(episode_video_data) == 0:
                # We have a textual page
                continue

            episode_id = re.findall(r'\d*', episode_video_data[0].attrib['id'])[0]
            episode_link = episode_video_data[0].attrib['src']

            episode_info_data = video_raw_datum.xpath('./div[@class="program_list_infoblock w-clearfix"]//'
                                                      '*[@class="program_list_link w-inline-block"]')
            assert len(episode_info_data) == 1
            raw_title = episode_info_data[0].xpath('./h2[@class="content_title"]/text()')
            assert len(raw_title) == 1
            raw_title = self._clear_text(raw_title[0])
            # raw_title = raw_title.split(' | ')
            # episode_number = [x for x in raw_title if self.episode_prefix in x]
            # episode_number = episode_number[0] if len(episode_number) > 0 else None
            # episode_name = [x for x in raw_title if self.season_prefix not in x and self.episode_prefix not in x]
            # episode_name = ' | '.join(episode_name) if len(episode_name) > 0 else raw_title[0]

            # episode_number, episode_name = self._parse_episode_title_and_season(raw_title, 0)
            episode_description = episode_info_data[0].xpath('./p/text()')
            assert len(episode_description) == 1
            episode_description = self._clear_text(episode_description[0])

            episode_data = VODCatalogNode(catalog_manager=self.catalog_manager,
                                          obj_id=episode_id,
                                          title=raw_title,
                                          # number=episode_number,
                                          url=urljoin(self.base_url, episode_link),
                                          image_link=episode_image,
                                          super_object=season_object,
                                          description=episode_description,
                                          additional_data={'id': episode_id},
                                          object_type=VODCategories.VIDEO,
                                          raw_data=video_raw_datum,
                                          )
            episodes.append(episode_data)

        season_object.add_sub_objects(episodes)
        return episodes

    def _parse_episode_title_and_season(self, raw_title, i):
        """
        Parses episode title and season from the raw title.
        :param raw_title: Raw title.
        :param i: episode index.
        :return:
        """
        title = raw_title.split(' | ')
        assert len(title) == 2
        if len(title[0].split(' - ')) > 1 and self.season_prefix in title[0]:
            # We have season encoded in the title
            tmp_title = title[0].split(' - ')
            assert len(tmp_title) == 2
            episode_title = tmp_title[0]
            # episode_season = tmp_title[1]

            tmp_title = title[1].split(' - ')
            assert len(tmp_title) == 2
            episode_number = tmp_title[0]
            # episode_video_url = tmp_title[1]
        else:
            # show_title = title[0]
            title = title[1].split(' - ')
            if len(title) == 3:
                # episode_season = title[0]
                episode_number = title[1]
                episode_title = title[2]
            elif len(title) == 2:
                # episode_season = season_object.number
                episode_number = title[0]
                episode_title = title[1]
            else:
                episode_number = '{p} {i}'.format(p=self.episode_prefix, i=i)
                episode_title = title[0]
        return episode_number, episode_title

    def get_live_stream_info(self):
        """
        Fetches the live stream data.
        :return: VODCatalogNode object.
        """
        day_key = datetime.now().strftime(self.schedule_date_format)
        if 'schedule' not in self.live_data or day_key not in self.live_data['schedule']:
            program_fetch_url = self.schedule_url
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

            params = {
                'stationID': self.schedule_index,
                'day': day_key,
            }
            err_cnt = 0
            max_err_cnt = 5
            raw_data = None
            while err_cnt < max_err_cnt:
                try:
                    req = self.session.get(program_fetch_url, headers=headers, params=params)
                    raw_data = req.json()
                    break
                except ValueError as err:
                    err_cnt += 1
                    time.sleep(1)
                    if err_cnt == max_err_cnt:
                        raise err
            if 'schedule' not in self.live_data:
                self.live_data['schedule'] = {}
            self.live_data['schedule'][day_key] = raw_data

        now_time = datetime.now()
        try:
            current_program = [x for x in self.live_data['schedule'][day_key]
                               if datetime.strptime(x['start_time'], '%Y-%m-%dT%H:%M:%S') < now_time]
        except TypeError:
            current_program = [x for x in self.live_data['schedule'][day_key]
                               if datetime(*(time.strptime(x['start_time'], '%Y-%m-%dT%H:%M:%S')[0:6])) < now_time]

        if len(current_program) == 0:
            raise RuntimeError('No live shows found!')
        current_program = current_program[-1]

        res = VODCatalogNode(catalog_manager=self.catalog_manager,
                             obj_id=(current_program['program_code'], current_program['program_id']),
                             title=current_program['title'],
                             description=current_program['live_desc'],
                             image_link=current_program['picture_code'],
                             number=current_program['chapter_number'],
                             object_type=VODCategories.LIVE_SCHEDULE,
                             )
        return res

    def get_live_stream_video_link(self):
        """
        Fetches the live stream video_link.
        :return: VideoNode object.
        """
        if 'live_show_link' not in self.live_data:
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
            req = self.session.get(self.object_urls[VODCategories.LIVE_VIDEO], headers=headers)
            link = re.findall(r'(?:<iframe.*src=")(.*?)(?:")', req.text)
            assert len(link) == 1
            self.live_data['live_show_link'] = link[0]

        return self._get_video_links_from_video_url(self.live_data['live_show_link'])

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        raise NotImplemented

    def search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        if query == self._previous_search_query:
            return self.objects[VODCategories.SEARCH_MAIN]

        headers = {
            'Accept': '*/*',
            'Host': 'cogito3.com',
            'Origin': self.base_url,
            'Referer': 'https://www.kan.org.il/search.aspx',
            'User-Agent': self.user_agent,
        }
        # if any(self.search_default_params[x] is None for x in ('cx', 'cselibv', 'cse_tok')):
        #     # We fetch the default parameters
        #     self._update_search_params()

        # params = self.search_default_params.copy()
        params = {'q': query, 'start': 0}

        # params['oq'] = query

        self.objects[VODCategories.SEARCH_MAIN].url = self.object_urls[VODCategories.SEARCH_MAIN]
        self.objects[VODCategories.SEARCH_MAIN].additional_data = {'params': params, 'headers': headers}

        return self._get_search_from_show_object(self.objects[VODCategories.SEARCH_MAIN])

    # def _update_search_cx_param(self, req):
    #     """
    #     Updates search cx param in default params.
    #     :param req: Fetched session request.
    #     :return:
    #     """
    #     cx = re.findall(r'(?:var cx = \')(.*?)(?:\')', req.text)
    #     self.search_default_params['cx'] = cx[0]
    #     new_search_param_url = re.findall(r'(?:gcse.src = \')(.*?)(?:\')', req.text)
    #     self.search_params_url = new_search_param_url[0].split('?')[0]
    #
    # def _update_search_params(self):
    #     """
    #     Updates search default_params
    #     :return:
    #     """
    #     if self.search_default_params['cx'] is None:
    #         headers = {
    #             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
    #                       'q=0.8,application/signed-exchange;v=b3',
    #             # 'Accept-Encoding': 'gzip, deflate, br',
    #             'Cache-Control': 'max-age=0',
    #             'Referer': self.base_url,
    #             'Sec-Fetch-Mode': 'navigate',
    #             'Sec-Fetch-Site': 'none',
    #             'Sec-Fetch-User': '?1',
    #             'User-Agent': self.user_agent
    #         }
    #         req = self.session.get(self.object_urls[CHANNEL_MAIN], headers=headers)
    #         assert req.ok
    #         self._update_search_cx_param(req)
    #
    #     headers = {
    #         'Referer': self.base_url,
    #         'User-Agent': self.user_agent,
    #     }
    #     params = {
    #         'cx': self.search_default_params['cx'],
    #     }
    #     req = self.session.get(self.search_params_url, headers=headers, params=params)
    #     assert req.ok
    #     cse_token = re.findall(r'(?:"cse_token": ")(.*?)(?:")', req.text)
    #     self.search_default_params['cse_tok'] = cse_token
    #     cse_lib = re.findall(r'(?:"cselibVersion": ")(.*?)(?:")', req.text)
    #     self.search_default_params['cselibv'] = cse_lib

    def _get_search_from_show_object(self, search_object):
        """
        Fetches the search results for the given search object.
        :param search_object: Search object.
        :return: list of VODCatalogNode objects.
        """
        raw_data, req = self._get_raw_search_data(search_object)
        total_pages = int(math.ceil(float(int(raw_data['total_results'])) / self.number_of_results_per_page))

        # At first we update the main shows in case it wasn't done before.
        if self.objects[VODCategories.CHANNELS_MAIN].sub_objects is None:
            self._update_base_categories(self.objects[VODCategories.CHANNELS_MAIN])
        # Now wee take care of the results
        if search_object.object_type is not VODCategories.PAGE and total_pages > 0:
            sub_pages = []
            for i in range(total_pages):
                # Now we create additional search pages
                new_page_params = search_object.additional_data['params'].copy()
                new_page_params['start'] = i * self.number_of_results_per_page
                search_additional_page = VODCatalogNode(catalog_manager=self.catalog_manager,
                                                        obj_id=(search_object.id, i+1),
                                                        title=search_object.title + ' | Page {p}'.format(p=i+1),
                                                        description=search_object.description,
                                                        url=search_object.url,
                                                        image_link=search_object.image_link,
                                                        super_object=search_object,
                                                        object_type=VODCategories.SEARCH_PAGE,
                                                        page_number=i+1,
                                                        additional_data={
                                                            'params': new_page_params,
                                                            'headers': search_object.additional_data['headers']
                                                        }
                                                        )
                sub_pages.append(search_additional_page)
            search_object.add_sub_objects(sub_pages)
            search_object = search_object.sub_objects[0]
            return self._get_search_sub_objects_from_search_object(search_object, req)

    def _get_raw_search_data(self, search_object):
        """
        Fetches the raw search results for the given search object.
        :param search_object: Search object.
        :return: list of VODCatalogNode objects.
        """
        req = self.session.get(search_object.url, **search_object.additional_data)
        assert req.ok
        raw_data = req.json()
        return raw_data, req

    def _get_search_sub_objects_from_search_object(self, search_object, page_request=None):
        """
        Fetches the search results for the given search object.
        :param search_object: Search object.
        :param page_request: Page request.
        :return: list of VODCatalogNode objects.
        """
        if page_request is None:
            page_request = self.session.get(search_object.url, **search_object.additional_data)
        assert page_request.ok
        raw_data = page_request.json()

        res = []
        for x in raw_data['items']:
            try:
                search_show_id = self._get_page_id_from_page_url(x['url'])
            except ValueError:
                # We have uncommon format. Skipping that result...
                continue
            page_params = parse_qs(urlparse(x['url'].lower()).query)
            if 'catid' in page_params:
                if not self.catalog_manager.is_node(page_params['catid'][0], False):
                    continue
                # We have a show, thus we want to update it
                search_show_main_object = self.catalog_manager.get_node(page_params['catid'][0], False)
                if search_show_main_object.sub_objects is None:
                    # We need to update the show
                    self._fetch_show_data(search_show_main_object)

                search_show_object = self.catalog_manager.get_node(search_show_id, False)
            elif 'landingpageid' in page_params:
                # We have either special page or another channel
                if not self.catalog_manager.is_node(page_params['landingpageid'][0], False):
                    continue
                if search_show_id in self.special_show_parsing:
                    search_show_main_object = self.catalog_manager.get_node(search_show_id, False)
                    # We have a special page
                    if search_show_main_object.sub_objects is None:
                        # We need to update the show
                        self._fetch_show_data(search_show_main_object)

                    search_show_object = self.catalog_manager.get_node(search_show_id, False)
                else:
                    continue

            elif 'stationid' in page_params:
                # We have a live show
                if x['url'] == self.object_urls[VODCategories.LIVE_VIDEO]:
                    search_show_object = self.get_live_stream_info()
                else:
                    continue
            else:
                # We have an episode
                if self.catalog_manager.is_node(search_show_id, False):
                    # We fetch it from the search
                    search_show_object = self.catalog_manager.get_node(search_show_id, False)
                else:
                    # We create a new object
                    search_show_object = VODCatalogNode(catalog_manager=self.catalog_manager,
                                                        obj_id=search_show_id,
                                                        title=x['title'],
                                                        description=x['description'],
                                                        url=x['url'],
                                                        image_link=x['image']['url'],
                                                        super_object=search_object,
                                                        object_type=VODCategories.VIDEO,
                                                        raw_data=x,
                                                        )
            res.append(search_show_object)
        search_object.add_sub_objects(res)

        return search_object

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        if fetched_request is None:
            fetched_request = self.get_object_request(category_data)
        raw_res = \
            json.loads(re.findall(r'(?:google.search.cse.api\d+\()(.*)(?:\);)', fetched_request.text, re.DOTALL)[0])
        total_results = raw_res['cursor']['estimatedResultCount']
        total_pages = int(math.ceil(float(total_results) / self.number_of_results_per_page))
        return total_pages

    def get_object_request(self, page_data, override_page_number=None, override_params=None, override_url=None):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :param override_page_number: Override page number.
        :param override_params: Override params.
        :param override_url: Override url.
        :return: Page request
        """
        if page_data.object_type == VODCategories.SHOW_SEASON:
            override_url = self.additional_content_page
        return super(Kan, self).get_object_request(page_data, override_page_number, override_params, override_url)

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

    # def _prepare_search_sub_objects(self, raw_results):
    #     """
    #     Prepares list of search sub objects.
    #     :param raw_results: Results given in raw format of the request page.
    #     :return: List of VODCatalogNode Objects.
    #     """


class KanEducation(Kan):
    schedule_index = 19

    @property
    def object_urls(self):
        return {
            VODCategories.CHANNELS_MAIN: 'https://www.kan.org.il/page.aspx?landingPageId=1083',
            VODCategories.LIVE_VIDEO: 'https://www.kan.org.il/live/tv.aspx?stationid=20',
            VODCategories.SEARCH_MAIN: 'https://cogito3.com/kansearch/',
        }

    def __init__(self, vod_name='KanEducation', vod_id=-5, store_dir='.', data_dir='../../Data', source_type='VOD',
                 session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(KanEducation, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, session_id)
        self.special_show_parsing = {
            'https://www.kan.org.il/page.aspx?landingpageid=1113': self._fetch_show_data_1113,
            'https://www.kan.org.il/page.aspx?landingpageid=1137': self._fetch_show_data_1137,
        }

    # def _update_base_categories(self, dummy=None):
    #     """
    #     Fetches all the available shows.
    #     :return: Object of all available shows (JSON).
    #     """
    #     program_fetch_url = self.shows_url
    #     headers = {
    #         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
    #                   'q=0.8,application/signed-exchange;v=b3',
    #         # 'Accept-Encoding': 'gzip, deflate, br',
    #         'Cache-Control': 'max-age=0',
    #         'Referer': self.base_url,
    #         'Sec-Fetch-Mode': 'navigate',
    #         'Sec-Fetch-Site': 'none',
    #         'Sec-Fetch-User': '?1',
    #         'User-Agent': self.user_agent
    #     }
    #
    #     req = self.session.get(program_fetch_url, headers=headers)
    #     tree = self.parser.parse(req.text)
    #     xpath = './/div[@class="component_section no_padding w-clearfix"]//' \
    #             'div[@class="component_big_item podcast w-clearfix"]/a'
    #     shows = tree.xpath(xpath)
    #     sub_objects1 = self._get_show_objects_from_show_main_component_trees(shows)
    #
    #     xpath = './/div[@class="component_sm_group"]//div[@class="component_sm_item w-clearfix"]/a'
    #     shows = tree.xpath(xpath)
    #     sub_objects2 = self._get_show_objects_from_show_small_component_trees(shows)
    #
    #     xpath = './/div[@class="component_section magazine"]/div[@class="magazine_item"]/' \
    #             'a[@class="magazine_info_link w-inline-block "]'
    #     shows = tree.xpath(xpath)
    #     sub_objects3 = self._get_show_objects_from_show_magazine_trees(shows)
    #
    #     self.available_shows.add_sub_objects(sub_objects1 + sub_objects2 + sub_objects3)
    #     # with open(self.available_shows_data_filename, 'wb') as fl:
    #     #     pickle.dump(self.available_categories, fl)

    def _fetch_show_data_1113(self, show_object):
        """
        Fetches the raw data about the page https://www.kan.org.il/page.aspx?landingpageid=1113.
        :param show_object: Show object.
        :return: JSON data of the page.
        """
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
        req = self.session.get(show_object.url, headers=headers)
        tree = self.parser.parse(req.text)
        videos = []
        season_episode_page_urls = [urljoin(self.base_url, x)
                                    for x in tree.xpath('.//a[@class="magazine_info_link w-inline-block "]/@href')]
        # season_episode_images = [urljoin(self.base_url, re.findall(r'(?:url\(\')(.*)(?:\'\))', x)[0])
        #                          for x in tree.xpath('.//div[@class="magazine_info_link w-inline-block "]/'
        #                                              'div[class="magazine_pict grayScaleImg"]/@style')]
        season_episode_images = [urljoin(self.base_url, re.findall(r'(?:url\(\')(.*)(?:\'\))', x)[0])
                                 for x in tree.xpath('.//a[@class="magazine_info_link w-inline-block "]/'
                                                     'div[@style]/@style')]
        season_episode_info_tree = tree.xpath('.//a[@class="magazine_info_link w-inline-block "]/'
                                              'div[@class="magazine_info_group"]')
        assert len(season_episode_page_urls) == len(season_episode_images)
        assert len(season_episode_page_urls) == len(season_episode_info_tree)
        sub_objects = []
        for i, (url, image_url, info_tree) in enumerate(zip(season_episode_page_urls, season_episode_images,
                                                            season_episode_info_tree)):
            # Fetching id
            episode_id = self._get_page_id_from_page_url(url)

            # Fetching link
            # Old implementation:
            # episode_req = self.session.get(url, headers=headers)
            # episode_tree = self.parser.parse(episode_req.text)
            # link = episode_tree.xpath('.//iframe/@src')
            # assert len(link) > 0
            # episode_link = link[0]
            # New implementation: we moved the logic to the video fetcher.
            episode_link = url

            # Fetching title
            title = info_tree.xpath('./h2[@class="magazine_info_title"]/text()')
            assert len(title) == 1
            title = title[0]
            # episode_number, episode_title = self._parse_episode_title_and_season(title[0], i)
            # Fetching description
            episode_description = info_tree.xpath('./div[@class="magazine_txt_inner "]/'
                                                  'div[@class="magazine_info_txt"]/text()')
            assert len(episode_description) == 1
            episode_description = re.sub(r'^[ \n]*|[ \n]*$', '', episode_description[0])

            episode_data = VODCatalogNode(catalog_manager=self.catalog_manager,
                                          obj_id=episode_id,
                                          title=title,
                                          # title=episode_title,
                                          # number=episode_number,
                                          url=episode_link,
                                          image_link=image_url,
                                          super_object=show_object,
                                          description=episode_description,
                                          object_type=VODCategories.VIDEO,
                                          raw_data=None,
                                          )

            videos.append(episode_data)
            sub_objects.append(episode_data)

        show_object.add_sub_objects(sub_objects)
        return videos

        # # Same format as 1137
        # return self._fetch_season_data_1135(show_object)

    def _fetch_show_data_1137(self, show_object):
        """
        Fetches the raw data about the page https://www.kan.org.il/page.aspx?landingpageid=1113.
        :param show_object: Show object.
        :return: JSON data of the page.
        """
        # Have the same structure as show 1113
        return self._fetch_show_data_1113(show_object)


class Makan(Kan):
    schedule_url = 'https://www.kan.org.il/tv-guide/tv_guidePrograms.ashx'
    additional_content_page = 'https://www.makan.org.il/program/getMoreProgram.aspx'

    @property
    def object_urls(self):
        return {
            VODCategories.CHANNELS_MAIN: 'https://www.makan.org.il/video/programs.aspx',
            VODCategories.LIVE_VIDEO: 'https://www.makan.org.il/live/tv.aspx?stationid=3',
            VODCategories.SEARCH_MAIN: 'https://cogito3.com/kansearch/',
        }
    schedule_index = 2

    def __init__(self, vod_name='Makan', vod_id=-20, store_dir='.', data_dir='../../Data', source_type='VOD',
                 session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(Makan, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, session_id)

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.makan.org.il/'

    def _update_base_categories(self, base_object):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
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

        req = self.session.get(base_object.url, headers=headers)
        tree = self.parser.parse(req.text)
        xpath = './/div[@id="moreProgram"]/div[@class="items sm_it_section"]/div[@class="it_small"]/' \
                'div[@class="it_small_pictgroup programs"]'
        shows = tree.xpath(xpath)
        sub_objects = self._get_show_objects_from_it_small_component_trees(shows, base_object)

        base_object.add_sub_objects(sub_objects)
        # with open(self.available_shows_data_filename, 'wb') as fl:
        #     pickle.dump(self.available_categories, fl)


if __name__ == '__main__':
    # search_word = u'היהודים באים'
    # show_id = IdGenerator.make_id('47')
    # season_id = IdGenerator.make_id(('47', '212'))
    # search_word = u'כאן דוקו'
    # show_id = IdGenerator.make_id('1076')
    # search_word = u'חנו על המפית'
    show_id = IdGenerator.make_id('1274')
    # season_id = IdGenerator.make_id('1135')
    # search_word = u'ימי בגין'
    # show_id = IdGenerator.make_id('1433')
    # search_word = u'והארץ הייתה תוהו ובוהו'
    # show_id = IdGenerator.make_id('64')
    # search_word = u'Tiul Shorashim'
    # show_id = IdGenerator.make_id('1472')
    # show_id = IdGenerator.make_id('1494')
    # search_word = u'Geula and London'
    # show_id = IdGenerator.make_id('1480')
    # search_word = u'Once in a week with Tom Aharon'
    # show_id = IdGenerator.make_id('1206')
    # kan = Kan(store_dir='D:\\')
    # kan = Kan(store_dir='.')
    # kan.get_show_object(show_id)
    # kan.get_show_object(show_id, season_id)
    # kan.download_objects(show_id, verbose=1)

    # kan.get_video_links_from_video_data('https://www.kan.org.il/item/?itemId=34710')
    # kan._prepare_new_search_query('זמן אמת')

    # kan.get_live_stream_info()
    # kan.get_live_stream_video_link()

    # search_word = u'חיות רשת'
    # show_id = IdGenerator.make_id('1113')
    # search_word = u'להציל את חיות הבר'
    # show_id = IdGenerator.make_id('1137')
    # kan = KanEducation(store_dir='.')
    # kan.get_show_object(show_id)
    # kan.get_show_object(show_id, season_id)
    # kan.get_video_links_from_video_data('https://www.kan.org.il/item?itemId=49346')
    # kan.get_video_links_from_video_data('https://www.kan.org.il/item/?itemId=38922')
    # kan.download_objects(show_id, verbose=1)

    # search_word = u'شو عَ النت مع سمر قبطي'
    # show_id = IdGenerator.make_id('3082')
    # kan = Makan(store_dir='..')
    # kan.get_show_object(show_id)
    # kan.get_video_links_from_video_data('https://kanapi.media.kan.org.il/Players/ByPlayer/V1/ipbc/S0282563_1/hls')
    # # kan.get_show_object(show_id, season_id)
    # kan.download_objects(show_id, verbose=1)

    # kan.get_live_stream_info()
    # kan.get_live_stream_video_link()

    kan = Kan(store_dir='.')
    # kan = KanEducation(store_dir='.')
    # kan = Makan(store_dir='.')
    kan.download_category_input_from_user()
