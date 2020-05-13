# -*- coding: UTF-8 -*-
# Regex
import re

# Internet tools
from .... import urljoin, unquote_plus
# Video catalog
from ....catalogs.vod_catalog import VODCatalogNode, VODCategories, VideoNode, VideoSource, VideoTypes
from ....fetchers.vod_fetcher import VODFetcher

# JSON manipulations
from ....tools.text_json_manioulations import prepare_json_from_not_formatted_text


class Channel9(VODFetcher):
    schedule_page = 'https://www.9tv.co.il/allprograms'

    # israel_time_timedelta = timedelta(seconds=3*3600)

    @property
    def object_urls(self):
        return {
            VODCategories.CHANNELS_MAIN: 'https://www.9tv.co.il/allprograms',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.9tv.co.il/'

    def __init__(self, source_name='Channel9', source_id=-17, store_dir='.', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        self.episodes_to_data = {}
        super(Channel9, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server, session_id)

    # # Obsolete
    # def _update_base_categories(self, base_object):
    #     """
    #     Fetches all the available shows.
    #     :return: Object of all available shows (JSON).
    #     """
    #     req = self.get_object_request(base_object)
    #     tree = self.parser.parse(req.content.decode('utf-8'))
    #     categories_trees = tree.xpath('.//ul[@class="tv-menu"]/li')
    #     main_categories = []
    #     for i, category_tree in enumerate(categories_trees):
    #         if i not in range(1, 4):
    #             # We skip the first one because it is the home category, which has no videos...
    #             continue
    #         main_category = CatalogNode(catalog_manager=self.catalog_manager,
    #                                     obj_id=i,
    #                                     title=category_tree.xpath('./a/text()')[0],
    #                                     url=self.base_url,
    #                                     super_object=base_object,
    #                                     object_type=GENERAL_CHANNEL_SUB_CATEGORY,
    #                                     raw_data=category_tree)
    #         sub_categories_trees = category_tree.xpath('./ul/li/a')
    #         sub_categories = [CatalogNode(catalog_manager=self.catalog_manager,
    #                                       obj_id=(i, j),
    #                                       title=sub_category_tree.text,
    #                                       url=urljoin(self.base_url, sub_category_tree.attrib['href']),
    #                                       super_object=main_category,
    #                                       object_type=Show,
    #                                       raw_data=sub_category_tree)
    #                           for j, sub_category_tree in enumerate(sub_categories_trees)]
    #         main_category.add_sub_objects(sub_categories)
    #         main_categories.append(main_category)
    #
    #     base_object.add_sub_objects(main_categories)
    #
    #     # with open(self.available_shows_data_filename, 'wb') as fl:
    #     #     pickle.dump(self.available_categories, fl)

    def _update_base_categories(self, base_object):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        req = self.get_object_request(base_object)
        tree = self.parser.parse(req.content.decode('utf-8'))
        categories_trees = tree.xpath('.//ul[@class="content_half_list programs w-list-unstyled"]/li/a')
        main_categories = []
        for category in categories_trees:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="item_pict programs"]')
            image = urljoin(base_object.url, re.findall(r'(?:url\()(.*?)(?:\))', image_data[0].attrib['style'])[0])
            description2 = image_data[0].attrib['title']

            title_data = category.xpath('./div[@class="program_tv_info"]/h2')
            title = title_data[0].text

            sub_title_data = category.xpath('./div[@class="program_tv_info"]/div')
            description = sub_title_data[0].text

            main_categories.append(VODCatalogNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  description=description,
                                                  subtitle=description2,
                                                  image_link=image,
                                                  super_object=base_object,
                                                  object_type=VODCategories.SHOW))

        base_object.add_sub_objects(main_categories)

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
        elif element_object.object_type in (VODCategories.GENERAL_CHANNEL_SUB_CATEGORY, VODCategories.SHOW,
                                            VODCategories.PAGE):
            return self._get_episodes_show_object(element_object)
        else:
            raise ValueError('Wrong additional_type parameter!')

    def get_video_links_from_video_data(self, video_data, verbose=0):
        """
        Fetches the video property from the given page.
        :param video_data: video data.
        The dummy parameter is used to find the proper episode by its id.
        :param verbose: Verbose indicator.
        :return: VideoNode object.
        """
        # We get the data of the page
        if video_data.url in self.episodes_to_data:
            episode_data = self.episodes_to_data[video_data.url]
            if (
                    episode_data.additional_data is not None and
                    'video_link' in episode_data.additional_data and
                    episode_data.additional_data['video_link'] is not None
            ):
                video_objects = VideoSource(link=episode_data.additional_data['video_link'],
                                            video_type=VideoTypes.VIDEO_REGULAR)
                return VideoNode(video_sources=[video_objects], raw_data=episode_data)

        req = self.get_object_request(video_data)
        tree = self.parser.parse(req.content.decode('utf-8'))
        raw_script = tree.xpath('.//div[@id="player"]/script')[0].text
        raw_source = re.findall(r'(?:source: )({.*})(?:,)', raw_script)[0]
        raw_video_data = prepare_json_from_not_formatted_text(raw_source)
        if 'src' in raw_video_data:
            video_objects = VideoSource(link=[raw_video_data['src']], video_type=VideoTypes.VIDEO_REGULAR)
            return VideoNode(video_sources=[video_objects])

        videos = [x for x in tree.xpath('.//script') if x.text is not None and 'source' in x.text]
        if len(videos) > 0:
            videos = re.findall(r'(?:src: \')(.*?)(?:\')', videos[0].text)
            video_objects = VideoSource(link=videos, video_type=VideoTypes.VIDEO_REGULAR)
            return VideoNode(video_sources=[video_objects])

        # We try another method...
        videos = [urljoin(video_data.url, x) for x in tree.xpath('.//source[@type="video/mp4"]/@src')]
        if len(videos) > 0:
            video_objects = VideoSource(link=videos, video_type=VideoTypes.VIDEO_REGULAR)
            return VideoNode(video_sources=[video_objects])

        # We try another method...
        videos = [x for x in tree.xpath('.//script') if x.text is not None and 'file' in x.text]
        if len(videos) > 0:
            videos = re.findall(r'(?:file: *["\'])(.*?)(?:["\'])', videos[0].text)
            video_objects = VideoSource(link=videos, video_type=VideoTypes.VIDEO_REGULAR)
            return VideoNode(video_sources=[video_objects])

        raise RuntimeError('Cannot fetch video link. Check thee url {u}'.format(u=video_data.url))

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

    def _get_episodes_show_object(self, show_object):
        """
        Fetches the show seasons from show object.
        :param show_object: Show object.
        :return: list of Season objects.
        """
        # In case we have it in our db, we fetch it from, there
        if show_object.id in self.show_data:
            return self.show_data[show_object.id]

        req = self.get_object_request(show_object)
        tree = self.parser.parse(req.content.decode('utf-8'))

        # Sub pages
        max_page = self._get_number_of_sub_pages(show_object, req)
        if show_object.object_type == VODCategories.SHOW and max_page > 1:
            additional_objects = [VODCatalogNode(catalog_manager=self.catalog_manager,
                                                 obj_id=(show_object.id, i+1),
                                                 title=show_object.title + ' | Page {i}'.format(i=i+1),
                                                 url=show_object.url + ('/{i}'.format(i=i+1) if i > 0 else ''),
                                                 super_object=show_object,
                                                 page_number=i+1,
                                                 object_type=VODCategories.PAGE,
                                                 )
                                  for i in range(max_page)]
            assert len(additional_objects) > 0
            show_object.add_sub_objects(additional_objects)
            self.show_data[show_object.id] = show_object
            show_object = show_object.sub_objects[0]

        # Sub objects
        # First object if found on page itself
        first_title = tree.xpath('.//div[@class="program_main_item"]/div[3]')[0].text
        first_description = tree.xpath('.//div[@class="program_main_item"]/div[@class="program_main_date"]')[0].text
        first_image = urljoin(show_object.url, re.findall(r'(?:poster: \')(.*?)(?:\')', req.text)[0])
        episodes = [VODCatalogNode(catalog_manager=self.catalog_manager,
                                   obj_id=(show_object.id, 1),
                                   title=first_title,
                                   description=first_description,
                                   url=show_object.url,
                                   image_link=first_image,
                                   super_object=show_object,
                                   object_type=VODCategories.VIDEO,
                                   )]
        episode_trees = tree.xpath('.//ul[@class="content_half_list program w-list-unstyled"]/li/a')
        for episode_tree in episode_trees:
            episode_link = urljoin(show_object.url, episode_tree.attrib['href'])
            episode_image = urljoin(show_object.url, episode_tree.xpath('./div/img')[0].attrib['src'])
            episode_title = episode_tree.xpath('.//div[@class="program_item_info"]/'
                                               'div[@class="program_item_title"]')[0].text
            episode_description = episode_tree.xpath('.//div[@class="program_item_info"]/'
                                                     'div[@class="program_item_date"]')[0].text
            episode = VODCatalogNode(catalog_manager=self.catalog_manager,
                                     obj_id=episode_link,
                                     title=episode_title,
                                     description=episode_description,
                                     url=episode_link,
                                     image_link=episode_image,
                                     super_object=show_object,
                                     object_type=VODCategories.VIDEO,
                                     raw_data=episode_tree)
            episodes.append(episode)
            self.episodes_to_data[episode.url] = episode

        show_object.add_sub_objects(episodes)

        self.show_data[show_object.id] = show_object
        # with open(self.shows_data_filename, 'wb') as fl:
        #     pickle.dump(self.category_data, fl)
        return show_object

    # # Obsolete
    # def _get_episodes_show_object(self, show_object):
    #     """
    #     Fetches the show seasons from show object.
    #     :param show_object: Show object.
    #     :return: list of Season objects.
    #     """
    #     # In case we have it in our db, we fetch it from, there
    #     if show_object.id in self.show_data:
    #         return self.show_data[show_object.id]
    #
    #     req = self.get_object_request(show_object)
    #     tree = self.parser.parse(req.content.decode('utf-8'))
    #
    #     # Additional objects
    #     max_page = self._get_number_of_sub_pages(show_object, req)
    #     if show_object.object_type == Show and max_page > 1:
    #         additional_objects = [CatalogNode(catalog_manager=self.catalog_manager,
    #                                           obj_id=(show_object.id, i+1),
    #                                           title=show_object.title,
    #                                           url=show_object.url,
    #                                           super_object=show_object,
    #                                           page_number=i+1,
    #                                           object_type=Page,
    #                                           )
    #                               for i in range(max_page)]
    #         assert len(additional_objects) > 0
    #         show_object.add_sub_objects(additional_objects)
    #         self.show_data[show_object.id] = show_object
    #         show_object = show_object.sub_objects[0]
    #
    #     # Sub objects
    #     episode_trees = tree.xpath('.//div[@class="articlesList"]/div[@class="col span_1_of_3"]')
    #     episodes = []
    #     for episode_tree in episode_trees:
    #         episode_link = urljoin(self.base_url, episode_tree.xpath('./div[@class="img-box"]/a/@href')[0])
    #         episode_video_link = \
    #             (urljoin(self.base_url, episode_tree.xpath('./div[@class="img-box"]/a/@hola_ve_preview')[0])
    #              if len(episode_tree.xpath('./div[@class="img-box"]/a/@hola_ve_preview')) > 0 else None)
    #         episode_image = urljoin(self.base_url, episode_tree.xpath('./div[@class="img-box"]/a/img/@src')[0])
    #         episode_title = episode_tree.xpath('./h3/a/text()')[0]
    #         episode_description = episode_tree.xpath('./p/a/text()')[0]
    #         episode_date = episode_tree.xpath('./div[@class="date-comments"]/text()')[0]
    #         episode = CatalogNode(catalog_manager=self.catalog_manager,
    #                               obj_id=episode_link,
    #                               title=episode_title,
    #                               description=episode_date + ' ' + episode_description,
    #                               url=episode_link,
    #                               image_link=episode_image,
    #                               super_object=show_object,
    #                               object_type=Video,
    #                               additional_data={'video_link': episode_video_link},
    #                               raw_data=episode_tree)
    #         episodes.append(episode)
    #         self.episodes_to_data[episode.url] = episode
    #
    #     show_object.add_sub_objects(episodes)
    #
    #     self.show_data[show_object.id] = show_object
    #     # with open(self.shows_data_filename, 'wb') as fl:
    #     #     pickle.dump(self.category_data, fl)
    #     return show_object
    #
    def get_live_stream_video_link(self):
        """
        Fetches the live stream video_link.
        :return: VideoNode object.
        """
        raise NotImplementedError

    # def _update_live_schedule_data(self):
    #     """
    #     Updates the live schedule data.
    #     :return:
    #     """
    #     program_fetch_url = self.schedule_page
    #     headers = {
    #         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
    #                   'q=0.8,application/signed-exchange;v=b3',
    #         'Accept-Encoding': 'gzip, deflate',
    #         'Cache-Control': 'max-age=0',
    #         'Host': urlparse(self.base_url).hostname,
    #         'Upgrade-Insecure-Requests': '1',
    #         'User-Agent': self.user_agent
    #     }
    #
    #     req = self.session.get(program_fetch_url, headers=headers)
    #     tree = self.parser.parse(req.content.decode('utf-8'))
    #     daily_schedule_trees = [x for x in tree.xpath('.//div')
    #                             if 'id' in x.attrib and 'tv_programm_' in x.attrib['id']]
    #     assert len(daily_schedule_trees) > 0
    #     res = {}
    #     for daily_schedule_tree in daily_schedule_trees:
    #         raw_date = re.findall(r'(?:tv_programm_)(\d+)', daily_schedule_tree.attrib['id'])[0]
    #         try:
    #             formatted_date = datetime.strptime(raw_date, '%Y%m%d').date()
    #         except TypeError:
    #             formatted_date = datetime(*(time.strptime(raw_date, '%Y%m%d')[0:6]))
    #         if formatted_date not in res:
    #             res[formatted_date] = []
    #         formatted_next_date = formatted_date + timedelta(days=1)
    #
    #         daily_shows = daily_schedule_tree.xpath('./ul/li/span[@class="time"]')
    #         assert len(daily_shows) > 0
    #         is_next_day = False
    #         for first_show, next_show in zip(daily_shows[:-1], daily_shows[1:]):
    #             clean_title = self._clear_text(first_show.tail)
    #             clean_start_time = self._clear_text(first_show.text)
    #             clean_end_time = self._clear_text(next_show.text)
    #             start_time = datetime.strptime(clean_start_time, '%H:%M').time()
    #             end_time = datetime.strptime(clean_end_time, '%H:%M').time()
    #             if is_next_day is False:
    #                 # We have a regular show
    #                 res[formatted_date].append({'date': formatted_date,
    #                                             'start_time': start_time,
    #                                             'end_time': end_time,
    #                                             'title': clean_title,
    #                                             })
    #             else:
    #                 if formatted_next_date not in res:
    #                     res[formatted_next_date] = []
    #                 res[formatted_next_date].append({'date': formatted_next_date,
    #                                                  'start_time': start_time,
    #                                                  'end_time': end_time,
    #                                                  'title': clean_title,
    #                                                  })
    #             if start_time > end_time:
    #                 is_next_day = True
    #
    #     self.live_data['daily_schedule'] = res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        if fetched_request is None:
            fetched_request = self.get_object_request(category_data)
        max_page = int(re.findall(r'(?:pagination\(\d+, )(\d+)(?:\))', fetched_request.text)[0])
        return max_page

    # Obsolete
    # def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
    #     if fetched_request is None:
    #         fetched_request = self.get_object_request(category_data)
    #     tree = self.parser.parse(fetched_request.content.decode('utf-8'))
    #     pages = [int(x.text) for x in tree.xpath('.//div[@class="listen_links_group"]/*/div') if x.text.isdigit()]
    #
    #     return max(pages) if len(pages) > 0 else 1

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        if page_data.page_number is not None and page_data.page_number > 1:
            params['p'] = page_data.page_number
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        req = self.session.get(fetch_base_url, headers=headers, params=params)
        return req

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Channel9, self)._version_stack + [self.__version]
