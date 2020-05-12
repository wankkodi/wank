# -*- coding: UTF-8 -*-
from ....fetchers.vod_fetcher import VODFetcher
# Video catalog
from ....catalogs.vod_catalog import VODCatalogNode, VODCategories, VideoNode, VideoSource, VideoTypes

# Regex

# Warnings and exceptions
# import warnings

# JSON
from ....tools.text_json_manioulations import prepare_json_from_not_formatted_text

# regex
import re

# M3U8
import m3u8

# Math
# import math

# Internet tools
from .... import urljoin


class Channel20(VODFetcher):
    video_fetch_url = 'https://secure.brightcove.com/services/mobile/streaming/index/master.m3u8'
    season_prefix = u"עונה"
    episode_prefix = u"פרק"
    full_episodes_title = u'פרקים מלאים'
    selected_parts_title = u'קטעים נבחרים'

    @property
    def object_urls(self):
        return {
            VODCategories.CHANNELS_MAIN: 'https://www.20il.co.il/vod/',
            VODCategories.LIVE_VIDEO: 'https://www.20il.co.il/vod/',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.20il.co.il/'

    def __init__(self, vod_name='Channel20', vod_id=-16, store_dir='.', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        self.episodes_to_data = {}
        self.season_to_show = {}
        super(Channel20, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)

    def fetch_sub_objects(self, element_object):
        """
        Fetches object's sub objects.
        :param element_object: Object element we want to fetch.
        :return:
        """
        if element_object.object_type == VODCategories.CHANNELS_MAIN:
            return self._update_base_categories(element_object)
        elif element_object.object_type in (VODCategories.SHOW, VODCategories.PAGE):
            return self._fetch_show(element_object)
        else:
            raise ValueError('Wrong additional_type parameter!')

    def _update_base_categories(self, base_object):
        """
        Fetches all the available shows.
        :return: Base object.
        """
        req = self.get_object_request(base_object)
        tree = self.parser.parse(req.text)
        shows = tree.xpath('.//div[@class="show-list"]/div[@class="show"]/div[@class="show-thumb"]/a')

        sub_objects = []
        for show in shows:
            if 'href' not in show.attrib:
                continue
            show_data = show.xpath('./img')
            x = VODCatalogNode(catalog_manager=self.catalog_manager,
                               obj_id=show.attrib['href'],
                               title=show_data[0].attrib['title'],
                               url=urljoin(self.base_url, show.attrib['href']),
                               image_link=show_data[0].attrib['src'],
                               super_object=base_object,
                               object_type=VODCategories.SHOW,
                               raw_data=show)
            sub_objects.append(x)

        base_object.add_sub_objects(sub_objects)

        # with open(self.available_shows_data_filename, 'wb') as fl:
        #     pickle.dump(self.available_categories, fl)

    def _fetch_show(self, request_object):
        """
        Fetches the show videos
        :param request_object: Request object.
        :return:
        """
        req = self.get_object_request(request_object)
        tree = self.parser.parse(req.text)

        # At first we produce pages
        number_of_pages = self._get_number_of_sub_pages(request_object, req)
        if request_object.object_type is not VODCategories.PAGE and number_of_pages > 1:
            self._add_category_sub_pages(request_object, VODCategories.PAGE, req)
            request_object = request_object.sub_objects[0]

        for xpath_substring, title_suffix, sub_id in (('catabfull', self.full_episodes_title, 0),
                                                      ('catabpart', self.selected_parts_title, 1)):
            episode_pages = tree.xpath('.//div[@id="{xs}"]/article'.format(xs=xpath_substring))
            if len(episode_pages) > 0:
                # We create full episodes object
                sub_obj = VODCatalogNode(catalog_manager=self.catalog_manager,
                                         obj_id=(request_object.id, sub_id, 1),
                                         title=request_object.title + ' - ' + title_suffix,
                                         page_number=1,
                                         url=request_object.url,
                                         image_link=request_object.image_link,
                                         super_object=request_object,
                                         object_type=VODCategories.GENERAL_CHANNEL_SUB_CATEGORY,
                                         additional_data={'sub_id': sub_id},
                                         )
                request_object.add_sub_objects([sub_obj])

                self._fetch_additional_page_from_html(sub_obj, req.text)

    def _fetch_additional_page_from_html(self, request_object, html):
        """
        Fetches the show videos for additional page from html.
        :param request_object: Request object.
        :return:
        """
        tree = self.parser.parse(html)

        sub_objects = []
        if 'sub_id' in request_object.additional_data and request_object.additional_data['sub_id'] == 0:
            xpath_substring = 'catabfull'
        elif 'sub_id' in request_object.additional_data and request_object.additional_data['sub_id'] == 1:
            xpath_substring = 'catabpart'
        else:
            raise RuntimeError('Unknown additional type of the page {p}'.format(p=request_object.additional_data))

        episode_pages = tree.xpath('.//div[@id="{xs}"]/article'.format(xs=xpath_substring))
        if len(episode_pages) > 0:
            # We create full episodes object
            sub_objects = []
            for episode_tree in episode_pages:
                episode_url = episode_tree.xpath('./div[@class="post-thumbnail"]/a/@href')
                assert len(episode_url) == 1
                image = episode_tree.xpath('./div[@class="post-thumbnail"]/a/img/@src')
                assert len(image) == 1
                title = episode_tree.xpath('./div[@class="entry"]/h2[@class="post-box-title"]/a/text()')
                assert len(title) == 1
                subtitle = episode_tree.xpath('./div[@class="entry"]/p/text()')
                # assert len(subtitle) == 1
                episode_object = VODCatalogNode(catalog_manager=self.catalog_manager,
                                                obj_id=episode_url[0],
                                                title=title[0],
                                                image_link=image[0],
                                                url=episode_url[0],
                                                super_object=request_object,
                                                subtitle=subtitle[0] if len(subtitle) > 0 else None,
                                                object_type=VODCategories.VIDEO,
                                                )
                sub_objects.append(episode_object)
        request_object.add_sub_objects(sub_objects)

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data (CatalogNode).
        :return:
        """
        # We get the data of the page
        req = self.get_object_request(video_data)
        tree = self.parser.parse(req.text)
        scripts = [x.attrib['src'] for x in tree.xpath('.//iframe[@src]') if 'cdn' in x.attrib['src']]
        assert len(scripts) == 1
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'nested-navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        req = self.session.get(scripts[0], headers=headers)
        new_url = re.findall(r'(?:player.src\()({.*}?)(?:\);)', req.text)
        assert len(new_url) == 1
        new_url = prepare_json_from_not_formatted_text(new_url[0])

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
        req = self.session.get(new_url['src'], headers=headers)
        video_m3u8 = m3u8.loads(req.text)
        video_playlists = video_m3u8.playlists
        if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
            video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)

        video_objects = [VideoSource(link=urljoin(new_url['src'], x.uri),
                                     video_type=VideoTypes.VIDEO_SEGMENTS,
                                     quality=x.stream_info.bandwidth,
                                     codec=x.stream_info.codecs)
                         for x in video_playlists]
        return VideoNode(video_sources=video_objects, raw_data=req.text)

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

    def get_live_stream_info(self):
        """
        Fetches the live stream data.
        :return: CatalogNode object.
        """
        return VODCatalogNode(catalog_manager=self.catalog_manager,
                              obj_id=-1,
                              title=u'שידור חי - ערוץ 20',
                              url=self.object_urls[VODCategories.LIVE_VIDEO],
                              object_type=VODCategories.LIVE_SCHEDULE
                              )

    def get_live_stream_video_link(self):
        """
        Fetches the live stream video_link.
        :return: VideoNode object.
        """
        return self.get_video_links_from_video_data(self.get_live_stream_info())

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        if fetched_request is None:
            fetched_request = self.get_object_request(category_data)
        tree = self.parser.parse(fetched_request.text)

        pages = [int(x) for x in tree.xpath('.//div[@class="pagination"]/a/text()') if x.isdigit()]
        return max(pages) if len(pages) > 0 else 1

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
        if page_data.page_number is not None and page_data.page_number > 1:
            fetch_base_url += 'page/{p}/'.format(p=page_data.page_number)

        req = self.session.get(fetch_base_url, headers=headers, params=params)
        return req

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Channel20, self)._version_stack + [self.__version]
