# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote

# JSON
import json

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


class PornTube(PornFetcher):
    category_prefix = '/tags/'
    channel_prefix = '/channels/'
    porn_stars_prefix = '/pornstars/'
    video_prefix = '/videos/'

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/tags'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/pornstars'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, '/videos'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/videos?sort=date'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/videos?sort=views'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/videos?sort=rating'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, 'videos?sort=duration'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
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
        return 'https://www.porntube.com/'

    @property
    def category_general_list_json(self):
        return self.base_url + 'api/tag/list'

    @property
    def channel_general_list_json(self):
        return self.base_url + 'api/channel/list'

    @property
    def porn_star_general_list_json(self):
        return self.base_url + 'api/pornstar/list'

    @property
    def video_general_list_json(self):
        return self.base_url + 'api/video/list'

    @property
    def search_general_list_json(self):
        return self.base_url + 'api/search/list'

    @property
    def category_particular_list_json(self):
        return self.base_url + 'api/tags/{slug}'

    @property
    def channel_particular_list_json(self):
        return self.base_url + 'api/channels/{slug}'

    @property
    def porn_star_particular_list_json(self):
        return self.base_url + 'api/pornstars/{slug}'

    @property
    def video_particular_list_json(self):
        return self.base_url + 'api/videos/{slug}'

    @property
    def video_final_link_json_template(self):
        return self.base_url + 'api/videos/{mid}'

    @property
    def video_request_json_template(self):
        return self.base_url.replace('www', 'token') + '{mid}/desktop/1080+720+480+360+240'

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return False

    @property
    def number_of_videos_per_video_page(self):
        """
        Base site url.
        :return:
        """
        return 27  # 3*1 + 4*6

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filters = {'general_filters': ((PornFilterTypes.StraightType, 'Straight', 'straight'),
                                               (PornFilterTypes.GayType, 'Gay', 'gay'),
                                               (PornFilterTypes.ShemaleType, 'Shemale', 'shemale'),
                                               ),
                           }
        category_filters = {'sort_order': ((PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'name'),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'videos'),
                                           (PornFilterTypes.DateOrder, 'Date added', 'date'),
                                           ),
                            }
        # todo: add filter breast size...
        porn_stars_filters = {'general_filters': ((PornFilterTypes.AllType, 'All', None),
                                                  (PornFilterTypes.GirlType, 'Female', 'female'),
                                                  (PornFilterTypes.GuyType, 'Male', 'male'),
                                                  ),
                              'sort_order': ((PornFilterTypes.SubscribersOrder, 'Most Subscribers', 'subscribers'),
                                             (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'name'),
                                             (PornFilterTypes.PopularityOrder, 'Popularity', 'popularity'),
                                             (PornFilterTypes.TwitterFollowersOrder, 'Twitter Followers', 'twitter'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'videos'),
                                             (PornFilterTypes.DateOrder, 'Date added', 'date'),
                                             (PornFilterTypes.FavorOrder, 'Likes', 'rating'),
                                             ),
                              }
        channels_filters = {'sort_order': ((PornFilterTypes.FavorOrder, 'Likes', 'rating'),
                                           (PornFilterTypes.AlphabeticOrder, 'Name', 'name'),
                                           (PornFilterTypes.DateOrder, 'Date added', 'date'),
                                           (PornFilterTypes.SubscribersOrder, 'Most Subscribers', 'subscribers'),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'video'),
                                           ),
                            }
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Latest', 'date'),
                                        (PornFilterTypes.PopularityOrder, 'Most Popular', 'popularity'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        ),
                         'added_before_filters': [(PornFilterTypes.AllAddedBefore, 'All time', None),
                                                  (PornFilterTypes.OneAddedBefore, '24 Hours', '24h'),
                                                  (PornFilterTypes.TwoAddedBefore, 'This week', 'week'),
                                                  (PornFilterTypes.ThreeAddedBefore, 'This month', 'month'),
                                                  (PornFilterTypes.FourAddedBefore, 'This Year', 'year'),
                                                  ],
                         'length_filters': [(PornFilterTypes.AllLength, 'Any duration', None),
                                            (PornFilterTypes.OneLength, 'Short (0-5 min.)', 'short'),
                                            (PornFilterTypes.TwoLength, 'Medium (5-20 min.)', 'medium'),
                                            (PornFilterTypes.ThreeLength, 'Long (20+ min.)', 'long'),
                                            ],
                         'quality_filters': [(PornFilterTypes.AllQuality, 'Any quality', None),
                                             (PornFilterTypes.HDQuality, 'HD quality', 'hd'),
                                             ],
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filters,
                                         categories_args=category_filters,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_category_args=video_filters,
                                         single_channel_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         single_tag_args=video_filters,
                                         video_args=video_filters,
                                         search_args=video_filters,
                                         )

    def __init__(self, source_name='PornTube', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_object):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_object)
        tmp_res = page_request.json()
        res = []
        for x in tmp_res['tags']['_embedded']['items']:
            url = urljoin(self.base_url, '{cp}{slug}'.format(cp=self.category_prefix, slug=x['slug']))
            cat_id = '{cp}{slug}'.format(cp=self.category_prefix, slug=x['slug'])
            additional_data = {'slug': x['slug'], 'category_id': x['id']}
            title = x['name']
            number_of_videos = None
            image = x['thumbDesktop'] if len(x['thumbDesktop']) > 0 else None

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=cat_id,
                                                  url=url,
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  additional_data=additional_data,
                                                  raw_data=x,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_object,
                                                  )
            res.append(object_data)

        category_object.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        tmp_res = page_request.json()
        res = []
        for x in tmp_res['embedded']['topTags']:
            url = urljoin(self.base_url, '{cp}{slug}'.format(cp=self.category_prefix, slug=x['slug']))
            cat_id = '{cp}{slug}'.format(cp=self.category_prefix, slug=x['slug'])
            additional_data = {'slug': x['slug'], 'category_id': None}
            title = x['name']
            number_of_videos = x['videoCount']
            image = None

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=cat_id,
                                                  url=url,
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.TAG,
                                                  super_object=tag_data,
                                                  )
            res.append(object_data)
        res.sort(key=lambda y: y.title)
        tag_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(porn_star_data)
        tmp_res = page_request.json()

        for x in tmp_res['pornstars']['_embedded']['items']:
            url = urljoin(self.base_url, '{cp}{slug}'.format(cp=self.porn_stars_prefix, slug=x['slug']))
            cat_id = '{cp}{slug}'.format(cp=self.porn_stars_prefix, slug=x['slug'])
            additional_data = {'slug': x['slug'], 'category_id': x['id']}
            title = x['name']
            number_of_videos = x['videoCount']
            rating = x['ratingValue']
            image = x['thumbUrl'] if len(x['thumbUrl']) > 0 else None

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=cat_id,
                                                  url=url,
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  additional_data=additional_data,
                                                  rating=rating,
                                                  raw_data=x,
                                                  object_type=PornCategories.PORN_STAR,
                                                  super_object=porn_star_data,
                                                  )
            res.append(object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(channel_data)
        tmp_res = page_request.json()

        for x in tmp_res['channels']['_embedded']['items']:
            url = urljoin(self.base_url, '{cp}{slug}'.format(cp=self.channel_prefix, slug=x['slug']))
            cat_id = '{cp}{slug}'.format(cp=self.channel_prefix, slug=x['slug'])
            additional_data = {'slug': x['slug'], 'category_id': x['id']}
            title = x['name']
            number_of_videos = x['videoCount']
            image = x['thumbUrl'] if len(x['thumbUrl']) > 0 else None

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=cat_id,
                                                  url=url,
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  additional_data=additional_data,
                                                  raw_data=x,
                                                  object_type=PornCategories.CHANNEL,
                                                  super_object=channel_data,
                                                  )
            res.append(object_data)
        channel_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Referer': video_data.super_object.url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        params = {
            'slug': video_data.raw_data['slug'],
            'orientation': 'straight',
            'ssr': False,
        }
        tmp_request = self.session.get(self.video_final_link_json_template.format(mid=video_data.raw_data['uuid']),
                                       headers=headers, params=params)
        video_json = tmp_request.json()
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Cache-Control': 'max-age=0',
            'Origin': self.base_url,
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(self.video_request_json_template.format(mid=video_json['video']['mediaId']),
                                       headers=headers)
        video_links = sorted((VideoSource(resolution=int(k), link=v['token'])
                              for k, v in tmp_request.json().items() if v['status'] == 'success'),
                             key=lambda x: x.resolution, reverse=True)

        return VideoNode(video_sources=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # if category_data.number_of_videos is not None:
        #     # return category_data.number_of_videos
        #     return math.ceil(category_data.number_of_videos / self.number_of_videos_per_video_page)
        # else:
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        res_json = page_request.json()
        parse_url = category_data.url.split('?')[0].split('/')
        category = parse_url[3]
        sub_category = parse_url[4] if len(parse_url) > 4 else ''
        if len(sub_category) > 0:
            # new_category = category[:-1]
            # return math.ceil(res_json[new_category]['videoCount'] / self.number_of_videos_per_video_page)
            return res_json['embedded']['videos']['pages']
        elif category == 'search':
            return res_json['videos']['pages']
        else:
            return res_json[category]['pages']

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)

        res_json = page_request.json()
        res = []
        # object_type = object_data.raw_data['type']
        items = res_json['videos']['_embedded']['items'] \
            if 'videos' in res_json else res_json['embedded']['videos']['_embedded']['items']
        for x in items:
            video_id = '{vp}{slug}_{uid}'.format(vp=self.video_prefix, slug=x['slug'], uid=x['uuid'])
            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_id,
                                                  url=urljoin(self.base_url, video_id),
                                                  title=x['title'],
                                                  image_link=urljoin(self.base_url, x['videoThumbnail']),
                                                  flip_images_link=[urljoin(self.base_url, y)
                                                                    for y in x['thumbnailsList']],
                                                  duration=x['durationInSeconds'],
                                                  is_hd=x['isHD'],
                                                  number_of_views=x['playsQty'],
                                                  raw_data=x,
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
        split_url = fetch_base_url.split('/')
        sub_category = split_url[-1]

        original_params = params
        if 'quality' in original_params:
            original_params['isHD'] = original_params.pop('quality') == 'hd'

        page_number = page_number if page_number is not None else 1
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Referer': page_data.url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        # Default params for videos
        # filter_value = '{}' if 'time' not in original_params \
        #     else '{' + '"{k}":"{v}"'.format(k='time', v=original_params['time']) + '}'

        # Prepare filter
        param_filter = {}
        if page_filter.general.value is not None:
            param_filter['sex'] = page_filter.general.value
        if page_filter.added_before.value is not None:
            param_filter['time'] = page_filter.added_before.value
        if page_filter.length.value is not None:
            param_filter['duration'] = page_filter.length.value
        if page_filter.quality.value is not None:
            param_filter['isHD'] = page_filter.quality.value
        param_filter.update({k: v for k, v in params.items() if k in param_filter})
        params = {
            # 'filter': urlencode(param_filter),
            'filter': json.dumps(param_filter) if len(param_filter) > 0 else '{}',
            'orientation': self.general_filter.current_filters.general.value,
            'order': page_filter.sort_order.value if 'sort' not in original_params else original_params['sort'],
            'ssr': 'false',
            'p': page_number,
        }
        if true_object.object_type in (PornCategories.TAG_MAIN, PornCategories.CATEGORY_MAIN):
            params.pop('p')
            url = self.category_general_list_json
        elif true_object.object_type in (PornCategories.TAG, PornCategories.CATEGORY):
            url = self.category_particular_list_json.format(slug=sub_category)
        elif true_object.object_type == PornCategories.CHANNEL_MAIN:
            url = self.channel_general_list_json
        elif true_object.object_type == PornCategories.CHANNEL:
            url = self.channel_particular_list_json.format(slug=sub_category)
        elif true_object.object_type == PornCategories.PORN_STAR_MAIN:
            url = self.porn_star_general_list_json
        elif true_object.object_type == PornCategories.PORN_STAR:
            url = self.porn_star_particular_list_json.format(slug=sub_category)
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            params['q'] = original_params['q']
            url = self.search_general_list_json
        else:
            url = self.video_general_list_json

        page_request = self.session.get(url, headers=headers, params=params)
        if not page_request.ok:
            page_request = self.session.get(url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote(query))
