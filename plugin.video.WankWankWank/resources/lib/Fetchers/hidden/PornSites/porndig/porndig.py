# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote_plus

# Regex
import re

# JSON
from ....tools.text_json_manioulations import prepare_json_from_not_formatted_text

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# Math
import math


class PornDig(PornFetcher):
    amateur_category_url = 'https://www.porndig.com/amateur'
    load_more_videos_url = 'https://www.porndig.com/posts/load_more_posts'
    load_more_channels_url = 'https://www.porndig.com/studios/load_more_studios'
    load_more_pornstars_url = 'https://www.porndig.com/pornstars/load_more_pornstars'
    number_of_thumbnails = 20

    @property
    def max_pages(self):
        return 200

    # todo: take care about live video...
    @property
    def object_urls(self):
        return {
            # AmateurCategoryMain: 'https://www.porndig.com/amateur',
            PornCategories.CATEGORY_MAIN: 'https://www.porndig.com/',
            PornCategories.CHANNEL_MAIN: 'https://www.porndig.com/studios/',
            PornCategories.PORN_STAR_MAIN: 'https://www.porndig.com/pornstars/',
            # LiveVideo: 'https://www.porndig.com/cams_landing',
            PornCategories.TOP_RATED_VIDEO: 'https://www.porndig.com/videos',
            PornCategories.SEARCH_MAIN: 'https://www.porndig.com/search/',
            # TopRatedAmateurVideo: 'https://www.porndig.com/amateur/videos/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.porndig.com/'

    @property
    def number_of_videos_per_video_page(self):
        """
        Base site url.
        :return:
        """
        return 50  # 50

    @property
    def number_of_videos_per_channel_page(self):
        """
        Base site url.
        :return:
        """
        return 30  # 30

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', None),
                                                     (PornFilterTypes.GayType, 'Gay', 'gays'),
                                                     (PornFilterTypes.ShemaleType, 'Shemale', 'transexual'),
                                                     (PornFilterTypes.AmateurType, 'Amateur', 'amateur'),
                                                     ],
                                 }
        channels_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Digs', 'likes'),
                                           (PornFilterTypes.CommentsOrder, 'Comments', 'comments'),
                                           (PornFilterTypes.ViewsOrder, 'Number of Views', 'video_views'),
                                           (PornFilterTypes.VideosPopularityOrder, 'Video Digs', 'video_likes'),
                                           (PornFilterTypes.DateOrder, 'Date', 'date'),
                                           ),
                            }
        porn_stars_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Digs', 'likes'),
                                             (PornFilterTypes.CommentsOrder, 'Comments', 'comments'),
                                             (PornFilterTypes.ViewsOrder, 'Number of Views', 'video_views'),
                                             (PornFilterTypes.VideosPopularityOrder, 'Video Digs', 'video_likes'),
                                             ),
                              }
        video_filters = {'sort_order': ((PornFilterTypes.ClicksOrder, 'Clicks', 'ctr'),
                                        (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                        (PornFilterTypes.CommentsOrder, 'Comments', 'comments'),
                                        (PornFilterTypes.ViewsOrder, 'Views', 'views'),
                                        (PornFilterTypes.DateOrder, 'Date', 'date'),
                                        (PornFilterTypes.LengthOrder, 'Length', 'duration'),
                                        ),
                         'period_filters': ([(PornFilterTypes.AllDate, 'All time', ''),
                                             (PornFilterTypes.OneDate, 'Month', 'month'),
                                             (PornFilterTypes.TwoDate, 'Year', 'year'),
                                             ],
                                            [('sort_order', [PornFilterTypes.ClicksOrder,
                                                             PornFilterTypes.RatingOrder,
                                                             PornFilterTypes.CommentsOrder,
                                                             PornFilterTypes.ViewsOrder,
                                                             PornFilterTypes.LengthOrder,
                                                             ])]),

                         'quality_filters': ((PornFilterTypes.R270Quality, 'min 270p', 270),
                                             (PornFilterTypes.R360Quality, 'min 360p', 360),
                                             (PornFilterTypes.R540Quality, 'min 540p', 540),
                                             (PornFilterTypes.R720Quality, 'min 720p', 720),
                                             (PornFilterTypes.R1080Quality, 'min 1080p', 1080),
                                             (PornFilterTypes.R2160Quality, 'min 4k', 2160),
                                             ),
                         'length_filters': ((PornFilterTypes.AllLength, 'Any duration', None),
                                            (PornFilterTypes.OneLength, '<15 min', 14),
                                            (PornFilterTypes.TwoLength, '15-25 min', 15),
                                            (PornFilterTypes.ThreeLength, '26-45 min', 26),
                                            (PornFilterTypes.ThreeLength, '45+ min', 45),
                                            ),

                         }
        single_channel_filters = {'sort_order': ((PornFilterTypes.ClicksOrder, 'Clicks', 'ctr'),
                                                 (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                                 (PornFilterTypes.CommentsOrder, 'Comments', 'comments'),
                                                 (PornFilterTypes.ViewsOrder, 'Views', 'views'),
                                                 (PornFilterTypes.DateOrder, 'Date', 'date'),
                                                 (PornFilterTypes.LengthOrder, 'Length', 'duration'),
                                                 ),
                                  'period_filters': ([(PornFilterTypes.OneDate, 'Month', 'month'),
                                                      (PornFilterTypes.TwoDate, 'Year', 'year'),
                                                      (PornFilterTypes.AllDate, 'All time', ''),
                                                      ],
                                                     [('sort_order', [PornFilterTypes.ClicksOrder,
                                                                      PornFilterTypes.RatingOrder,
                                                                      PornFilterTypes.CommentsOrder,
                                                                      PornFilterTypes.ViewsOrder,
                                                                      PornFilterTypes.LengthOrder,
                                                                      ])]),

                                  'quality_filters': ((PornFilterTypes.R270Quality, 'min 270p', '270'),
                                                      (PornFilterTypes.R360Quality, 'min 360p', '360'),
                                                      (PornFilterTypes.R540Quality, 'min 540p', '540'),
                                                      (PornFilterTypes.R720Quality, 'min 720p', '720'),
                                                      (PornFilterTypes.R1080Quality, 'min 1080p', '1080'),
                                                      (PornFilterTypes.R2160Quality, 'min 4k', '2160'),
                                                      ),
                                  }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         channels_args=channels_filters,
                                         porn_stars_args=porn_stars_filters,
                                         single_channel_args=single_channel_filters,
                                         single_porn_star_args=video_filters,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='PornDig', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornDig, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _update_available_categories(self, object_data):
        return self._update_available_general_categories(object_data, PornCategories.CATEGORY)

    def _update_available_general_categories(self, object_data, object_type):
        """
        Fetches all the available shows for the given params.
        :param object_data: Object data.
        :param object_type: Object type.
        :return: Object of all available shows (JSON).
        """
        headers = {
            'Accept': '*/*',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        page_request = self.session.get(object_data.url, headers=headers)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@id="sidebar_category_list_wrapper"]//a[@class="sidebar_section_item"]')
        res = []
        for category in categories:
            cat_id = re.findall(r'\d+', category.attrib['href'])
            if len(cat_id) == 0:
                continue
            category_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                    obj_id=category.attrib['href'],
                                                    url=urljoin(self.base_url, category.attrib['href']),
                                                    title=category.attrib['title'],
                                                    additional_data={'category_id': int(cat_id[0]),
                                                                     'object_type': 'Category',
                                                                     },
                                                    object_type=object_type,
                                                    super_object=object_data,
                                                    )
            res.append(category_data)
        object_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, pornstar_data):
        """
        Fetches all the available shows for the given params.
        :param pornstar_data: Porn star data.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(pornstar_data)
        if pornstar_data.page_number > 1:
            objects = page_request.json()
            tree = self.parser.parse(objects['data']['content'])
            objects = [x for x in tree.xpath('.//div[@class="showcase_item_wrapper"]') if 'id' in x.attrib]
        else:
            tree = self.parser.parse(page_request.text)
            objects = tree.xpath('.//div[@class="js_entity_container js_content_top_pornstars '
                                 'showcases_grid_wrapper"]/div')
        res = []
        for raw_object in objects:
            link = raw_object.xpath('./div[@class="showcase_item_thumbnail"]/a')
            assert len(link) == 1
            title = link[0].attrib['title']
            link = link[0].attrib['href']

            image = raw_object.xpath('./div[@class="showcase_item_thumbnail"]/a/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            nationality = raw_object.xpath('./div[@class="showcase_item_title"]/a/img[@class="flag"]')
            assert len(nationality) == 1

            info = raw_object.xpath('./div[@class="showcase_item_content"]')
            assert len(info) == 1
            rating = info[0].xpath('./div[@class="showcase_small_box showcase_rating"]/p/text()')
            number_of_videos = info[0].xpath('./div[@class="showcase_small_box showcase_views"]/p/text()')
            ranking = info[0].xpath('./div[@class="showcase_middle_box showcase_ranking"]/span/text()')
            ranking = re.findall(r'\d+', ranking[0])
            video_average_ranking = info[0].xpath('./div[@class="showcase_small_box showcase_videos"]/p/text()')
            total_number_of_views = info[0].xpath('./div[@class="showcase_small_box showcase_average"]/p/text()')

            category_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                    obj_id=link,
                                                    url=urljoin(self.base_url, link),
                                                    title=title,
                                                    image_link=image,
                                                    additional_data={'category_id': raw_object.attrib['id'],
                                                                     'nationality': nationality[0].attrib['alt'],
                                                                     'nationality_image': nationality[0].attrib['src'],
                                                                     'ranking': ranking[0],
                                                                     'video_average_ranking': video_average_ranking[0],
                                                                     'total_number_of_views': total_number_of_views[0]
                                                                     if len(total_number_of_views) > 0 else 0,
                                                                     'object_type': 'Porn Star',
                                                                     },
                                                    rating=rating[0],
                                                    number_of_videos=number_of_videos[0]
                                                    if len(number_of_videos) > 0 else 0,
                                                    object_type=PornCategories.PORN_STAR,
                                                    super_object=pornstar_data,
                                                    )
            res.append(category_data)
        pornstar_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows for the given params.
        :param channel_data: Porn star data.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        if channel_data.page_number > 1:
            objects = page_request.json()
            tree = self.parser.parse(objects['data']['content'])
            objects = [x for x in tree.xpath('.//div[@class="showcase_item_wrapper"]') if 'id' in x.attrib]
        else:
            tree = self.parser.parse(page_request.text)
            objects = tree.xpath('.//div[@class="js_entity_container js_content_top_studios showcases_grid_'
                                 'wrapper"]/div')
        res = []
        for raw_object in objects:
            link = raw_object.xpath('./div[@class="showcase_item_thumbnail"]/a')
            assert len(link) == 1
            title = link[0].attrib['title']
            link = link[0].attrib['href']

            image = raw_object.xpath('./div[@class="showcase_item_thumbnail"]/a/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            info = raw_object.xpath('./div[@class="showcase_item_content"]')
            assert len(info) == 1
            rating = info[0].xpath('./div[@class="showcase_small_box showcase_rating"]/p/text()')
            number_of_videos = info[0].xpath('./div[@class="showcase_small_box showcase_views"]/p/text()')
            ranking = info[0].xpath('./div[@class="showcase_middle_box showcase_ranking"]/span/text()')
            ranking = re.findall(r'\d+', ranking[0])
            video_average_ranking = info[0].xpath('./div[@class="showcase_small_box showcase_videos"]/p/text()')
            total_number_of_views = info[0].xpath('./div[@class="showcase_small_box showcase_average"]/p/text()')

            category_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                    obj_id=link,
                                                    url=urljoin(self.base_url, link),
                                                    title=title,
                                                    image_link=image,
                                                    additional_data={'category_id': raw_object.attrib['id'],
                                                                     'ranking': ranking[0],
                                                                     'video_average_ranking': video_average_ranking[0],
                                                                     'total_number_of_views': total_number_of_views[0],
                                                                     'object_type': PornCategories.CHANNEL,
                                                                     },
                                                    rating=rating[0],
                                                    number_of_videos=number_of_videos[0],
                                                    object_type=PornCategories.CHANNEL,
                                                    super_object=channel_data,
                                                    )
            res.append(category_data)
        channel_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        request_data = tmp_tree.xpath('.//link[@rel="prefetch"]/@href')
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(request_data[0], headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)
        request_data = [x for x in tmp_tree.xpath('.//script/text()') if 'vc' in x]
        raw_data = re.findall(r'(?:var vc *= *)({.*})(?:;\n)', request_data[0], re.DOTALL)
        assert len(raw_data) == 1
        raw_data = prepare_json_from_not_formatted_text(raw_data[0])
        res = sorted((VideoSource(link=x['src'].replace('\\/', '/'), resolution=x['res'])
                      for x in raw_data['sources'] if 'res' in x and 'src' in x),
                     key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=res)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN,):
            return 1
        return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _binary_search_max_number_of_pages(self, category_data, last_available_number_of_pages):
        """
        Performs binary search in order to find the last available page.
        :param category_data: Category data.
        :param last_available_number_of_pages: Last available number of pages. Will be the pivot for our next search.
        By default is None, which mean the original pivot will be used...
        :return: Page request
        """
        left_page = 1
        right_page = self.max_pages
        page = last_available_number_of_pages if last_available_number_of_pages is not None \
            else int(math.ceil((right_page + left_page) / 2))
        while 1:
            page_request = self._get_object_request_no_exception_check(category_data, override_page_number=page)
            if self._check_is_available_page(category_data, page_request):
                if page == 1:
                    # todo: take care of this section...
                    print('debug, remove afterwards...')
                raw_data = page_request.json()
                if raw_data['data']['has_more'] is False:
                    # We also moved too far...
                    if len(raw_data['data']['content']) > 0:
                        # We have some data, thus this is the last page
                        return page
                    right_page = page - 1
                    if left_page >= right_page:
                        return left_page
                else:
                    left_page = page
                    if left_page >= right_page:
                        return left_page
            else:
                # We moved too far...
                return 1
            page = int(math.ceil((right_page + left_page) / 2))

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        videos = page_request.json()
        tree = self.parser.parse(videos['data']['content'])
        videos = [x for x in tree.xpath('.//section') if 'id' in x.attrib]

        # if page_data.page_number > 1:
        #     videos = page_request.json()
        #     tree = self.parser.parse(videos['data']['content'])
        #     videos = [x for x in tree.xpath('.//section') if 'id' in x.attrib]
        # else:
        #     tree = self.parser.parse(page_request.text)
        #     videos = (tree.xpath('.//div[@class="js_entity_container js_content_category_videos '
        #                          'videos_grid_wrapper videos_grid_wrapper_medium"]/section') +
        #               tree.xpath('.//div[@class="js_entity_container js_content_pornstar_related_videos '
        #                          'videos_grid_wrapper videos_grid_wrapper_medium"]/section') +
        #               tree.xpath('.//div[@class="js_entity_container js_content_studio_related_videos '
        #                          'videos_grid_wrapper videos_grid_wrapper_medium"]/section') +
        #               tree.xpath('.//div[@class="js_entity_container js_content_all_videos '
        #                          'videos_grid_wrapper videos_grid_wrapper_medium"]/section') +
        #               tree.xpath('.//div[@class="js_entity_container js_content_search_posts '
        #                          'videos_grid_wrapper videos_grid_wrapper_medium"]/section')
        #               )
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1
            url = urljoin(self.base_url, link[0].attrib['href'])
            title = link[0].attrib['alt'] if 'alt' in link[0].attrib else link[0].attrib['title']

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) > 0
            image = image_data[0].attrib['data-src']
            flip_images = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=x), image)
                           for x in range(1, self.number_of_thumbnails + 1)]
            video_preview = image_data[1].attrib['data-vid'] if 'data-vid' in image_data[1].attrib else None

            video_length = video_tree_data.xpath('./a/div[@class="video_item_section video_item_stats clearfix"]/'
                                                 'span[@class="pull-left"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            rating = video_tree_data.xpath('./a/div[@class="video_item_section video_item_stats clearfix"]/'
                                           'span[@class="pull-right"]/i')
            assert len(rating) == 1
            rating = rating[0].tail

            is_hd = video_tree_data.xpath('./a/div[@class="video_item_section video_item_title"]/header/'
                                          'i[@class="icon icon-ic_19_qlt_hd pull-right"]')

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['data-post_id'],
                                                  url=url,
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  is_hd=len(is_hd) > 0,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        if true_object.object_type == PornCategories.VIDEO:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3*',
                'Cache-Control': 'max-age=0',
                'Host': self.host_name,
                'Referer': page_data.super_object.url,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }
            return self.session.get(page_data.url, headers=headers)

        # if page_number == 1:
        #     split_url = fetch_base_url.split('/')
        #     if self.general_filter.current_filters.general.value is not None:
        #         split_url.insert(3, self.general_filter.current_filters.general.value)
        #
        #     headers = {
        #         'Accept': '*/*',
        #         'Cache-Control': 'max-age=0',
        #         'Referer': self.base_url,
        #         'Sec-Fetch-Mode': 'navigate',
        #         'Sec-Fetch-Site': 'same-origin',
        #         'Sec-Fetch-User': '?1',
        #         'Upgrade-Insecure-Requests': '1',
        #         'User-Agent': self.user_agent
        #     }
        #     fetch_base_url = '/'.join(split_url)
        #     page_request = self.session.get(fetch_base_url, headers=headers)
        #     return page_request

        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        # program_fetch_url = category_data['url'] + '/{p}'.format(p=page_number) if page_number != 1 else ''
        headers = {
            'Accept': '*/*',
            'Cache-Control': 'max-age=0',
            'Origin': self.base_url,
            'Referer': page_data.url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            # 'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest'
        }
        # parsed_url = urlparse(page_data.url)
        # split_url_path = parsed_url.path.split('/')
        # prefix = split_url_path[1]
        cat_id = page_data.additional_data['category_id'] if page_data.additional_data is not None else None

        if self.general_filter.current_filters.general.filter_id == PornFilterTypes.GayType:
            main_category_id = 2
        elif self.general_filter.current_filters.general.filter_id == PornFilterTypes.ShemaleType:
            main_category_id = 3
        elif self.general_filter.current_filters.general.filter_id == PornFilterTypes.AmateurType:
            main_category_id = 4
        else:
            main_category_id = 1

        program_fetch_url = self.load_more_videos_url
        if true_object.object_type == PornCategories.CATEGORY:
            params.update({
                'main_category_id': [main_category_id],
                'type': ['post'],
                'name': ['category_videos'],
                'filters[filter_type]': ['date'],
                'filters[filter_period]': [''],
                'filters[filter_quality][]': [270],
                'filters[filter_duration][]': [45, 26, 15, 14],
                'category_id[]': [cat_id],
                'offset': [self.number_of_videos_per_video_page * (page_number-1)],
                # 'use_unique_videos': [1],
                # 'current_page_offset': [0],
            })
        elif true_object.object_type == PornCategories.CHANNEL:
            cat_id = re.findall(r'\d+', cat_id)[0]
            params.update({
                'main_category_id': [main_category_id],
                'type': ['post'],
                'name': ['studio_related_videos'],
                'filters[filter_type]': ['ctr'],
                'filters[filter_period]': [''],
                'filters[filter_quality][]': [270],
                'content_id': [cat_id],
                'offset': [self.number_of_videos_per_channel_page * (page_number-1)],
            })
        elif true_object.object_type == PornCategories.PORN_STAR:
            cat_id = re.findall(r'\d+', cat_id)[0]
            params.update({
                'main_category_id': [main_category_id],
                'type': ['post'],
                'name': ['pornstar_related_videos'],
                'filters[filter_type]': ['ctr'],
                'filters[filter_period]': [''],
                'filters[filter_quality][]': [270],
                'filters[filter_duration][]': [45, 26, 15, 14],
                'content_id': [cat_id],
                'offset': [self.number_of_videos_per_channel_page * (page_number-1)],
            })

        elif true_object.object_type == PornCategories.CHANNEL_MAIN:
            program_fetch_url = self.load_more_channels_url
            params.update({
                'main_category_id': [main_category_id],
                'type': ['studio'],
                'name': ['top_studios'],
                'filters[filter_type]': ['likes'],
                'country_code': [''],
                'starting_letter': [''],
                'offset': [self.number_of_videos_per_channel_page * (page_number - 1)],
            })
        elif true_object.object_type == PornCategories.PORN_STAR_MAIN:
            program_fetch_url = self.load_more_pornstars_url
            params.update({
                'main_category_id': [main_category_id],
                'type': ['pornstar'],
                'name': ['top_pornstars'],
                'filters[filter_type]': ['likes'],
                'country_code': [''],
                'starting_letter': [''],
                'offset': [self.number_of_videos_per_channel_page * (page_number - 1)],
            })
        else:
            program_fetch_url = self.load_more_videos_url
            params.update({
                'main_category_id': [main_category_id],
                'type': ['post'],
                'name': ['all_videos'],
                'filters[filter_type]': ['ctr'],
                'filters[filter_period]': ['month'],
                'filters[filter_quality][]': [540],
                'filters[filter_duration][]': [45, 26, 15, 14],
                'offset': [self.number_of_videos_per_video_page * (page_number - 1)],
            })
        if page_filter.sort_order.value is not None:
            params['filters[filter_type]'] = [page_filter.sort_order.value]
        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            params['filters[filter_period]'] = [page_filter.period.value]
        if page_filter.quality.value is not None:
            params['filters[filter_quality][]'] = [page_filter.quality.value]
        if page_filter.length.value is not None:
            params['filters[filter_duration][]'] = [page_filter.quality.value]
        page_request = self.session.post(program_fetch_url, headers=headers, data=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}'.format(q=quote_plus(query))
