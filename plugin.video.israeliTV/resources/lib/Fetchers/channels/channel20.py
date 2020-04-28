# -*- coding: UTF-8 -*-
from ..fetchers.vod_fetcher import VODFetcher
# Video catalog
from ..catalogs.vod_catalog import VODCatalogNode, VODCategories, VideoNode, VideoSource, VideoTypes

# Regex

# Warnings and exceptions
# import warnings

# # JSON
# import json

# JSON
from ..tools.text_json_manioulations import prepare_json_from_not_formatted_text

# regex
import re

# M3U8
import m3u8

# Math
# import math

# ID generator
from ..id_generator import IdGenerator

# Internet tools
from .. import urljoin


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


if __name__ == '__main__':
    loc_show_id = IdGenerator.make_id('https://www.20il.co.il/%d7%aa%d7%95%d7%9b%d7%a0%d7%99%d7%95%d7%aa/'
                                      '%d7%94%d7%a4%d7%98%d7%a8%d7%99%d7%95%d7%98%d7%99%d7%9d/')  # The patriots
    loc_season_id = IdGenerator.make_id((loc_show_id, 0, 2))
    loc_episode_id = IdGenerator.make_id('https://www.20il.co.il/%d7%aa%d7%95%d7%9b%d7%a0%d7%99%d7%95%d7%aa/'
                                         '%d7%94%d7%a4%d7%98%d7%a8%d7%99%d7%95%d7%98%d7%99%d7%9d/%d7%94%d7%'
                                         'a4%d7%98%d7%a8%d7%99%d7%95%d7%98%d7%99%d7%9d-%d7%99%d7%95%d7%9d-%d7%'
                                         '90-8-9-%d7%94%d7%aa%d7%9b%d7%a0%d7%99%d7%aa-%d7%94%d7%9e%d7%9c%d7%'
                                         '90%d7%94/')
    # loc_show_id = int('101794581731159521225600776059010804004283617640567403183725348334278765309790471239102578351'
    #                   '101897538432381250175601909422303126600444225930591310075381831845841933360357488687026378783'
    #                   '923019780637895461313164004435267537009540610351902754913042913454085479098729419210613865280'
    #                   '0827279369263')
    # loc_season_id = int('7102493508383351395849822970694131724042227119700339337087833700418730489463542749242250616'
    #                     '4195955794759578253688617298036897689687041690409815855807827619906035151266957323464716989'
    #                     '1984721718805220599704498147668606780903802362168938289460497290359598519723727822392560339'
    #                     '1289469884057150732422432299984261102641928910393278729249647844751122419241043639110387265'
    #                     '4967463853368825411598204128107695398529375688251261006022418714577309265626181100090165190'
    #                     '6175296103758960412055112242158408401780049182430241880520222082205413846967069222865526119'
    #                     '8502903299351732699361775703050200113571022030665514155248827228847933042174813508586698191'
    #                     '36814694994855679483562447911027721177373827804687587793102647784143586557177897')
    # loc_season_id = int('7102493508383351395849822970694131724042227119700339337087833700418730489463542749242250616'
    #                     '4195955794759578253688617298036897689687041690409815855807827619906035151266957323464716989'
    #                     '1984721718805220599704498147668606780903802362168938289460497290359598519723727822392560339'
    #                     '1289469884057150732422432299984261102641928910393278729249647844751122419241043639110387265'
    #                     '4967463853368825411598204128107695398529375688251261006022418714577309265626181100090165190'
    #                     '6175296103758960412055112242158408401780049182430241880520222082205413846967069222865526119'
    #                     '8502903299351732699361775703050200113571022030665514155248827228847933042174813508586698191'
    #                     '36814694994855679483562447911027721177373827804687587793102647784143586557177897')
    # loc_episode_id = int('752799497009087062736443045613640618329145588542836704144603012207569778386408420466144079'
    #                      '035973119694593044441192534322147567331045159309325999703751307247934850183998256091665349'
    #                      '936544702535962552464711336521882674874635646079880509138665782901445172952184104684197090'
    #                      '344705592783518978996249632721877003137829904876035557730107827899188837133298367532620112'
    #                      '442259928373895708719052745684570162345418447691130887993513658267361336239928341351939276'
    #                      '303747771816427745343507890327034334054715022152947725745554678407022377793435874734775856'
    #                      '909747848572011744301596411384127612378748883283927510821241772749289619325082139983041327'
    #                      '30258089810164540533025426453551')

    kan = Channel20(store_dir='D:\\')
    # kan.get_video_links_from_video_data('https://vod.walla.co.il/movie/2969050')
    # kan.fetch_video_from_episode_url('https://13tv.co.il/item/entertainment/the-voice/season-02/'
    #                                   'episodes/episode1-25/')
    # kan.update_available_shows()
    # kan.get_show_object(*())
    # kan.get_show_object(*(loc_show_id, ))
    # kan.get_show_object(*(loc_show_id, loc_season_id))
    # kan.get_show_object(*(loc_show_id, loc_season_id, loc_episode_id))
    #
    # kan.get_live_stream_info()
    # kan.get_live_stream_video_link()

    # kan.download_objects(loc_show_id, verbose=1)
    # kan.download_objects(loc_show_id, loc_season_id, verbose=1)
    # kan.download_objects(loc_show_id, loc_season_id, loc_episode_id, verbose=1)
    # kan.download_objects(cat_id, episode_id, episode_id=, verbose=1)
    # kan._get_video_links_from_episode_url('https://www.kan.org.il/program/?catid=1464', verbose=1)
    kan.download_category_input_from_user()
