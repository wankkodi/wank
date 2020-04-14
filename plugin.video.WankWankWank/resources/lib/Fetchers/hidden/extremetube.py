# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornErrorModule, PornNoVideoError, PornFetchUrlError

# Internet tools
from .. import urljoin, quote_plus, parse_qs

# Regex
import re

# JSON
import json

# Generator id
from ..id_generator import IdGenerator

# Playlist tools
import m3u8

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, PornCatalogPageNode, \
    VideoNode, VideoSource, VideoTypes
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter


class ExtremeTube(PornFetcher):
    category_json_url = 'www.extremetube.com/category/{cat}'
    tag_list_json_url = 'https://www.extremetube.com/tag/{letter}/json'
    video_list_json_url = 'https://www.extremetube.com/videos/keyword/{key}'
    json_params = {
        'format': ['json'],
        'number_pages': [1],
    }
    max_flip_images = 16

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/video-categories'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags'),
            PornCategories.HOTTEST_VIDEO: urljoin(self.base_url, '/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/videos?o=mr'),
            PornCategories.BEING_WATCHED_VIDEO: urljoin(self.base_url, '/videos?o=bw'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/videos?o=mv'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/videos?o=tr'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/videos?o=lg'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/videos'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.HOTTEST_VIDEO: PornFilterTypes.HottestOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.BEING_WATCHED_VIDEO: PornFilterTypes.BeingWatchedOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.extremetube.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', ''),
                                              (PornFilterTypes.GayType, 'Gay', 'gay'),
                                              (PornFilterTypes.ShemaleType, 'Transsexual', 'trans'),
                                              ],
                          }
        video_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Most relevant', ''),
                                        (PornFilterTypes.DateOrder, 'Most recent', 'mr'),
                                        (PornFilterTypes.ViewsOrder, 'Most viewed', 'mv'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'tr'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'lg'),
                                        ],
                         }
        # search_filters = {'sort_order': [(FilterTypes.RelevanceOrder, 'Most relevant', ''),
        #                                  (FilterTypes.DateOrder, 'Most recent', 'mr'),
        #                                  (FilterTypes.ViewsOrder, 'Most viewed', 'mv'),
        #                                  (FilterTypes.RatingOrder, 'Top rated', 'tr'),
        #                                  (FilterTypes.LengthOrder, 'Longest', 'lg'),
        #                                  ],
        #                   }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter,
                                         single_category_args=video_filters,
                                         single_tag_args=video_filters,
                                         # search_args=search_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='ExtremeTube', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(ExtremeTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                          session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="categories-list-thumb"]/p/a')
        res = []
        for category in categories:
            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = urljoin(category_data.url, image_data[0].attrib['src'])
            title = image_data[0].attrib['title']

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=category.attrib['href'],
                                               url=urljoin(category_data.url, category.attrib['href']),
                                               title=title,
                                               image_link=image,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))
        res.sort(key=lambda x: x.title)
        category_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available tags.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data, page_type='regular')
        tree = self.parser.parse(page_request.text)
        tags = tree.xpath('.//ul[@class="tags-list-columns float-right"]/li/a')
        res = []
        for tag in tags:
            number_of_videos = tag.xpath('./span')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])
            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=tag.attrib['href'],
                                               url=urljoin(tag_data.url, tag.attrib['href']),
                                               title=self._clear_text(tag.text),
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.TAG,
                                               super_object=tag_data,
                                               ))

        # page_request = self.get_object_request(tag_data, page_type='json')
        # page_json = page_request.json()
        # res.extend([(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
        #                                      obj_id=x['link'],
        #                                      url=urljoin(tag_data.url, x['link']),
        #                                      title=x['name'],
        #                                      number_of_videos=x['videos_tagged'],
        #                                      object_type=Tag,
        #                                      super_object=tag_data,
        #                                      ) for x in tags['tags'])
        # res.sort(key=lambda x: x.title)
        tag_data.add_sub_objects(res)
        return res

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return False

    def _add_category_sub_pages(self, category_data, sub_object_type, page_request=None, clear_sub_elements=True):
        """
        Adds category sub pages.
        :param category_data: Category data object (PornCatalogCategoryNode).
        :param sub_object_type: Sub object type.
        :param page_request: Page request if such exist. In case it doesn't exist we fetch the object's url.
        :param clear_sub_elements: Flag that indicates whether we clear previous sub elements.
        :return:
        """
        if category_data.object_type == PornCategories.TAG_MAIN:
            if clear_sub_elements is True:
                category_data.clear_sub_objects()
            return self._add_tag_sub_pages(category_data, sub_object_type)
        return super(ExtremeTube, self)._add_category_sub_pages(category_data, sub_object_type, page_request,
                                                                clear_sub_elements)

    def _add_tag_sub_pages(self, tag_data, sub_object_type):
        """
        Adds sub pages to the tags according to the first letter of the title. Stores all the tags to the proper pages.
        Notice that the current method contradicts with the _get_tag_properties method, thus you must use either of
        them, according to the way you want to implement the parsing (Use the _make_tag_pages_by_letter property to
        indicate which of the methods you are about to use...)
        :param tag_data: Tag data.
        :param sub_object_type: Object types of the sub pages (either Page or VideoPage).
        :return:
        """
        page_request = self.get_object_request(tag_data)
        tree = self.parser.parse(page_request.text)
        tag_letters_data = tree.xpath('.//div[@class="relative tagsBlock"]')
        tag_pages = []
        for tag_letter_data in tag_letters_data:
            tag_letter = tag_letter_data.xpath('./div[@class="float-left bold gray-tab-square"]/'
                                               'div[@class="relative letterIdentifier"]/text()')
            assert len(tag_letter) == 1
            tag_link = tag_letter_data.xpath('.//div[@class="float-right"]/a/@href')
            tag_link = tag_link[0] if len(tag_link) > 0 else '/tag/{l}'.format(l=tag_letter[0])
            tag_page = PornCatalogPageNode(catalog_manager=self.catalog_manager,
                                           obj_id=tag_link,
                                           url=urljoin(tag_data.url, tag_link),
                                           title='{c} | Letter {p}'.format(c=tag_data.title, p=tag_letter[0]),
                                           object_type=sub_object_type,
                                           additional_data={'letter': '123' if tag_letter[0] == '#' else tag_letter[0]},
                                           super_object=tag_data,
                                           )

            tag_pages.append(tag_page)
        tag_data.add_sub_objects(tag_pages)
        return tag_pages

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_data.url, headers=headers)
        assert tmp_request.status_code == 200
        raw_data = re.findall(r'(?:flashvars = )({.*?})(?:;)', tmp_request.text, re.DOTALL)
        # raw_data = re.sub(r'\'', '"', raw_data[0])
        # raw_data = re.sub(r'\w+(?=:)(?!:/)', lambda x: '"' + x[0] + '"', raw_data)
        raw_data = json.loads(raw_data[0])
        res = sorted([VideoSource(link=v, resolution=re.findall(r'(?:quality_)(\d+)(?:p*)', k)[0])
                      for k, v in raw_data.items() if 'quality_' in k],
                     key=lambda x: x.resolution, reverse=True)
        if 'HLS' in raw_data and raw_data['HLS'] is not None:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;'
                          'q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Cache-Control': 'max-age=0',
                'Referer': video_data.url,
                'User-Agent': self.user_agent
            }
            segment_request = self.session.get(raw_data['HLS'], headers=headers)
            if not self._check_is_available_page(segment_request):
                server_data = PornErrorModule(self.data_server, self.source_name, video_data.url,
                                              'Cannot fetch video links from the url {u}'.format(
                                                  u=segment_request.url),
                                              None, None)
                raise PornNoVideoError('No Video link for url {u}'.format(u=segment_request.url), server_data)
            video_m3u8 = m3u8.loads(segment_request.text)
            video_playlists = video_m3u8.playlists
            res.extend([VideoSource(link=urljoin(raw_data['HLS'], x.uri),
                                    video_type=VideoTypes.VIDEO_SEGMENTS,
                                    quality=x.stream_info.bandwidth,
                                    resolution=x.stream_info.resolution[1],
                                    codec=x.stream_info.codecs)
                        for x in video_playlists])

        return VideoNode(video_sources=res)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.HOTTEST_VIDEO):
            return 1
        try:
            page_request = self.get_object_request(category_data, page_type='json', send_error=False) \
                if fetched_request is None else fetched_request
        except PornFetchUrlError:
            return 1
        raw_res = page_request.json()
        return raw_res['1']['navigation']['lastPage'] \
            if type(raw_res) is dict else raw_res[0]['navigation']['lastPage']

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        if page_data.page_number > 1:
            page_request = self.get_object_request(page_data, page_type='json')
            assert page_request.status_code == 200
            videos = page_request.json()
            raw_videos = videos['1']['items'] if type(videos) is dict else videos[0]['items']
            videos = [PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                               obj_id=x['video_link'],
                                               url=urljoin(self.base_url, x['video_link']),
                                               title=x['title_long'],
                                               image_link=x['thumbs']['wide_medium_320']['url'],
                                               flip_images_link=[x['thumbs']['wide_medium_320']['path'].format(index=i)
                                                                 for i in range(1, self.max_flip_images)],
                                               duration=x['duration_sec'],
                                               added_before=x['time_approved_on'],
                                               rating=x['real_rating']['percent'],
                                               number_of_views=x['real_times_viewed'],
                                               additional_data={'tags': x['tags'], 'id': x['id']},
                                               raw_data=x,
                                               object_type=PornCategories.VIDEO,
                                               super_object=page_data,
                                               ) for x in raw_videos]
        else:
            page_request = self.get_object_request(page_data, page_type='regular')
            assert page_request.status_code == 200
            tree = self.parser.parse(page_request.text)
            videos_trees = [x for x in tree.xpath('.//ul')
                            if 'class' in x.attrib and 'ggs-list-videos' in x.attrib['class']]
            assert len(videos_trees) >= 1
            videos_trees = [x for x in videos_trees[0].xpath('./li')
                            if 'id' in x.attrib and 'obj' in x.attrib['id']]
            videos = []
            for video_tree_data in videos_trees:
                link_data = video_tree_data.xpath('./div/a')
                assert len(link_data) >= 1
                link = link_data[0].attrib['href']
                video_length = link_data[0].attrib['data-duration']

                image_data = link_data[0].xpath('./img')
                assert len(image_data) >= 1
                image = urljoin(self.base_url, image_data[0].attrib['src'])
                if 'data:image' in image:
                    image = urljoin(self.base_url, image_data[0].attrib['data-srcmedium'])
                flip_raw_data = re.findall(r'(?:startThumbChange\()(.*?)(?:\);)', link_data[0].attrib['onmouseover'])
                flip_raw_data = flip_raw_data[0].split(', ')
                max_flip_images = int(flip_raw_data[1])
                flip_image_template = flip_raw_data[2][1:-1]

                flip_images = [flip_image_template.format(index=i)
                               for i in range(1, max_flip_images + 1)]

                title = video_tree_data.xpath('./div/div[@class="fullDescrBox"]/a')
                assert len(title) == 1
                title = title[0].text

                description = video_tree_data.xpath('./div/div[@class="fullDescrBox"]/a')
                assert len(description) == 1
                description = description[0].attrib['title']

                viewers = video_tree_data.xpath('./div/div[@class="float-left views-block"]')
                assert len(viewers) == 1
                viewers = viewers[0].attrib['title']

                rating = video_tree_data.xpath('./div/div[@class="float-right rating-block"]/span')
                assert len(rating) == 1
                rating = rating[0].tail

                additional_data = {'id': video_tree_data.attrib['id']}

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      description=description,
                                                      image_link=image,
                                                      flip_images_link=flip_images,
                                                      duration=self._format_duration(video_length),
                                                      rating=rating,
                                                      number_of_views=viewers,
                                                      additional_data=additional_data,
                                                      object_type=PornCategories.VIDEO,
                                                      super_object=page_data,
                                                      )
                videos.append(video_data)
        page_data.add_sub_objects(videos)
        return videos

    def _prepare_request_params(self, object_data):
        """
        Prepares request params according to the object type.
        """
        object_type = object_data.object_type if object_data.object_type not in (PornCategories.PAGE,
                                                                                 PornCategories.VIDEO_PAGE) \
            else object_data.super_object.object_type
        if len(object_data.url.split('?')) > 1:
            url = object_data.url.split('?')[0]
            params = object_data.url.split('?')[1]
            params = parse_qs(params)
        else:
            url = object_data.url
            params = {}

        params.update(self.json_params)
        if object_type == PornCategories.TAG_MAIN:
            url = self.tag_list_json_url.format(tid=object_data.super_object.additional_data['letter'])
        elif object_type in (PornCategories.HOTTEST_VIDEO, PornCategories.LATEST_VIDEO,
                             PornCategories.MOST_VIEWED_VIDEO, PornCategories.TOP_RATED_VIDEO,
                             PornCategories.LONGEST_VIDEO, PornCategories.BEING_WATCHED_VIDEO,
                             PornCategories.TAG, PornCategories.SEARCH_MAIN, PornCategories.SEARCH_PAGE):
            pass
        elif object_type in (PornCategories.CATEGORY,):
            params['fromPage'] = ['categories']
        else:
            # raise RuntimeError('Wrong object type {o}!'.format(o=object_type))
            url = object_data.url
            params = {}

        return url, params

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        raise NotImplemented

    def get_object_request(self, page_data, override_page_number=None, override_params=None, override_url=None,
                           page_type='regular', send_error=True):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :param override_page_number: Override page number.
        :param override_params: Override params.
        :param override_url: Override url.
        :param page_type: Indicates whether we want to have 'regular' or 'json' page.
        :param send_error: Flag that indicates whether we send the error to the server. True by default.
        :return: Page request
        """
        if page_type == 'json':
            url, additional_params = self._prepare_request_params(page_data)
            headers = {
                'Accept': '*/*',
                'Cache-Control': 'max-age=0',
                # 'Host': self.host_name,
                'Referer': page_data.url,
                # 'Sec-Fetch-Mode': 'navigate',
                # 'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
        else:
            url = page_data.url
            additional_params = {}
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3',
                'Cache-Control': 'max-age=0',
                # 'Host': self.host_name,
                'Referer': page_data.url,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }

        true_object = page_data.true_object

        page_filters = self.get_proper_filter(page_data).current_filters
        general_filters = self.general_filter.current_filters

        if len(page_data.url.split('?')) > 1:
            url = page_data.url.split('?')[0]
            params = page_data.url.split('?')[1]
            params = parse_qs(params)
        else:
            params = {}

        if (
                general_filters.general.filter_id != PornFilterTypes.StraightType
                and (page_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN,) or
                     true_object.object_type in (PornCategories.LATEST_VIDEO, PornCategories.BEING_WATCHED_VIDEO,
                                                 PornCategories.MOST_VIEWED_VIDEO, PornCategories.TOP_RATED_VIDEO,
                                                 PornCategories.LONGEST_VIDEO, PornCategories.HOTTEST_VIDEO,
                                                 PornCategories.SEARCH_MAIN))
        ):
            split_url = url.split('/')
            split_url.insert(-1, general_filters.general.value)
            url = '/'.join(split_url)

        if true_object.object_type in (PornCategories.HOTTEST_VIDEO, PornCategories.LATEST_VIDEO,
                                       PornCategories.BEING_WATCHED_VIDEO, PornCategories.MOST_VIEWED_VIDEO,
                                       PornCategories.TOP_RATED_VIDEO, PornCategories.LONGEST_VIDEO,
                                       PornCategories.CATEGORY, PornCategories.TAG):
            if page_filters.sort_order.filter_id != PornFilterTypes.RelevanceOrder:
                additional_params['o'] = [page_filters.sort_order.value]

        params.update({k: v for k, v in additional_params.items() if k not in params})
        page_number = page_data.page_number if override_page_number is None else override_page_number
        if page_number is not None and page_number != 1:
            params['page'] = [page_number]

        page_request = self.session.get(url, headers=headers, params=params)

        if not self._check_is_available_page(page_request):
            if send_error is True:
                error_module = PornErrorModule(self.data_server,
                                               self.source_name,
                                               page_request.url,
                                               'Could not fetch {url}'.format(url=page_request.url),
                                               repr(page_filters),
                                               repr(general_filters)
                                               )
            else:
                error_module = None
            raise PornFetchUrlError(page_request, error_module)

        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?search={q}'.format(q=quote_plus(query))


# class KeezMoovies(ExtremeTube):
#     video_request_format = 'https://www.spankwire.com/api/video/{vid}.json'
#
#     @property
#     def max_pages(self):
#         """
#         Most viewed videos page url.
#         :return:
#         """
#         return 50000
#
#     @property
#     def object_urls(self):
#         return {
#             CategoryMain: urljoin(self.base_url, '/categories'),
#             TagMain: urljoin(self.base_url, '/tags'),
#             PornStarMain: urljoin(self.base_url, '/pornstar'),
#             LatestVideo: urljoin(self.base_url, '/videos'),
#             BeingWatchedVideo: urljoin(self.base_url, '/videos?o=bw'),
#             MostViewedVideo: urljoin(self.base_url, '/videos?o=mv'),
#             TopRatedVideo: urljoin(self.base_url, '/videos?o=tr'),
#             LongestVideo: urljoin(self.base_url, '/videos?o=lg'),
#             SearchMain: urljoin(self.base_url, '/video'),
#         }
#
#     @property
#     def base_url(self):
#         """
#         Base site url.
#         :return:
#         """
#         return 'https://www.keezmovies.com/'
#
#     def _set_video_filter(self):
#         """
#         Sets the video filters and the default values of the current filters
#         :return:
#         """
#         self._video_filters = VideoFilter(data_dir=self.fetcher_data_dir,
#                                           sort_order=((RelevanceOrder, 'Most relevant', ''),
#                                                       (DateOrder, 'Most recent', 'mr'),
#                                                       (ViewsOrder, 'Most viewed', 'mv'),
#                                                       (RatingOrder, 'Top rated', 'tr'),
#                                                       (LengthOrder, 'Longest', 'lg'),
#                                                       ),
#                                           period_filter=((AllDate, 'All time', ''),
#                                                          (OneDate, 'This week', 'w'),
#                                                          (TwoDate, 'This month', 'm'),
#                                                          ),
#                                           )
#
#     def __init__(self, source_name='KeezMoovies', source_id=0, store_dir='.', data_dir='../Data'):
#         """
#         C'tor
#         :param source_name: save directory
#         """
#         super(KeezMoovies, self).__init__(source_name, source_id, store_dir, data_dir)
#
#     def _update_available_categories(self, category_data):
#         """
#         Fetches all the available categories.
#         :return: Object of all available shows (JSON).
#         """
#         page_request = self.get_object_request(category_data)
#         tree = self.parser.parse(page_request.text)
#
#         headers = tree.xpath('.//div[@class="block_heading"]//h2[@class="h2cat"]')
#         bodies = tree.xpath('.//div[@class="float-left"]/a[@class="category_img"]')
#         assert len(headers) == len(bodies)
#         res = []
#         for header, body in zip(headers, bodies):
#             title = self._clear_text(header.text)
#
#             number_of_videos = header.xpath('./span[@class="inhsp"]/text()')
#             assert len(number_of_videos) == 1
#             number_of_videos = re.findall(r'(?:\()(\d*,*\d*)(?: Videos\))', number_of_videos[0])
#             assert len(number_of_videos) == 1
#             number_of_videos = int(re.sub(',', '', number_of_videos[0]))
#
#             link = urljoin(self.base_url, body.attrib['href'])
#             cat_id = body.attrib['href']
#             image = body.xpath('./img/@src')
#             assert len(image) == 1
#             image = image[0]
#
#             object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
#                                                   obj_id=cat_id,
#                                                   url=link,
#                                                   title=title,
#                                                   image_link=image,
#                                                   number_of_videos=number_of_videos,
#                                                   object_type=Category,
#                                                   super_object=category_data,
#                                                   )
#             res.append(object_data)
#         category_data.add_sub_objects(res)
#         return res
#
#     def _update_available_porn_stars(self, porn_star_data):
#         """
#         Fetches all the available porn stars.
#         :return: Object of all available shows (JSON).
#         """
#         page_request = self.get_object_request(porn_star_data)
#         tree = self.parser.parse(page_request.text)
#         porn_stars = [x for x in tree.xpath('.//ul[@class="all-ps-list main_pornst_block"]/li')
#                       if 'class' in x.attrib and 'allpornstars' in x.attrib['class']]
#         res = []
#         for porn_star in porn_stars:
#             link_data = porn_star.xpath('./a')
#             assert len(link_data)
#
#             image_data = porn_star.xpath('./a/div/img')
#             assert len(image_data) == 1
#             image = image_data[0].attrib['src']
#             if 'blank_pornstarimage.jpg' in image and 'data-srcsmall' in image_data[0].attrib:
#                 # We fetch another image
#                 image = image_data[0].attrib['data-srcsmall']
#             image = urljoin(porn_star_data.url, image)
#
#             additional_info = porn_star.xpath('./div[@class="pornstar_item_bottom"]/div/span')
#             assert len(additional_info) == 6
#             number_of_videos = int(additional_info[3].text)
#             number_of_photos = int(additional_info[1].text)
#             number_of_views = int(re.sub(',', '', additional_info[5].text))
#
#             object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
#                                                   obj_id=link_data[0].attrib['href'],
#                                                   url=urljoin(porn_star_data.url, link_data[0].attrib['href']),
#                                                   title=link_data[0].attrib['title'],
#                                                   image_link=image,
#                                                   number_of_videos=number_of_videos,
#                                                   number_of_photos=number_of_photos,
#                                                   number_of_views=number_of_views,
#                                                   object_type=PornStar,
#                                                   super_object=porn_star_data,
#                                                   )
#             res.append(object_data)
#         porn_star_data.add_sub_objects(res)
#         return res
#
#     def _get_tag_properties(self, page_request):
#         """
#         Fetches tag links and titles. The fetched objects MUST be sorted wrt title.
#         :param page_request: Page request.
#         :return:
#         """
#         tree = self.parser.parse(page_request.text)
#         links = tree.xpath('.//div[@style="padding:10px;"]/ul[@class="auto"]/a/@href')
#         titles = [x.title() for x in tree.xpath('.//div[@style="padding:10px;"]/ul[@class="auto"]/a/li/text()')]
#         assert len(links) == len(titles)
#         numbers_of_videos = [None] * len(titles)
#         return links, titles, numbers_of_videos
#
#     def get_video_links_from_video_data(self, video_data):
#         """
#         Extracts episode link from episode data.
#         :param video_data: Video data.
#         :return:
#         """
#         page_request = self.get_object_request(video_data)
#         raw_url = re.findall(r'(?:var htmlStr.*ArticleId=")(\d+?)(?:[&"])', page_request.text)
#         if len(raw_url) == 0:
#             raise RuntimeError('Could not fetch video from page {p}!'.format(p=video_data.url))
#         data_url = self.video_request_format.format(vid=raw_url[0])
#         headers = {
#             'Accept': 'application/json, text/plain, */*, image/webp',
#             'Cache-Control': 'max-age=0',
#             'Host': 'www.spankwire.com',
#             'Sec-Fetch-Mode': 'cors',
#             'Sec-Fetch-Site': 'same-origin',
#             'Upgrade-Insecure-Requests': '1',
#             'User-Agent': self.user_agent
#         }
#         tmp_request = self.session.get(data_url, headers=headers)
#         video_data = tmp_request.json()
#         if video_data is False:
#             raise RuntimeError('Could not fetch video from page {p}!'.format(p=video_data.url))
#
#         video_sources = sorted(((int(re.findall(r'(?:quality_)(\d*)(?:p)', k)[0]), v)
#                               for k, v in video_data['videos'].items()),
#                              key=lambda y: int(y[0]), reverse=True)
#         video_sources = [x[1] for x in video_sources]
#         return VideoNode(video_sources=video_sources)
#
#     def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
#         """
#         Extracts category number of videos out of category data.
#         :param fetched_request:
#         :param category_data: Category data (dict).
#         :return:
#         """
#         # We perform binary search
#         start_page = category_data.page_number if category_data.page_number is not None else 1
#         page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
#         tree = self.parser.parse(page_request.text)
#         pages = self._get_available_pages_from_tree(tree)
#         if len(pages) == 0:
#             return 1
#         max_page = max(pages)
#         if (max_page - start_page) < self._binary_search_page_threshold:
#             return max_page
#         else:
#             return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)
#
#     def _check_is_available_page(self, page_request):
#         """
#         In binary search performs test whether the current page is available.
#         :param page_request: Page request.
#         :return:
#         """
#         return page_request.ok
#
#     def _get_available_pages_from_tree(self, tree):
#         """
#         In binary looks for the available pages from current page tree.
#         :param tree: Current page tree.
#         :return: List of available trees
#         """
#         pages = (tree.xpath('.//ul[@class="pagination"]/li/*/text()') +
#                  tree.xpath('.//ul[@class="pagination"]/li/text()'))
#         return [int(x) for x in pages if x.isdigit()]
#
#     @property
#     def _binary_search_page_threshold(self):
#         """
#         Available pages threshold. 1 by default.
#         """
#         return 5
#
#     def get_videos_data(self, object_data):
#         """
#         Gets videos data for the given category.
#         :param object_data: Page data.
#         :return:
#         """
#         page_request = self.get_object_request(object_data)
#         tree = self.parser.parse(page_request.text)
#         videos = [x for x in tree.xpath('.//ul[@class="ul_video_block"]/li') if 'id' in x.attrib] + \
#                  [x for x in tree.xpath('.//ul[@class="ul_ps_video_block videos-pagination"]/li') if 'id' in x.attrib]
#         res = []
#         for video_tree_data in videos:
#             link_data = video_tree_data.xpath('./div[@class="hoverab"]/a')
#             assert len(link_data) >= 1
#             link = link_data[0].attrib['href']
#
#             image_data = link_data[0].xpath('./img')
#             assert len(image_data) >= 1
#             image = urljoin(self.base_url, image_data[0].attrib['src'])
#             flip_images = [image_data[0].attrib['data-flipbook'].format(index=i)
#                            for i in image_data[0].attrib['data-flipbook-values'].split(',')]
#
#             vd_data = video_tree_data.xpath('./div[@class="hoverab"]/div[@class="vd_dr"]/span')
#             is_hd = [x for x in vd_data if 'class' in x.attrib]
#             is_hd = len(is_hd) > 0 and is_hd[0].attrib['class'] == 'vdIsHD'
#
#             video_length = [x for x in vd_data if 'class' not in x.attrib]
#             assert len(video_length) == 1
#             video_length = video_length[0].text
#
#             title = video_tree_data.xpath('./div[@class="video_name"]/a')
#             assert len(title) == 1
#             title = title[0].text if title[0].text is not None else ''
#
#             rating = video_tree_data.xpath('./div[@class="video_extra"]/span[@class="liked_span"]')
#             assert len(rating) == 1
#             rating = rating[0].text
#
#             viewers = video_tree_data.xpath('./div[@class="video_extra"]/span[@class="views"]')
#             assert len(viewers) == 1
#             viewers = viewers[0].text
#
#             additional_data = {'id': video_tree_data.attrib['id']}
#
#             video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
#                                                   obj_id=link,
#                                                   url=urljoin(self.base_url, link),
#                                                   title=title,
#                                                   image_link=image,
#                                                   flip_images_link=flip_images,
#                                                   is_hd=is_hd,
#                                                   duration=self._format_duration(video_length),
#                                                   rating=rating,
#                                                   number_of_views=viewers,
#                                                   additional_data=additional_data,
#                                                   object_type=Video,
#                                                   super_object=object_data,
#                                                   )
#             res.append(video_data)
#         object_data.add_sub_objects(res)
#         return res
#
#     def get_object_request(self, object_data, override_page_number=None, page_type='regular'):
#         """
#         Fetches the page number with respect to base url.
#         :param object_data: Page data.
#         :param override_page_number: Override page number.
#         :param page_type: Indicates whether we want to have 'regular' or 'json' page.
#         :return: Page request
#         """
#         if page_type == 'json':
#             url, additional_params = self._prepare_request_params(object_data)
#             headers = {
#                 'Accept': '*/*',
#                 'Cache-Control': 'max-age=0',
#                 # 'Host': self.host_name,
#                 'Referer': object_data.url,
#                 # 'Sec-Fetch-Mode': 'navigate',
#                 # 'Sec-Fetch-Site': 'same-origin',
#                 'Sec-Fetch-User': '?1',
#                 'Upgrade-Insecure-Requests': '1',
#                 'User-Agent': self.user_agent,
#                 'X-Requested-With': 'XMLHttpRequest',
#             }
#         else:
#             url = object_data.url
#             additional_params = {}
#             headers = {
#                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
#                           'q=0.8,application/signed-exchange;v=b3',
#                 'Cache-Control': 'max-age=0',
#                 # 'Host': self.host_name,
#                 'Referer': object_data.url,
#                 'Sec-Fetch-Mode': 'navigate',
#                 'Sec-Fetch-Site': 'same-origin',
#                 'Sec-Fetch-User': '?1',
#                 'Upgrade-Insecure-Requests': '1',
#                 'User-Agent': self.user_agent
#             }
#
#         if len(object_data.url.split('?')) > 1:
#             url = object_data.url.split('?')[0]
#             params = object_data.url.split('?')[1]
#             params = parse_qs(params)
#         else:
#             params = {}
#
#         if all(x not in (LatestVideo, BeingWatchedVideo, LongestVideo)
#                for x in (object_data.object_type, object_data.super_object.object_type)):
#             if all(x not in (MostViewedVideo, TopRatedVideo,)
#                    for x in (object_data.object_type, object_data.super_object.object_type)):
#                 additional_params['o'] = self._video_filters.current_filter_values['sort_order'].value
#             additional_params['t'] = self._video_filters.current_filter_values['period'].value
#
#         if object_data.object_type != Video:
#             params.update({k: [v] for k, v in additional_params.items() if k not in params})
#         page_number = object_data.page_number if override_page_number is None else override_page_number
#         if page_number is not None and page_number != 1:
#             params['page'] = [page_number]
#
#         page_request = self.session.get(url, headers=headers, params=params)
#         return page_request


class SpankWire(PornFetcher):
    category_json_url = 'https://www.spankwire.com/api/categories/list.json'
    porn_star_list_json_url = 'https://www.spankwire.com/api/pornstars'
    video_list_json_url = 'https://www.spankwire.com/api/video/list.json'
    video_request_format = 'https://www.spankwire.com/api/video/{vid}.json'
    search_request_format = 'https://www.spankwire.com/api/search'

    @property
    def category_json_params(self):
        if self.general_filter.current_filters.general.filter_id == \
                PornFilterTypes.StraightType:
            segment_id = 0
        elif self.general_filter.current_filters.general.filter_id == \
                PornFilterTypes.StraightType:
            segment_id = 1
        elif self.general_filter.current_filters.general.filter_id == \
                PornFilterTypes.ShemaleType:
            segment_id = 2
        else:
            raise TypeError('Not suppose to be here...')
        return {
            'segmentId': segment_id,
            'limit': 100,
            'sort': self._video_filters[PornCategories.CATEGORY_MAIN].current_filters.sort_order.value,
        }

    @property
    def porn_star_json_params(self):
        return {
            'limit': 25,
            'sort': self._video_filters[PornCategories.PORN_STAR_MAIN].current_filters.sort_order.value,
            'letter': '',
        }

    @property
    def video_from_category_json_params(self):
        return {
            'segment': self.general_filter.current_filters.general.value,
            'limit': 33,
            'sortby': self._video_filters[PornCategories.CATEGORY_MAIN].current_filters.sort_order.value,
            'period': self._video_filters[PornCategories.CATEGORY_MAIN].current_filters.added_before.value,
        }

    @property
    def video_from_porn_star_json_params(self):
        return {
            'hasLogged': False,
            'limit': 25,
            'sortby': self._video_filters[PornCategories.PORN_STAR].current_filters.sort_order.value,
        }

    @property
    def video_latest_json_params(self):
        return {
            'segment': self.general_filter.current_filters.general.value,
            'limit': 33,
            'sortby': 'recent',
        }

    @property
    def video_trending_json_params(self):
        return {
            'segment': self.general_filter.current_filters.general.value,
            'limit': 33,
            'sortby': 'trending',
        }

    @property
    def video_most_viewed_json_params(self):
        return {
            'segment': self.general_filter.current_filters.general.value,
            'limit': 33,
            'sortby': 'views',
            'period': self._video_filters[PornCategories.VIDEO].current_filters.period.value,
        }

    @property
    def video_top_rated_json_params(self):
        return {
            'segment': self.general_filter.current_filters.general.value,
            'limit': 33,
            'sortby': 'rating',
            'period': self._video_filters[PornCategories.VIDEO].current_filters.period.value,
        }

    @property
    def video_longest_json_params(self):
        return {
            'segment': self.general_filter.current_filters.general.value,
            'limit': 33,
            'sortby': 'duration',
            'period': self._video_filters[PornCategories.VIDEO].current_filters.period.value,
        }

    @property
    def video_most_talked_json_params(self):
        return {
            'segment': self.general_filter.current_filters.general.value,
            'limit': 33,
            'sortby': 'comments',
            'period': self._video_filters[PornCategories.VIDEO].current_filters.period.value,
        }

    @property
    def search_json_params(self):
        return {
            'segment': self.general_filter.current_filters.general.value,
            'limit': 33,
            'sort': self._video_filters[PornCategories.SEARCH_MAIN].current_filters.sort_order.value,
            'uploaded': self._video_filters[PornCategories.SEARCH_MAIN].current_filters.period.value,
        }

    max_flip_images = 16

    @property
    def object_urls(self):
        general_filter_value = self.general_filter.current_filters.general.value
        return {
            PornCategories.CATEGORY_MAIN:
                'https://www.spankwire.com/categories/{type}'.format(type=general_filter_value),
            PornCategories.PORN_STAR_MAIN:
                'https://www.spankwire.com/pornstars',
            PornCategories.LATEST_VIDEO:
                'https://www.spankwire.com/recentvideos/{type}'.format(type=general_filter_value),
            PornCategories.MOST_VIEWED_VIDEO:
                'https://www.spankwire.com/home1/{type}/Year/Views'.format(type=general_filter_value),
            PornCategories.TOP_RATED_VIDEO:
                'https://www.spankwire.com/home1/{type}/Year/Rating'.format(type=general_filter_value),
            PornCategories.MOST_DISCUSSED_VIDEO:
                'https://www.spankwire.com/home1/{type}/Year/Comments'.format(type=general_filter_value),
            PornCategories.LONGEST_VIDEO:
                'https://www.spankwire.com/home1/{type}/Year/Duration'.format(type=general_filter_value),
            PornCategories.POPULAR_VIDEO:
                'https://www.spankwire.com/trendingvideos/{type}'.format(type=general_filter_value),
            PornCategories.SEARCH_MAIN:
                'https://www.spankwire.com/search/{type}/keyword'.format(type=general_filter_value),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.spankwire.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', 'Straight'),
                                              (PornFilterTypes.GayType, 'Gay', 'Gay'),
                                              (PornFilterTypes.ShemaleType, 'Shemale', 'Tranny'),
                                              ],
                          }
        porn_stars_filter = {'sort_order': [(PornFilterTypes.PopularityOrder, 'By popularity', 'popular'),
                                            (PornFilterTypes.AlphabeticOrder, 'By alphabet', 'abc'),
                                            (PornFilterTypes.NumberOfVideosOrder, 'By no. of videos', 'number'),
                                            ],
                             }
        single_porn_star_filter = {'sort_order': [(PornFilterTypes.DateOrder, 'Recent videos', 'recent'),
                                                  (PornFilterTypes.ViewsOrder, 'Most viewed', 'views'),
                                                  (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                                  ],
                                   }
        categories_filter = {'sort_order': [(PornFilterTypes.DateOrder, 'Recently Updated', 'recent'),
                                            (PornFilterTypes.AlphabeticOrder, 'Alphabetical', 'abc'),
                                            (PornFilterTypes.NumberOfVideosOrder, 'No. of videos', 'number'),
                                            ],
                             }
        single_category_filter = {'sort_order': [(PornFilterTypes.ViewsOrder, 'Most viewed', 'views'),
                                                 (PornFilterTypes.DateOrder, 'Most recent', 'recent'),
                                                 (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                                 (PornFilterTypes.TrendingOrder, 'Trending', 'trending'),
                                                 (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                                 ],
                                  'period_filters': [(PornFilterTypes.AllAddedBefore, 'All time', 'All_time'),
                                                     (PornFilterTypes.OneAddedBefore, 'Today', 'today'),
                                                     (PornFilterTypes.TwoAddedBefore, 'Yesterday', 'yesterday'),
                                                     (PornFilterTypes.ThreeAddedBefore, 'Week', 'week'),
                                                     (PornFilterTypes.FourAddedBefore, 'Month', 'month'),
                                                     (PornFilterTypes.FiveAddedBefore, 'Year', 'year'),
                                                     ],
                                  }
        video_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Most recent', 'recent'),
                                        (PornFilterTypes.ViewsOrder, 'Most viewed', 'views'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        (PornFilterTypes.RelevanceOrder, 'Most relevant', 'relevance'),
                                        (PornFilterTypes.PopularityOrder, 'Popularity', 'popularity'),
                                        (PornFilterTypes.NumberOfVideosOrder, 'Number of videos', 'number'),
                                        (PornFilterTypes.AlphabeticOrder, 'Alphabetic', 'abc'),
                                        ],
                         'period_filters': [(PornFilterTypes.AllAddedBefore, 'All time', 'All_time'),
                                            (PornFilterTypes.OneAddedBefore, 'Today', 'today'),
                                            (PornFilterTypes.TwoAddedBefore, 'Yesterday', 'yesterday'),
                                            (PornFilterTypes.ThreeAddedBefore, 'Week', 'week'),
                                            (PornFilterTypes.FourAddedBefore, 'Month', 'month'),
                                            (PornFilterTypes.FiveAddedBefore, 'Year', 'year'),
                                            ],
                         }
        search_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Most relevant', 'relevance'),
                                         (PornFilterTypes.DateOrder, 'Most recent', 'recent'),
                                         ],
                          'period_filters': [(PornFilterTypes.AllAddedBefore, 'All time', 'all_time'),
                                             (PornFilterTypes.OneAddedBefore, 'Past 24 hours', 'past_24_hours'),
                                             (PornFilterTypes.TwoAddedBefore, 'Past 2 days', 'past_2_days'),
                                             (PornFilterTypes.ThreeAddedBefore, 'Past week', 'past_week'),
                                             (PornFilterTypes.FourAddedBefore, 'Past month', 'past_month'),
                                             (PornFilterTypes.FiveAddedBefore, 'Past year', 'past_year'),
                                             ],
                          }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter,
                                         porn_stars_args=porn_stars_filter,
                                         categories_args=categories_filter,
                                         single_category_args=single_category_filter,
                                         single_porn_star_args=single_porn_star_filter,
                                         single_tag_args=video_filters,
                                         search_args=search_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='SpankWire', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SpankWire, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        page_json = page_request.json()

        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x['id'],
                                       url=urljoin(self.base_url, x['url']),
                                       title=x['name'],
                                       image_link=x['image'],
                                       number_of_videos=x['videosNumber'],
                                       raw_data=x,
                                       object_type=PornCategories.CATEGORY,
                                       super_object=category_data,
                                       )
               for x in page_json['items']]
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        page_json = page_request.json()

        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x['id'],
                                       url=urljoin(self.base_url, x['url']),
                                       title=x['name'],
                                       image_link=x['thumb'],
                                       number_of_videos=x['videos'],
                                       raw_data=x,
                                       object_type=PornCategories.PORN_STAR,
                                       super_object=porn_star_data,
                                       )
               for x in page_json['items']]
        porn_star_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """

        video_url = self.video_request_format.format(vid=video_data.raw_data['id'])
        headers = {
            'Accept': 'application/json, text/plain, */*, image/webp',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_url, headers=headers)
        assert tmp_request.status_code == 200
        request_data = tmp_request.json()

        res = [VideoSource(link=v, video_type=VideoTypes.VIDEO_REGULAR,
                           resolution=re.findall(r'(?:quality_)(\d+)(?:p*)', k)[0])
               for k, v in request_data['videos'].items()]
        if 'HLS' in request_data and request_data['HLS'] is not None:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;'
                          'q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Cache-Control': 'max-age=0',
                'Referer': video_data.url,
                'User-Agent': self.user_agent
            }
            segment_request = self.session.get(request_data['HLS'], headers=headers)
            if not self._check_is_available_page(segment_request):
                server_data = PornErrorModule(self.data_server, self.source_name, video_data.url,
                                              'Cannot fetch video links from the url {u}'.format(
                                                  u=segment_request.url),
                                              None, None)
                raise PornNoVideoError('No Video link for url {u}'.format(u=segment_request.url), server_data)
            video_m3u8 = m3u8.loads(segment_request.text)
            video_playlists = video_m3u8.playlists
            res.extend([VideoSource(link=urljoin(request_data['HLS'], x.uri),
                                    video_type=VideoTypes.VIDEO_SEGMENTS,
                                    quality=x.stream_info.bandwidth,
                                    resolution=x.stream_info.resolution[1],
                                    codec=x.stream_info.codecs)
                        for x in video_playlists])

        res.sort(key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=res)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        try:
            page_request = self.get_object_request(category_data, send_error=False) if fetched_request is None \
                else fetched_request
        except PornFetchUrlError:
            return 1
        raw_res = page_request.json()
        return raw_res['pages']

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        assert page_request.status_code == 200
        videos = page_request.json()
        videos = [PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                           obj_id=x['id'],
                                           url=urljoin(self.base_url, x['url']),
                                           title=x['title'],
                                           description=x['description'],
                                           image_link=x['flipBookPath'].format(index=1),
                                           flip_images_link=[x['flipBookPath'].format(index=i)
                                                             for i in range(1, self.max_flip_images)],
                                           preview_video_link=x['videoPreview'],
                                           is_hd=x['isHD'],
                                           duration=x['duration'],
                                           added_before=x['time_approved_on'],
                                           rating=x['rating'],
                                           number_of_views=x['viewed'],
                                           raw_data=x,
                                           object_type=PornCategories.VIDEO,
                                           super_object=page_data,
                                           )
                  for x in videos['items']]
        page_data.add_sub_objects(videos)
        return videos

    def _prepare_request_params(self, object_data):
        """
        Prepares request params according to the object type.
        """
        object_type = object_data.object_type \
            if object_data.object_type not in (PornFilterTypes.PAGE, PornFilterTypes.VIDEO_PAGE,
                                               PornFilterTypes.SEARCH_PAGE) \
            else object_data.super_object.object_type
        if object_type == PornFilterTypes.PORN_STAR:
            url = self.video_list_json_url
            params = self.video_from_category_json_params.copy()
            params['pornstarId'] = object_data.raw_data['id']
        elif object_type == PornFilterTypes.CATEGORY:
            url = self.video_list_json_url
            params = self.video_from_category_json_params.copy()
            params['category'] = object_data.raw_data['id']
        elif object_type == PornFilterTypes.PORN_STAR_MAIN:
            url = self.porn_star_list_json_url
            params = self.porn_star_json_params.copy()
        elif object_type == PornFilterTypes.CATEGORY_MAIN:
            url = self.category_json_url
            params = self.category_json_params.copy()
        elif object_type == PornFilterTypes.LATEST_VIDEO:
            url = self.video_list_json_url
            params = self.video_latest_json_params.copy()
        elif object_type == PornFilterTypes.MOST_VIEWED_VIDEO:
            url = self.video_list_json_url
            params = self.video_most_viewed_json_params.copy()
        elif object_type == PornFilterTypes.TOP_RATED_VIDEO:
            url = self.video_list_json_url
            params = self.video_top_rated_json_params.copy()
        elif object_type == PornFilterTypes.MOST_DISCUSSED_VIDEO:
            url = self.video_list_json_url
            params = self.video_most_talked_json_params.copy()
        elif object_type == PornFilterTypes.LONGEST_VIDEO:
            url = self.video_list_json_url
            params = self.video_longest_json_params.copy()
        elif object_type == PornFilterTypes.POPULAR_VIDEO:
            url = self.video_list_json_url
            params = self.video_trending_json_params.copy()
        elif object_type == PornFilterTypes.SEARCH_MAIN:
            split_url = object_data.url.split('/')
            url = self.search_request_format
            params = self.search_json_params.copy()
            params['query'] = split_url[-1]
        else:
            raise RuntimeError('Wrong object type {o}!'.format(o=object_type))
            # url = object_data.url
            # params = {}
        return url, params

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        raise NotImplemented

    def get_object_request(self, page_data, override_page_number=None, override_params=None, override_url=None,
                           send_error=True):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :param override_page_number: Override page number.
        :param override_params: Override params.
        :param override_url: Override url.
        :param send_error: Flag that indicates whether we send the error to the server. True by default.
        :return: Page request
        """
        url, additional_params = self._prepare_request_params(page_data)

        base_url = page_data.url.split('?')[0]
        if len(page_data.url.split('?')) > 1:
            params = page_data.url.split('?')[1]
            params = parse_qs(params)
        else:
            params = {}

        params.update({k: v for k, v in additional_params.items() if k not in params})
        page_number = page_data.page_number if override_page_number is None else override_page_number
        if page_number is not None and page_number != 1:
            params['page'] = page_number

        headers = {
            'Accept': 'application/json, text/plain, */*, image/webp',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Referer': base_url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        page_request = self.session.get(url, headers=headers, params=params)

        if not self._check_is_available_page(page_request):
            if send_error is True:
                object_filters = self.get_proper_filter(page_data).current_filters
                general_filters = self.general_filter.current_filters
                error_module = PornErrorModule(self.data_server,
                                               self.source_name,
                                               page_request.url,
                                               'Could not fetch {url}'.format(url=page_request.url),
                                               repr(object_filters),
                                               repr(general_filters)
                                               )
            else:
                error_module = None
            raise PornFetchUrlError(page_request, error_module)

        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '/{q}'.format(q=quote_plus(query))


if __name__ == '__main__':
    category_id = IdGenerator.make_id(5000)  # 10 Inch Cock
    # porn_star_id = IdGenerator.make_id(6283)  # Riley Reed
    porn_star_id = IdGenerator.make_id(6763)  # Eva Notty
    # module = ExtremeTube()
    # module = KeezMoovies()
    module = SpankWire()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['porn_stars']['obj'], (porn_star_id, ), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
