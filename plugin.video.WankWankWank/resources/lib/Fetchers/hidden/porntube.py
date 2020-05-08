# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornNoVideoError

# Internet tools
from .. import urljoin, quote, quote_plus

# JSON
import json

# Regex
import re

# Generator id
from ..id_generator import IdGenerator

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


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


class FourTube(PornTube):
    video_request_format = 'https://token.4tube.com/{id}/desktop/{formats}'

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        res = super(FourTube, self).object_urls
        res.pop(PornCategories.TAG_MAIN)
        return res
        # return {
        #     PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/tags'),
        #     PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels'),
        #     PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/pornstars'),
        #     PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/videos?sort=date'),
        #     PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/videos?sort=views&time=month'),
        #     PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/videos?sort=rating&time=month'),
        #     PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search'),
        # }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.4tube.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filters = {'general_filters': ((PornFilterTypes.StraightType, 'Straight', None),
                                               (PornFilterTypes.GayType, 'Gay', 'gay'),
                                               (PornFilterTypes.ShemaleType, 'Shemale', 'shemale'),
                                               ),
                           }
        category_filters = {'sort_order': ((PornFilterTypes.AlphabeticOrder, 'Alphabetically', None),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'qty'),
                                           (PornFilterTypes.DateOrder, 'Date added', 'date'),
                                           ),
                            }
        # todo: add filter breast size...
        porn_stars_filters = {'general_filters': ((PornFilterTypes.AllType, 'All', None),
                                                  (PornFilterTypes.GirlType, 'Female', 'female'),
                                                  (PornFilterTypes.GuyType, 'Male', 'male'),
                                                  ),
                              'sort_order': ((PornFilterTypes.PopularityOrder, 'Popularity', None),
                                             (PornFilterTypes.SubscribersOrder, 'Most Subscribers', 'subscribers'),
                                             (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'name'),
                                             (PornFilterTypes.TwitterFollowersOrder, 'Twitter Followers', 'twitter'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'videos'),
                                             (PornFilterTypes.DateOrder, 'Date added', 'date'),
                                             (PornFilterTypes.FavorOrder, 'Likes', 'likes'),
                                             ),
                              }
        channels_filters = {'sort_order': ((PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', None),
                                           (PornFilterTypes.AlphabeticOrder, 'Name', 'name'),
                                           (PornFilterTypes.DateOrder, 'Date added', 'date'),
                                           (PornFilterTypes.SubscribersOrder, 'Most Subscribers', 'subscribers'),
                                           (PornFilterTypes.FavorOrder, 'Likes', 'likes'),
                                           ),
                            }
        video_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Most Popular', None),
                                        (PornFilterTypes.DateOrder, 'Latest', 'date'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
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

    def __init__(self, source_name='4Tube', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(FourTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_general_category(category_data, PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_general_category(channel_data, PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_general_category(porn_star_data, PornCategories.PORN_STAR)

    def _update_available_general_category(self, object_data, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = (tree.xpath('.//div[@class="grid-col4 mb1"]//div[@class="col"]/a') +
                      tree.xpath('.//div[@class="grid-col4 mb1"]//div[@class="col thumb_video"]/a') +
                      tree.xpath('.//div[@class="grid-col4"]//div[@class="col"]/a') +
                      tree.xpath('.//div[@class="grid-col4"]//div[@class="col thumb_video"]/a')
                      )
        res = []
        for category in categories:
            assert 'href' in category.attrib
            title = category.attrib['title']

            number_of_videos = category.xpath('./div[@class="bottom"]//i[@class="icon icon-video"]')
            assert len(number_of_videos) == 1

            image_data = category.xpath('./div[@class="thumb"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-original'] if 'data-original' in image_data[0].attrib \
                else image_data[0].attrib['src']

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=category.attrib['href'],
                                                      url=urljoin(object_data.url, category.attrib['href']),
                                                      image_link=image,
                                                      title=title,
                                                      number_of_videos=int(re.sub(r'[(),]', '',
                                                                                  str(number_of_videos[0].tail))),
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        object_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        page_id = tmp_tree.xpath('.//div[@class="links-list inline text-center"]//button/@data-id')
        if any(x != page_id[0] for x in page_id):
            error_module = self._prepare_porn_error_module_for_video_page(
                video_data, tmp_request.url, 'Inconsistent page id in url {u}'.format(u=tmp_request.url))
            raise PornNoVideoError(error_module.message, error_module)
        page_id = page_id[0].zfill(16)
        formats = sorted((int(x.attrib['data-quality']) for x in tmp_tree.xpath('.//button')
                          if 'data-quality' in x.attrib), reverse=True)
        video_request_page = self.video_request_format.format(id=page_id, formats='+'.join(str(x) for x in formats))
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Origin': self.base_url,
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'cors',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        raw_video = self.session.post(video_request_page, headers=headers)
        videos = raw_video.json()

        video_links = sorted((VideoSource(resolution=int(k), link=v['token'])
                              for k, v in videos.items() if v['status'] == 'success'),
                             key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Get number of pages from category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _check_is_available_page(self, page_object, page_request=None):
        """
        In binary search performs test whether the current page is available.
        :param page_request: Page request.
        :return:
        """
        if page_request is None:
            page_request = self.get_object_request(page_object)
        tree = self.parser.parse(page_request.text)
        error_message = tree.xpath('.//div[@class="col-xs-12 text-center"]/h1/strong')
        return not (len(error_message) == 1 and error_message[0].text == 'Oops!' and
                    error_message[0].tail == ' Not Found')

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(self._clear_text(x)) for x in tree.xpath('.//ul[@class="pagination"]/li/a/text()')
                if self._clear_text(x).isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 4

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@id="video_list_column"]//div[@class="col thumb_video"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1

            img = video_tree_data.xpath('./a/div[@class="thumb"]/img/@src')
            assert len(img) == 1

            mini_slide = video_tree_data.xpath('./a/ul//li/@data-src')
            assert len(mini_slide) > 0

            star_info = video_tree_data.xpath('./ul[@class="thumb-info_top"]/li[@class="master-pornstar"]/a')

            is_hd = video_tree_data.xpath('./ul[@class="thumb-info_top"]/li[@class="topHD"]/text()')

            video_length = video_tree_data.xpath('./ul[@class="thumb-info_top"]/li[@class="duration-top"]/text()')
            assert len(video_length) == 1

            title = video_tree_data.xpath('./div[@class="bottom"]/p[@class="thumb-title"]/text()')
            assert len(title) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(self.base_url, link_data[0].attrib['href']),
                                                  image_link=img[0],
                                                  additional_data={'name': star_info[0].text,
                                                                   'url': star_info[0].attrib['href']}
                                                  if len(star_info) > 0 else None,
                                                  is_hd=len(is_hd) > 0 and is_hd[0] == 'HD',
                                                  flip_images_link=mini_slide,
                                                  title=title[0],
                                                  duration=self._format_duration(video_length[0]),
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
        if self.general_filter.current_filters.general.value is not None:
            if len(split_url) <= 3 or split_url[3] != self.general_filter.current_filters.general.value:
                split_url.insert(3, self.general_filter.current_filters.general.value)
        original_params = params

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            # 'Referer': self.base_url,
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        params = {}
        if page_filter.sort_order.value is not None:
            params['sort'] = page_filter.sort_order.value
        if page_filter.quality.value is not None:
            params['quality'] = page_filter.sort_order.value
        if page_filter.length.value is not None:
            params['duration'] = page_filter.length.value
        if page_filter.added_before.value is not None:
            params['time'] = page_filter.added_before.value
        if page_number is not None and page_number > 1:
            params['p'] = page_number
        params.update(original_params)
        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


class Fux(PornTube):
    @property
    def object_urls(self):
        res = super(Fux, self).object_urls
        res.pop(PornCategories.TAG_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.fux.com/'

    def __init__(self, source_name='Fux', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Fux, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server, session_id)


class PornerBros(PornTube):
    @property
    def object_urls(self):
        res = super(PornerBros, self).object_urls
        res.pop(PornCategories.TAG_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornerbros.com/'

    def __init__(self, source_name='PornerBros', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornerBros, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)


if __name__ == '__main__':
    category_id = IdGenerator.make_id('/tags/amateur')
    channel_id = IdGenerator.make_id('/channels/innocent-high')
    porn_star_id = IdGenerator.make_id('/pornstars/capri-cavanni')
    # module = PornTube()
    # module = FourTube()
    # module = Fux()
    module = PornerBros()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['channels']['obj'], (channel_id, ), verbose=1)
    # module.download_object(module.objects['porn_stars']['obj'], (porn_star_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
