# -*- coding: UTF-8 -*-
from ..fetchers.vod_fetcher import VODFetcher
# Video catalog
from ..catalogs.vod_catalog import VODCatalogNode, Enum, VideoNode, VideoSource, VideoTypes
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
from .. import urljoin, urlparse


class WallaCategories(Enum):
    # Copy from VODCategories :(
    PAGE = 0
    VIDEO = 1
    VIDEO_PAGE = 2
    SEARCH_MAIN = 3
    SEARCH_PAGE = 4
    GENERAL_MAIN = 5
    LIVE_VIDEO = 6
    LIVE_SCHEDULE = 7

    # Special VOD object types
    CHANNELS_MAIN = ('VOD', 0)
    GENERAL_CHANNEL_SUB_CATEGORY = (CHANNELS_MAIN, 0)
    SHOWS_MAIN = ('VOD', 1)
    MOVIES_MAIN = ('VOD', 2)
    SERIES_MAIN = ('VOD', 3)
    KIDS_MAIN = ('VOD', 4)
    SHOW_GENRE = ('VOD', 5)
    MOVIE_GENRE = ('VOD', 6)
    KIDS_GENRE = ('VOD', 7)
    SHOW_SEASON = ('VOD', 8)
    SHOW = ('VOD', 9)
    KIDS_SHOW = ('VOD', 10)
    KIDS_SHOW_SEASON = ('VOD', 11)
    TV_CHANNELS_MAIN = ('VOD', 12)
    TV_CHANNEL = ('VOD', 13)

    # Walla add-ons
    VIVA_MAIN = ('Walla', 0)
    VIVA_TITLES = ('Walla', 1)
    VIVA_SHORT = ('Walla', 2)
    VIVA_SHOW = ('Walla', 3)
    YES = ('Walla', 4)


class WallaCatalogNode(VODCatalogNode):
    @property
    def _false_object_types(self):
        return WallaCategories.PAGE, WallaCategories.VIDEO_PAGE, WallaCategories.SEARCH_PAGE


# todo: implement search
class Walla(VODFetcher):
    _catalog_node_object = WallaCatalogNode

    url_2_main_categories_mapping = {
        '/movies': WallaCategories.MOVIES_MAIN,
        '/tvshows': WallaCategories.SHOWS_MAIN,
        '/kids': WallaCategories.KIDS_MAIN,
        '/channels': WallaCategories.TV_CHANNELS_MAIN,
    }
    number_of_titles_per_page = 30  # 5*6
    number_of_viva_titles_per_page = 50  # 5*10

    viva_base_url = 'https://viva.walla.co.il/'
    viva_netloc = urlparse(viva_base_url).netloc
    viva_special_channel_mapping = {viva_base_url: 'https://vod.walla.co.il/tvshows/7587'}
    # viva_paths = ('/shorts', '/tvshows', '/fullepisodes',)
    viva_paths = {'/shorts': WallaCategories.VIVA_SHORT, '/fullepisodes': WallaCategories.VIVA_TITLES, }

    video_request_template = 'https://walla-metadata-rr-d.vidnt.com/vod/vod/{vid}/hls/' \
                             'metadata.xml?&https_streaming=true'
    video_initial_server = 'walla-s.vidnt.com'
    episode_image_template = 'https://img.wcdn.co.il/f_auto,w_200,t_54/{fl[0]}/{fl[1]}/{fl[2]}/{fl[3]}/{fl}'
    episode_url_template = 'https://vod.walla.co.il/episode/{eid}'
    current_page_episodes = 'https://dal.walla.co.il/talkback/list/{sid}'
    season_prefix = u"עונה"
    episode_prefix = u"פרק"

    @property
    def object_urls(self):
        return {
            WallaCategories.CHANNELS_MAIN: 'https://vod.walla.co.il/',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://vod.walla.co.il/'

    def __init__(self, vod_name='Walla', vod_id=-12, store_dir='.', data_dir='../../Data', source_type='VOD',
                 session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        self.episodes_to_data = {}
        self.season_to_show = {}
        super(Walla, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, session_id)

    def _prepare_main_sub_objects(self):
        """
        Prepares main sub objects.
        :return:
        """
        self.objects = {
            WallaCategories.CHANNELS_MAIN:
                self._prepare_main_single_sub_object(self.source_name, WallaCategories.CHANNELS_MAIN),
            WallaCategories.SEARCH_MAIN: self._prepare_main_single_sub_object('Search', WallaCategories.SEARCH_MAIN),
            WallaCategories.LIVE_VIDEO: self._prepare_main_single_sub_object('Live', WallaCategories.LIVE_VIDEO),
        }

    def _update_base_categories(self, base_object):
        """
        Fetches all the available shows.
        :return: Base object.
        """
        req = self.get_object_request(base_object)
        tree = self.parser.parse(req.text)
        xpath = './/ul[@class="vod-main-items"]/li/a'
        shows = tree.xpath(xpath)

        sub_objects = []
        for show in shows:
            if (
                'href' not in show.attrib or
                urlparse(urljoin(self.base_url, show.attrib['href'])).hostname != urlparse(self.base_url).hostname or
                urljoin(self.base_url, show.attrib['href']) == self.base_url
            ):
                continue

            if show.attrib['href'] not in self.url_2_main_categories_mapping:
                raise RuntimeError('Unknown main category! Recheck the site structure at {u}'.format(u=self.base_url))
            x = WallaCatalogNode(catalog_manager=self.catalog_manager,
                                 obj_id=show.attrib['href'],
                                 title=show.xpath('./span/text()')[0],
                                 url=urljoin(self.base_url, show.attrib['href']),
                                 image_link=None,
                                 super_object=base_object,
                                 object_type=self.url_2_main_categories_mapping[show.attrib['href']],
                                 raw_data=None)
            sub_objects.append(x)

        base_object.add_sub_objects(sub_objects)

    def fetch_sub_objects(self, element_object):
        """
        Fetches object's sub objects.
        :param element_object: Object element we want to fetch.
        :return:
        """
        true_object = element_object.true_object
        if true_object.object_type == WallaCategories.CHANNELS_MAIN:
            return self._update_base_categories(element_object)
        elif true_object.object_type == WallaCategories.MOVIES_MAIN:
            return self._update_movie_categories(element_object)
        elif true_object.object_type == WallaCategories.MOVIE_GENRE:
            return self._update_movie_titles(element_object)
        elif true_object.object_type == WallaCategories.SHOWS_MAIN:
            return self._update_series_categories(element_object)
        elif true_object.object_type == WallaCategories.SHOW_GENRE:
            return self._update_series_titles(element_object)
        elif true_object.object_type in (WallaCategories.SHOW, WallaCategories.SHOW_SEASON):
            return self._update_series_episodes(element_object)
        elif true_object.object_type == WallaCategories.KIDS_MAIN:
            return self._update_kid_categories(element_object)
        elif true_object.object_type == WallaCategories.KIDS_GENRE:
            return self._update_kid_titles(element_object)
        elif true_object.object_type in (WallaCategories.KIDS_SHOW, WallaCategories.KIDS_SHOW_SEASON):
            return self._update_kids_episodes(element_object)
        elif true_object.object_type == WallaCategories.TV_CHANNELS_MAIN:
            return self._update_channel_categories(element_object)
        elif true_object.object_type == WallaCategories.TV_CHANNEL:
            return self._update_channel_subcategories(element_object)
        elif true_object.object_type == WallaCategories.VIVA_MAIN:
            return self._update_viva_base_categories(element_object)
        elif true_object.object_type == WallaCategories.VIVA_TITLES:
            return self._update_viva_categories(element_object)
        elif true_object.object_type == WallaCategories.VIVA_SHORT:
            return self._update_viva_series_subcategories(element_object)
        elif true_object.object_type == WallaCategories.VIVA_SHOW:
            return self._update_viva_episodes(element_object)
        elif true_object.object_type == WallaCategories.YES:
            return self._update_yes_categories(element_object)
        else:
            raise ValueError('Unknown url {u} type.'.format(u=element_object.object_type))

    def _update_movie_categories(self, super_object):
        """
        Fetches all the available movie categories.
        :param super_object: Super object.
        :return: Object of all available shows (JSON).
        """
        return self._update_general_categories(super_object, WallaCategories.MOVIE_GENRE)

    def _update_general_categories(self, super_object, object_type):
        """
        Fetches all the available movie categories.
        :param super_object: Super object.
        :param object_type: Object type.
        :return: Object of all available shows (JSON).
        """
        req = self.get_object_request(super_object)
        tree = self.parser.parse(req.text)
        xpath = './/nav[@class="side-nav"]//li/a'
        shows = tree.xpath(xpath)

        sub_objects = []
        for show in shows:
            if 'href' not in show.attrib or urljoin(self.base_url, show.attrib['href']) == super_object.url:
                continue
            title = show.xpath('./span')
            x = WallaCatalogNode(catalog_manager=self.catalog_manager,
                                 obj_id=show.attrib['href'],
                                 title=title[0].text,
                                 url=urljoin(self.base_url, show.attrib['href']),
                                 image_link=None,
                                 super_object=super_object,
                                 object_type=object_type,
                                 raw_data=None)

            sub_objects.append(x)

        super_object.add_sub_objects(sub_objects)

    def _update_movie_titles(self, super_object):
        """
        Fetches all the available movies for a given category object.
        :param super_object: Super object.
        :return:
        """
        return self._update_general_titles(super_object, WallaCategories.VIDEO)

    def _update_general_titles(self, super_object, object_type):
        """
        Fetches all the available movies for a given category object.
        :param super_object: Super object.
        :param object_type: Object type.
        :return:
        """
        req = self.get_object_request(super_object)
        tree = self.parser.parse(req.text)

        if super_object.object_type != WallaCategories.PAGE:
            number_of_sub_pages = self._get_available_pages_from_tree(tree)
            if len(number_of_sub_pages) > 0:
                self._add_category_sub_pages(super_object, WallaCategories.PAGE, req)
        else:
            xpath = './/li/article/a[@itemprop="url"]'
            shows = tree.xpath(xpath)

            sub_objects = []
            for episode in shows:
                show_id = re.findall(r'\d+$', episode.attrib['href'])
                additional_data = self._fetch_additional_title_data(show_id[0])
                x = WallaCatalogNode(catalog_manager=self.catalog_manager,
                                     obj_id=additional_data['id'],
                                     title=additional_data['title'],
                                     description=additional_data['subtitle'],
                                     url=urljoin(self.base_url, episode.attrib['href']),
                                     image_link=urljoin(self.base_url,
                                                        episode.xpath('./div/picture/img/@src')[0]),
                                     super_object=super_object,
                                     duration=self._format_duration(additional_data['duration']),
                                     date=additional_data['release_date'][0]
                                     if len(additional_data['release_date']) > 0 else None,
                                     object_type=object_type,
                                     raw_data=additional_data,
                                     )
                sub_objects.append(x)

            super_object.add_sub_objects(sub_objects)

    def _update_series_categories(self, super_object):
        """
        Fetches all the available series categories.
        :param super_object: Super object.
        :return:
        """
        # The pages have the same structure as for the movie
        return self._update_general_categories(super_object, WallaCategories.SHOW_GENRE)

    def _update_series_titles(self, super_object):
        """
        Fetches all the available series for a given category object.
        :param super_object: Super object.
        :return:
        """
        # The pages have the same structure as for the movie
        return self._update_general_titles(super_object, WallaCategories.SHOW)

    def _update_series_episodes(self, super_object):
        """
        Fetches all the available episodes of the given series.
        :param super_object: Super object.
        :return: Object of all available shows (JSON).
        """
        return self._update_general_episodes(super_object, WallaCategories.SHOW_SEASON)

    def _update_general_episodes(self, super_object, sub_season_object_type):
        """
        Fetches all the available episodes of the given series.
        :param super_object: Super object.
        :param sub_season_object_type: Object type of the sub seasons (in case such exist).
        :return: Object of all available shows (JSON).
        """
        req = self.get_object_request(super_object)
        tree = self.parser.parse(req.text)

        # At first we check whether there are several seasons, and if som we update the super class
        if super_object.object_type in (WallaCategories.SHOW, WallaCategories.KIDS_SHOW):
            available_seasons = tree.xpath('.//section[@class="more-episodes"]//div[@class="drop"]//ul/li/a')
            if len(available_seasons) > 0:
                new_seasons = []
                for i, season in enumerate(available_seasons):
                    new_object = WallaCatalogNode(catalog_manager=self.catalog_manager,
                                                  obj_id=season.attrib['href'],
                                                  title=self.season_prefix + ' ' + season.xpath('./span/text()')[0],
                                                  url=urljoin(self.base_url, season.attrib['href']),
                                                  image_link=super_object.image_link,
                                                  super_object=super_object,
                                                  object_type=sub_season_object_type,
                                                  raw_data=None)
                    new_seasons.append(new_object)
                super_object.add_sub_objects(new_seasons)
                super_object = super_object.sub_objects[0]

        # We add additional pages
        if super_object.object_type != WallaCategories.PAGE:
            additional_pages = self._get_available_pages_from_tree(tree)
            if len(additional_pages) > 0:
                self._add_category_sub_pages(super_object, WallaCategories.PAGE, req)
                super_object = super_object.sub_objects[0]

        split_url = req.url.split('?')
        true_series_id = re.findall(r'\d+$', split_url[0])[0]
        page_number = super_object.page_number if super_object.page_number is not None else 1
        season_object = super_object
        while season_object.object_type not in (WallaCategories.SHOW_SEASON, WallaCategories.KidsShowSeason):
            season_object = season_object.super_object
            if season_object is None:
                break
        season_number = season_object.super_object.sub_objects.index(season_object) + 1 \
            if season_object is not None else 0
        raw_episodes = self._fetch_additional_episodes_data(true_series_id, season_number, page_number-1)

        new_episodes = []
        for raw_episode in raw_episodes:
            img_url = \
                self.episode_image_template.format(fl=raw_episode['media']['types']['46']['file'])
            x = WallaCatalogNode(catalog_manager=self.catalog_manager,
                                 obj_id=raw_episode['id'],
                                 title=raw_episode['title'],
                                 description=raw_episode['subtitle'],
                                 number=self.episode_prefix + ' ' + raw_episode['episodeNumber'],
                                 url=self.episode_url_template.format(eid=raw_episode['id']),
                                 image_link=img_url,
                                 super_object=super_object,
                                 duration=self._format_duration(raw_episode['duration'])
                                 if 'duration' in raw_episode else None,
                                 date=raw_episode['release_date'][0]
                                 if 'release_date' in raw_episode and
                                    len(raw_episode['release_date']) > 0 else None,
                                 object_type=WallaCategories.VIDEO,
                                 raw_data=raw_episode,
                                 )
            new_episodes.append(x)

        super_object.add_sub_objects(new_episodes)

    def _update_yes_categories(self, super_object):
        """
        Fetches all the available YES categories.
        :param super_object: Super object.
        :return:
        """
        # The pages have the same structure as for the movie
        req = self.get_object_request(super_object)
        tree = self.parser.parse(req.text)
        xpath = './/div[@class="container"]/section/section/header[@class="header-section "]/' \
                'h2[@class="section-title "]/a'
        shows = tree.xpath(xpath)

        sub_objects = []
        for show in shows:
            if 'href' not in show.attrib or urljoin(self.base_url, show.attrib['href']) == super_object.url:
                continue
            x = WallaCatalogNode(catalog_manager=self.catalog_manager,
                                 obj_id=show.attrib['href'],
                                 title=show.text,
                                 url=urljoin(self.base_url, show.attrib['href']),
                                 image_link=super_object.image_link,
                                 super_object=super_object,
                                 object_type='category_' + '_'.join(super_object.object_type.split('_')[1:]),
                                 raw_data=None)

            sub_objects.append(x)

        super_object.add_sub_objects(sub_objects)

    def _update_viva_base_categories(self, super_object):
        """
        Fetches all the available shows.
        :return: Base object.
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
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        req = self.session.get(super_object.url, headers=headers)
        tree = self.parser.parse(req.text)
        xpath = './/ul[@class="fc second-nav-items"]/li/a'
        categories = tree.xpath(xpath)

        sub_objects = []
        for category in categories:
            url_path = urlparse(urljoin(self.base_url, category.attrib['href'])).path
            if (
                'href' not in category.attrib or
                urlparse(urljoin(self.base_url, category.attrib['href'])).path not in self.viva_paths
            ):
                continue

            x = WallaCatalogNode(catalog_manager=self.catalog_manager,
                                 obj_id=category.attrib['href'],
                                 title=category.xpath('./span/text()')[0],
                                 url=urljoin(super_object.url, category.attrib['href']),
                                 image_link=super_object.image_link,
                                 super_object=super_object,
                                 object_type=self.viva_paths[url_path],
                                 raw_data=None)
            sub_objects.append(x)

        super_object.add_sub_objects(sub_objects)

    def _update_viva_categories(self, super_object):
        """
        Fetches all the available shows.
        :return: Base object.
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
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        req = self.session.get(super_object.url, headers=headers)
        tree = self.parser.parse(req.text)
        shows = (tree.xpath('.//ul[@class=" fc"]/li[@class="event-default"]/article/a') +
                 tree.xpath('.//ul[@class=" fc"]/li[@class="event-default last-child"]/article/a'))

        sub_objects = []
        for show in shows:
            show_url = urljoin(super_object.url, show.attrib['href'])
            show_id = re.findall(r'\d+$', show_url)[0]
            show_image = urljoin(super_object.url, show.xpath('./div/picture/img/@src')[0])
            show_title = show.xpath('./h3[@class="title "]/div/span[@class="text"]/text()')[0]
            x = WallaCatalogNode(catalog_manager=self.catalog_manager,
                                 obj_id=show_id,
                                 title=show_title,
                                 url=show_url,
                                 image_link=show_image,
                                 super_object=super_object,
                                 object_type=WallaCategories.VIVA_SHOW,
                                 raw_data=None)
            raw_additional_data = json.loads(show.attrib['data-tooltip-event'])
            if 'subtitle' in raw_additional_data:
                x.description = raw_additional_data['subtitle']
            sub_objects.append(x)

        super_object.add_sub_objects(sub_objects)

    def _update_viva_series_subcategories(self, super_object):
        """
        Fetches all the available viva subcategories of the given series.
        :param super_object: Super object.
        :return: Object of all available shows (JSON).
        """
        req = self.get_object_request(super_object)
        tree = self.parser.parse(req.text)

        xpath = './/nav[@class="common-sub-menu"]/ul/li/a'
        subcategories = tree.xpath(xpath)
        sub_objects = []
        for subcategory in subcategories:
            if urljoin(super_object.url, subcategory.attrib['href']) == super_object.url:
                continue
            x = WallaCatalogNode(catalog_manager=self.catalog_manager,
                                 obj_id=subcategory.attrib['href'],
                                 title=subcategory.text,
                                 url=urljoin(super_object.url, subcategory.attrib['href']),
                                 image_link=super_object.image_link,
                                 super_object=super_object,
                                 object_type=WallaCategories.VIVA_SHOW,
                                 )
            sub_objects.append(x)

        super_object.add_sub_objects(sub_objects)

    def _update_viva_episodes(self, super_object):
        """
        Fetches all the available viva subcategories of the given series.
        :param super_object: Super object.
        :return: Object of all available shows (JSON).
        """
        req = self.get_object_request(super_object)
        tree = self.parser.parse(req.text)

        # We add additional pages
        if super_object.object_type != WallaCategories.PAGE:
            additional_pages = self._get_available_pages_from_tree(tree)
            if len(additional_pages) > 0:
                self._add_category_sub_pages(super_object, WallaCategories.PAGE, req)
                super_object = super_object.sub_objects[0]

        episodes = (tree.xpath('.//li[@class="event-default"]/article[@class="article fc common-article "]/a') +
                    tree.xpath('.//li[@class="event-default last-child"]/'
                               'article[@class="article fc common-article "]/a'))

        sub_objects = []
        for episode in episodes:
            if urlparse(episode.attrib['href']).path.split('/')[1] != 'episode':
                continue
            episode_id = re.findall(r'\d+$', episode.attrib['href'])
            x = WallaCatalogNode(catalog_manager=self.catalog_manager,
                                 obj_id=episode_id,
                                 title=episode.xpath('./h3[@class="title "]/div/span/text()')[0],
                                 url=urljoin(super_object.url, episode.attrib['href']),
                                 image_link=urljoin(self.base_url,
                                                    episode.xpath('./div[@class=" figure "]/picture/img/@src')[0]),
                                 super_object=super_object,
                                 raw_data=episode,
                                 object_type=WallaCategories.VIDEO,
                                 )
            raw_additional_data = json.loads(episode.attrib['data-tooltip-event'])
            if 'subtitle' in raw_additional_data:
                x.description = raw_additional_data['subtitle']
            sub_objects.append(x)

        super_object.add_sub_objects(sub_objects)

    def _update_kid_categories(self, super_object):
        """
        Fetches all the available kids categories.
        :param super_object: Super object.
        :return:
        """
        # The pages have the same structure as for the movie
        return self._update_general_categories(super_object, WallaCategories.KidsGenre)

    def _update_kid_titles(self, super_object):
        """
        Fetches all the available kids shows for a given category object.
        :param super_object: Super object.
        :return:
        """
        # The pages have the same structure as for the movie
        return self._update_general_titles(super_object, WallaCategories.KidsShow)

    def _update_kids_episodes(self, super_object):
        """
        Fetches all the available episodes of the given series.
        :param super_object: Super object.
        :return: Object of all available shows (JSON).
        """
        return self._update_general_episodes(super_object, WallaCategories.KidsShowSeason)

    def _update_channel_categories(self, super_object):
        """
        Fetches all the channel categories.
        :param super_object: Super object.
        :return:
        """
        req = self.get_object_request(super_object)
        tree = self.parser.parse(req.text)

        xpath = './/div[@class="provider"]/a'
        shows = tree.xpath(xpath)

        sub_objects = []
        for show in shows:
            image = show.xpath('./img')

            # todo: temporary solution. Need to build special hierarchy for viva...
            channel_url = urljoin(self.base_url, show.attrib['href'])
            if channel_url in self.viva_special_channel_mapping:
                channel_url = self.viva_special_channel_mapping[channel_url]

            split_url = urlparse(channel_url)
            split_path = split_url.path.split('/')
            if len(split_path) <= 2:
                if urlparse(channel_url).hostname == urlparse(self.viva_base_url).hostname:
                    object_type = WallaCategories.VIVA_MAIN
                else:
                    object_type = WallaCategories.TV_CHANNEL
            else:
                object_type = WallaCategories.SHOW_GENRE

            x = WallaCatalogNode(catalog_manager=self.catalog_manager,
                                 obj_id=show.attrib['href'],
                                 title=image[0].attrib['title'].capitalize(),
                                 url=channel_url,
                                 image_link=urljoin(self.base_url, image[0].attrib['src']),
                                 super_object=super_object,
                                 object_type=object_type,
                                 )
            sub_objects.append(x)

        super_object.add_sub_objects(sub_objects)

    def _update_channel_subcategories(self, super_object):
        """
        Fetches all the channel categories.
        :param super_object: Super object.
        :return:
        """
        req = self.get_object_request(super_object)
        tree = self.parser.parse(req.text)

        xpath = './/h2[@class="section-title "]/a'
        shows = tree.xpath(xpath)

        sub_objects = []
        for show in shows:
            url = urljoin(self.base_url, show.attrib['href'])
            x = WallaCatalogNode(catalog_manager=self.catalog_manager,
                                 obj_id=show.attrib['href'],
                                 title=show.text,
                                 url=url,
                                 image_link=super_object.image_link,
                                 super_object=super_object,
                                 object_type=WallaCategories.SHOW_GENRE,
                                 )
            sub_objects.append(x)

        super_object.add_sub_objects(sub_objects)

    def _fetch_additional_title_data(self, title_id):
        """
        Fetches additional data for the given object
        :param title_id: Id number of the wanted title
        :return: Raw data (json) of the wanted data
        """
        headers = {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        params = {
            'ajax': 1,
            'ac': 'movieToolTip',
            'movieId': title_id,
        }
        req = self.session.get(self.base_url, headers=headers, params=params)
        return req.json()

    def _fetch_additional_episodes_data(self, title_id, season_num=0, page_num=1):
        """
        Fetches additional data for the given object
        :param title_id: Id number of the wanted title
        :param season_num: Number of the season of the title. By default is 0 (the season have only one season)
        :param page_num: Number of the page of the title. By default is 1
        :return: Raw data (json) of the wanted data
        """
        headers = {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        params = {
            'ajax': 1,
            'ac': 'getEpisodes',
            'pageId': page_num,
            'itemId': title_id,
            'seasonNumber': season_num,
        }
        req = self.session.get(self.base_url, headers=headers, params=params)
        return req.json()

    def get_video_links_from_video_data(self, video_object):
        """
        Fetches the video property from the given page.
        :param video_object: Video object.
        :return: VideoNode object.
        """
        # We get the data of the page
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': self.object_urls[WallaCategories.CHANNELS_MAIN],
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'User-Agent': self.user_agent
        }
        req = self.session.get(video_object.url, headers=headers)
        tree = self.parser.parse(req.text)
        scripts = tree.xpath('.//video[@class="video-js vjs-default-skin "]')
        assert len(scripts) == 1
        raw_data = json.loads(scripts[0].attrib['data-player'])
        if 'subtitle' in raw_data:
            subtitles = raw_data['subtitle']
            subtitles = {x['language']: x['src'] for x in subtitles}
        else:
            subtitles = None
        new_url = self.video_request_template.format(vid=raw_data['vimmeId'])
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': video_object.url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'User-Agent': self.user_agent
        }
        req = self.session.get(new_url, headers=headers)
        tree = self.parser.parse(req.text)
        playlist_url = tree.xpath('.//fileurl')
        servers = sorted(tree.xpath('.//servers/server'), key=lambda x: int(x.attrib['priority']))
        video_playlists = sorted(((x.attrib['bitrate'], x.text) for x in playlist_url),
                                 key=lambda x: int(x[0]), reverse=True)
        video_playlists = [x[1].replace(self.video_initial_server, y.text) for x in video_playlists for y in servers]
        video_playlists = [urljoin(x, y.uri) for x in video_playlists for y in self.get_video_m3u8(x)]
        video_objects = [VideoSource(link=urljoin(x, y.uri), video_type=VideoTypes.VIDEO_SEGMENTS,
                                     quality=y.stream_info.bandwidth, codec=y.stream_info.codecs)
                         for x in video_playlists for y in self.get_video_m3u8(x)]
        return VideoNode(video_sources=video_objects, raw_data=raw_data, subtitles=subtitles)

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
        req = self.session.get(video_link, headers=headers)
        # req = self.session.get(video_fetch_url, params=params)
        if req.status_code != 200:
            raise RuntimeError('Wrong download status. Got {s}'.format(s=req.status_code))
        video_m3u8 = m3u8.loads(req.text)

        return video_m3u8.playlists

    @staticmethod
    def _format_duration(raw_duration):
        """
        Formats the duration of the given video.
        :param raw_duration: Raw duration (string with minutes).
        :return: Duration in seconds (int).
        """
        return int(raw_duration) * 60

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (WallaCategories.CHANNELS_MAIN,):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        if not page_request.ok:
            return 1
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    @staticmethod
    def _get_available_pages_from_tree(tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return ([int(x) for x in tree.xpath('.//nav/ul/li/a/text()') if x.isdigit()] +
                [i+1 for i, _ in enumerate(tree.xpath('.//nav/ul/li/a/span/text()'))])

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
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': page_data.url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if re.findall(r'\d+$', page_data.url):
            i = page_data.page_number if page_data.page_number is not None else 1
            params = {'page': i}
        else:
            params = {}

        req = self.session.get(page_data.url, headers=headers, params=params)
        return req

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        raise NotImplementedError


if __name__ == '__main__':
    # loc_show_id = IdGenerator.make_id('/movies')
    # loc_season_id = IdGenerator.make_id('/movies/6256')
    # loc_episode_id = IdGenerator.make_id('/movie/2968988')
    # loc_show_id = IdGenerator.make_id('/tvshows')
    # loc_season_id = IdGenerator.make_id('/tvshows/7752')
    # loc_episode_id = IdGenerator.make_id('2855819')  # Shtisel
    # loc_season_id = IdGenerator.make_id('/tvshows/9006')
    # loc_episode_id = IdGenerator.make_id('2928982')  # Rincón de Luz
    # loc_season_id = IdGenerator.make_id('/tvshows/9006')
    # loc_show_id = IdGenerator.make_id('/kids')
    # loc_season_id = IdGenerator.make_id('/kids/8524')  # כוכב הצפון
    # loc_episode_id = IdGenerator.make_id('2855972')  # כוכב הצפון
    # loc_show_id = IdGenerator.make_id('/channels')
    # loc_season_id = IdGenerator.make_id('/yes')  # כוכב הצפון
    # loc_episode_id = IdGenerator.make_id('/tvshows/8523/drama')  # כוכב הצפון
    # loc_episode_id2 = IdGenerator.make_id('3211034')  # כוכב הצפון
    loc_show_id = IdGenerator.make_id('/channels')
    loc_season_id = IdGenerator.make_id('http://viva.walla.co.il')  # ויוה
    loc_episode_id = IdGenerator.make_id('/fullepisodes')  # פרקים מלאים
    loc_episode_id2 = IdGenerator.make_id('3206104')  # הכלה מאיסטנבול
    loc_episode_id3 = IdGenerator.make_id((u'3206104', 2))  # הכלה מאיסטנבול
    kan = Walla(store_dir='D:\\')
    # todo: to run test on viva
    # kan.get_show_object(loc_show_id, )
    # kan.get_show_object(loc_show_id, loc_season_id)
    # kan.get_show_object(loc_show_id, loc_season_id, loc_episode_id)
    # kan.get_show_object(loc_show_id, loc_season_id, loc_episode_id, loc_episode_id2)
    # kan.get_show_object(loc_show_id, loc_season_id, loc_episode_id, loc_episode_id2)
    # kan.get_show_object(loc_show_id, loc_season_id, loc_episode_id, loc_episode_id3)
    # kan.update_available_shows()
    # kan.download_objects(loc_show_id, verbose=1)
    # kan.download_objects(loc_show_id, loc_season_id, verbose=1)
    # kan.download_objects(loc_show_id, loc_season_id, loc_episode_id, verbose=1)
    # kan.download_objects(cat_id, episode_id, episode_id=, verbose=1)
    kan.download_category_input_from_user()
