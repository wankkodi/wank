# -*- coding: UTF-8 -*-
from ....fetchers.vod_fetcher import VODFetcher
# Video catalog
from ....catalogs.vod_catalog import VODCatalogNode, VODCategories, VideoNode, VideoSource, VideoTypes

# Brightcove
from ....tools.common_video_host import Brightcove

# Regex
import re

# M3U8
import m3u8

# Internet tools
from .... import urljoin


class Sport1(VODFetcher):
    video_data_request_url_template = 'https://edge.api.brightcove.com/playback/v1/accounts/{uid}/videos/{vid}'
    playlist_request_url_template = 'https://edge.api.brightcove.com/playback/v1/accounts/{aid}/playlists/{pid}'

    dummy_id_key = 'dummy_id'

    @property
    def object_urls(self):
        return {
            VODCategories.CHANNELS_MAIN: 'https://sport1.maariv.co.il/VOD',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://sport1.maariv.co.il/'

    def __init__(self, vod_name='Sport1', vod_id=-15, store_dir='.', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(Sport1, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)
        self.brightcove = Brightcove(self.session, self.user_agent)

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
        req = self.get_object_request(base_object)
        tree = self.parser.parse(req.text)
        xpath = './/div[@class="col-xs-12 text-right"]/a'
        shows = tree.xpath(xpath)

        main_objects = [VODCatalogNode(catalog_manager=self.catalog_manager,
                                       obj_id=show.attrib['href'],
                                       title=show.text,
                                       url=urljoin(self.base_url, show.attrib['href']),
                                       super_object=base_object,
                                       object_type=VODCategories.GENERAL_CHANNEL_SUB_CATEGORY,
                                       raw_data=show)
                        for show in shows]

        base_object.add_sub_objects(main_objects)

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data (dict).
        :return:
        """
        # We get the data of the page
        req = self.get_object_request(video_data)
        tree = self.parser.parse(req.text)
        video_raw_data = tree.xpath('.//video-js')
        assert len(video_raw_data) == 1
        video_raw_data = video_raw_data[0]

        data_video_id = re.findall(r'(?:beforePlaylistVideo = \')(\d+)(?:\')', req.text)
        raw_m3u8 = self.brightcove.get_video_links(vid=data_video_id,
                                                   secure=True)

        new_data = m3u8.loads(raw_m3u8)
        video_playlists = new_data.playlists
        if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
            video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)
        res = [VideoSource(link=x.uri, video_type=VideoTypes.VIDEO_SEGMENTS,
                           quality=x.stream_info.bandwidth, codec=x.stream_info.codecs)
               for x in video_playlists]

        if len(res) == 0:
            # We use another method
            new_data = \
                self.brightcove.get_video_links_alt(account_id=video_raw_data.attrib['data-account'],
                                                    player_id=video_raw_data.attrib['data-player'],
                                                    referer=video_data.url,
                                                    video_id=data_video_id[0])

            res = sorted(((x['avg_bitrate'], x['src']) for x in new_data['sources']
                          if 'avg_bitrate' in x and 'src' in x),
                         key=lambda y: y[0], reverse=True)
            res = [VideoSource(link=x[1], video_type=VideoTypes.VIDEO_REGULAR, quality=x[0])
                   for x in res]

        return VideoNode(video_sources=res, raw_data=new_data)

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
        tree = self.parser.parse(req.text)

        main_raw_object = tree.xpath('.//div[@class="row top-story-video"]')
        assert len(main_raw_object) == 1
        sub_objects = [VODCatalogNode(catalog_manager=self.catalog_manager,
                                      obj_id=(show_object.id, 'video'),
                                      title=re.sub(r'^[ \t\n]*|[ \t\n]*$', '',
                                                   main_raw_object[0].xpath('./div[@class="top-story-video-title"]/'
                                                                            'text()')[0]),
                                      url=show_object.url,
                                      date=main_raw_object[0].xpath('./span[@class="video-date"]/text()')[0],
                                      # image_link=urljoin(show_object.url,
                                      #                    main_raw_object[0].xpath('./div[@class="main-video"]//'
                                      #                                             'video_js/video/@poster')[0]),
                                      object_type=VODCategories.VIDEO,
                                      super_object=show_object)]

        raw_sub_objects = tree.xpath('.//div[@class="videos-list"]/div[@class="videos-article-inner-list"]/'
                                     'div[@class="video-item"]')
        # At first we add the additional objects
        for x in raw_sub_objects:
            sub_objects.append(VODCatalogNode(catalog_manager=self.catalog_manager,
                                              obj_id=x.xpath('./a[@class="video-img-link"]/@href')[0],
                                              title=x.xpath('./a[@class="video-title-link"]/div/text()')[0],
                                              url=urljoin(show_object.url,
                                                          x.xpath('./a[@class="video-img-link"]/@href')[0]),
                                              date=x.xpath('./a[@class="video-date-link"]/div/text()')[0],
                                              image_link=urljoin(show_object.url,
                                                                 x.xpath('./a[@class="video-img-link"]/img/@src')[0]),
                                              object_type=VODCategories.VIDEO,
                                              super_object=show_object)
                               )

        show_object.add_sub_objects(sub_objects)

        return show_object

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
        url = page_data.url
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
        req = self.session.get(url, headers=headers)
        return req

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        raise NotImplementedError

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        return NotImplemented

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Sport1, self)._version_stack + [self.__version]
