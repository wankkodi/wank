# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher, PornFetchUrlError

# Internet tools
from .... import urljoin, quote_plus, parse_qs
import requests

# Regex
import re

# JSON
from ....tools.text_json_manioulations import prepare_json_from_not_formatted_text
# import json

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

# Playlist tools
import m3u8

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, PornCatalogPageNode, \
    VideoNode, VideoSource, VideoTypes
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter


class ExtremeTube(PornFetcher):
    category_json_url = 'www.extremetube.com/category/{cat}'
    tag_list_json_url = 'https://www.extremetube.com/tag/{letter}/json'
    # video_list_json_url = 'https://www.extremetube.com/videos/keyword/{key}'
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
            # PornCategories.HOTTEST_VIDEO: urljoin(self.base_url, '/'),
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
            # PornCategories.HOTTEST_VIDEO: PornFilterTypes.HottestOrder,
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

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        raw_data = re.findall(r'(?:flashvars = )({.*?})(?:;)', tmp_request.text, re.DOTALL)
        raw_data = prepare_json_from_not_formatted_text(raw_data[0])
        res = sorted([VideoSource(link=v.replace('\\/', '/'), resolution=re.findall(r'(?:quality_)(\d+)(?:p*)', k)[0])
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
        page_request = self.get_object_request(category_data, page_type='json') \
            if fetched_request is None else fetched_request
        if not self._check_is_available_page(category_data, page_request):
            return 1
        try:
            raw_res = page_request.json()
            return raw_res['1']['navigation']['lastPage'] \
                if type(raw_res) is dict else raw_res[0]['navigation']['lastPage']
        except JSONDecodeError:
            tree = self.parser.parse(page_request.text)
            pages = [int(re.findall(r'(?:page=)(\d+)', x.attrib['href'])[0])
                     for x in tree.xpath('.//ul[@class="pagination"]/li/*')
                     if 'href' in x.attrib and len(re.findall(r'(?:page=)(\d+)', x.attrib['href'])) > 0]
            return max(pages)

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
                           page_type='regular'):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :param override_page_number: Override page number.
        :param override_params: Override params.
        :param override_url: Override url.
        :param page_type: Indicates whether we want to have 'regular' or 'json' page.
        :return: Page request
        """
        res = self._get_object_request_no_exception_check(page_data, override_page_number, override_params,
                                                          override_url, page_type)
        if not self._check_is_available_page(page_data, res):
            error_module = self._prepare_porn_error_module(
                page_data, 0, res.url,
                'Could not fetch {url} in object {obj}'.format(url=res.url, obj=page_data.title))
            raise PornFetchUrlError(res, error_module)
        return res

    def _get_object_request_no_exception_check(self, page_data, override_page_number=None, override_params=None,
                                               override_url=None, page_type='regular'):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :param override_page_number: Override page number.
        :param override_params: Override params.
        :param override_url: Override url.
        :param page_type: Indicates whether we want to have 'regular' or 'json' page.
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
        try:
            page_request = self.session.get(url, headers=headers, params=params)
        except (requests.exceptions.RetryError, ) as err:
            if 'format' in params:
                params.pop('format')
                page_request = self.session.get(url, headers=headers, params=params)
            else:
                raise err

        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?search={q}'.format(q=quote_plus(query))
