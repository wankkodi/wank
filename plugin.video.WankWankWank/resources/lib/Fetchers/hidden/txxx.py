# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornValueError

# Internet tools
from .. import urljoin, quote, parse_qs, urlparse

# Regex
import re

# Generator id
from ..id_generator import IdGenerator

# Math
import math

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


class Txxx(PornFetcher):
    _max_pages = 6670

    number_of_videos_per_page = 60
    number_of_channels_per_page = 80
    number_of_porn_stars_per_page = 48

    @property
    def video_data_request_url(self):
        return urljoin(self.base_url, "/api/videofile.php")

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels/1/?sort=latest-updates'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/1/?sort=most-popular&gender=str'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/1/?sort=latest-updates&type=all'),
            PornCategories.POPULAR_VIDEO:
                urljoin(self.base_url, '/most-popular/1/?sort=most-popular&date=day&type=all'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/1/?sort=top-rated&date=day&type=all'),
            PornCategories.MOST_VIEWED_VIDEO:
                urljoin(self.base_url, '/most-viewed/1/?sort=most-viewed&date=day&type=all&duration=all'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/longest/1/?sort=longest&type=all'),
            PornCategories.MOST_DISCUSSED_VIDEO:
                urljoin(self.base_url, '/most-commented/1/?sort=most-commented&type=all&duration=all'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def possible_empty_pages(self):
        """
        Defines whether it is possible to have empty pages in the site.
        :return:
        """
        return True

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://txxx.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filters, video_filters, search_filter, _, porn_stars_filters, channels_filters = self._prepare_filters()

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filters,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filter,
                                         )

    def _prepare_filters(self):
        general_filters = {'general_filters': ((PornFilterTypes.StraightType, 'Heterosexual', 'str'),
                                               (PornFilterTypes.GayType, 'Gay', 'gay'),
                                               (PornFilterTypes.ShemaleType, 'Transgender', 'she'),
                                               ),
                           }
        video_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Popularity', 'most-popular'),
                                        (PornFilterTypes.DateOrder, 'Date', 'latest-updates'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        (PornFilterTypes.CommentsOrder, 'Number of Comments', 'most-commented'),
                                        (PornFilterTypes.ViewsOrder, 'Number of Views', 'most-viewed'),
                                        ),
                         'period_filters': (((PornFilterTypes.AllDate, 'All time', ''),
                                             (PornFilterTypes.TwoDate, 'Week', 'week'),
                                             (PornFilterTypes.OneDate, 'Month', 'month'),
                                             (PornFilterTypes.ThreeDate, 'Today', 'day'),
                                             ),
                                            (('sort_order', [PornFilterTypes.PopularityOrder,
                                                             PornFilterTypes.ViewsOrder,
                                                             PornFilterTypes.RatingOrder]),
                                             ),
                                            ),
                         'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', 'all'),
                                             (PornFilterTypes.HDQuality, 'HD quality', 'hd'),
                                             (PornFilterTypes.VRQuality, 'VR quality', 'vr'),
                                             ),
                         'length_filters': ((PornFilterTypes.AllLength, 'Any duration', ''),
                                            (PornFilterTypes.OneLength, '0-10 min', '1'),
                                            (PornFilterTypes.TwoLength, '10-40 min.', '2'),
                                            (PornFilterTypes.ThreeLength, '40+ min.', '3'),
                                            ),
                         }
        # video_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Popularity', 'most-popular'),
        #                                 (PornFilterTypes.DateOrder, 'Date', 'latest-updates'),
        #                                 (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
        #                                 (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
        #                                 (PornFilterTypes.CommentsOrder, 'Number of Comments', 'most-commented'),
        #                                 (PornFilterTypes.ViewsOrder, 'Number of Views', 'most-viewed'),
        #                                 ),
        #                  'period_filters': (((PornFilterTypes.AllDate, 'All time', 'all'),
        #                                      (PornFilterTypes.TwoDate, 'Week', 'week'),
        #                                      (PornFilterTypes.OneDate, 'Month', 'month'),
        #                                      (PornFilterTypes.ThreeDate, 'Today', 'day'),
        #                                      ),
        #                                     (('sort_order', [PornFilterTypes.PopularityOrder,
        #                                                      PornFilterTypes.ViewsOrder,
        #                                                      PornFilterTypes.RatingOrder]),
        #                                      ),
        #                                     ),
        #                  'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', 'all'),
        #                                      (PornFilterTypes.HDQuality, 'HD quality', 'hd'),
        #                                      (PornFilterTypes.VRQuality, 'VR quality', 'vr'),
        #                                      ),
        #                  'length_filters': ((PornFilterTypes.AllLength, 'Any duration', 'all'),
        #                                     (PornFilterTypes.OneLength, '0-10 min', '1'),
        #                                     (PornFilterTypes.TwoLength, '10-40 min.', '2'),
        #                                     (PornFilterTypes.ThreeLength, '40+ min.', '3'),
        #                                     ),
        #                  }
        search_filters = {'quality_filters': video_filters['quality_filters'],
                          'length_filters': video_filters['length_filters'],
                          }
        # todo: add more single porn star filters...
        porn_stars_filters = \
            {'sort_order': ((PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'alphabet'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'count-videos'),
                            (PornFilterTypes.DateOrder, 'Date of Last Update', 'latest-updates'),
                            (PornFilterTypes.CommentsOrder, 'Number of Comments', 'most-commented'),
                            (PornFilterTypes.PopularityOrder, 'Popularity', 'most-popular'),
                            (PornFilterTypes.SubscribersOrder, 'Number of Subscribers', 'most-subscribed'),
                            (PornFilterTypes.ViewsOrder, 'Number of Views', 'most-viewed'),
                            (PornFilterTypes.DateAddedOrder, 'Date Added', 'recent'),
                            (PornFilterTypes.RatingOrder, 'Rating', 'top-rated'),
                            ),
             # 'general_filter': ((PornFilterTypes.GirlType, 'Women', 'str'),
             #                 (PornFilterTypes.AllType, 'All', 'all'),
             #                 (PornFilterTypes.GuyType, 'Man', 'gay'),
             #                 (PornFilterTypes.ShemaleType, 'Transgender', 'she'),
             #                 ),
             }
        channels_filters = \
            {'sort_order': ((PornFilterTypes.DateOrder, 'Date of Last Update', 'latest-updates'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically A-Z', 'alphabetaz'),
                            (PornFilterTypes.AlphabeticOrder2, 'Alphabetically Z-A', 'alphabetza'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'count-videos'),
                            (PornFilterTypes.PopularityOrder, 'Popularity', 'most-popular'),
                            (PornFilterTypes.ViewsOrder, 'Number of Views', 'most-viewed'),
                            (PornFilterTypes.DateAddedOrder, 'Date Added', 'recent'),
                            (PornFilterTypes.RatingOrder, 'Rating', 'top-rated'),
                            ),
             }
        return general_filters, video_filters, search_filters, None, porn_stars_filters, channels_filters

    def __init__(self, source_name='Txxx', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Txxx, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                   session_id)
        self.channels_json = urljoin(self.base_url, '/api/json/channels/86400/{gender}/{sort}/{npp}/..{p}.json')
        self.channel_json = urljoin(self.base_url, '/api/json/videos/86400/{gender}/{sort}/{npp}/'
                                                   'channel.{channel}.{p}.{type}.{length}.{period}.json')
        self.porn_stars_json = urljoin(self.base_url, '/api/json/models/86400/{gender}/'
                                                      'filt........../{sort}/{npp}/{p}.json')
        self.porn_star_json = urljoin(self.base_url, '/api/json/videos/86400/{gender}/{sort}/{npp}/'
                                                     'model.{model}.{p}.{type}.{length}.{period}.json')
        self.category_json = urljoin(self.base_url, '/api/json/videos/86400/{gender}/{sort}/{npp}/'
                                                    'categories.{cat}.{p}.{type}.{length}.{period}.json')
        self.categories_json = urljoin(self.base_url, '/api/json/categories/14400/{gender}.{type}.json')
        self.video_json = urljoin(self.base_url, '/api/json/videos/86400/{gender}/{sort}/{npp}/'
                                                 '..{p}.{type}.{length}.{period}.json')
        self.search_json = urljoin(self.base_url, '/api/videos.php?params=259200/{gender}/relevance/{npp}/'
                                                  'search..{p}.{type}.{length}.{period}&s={query}')
        self.category_url2 = urljoin(self.base_url, '/tc_cats.php')
        self.number_of_flip_images = 12
        self.single_channel_prefix = urljoin(self.base_url, '/channel/')
        self.single_porn_star_prefix = urljoin(self.base_url, '/models/')
        self.video_page_template = urljoin(self.base_url, '/videos/{vid}/{dir}/')

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        raw_data = page_request.json()
        object_data = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=x['dir'],
                                               url=category_data.url + '{c}/'.format(c=x['dir']),
                                               title=x['title'],
                                               number_of_videos=int(x['total_videos']),
                                               raw_data=x,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ) for x in raw_data['categories']]

        category_data.add_sub_objects(object_data)
        return object_data

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        raw_data = page_request.json()
        object_data = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=x['channel_id'],
                                               url=self.single_channel_prefix + '{c}/1/'.format(c=x['dir']),
                                               title=x['title'],
                                               number_of_videos=int(x['statistics']['videos']),
                                               image_link=x['img'],
                                               raw_data=x,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ) for x in raw_data['channels']]

        channel_data.add_sub_objects(object_data)
        return object_data

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        raw_data = page_request.json()
        object_data = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=x['dir'],
                                               url=self.single_porn_star_prefix + '{c}/1/'.format(c=x['dir']),
                                               title=x['title'],
                                               number_of_videos=int(x['statistics']['videos']),
                                               image_link=x['img'],
                                               raw_data=x,
                                               rating=x['rating'],
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ) for x in raw_data['models']]

        porn_star_data.add_sub_objects(object_data)
        return object_data

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of pages out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request

        raw_data = page_request.json()
        number_of_videos = int(raw_data['total_count']) if 'total_count' in raw_data else 0
        if category_data.object_type in (PornCategories.CHANNEL_MAIN, ):
            return math.ceil(number_of_videos / self.number_of_channels_per_page)
        elif category_data.object_type in (PornCategories.PORN_STAR_MAIN, ):
            return math.ceil(number_of_videos / self.number_of_porn_stars_per_page)
        else:
            return min(math.ceil(number_of_videos / self.number_of_videos_per_page), self._max_pages)

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
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        params = {
            'video_id': video_data.raw_data['video_id'],
            'lifetime': 8640000,
        }
        request = self.session.post(self.video_data_request_url, headers=headers, params=params)
        raw_data = request.json()
        video_url = [VideoSource(link=urljoin(self.base_url, self._dpww3dw64(x['video_url']))) for x in raw_data]

        return VideoNode(video_sources=video_url)

    @staticmethod
    def _dpww3dw64(raw_video_url):
        """
        Implementation of the Dpww3Dw64 encoding
        :return:
        """
        key_str = "АВСDЕFGHIJKLМNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~"
        c = ""
        b = 0
        # if not re.findall(r'[^АВСЕМA-Za-z0-9.,~]', raw_video_url):
        #     raise RuntimeError
        if isinstance(raw_video_url, str):
            raw_video_url = re.sub(r'[^АВСЕМA-Za-z0-9.,~]', '', raw_video_url)
        else:
            raw_video_url = re.sub(ur'[^\u0410\u0412\u0421\u0415\u041CA-Za-z0-9.,~]', '', raw_video_url)

        while 1:
            e = key_str.index(raw_video_url[b])
            b += 1
            d = key_str.index(raw_video_url[b])
            b += 1
            f = key_str.index(raw_video_url[b])
            b += 1
            g = key_str.index(raw_video_url[b])
            b += 1

            e = e << 2 | d >> 4
            d = (d & 15) << 4 | f >> 2
            h = (f & 3) << 6 | g
            c += chr(e)
            if 64 != f:
                c += chr(d)
            if 64 != g:
                c += chr(h)
            if b >= len(raw_video_url):
                break
        return c

    @staticmethod
    def _get_video_url_from_raw_url(raw_url):
        """
        Returns video url from raw url
        :param raw_url: Raw (encoded) url
        :return:
        """
        b = raw_url.split('||')
        if not re.findall('/get_file/', b[0]):
            raw_url = Txxx._do_some_magic(b[0])
        if len(b) > 1:
            raw_url = re.sub(r'/get_file/\d+/[0-9a-z]{32}/', b[1], raw_url)
        if len(b) > 2:
            raw_url += '&' if r'\?' in raw_url else '?' + 'lip=' + b[2] + '&ti' + b[3]
        return raw_url

    @staticmethod
    def _do_some_magic(e):
        c = ''
        e = re.sub(r'[^\u0410\u0412\u0421\u0415\u041cA-Za-z0-9.,~]g', '', e)
        f = 0
        while f < len(e):
            h = "\u0410\u0412\u0421D\u0415FGHIJKL\u041cNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~".index(e[f])
            f += 1
            n = "\u0410\u0412\u0421D\u0415FGHIJKL\u041cNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~".index(e[f])
            f += 1
            ll = "\u0410\u0412\u0421D\u0415FGHIJKL\u041cNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~" \
                 "".index(e[f])
            f += 1
            q = "\u0410\u0412\u0421D\u0415FGHIJKL\u041cNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~".index(e[f])
            f += 1
            h = h << 2 | n >> 4
            n = (n & 15) << 4 | ll >> 2
            u = (ll & 3) << 6 | q
            c += chr(h)
            if ll != 64:
                c += chr(n)
            if q != 64:
                c += chr(u)

        return c

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        raw_data = page_request.json()
        if 'error' in raw_data:
            if raw_data['error'] == 1:
                # We have no videos for the requested parameters
                return None
            else:
                raise PornValueError('Cannot fetch the request, got error: {e}'.format(e=raw_data['code']))
        res = [PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                        obj_id=x['video_id'],
                                        url=self.video_page_template.format(vid=x['video_id'], dir=x['dir']),
                                        title=x['title'],
                                        description=x['description'],
                                        image_link=x['scr'],
                                        flip_images_link=[re.sub('1.jpg', '{i}.jpg'.format(i=i), x['scr'])
                                                          for i in range(1, self.number_of_flip_images+1)],
                                        is_hd='hd' in x['props'] and x['props']['hd'] == 1,
                                        duration=self._format_duration(x['duration']),
                                        number_of_views=x['video_viewed'],
                                        rating=x['rating'] if 'rating' in x else None,
                                        raw_data=x,
                                        object_type=PornCategories.VIDEO,
                                        super_object=page_data,
                                        )
               for x in raw_data['videos']]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        conditions = self.get_proper_filter(page_data).conditions
        if page_number is None:
            page_number = 1
        program_fetch_url = self._prepare_json_url_from_params(page_data, fetch_base_url, page_number, true_object,
                                                               page_filter, conditions)
        # referer = fetch_base_url + '{p}/?'.format(p=page_number)
        referer = fetch_base_url
        referer_params = []
        if true_object.object_type == PornCategories.SEARCH_MAIN:
            referer_params.append('s={s}'.format(s=self._search_query))
        if page_filter.sort_order.value is not None:
            referer_params.append('sort={s}'.format(s=page_filter.sort_order.value))
        if page_filter.period.value is not None:
            referer_params.append('date={s}'.format(s=page_filter.period.value))
        if page_filter.quality.value is not None:
            referer_params.append('type={s}'.format(s=page_filter.quality.value))
        if page_filter.length.value is not None:
            referer_params.append('duration={s}'.format(s=page_filter.length.value))
        if len(referer_params) > 0:
            referer += '?' + '&'.join(referer_params)
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Referer': referer,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        page_request = self.session.get(program_fetch_url, headers=headers)
        return page_request

    def _prepare_json_params_from_request(self, page_data, url, page_filter, conditions):
        split_path = url.split('/')
        obj_id = split_path[4]

        true_sort_filter_id = self._default_sort_by[page_data.true_object.object_type] \
            if page_data.true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id
        sort = self.get_proper_filter(page_data).filters.sort_order[true_sort_filter_id].value

        gender_value = self.general_filter.current_filters.general.value
        # sort = page_filter.sort_order.value
        length = page_filter.length.value
        quality = page_filter.quality.value
        period = page_filter.period.value \
            if (conditions.period.sort_order is not None and
                true_sort_filter_id in conditions.period.sort_order) else ''
        return obj_id, gender_value, sort, length, quality, period

    def _prepare_json_url_from_params(self, page_data, url, page, true_object, page_filter, conditions):
        obj_id, gender_value, sort, length, quality, period = \
            self._prepare_json_params_from_request(page_data, url, page_filter, conditions)
        if true_object.object_type == PornCategories.CATEGORY_MAIN:
            program_fetch_url = self.categories_json.format(gender=gender_value, type='all')
        elif true_object.object_type == PornCategories.CATEGORY:
            program_fetch_url = self.category_json.format(gender=gender_value, sort=sort,
                                                          p=page, cat=obj_id,
                                                          type=quality, length=length, period=period,
                                                          npp=self.number_of_videos_per_page)
        elif true_object.object_type == PornCategories.CHANNEL_MAIN:
            program_fetch_url = self.channels_json.format(gender=gender_value, sort=sort,
                                                          p=page,
                                                          npp=self.number_of_channels_per_page)
        elif true_object.object_type == PornCategories.CHANNEL:
            program_fetch_url = self.channel_json.format(gender=gender_value, sort=sort,
                                                         p=page, channel=obj_id,
                                                         type=quality, length=length, period=period,
                                                         npp=self.number_of_videos_per_page)
        elif true_object.object_type == PornCategories.PORN_STAR_MAIN:
            program_fetch_url = self.porn_stars_json.format(gender=gender_value, sort=sort,
                                                            p=page,
                                                            npp=self.number_of_porn_stars_per_page)
        elif true_object.object_type == PornCategories.PORN_STAR:
            program_fetch_url = self.porn_star_json.format(gender=gender_value, sort=sort,
                                                           p=page, model=obj_id,
                                                           type=quality, length=length, period=period,
                                                           npp=self.number_of_videos_per_page)
        elif true_object.object_type in self._default_sort_by:
            program_fetch_url = self.video_json.format(gender=gender_value, sort=sort, p=page,
                                                       type=quality, length=length, period=period,
                                                       npp=self.number_of_videos_per_page)
        # elif true_object.object_type == PornCategories.LATEST_VIDEO:
        #     program_fetch_url = self.video_json.format(gender=gender_value, sort='latest-updates', p=page,
        #                                                type=quality, length=length, period=period,
        #                                                npp=self.number_of_videos_per_page)
        # elif true_object.object_type == PornCategories.POPULAR_VIDEO:
        #     program_fetch_url = self.video_json.format(gender=gender_value, sort='most-popular', p=page,
        #                                                type=quality, length=length, period=period,
        #                                                npp=self.number_of_videos_per_page)
        # elif true_object.object_type == PornCategories.TOP_RATED_VIDEO:
        #     program_fetch_url = self.video_json.format(gender=gender_value, sort='top-rated', p=page,
        #                                                type=quality, length=length, period=period,
        #                                                npp=self.number_of_videos_per_page)
        # elif true_object.object_type == PornCategories.LONGEST_VIDEO:
        #     program_fetch_url = self.video_json.format(gender=gender_value, sort='longest', p=page,
        #                                                type=quality, length=length, period=period,
        #                                                npp=self.number_of_videos_per_page)
        # elif true_object.object_type == PornCategories.MOST_DISCUSSED_VIDEO:
        #     program_fetch_url = self.video_json.format(gender=gender_value, sort='most-commented', p=page,
        #                                                type=quality, length=length, period=period,
        #                                                npp=self.number_of_videos_per_page)
        # elif true_object.object_type == PornCategories.MOST_VIEWED_VIDEO:
        #     program_fetch_url = self.video_json.format(gender=gender_value, sort='most-viewed', p=page,
        #                                                type=quality, length=length, period=period,
        #                                                npp=self.number_of_videos_per_page)
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            program_fetch_url = self.search_json.format(gender=gender_value, sort=sort, p=page,
                                                        type=quality, length=length, period=period,
                                                        npp=self.number_of_videos_per_page,
                                                        query=self._search_query)
        else:
            raise RuntimeError('Unknown url form {u}'.format(u=url))
        return program_fetch_url

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = quote(query)
        return self.object_urls[PornCategories.SEARCH_MAIN] + '1/?s={q}'.format(q=self._search_query)


class HClips(Txxx):
    number_of_flip_images = 15

    # @property
    # def video_data_request_url(self):
    #     """
    #     Most viewed videos page url.
    #     :return:
    #     """
    #     return urljoin(self.base_url, '/sn4diyux.php')

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 50000

    @property
    def object_urls(self):
        res = super(HClips, self).object_urls
        res.pop(PornCategories.PORN_STAR_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://hclips.com/'

    def __init__(self, source_name='HClips', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HClips, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)
        self.search_json = urljoin(self.base_url, '/api/videos.php?params=259200/{gender}/relevance/{npp}/'
                                                  'search..{p}.{type}.{length}.{period}&s={query}&sort={sort}&'
                                                  'date={period}&type={type}')

    def _prepare_filters(self):
        general_filters, _, _, _, _, channels_filters = \
            super(HClips, self)._prepare_filters()
        video_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Popularity', 'most-popular'),
                                        (PornFilterTypes.DateOrder, 'Date', 'latest-updates'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        (PornFilterTypes.CommentsOrder, 'Number of Comments', 'most-commented'),
                                        (PornFilterTypes.ViewsOrder, 'Number of Views', 'most-viewed'),
                                        ),
                         'period_filters': (((PornFilterTypes.AllDate, 'All time', ''),
                                             (PornFilterTypes.TwoDate, 'Week', 'week'),
                                             (PornFilterTypes.OneDate, 'Month', 'month'),
                                             (PornFilterTypes.ThreeDate, 'Today', 'day'),
                                             ),
                                            (('sort_order', [PornFilterTypes.PopularityOrder,
                                                             PornFilterTypes.ViewsOrder,
                                                             PornFilterTypes.RatingOrder]),
                                             ),
                                            ),
                         'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', 'all'),
                                             (PornFilterTypes.HDQuality, 'HD quality', 'hd'),
                                             ),
                         'length_filters': ((PornFilterTypes.AllLength, 'Any duration', ''),
                                            (PornFilterTypes.OneLength, '0-10 min', '1'),
                                            (PornFilterTypes.TwoLength, '10-40 min.', '2'),
                                            (PornFilterTypes.ThreeLength, '40+ min.', '3'),
                                            ),
                         }
        return general_filters, video_filters, video_filters, None, None, channels_filters

    def _prepare_json_params_from_request(self, page_data, url, page_filter, conditions):
        obj_id, gender_value, sort, length, quality, period = \
            super(HClips, self)._prepare_json_params_from_request(page_data, url, page_filter, conditions)
        length = page_filter.length.value if page_filter.length.value != 'all' else ''
        return obj_id, gender_value, sort, length, quality, period


class UPornia(Txxx):
    number_of_flip_images = 15

    @property
    def video_data_request_url(self):
        """
        Most viewed videos page url.
        :return:
        """
        return urljoin(self.base_url, '/sn4diyux.php')

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/longest/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://upornia.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filters, video_filters, search_filter, categories_filters, porn_stars_filters, channels_filters = \
            self._prepare_filters()

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filters,
                                         categories_args=categories_filters,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filter,
                                         )

    def _prepare_filters(self):
        general_filters = {'general_filters': ((PornFilterTypes.StraightType, 'Heterosexual', '1'),
                                               (PornFilterTypes.GayType, 'Gay', '2'),
                                               (PornFilterTypes.ShemaleType, 'Transgender', '3'),
                                               ),
                           }
        video_filters = \
            {'sort_order': ((PornFilterTypes.DateOrder, 'Latest', 'sort_by=post_date'),
                            (PornFilterTypes.ViewsOrder, 'Most Viewed', 'sort_by=video_viewed'),
                            (PornFilterTypes.RatingOrder, 'Top Rated', 'sort_by=rating'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'sort_by=duration'),
                            (PornFilterTypes.CommentsOrder, 'Most Commented', 'sort_by=most_commented'),
                            (PornFilterTypes.FavorOrder, 'Most Favorite', 'sort_by=most_favourited'),
                            ),
             'period_filters': (((PornFilterTypes.AllDate, 'All time', None),
                                 (PornFilterTypes.TwoDate, 'Week', 'week'),
                                 (PornFilterTypes.OneDate, 'Month', 'month'),
                                 (PornFilterTypes.ThreeDate, 'Today', 'day'),
                                 ),
                                (('sort_order', [PornFilterTypes.ViewsOrder,
                                                 PornFilterTypes.RatingOrder]),
                                 ),
                                ),
             'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', None),
                                 (PornFilterTypes.HDQuality, 'HD quality', 'show_only_hd=1'),
                                 ),
             'length_filters': ((PornFilterTypes.AllLength, 'Any duration', None),
                                (PornFilterTypes.OneLength, '0-8 min', 'duration_from=&duration_to=480'),
                                (PornFilterTypes.TwoLength, '10-40 min.', 'duration_from=481&duration_to=1200'),
                                (PornFilterTypes.ThreeLength, '40+ min.', 'duration_from=1200&duration_to=1201'),
                                ),
             }
        categories_filters = \
            {'sort_order': ((PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sort_by=title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Video Count', 'sort_by=total_videos'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'sort_by=avg_videos_rating'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'sort_by=avg_videos_popularity'),
                            ),
             }
        porn_stars_filters = \
            {'sort_order': ((PornFilterTypes.VideosRatingOrder, 'Top Rated', 'sort_by=avg_videos_rating'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'sort_by=avg_videos_popularity'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Total Videos', 'sort_by=total_videos'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sort_by=title'),
                            (PornFilterTypes.SubscribersOrder, 'Most Subscribers', 'sort_by=subscribers_count'),
                            ),
             }
        channels_filters = \
            {'sort_order': ((PornFilterTypes.VideosRatingOrder, 'Top Rated', 'sort_by=avg_videos_rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sort_by=title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Video Count', 'sort_by=total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'sort_by=avg_videos_popularity'),
                            (PornFilterTypes.DateOrder, 'Recently Updated', 'sort_by=last_content_date'),
                            ),
             }
        return general_filters, video_filters, video_filters, categories_filters, porn_stars_filters, channels_filters

    def __init__(self, source_name='UPornia', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(UPornia, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@id="list_categories_categories_list_items"]/article/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="thumbnail__label"]/i')
            assert len(number_of_videos) == 1
            number_of_videos = int(''.join(re.findall(r'\d+', number_of_videos[0].tail)))

            rating = category.xpath('./div[@class="thumbnail__info"]/span[@class="thumbnail__info__right"]/i')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].tail)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               rating=rating,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channels.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        channels = tree.xpath('.//div[@id="list_content_sources2_sponsors_list_items"]/article/a')
        res = []
        for channel in channels:
            link = channel.attrib['href']

            image_data = channel.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = channel.xpath('./div[@class="thumbnail__info"]/span[@class="thumbnail__info__right"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ))

        channel_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = tree.xpath('.//div[@id="list_models_sphinx_models_list_items"]/article/a')
        res = []
        for porn_star in porn_stars:
            link = porn_star.attrib['href']

            image_data = porn_star.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = porn_star.xpath('./div[@class="thumbnail__label"]/i')
            assert len(number_of_videos) == 1
            number_of_videos = int(''.join(re.findall(r'\d+', number_of_videos[0].tail)))

            country = porn_star.xpath('./div[@class="thumbnail__label thumbnail__label thumbnail__label--left"]/i')
            additional_info = {'country': re.findall(r'(?:flag-)(\w*$)',
                                                     country[0].attrib['class'])[0]} if len(country) == 1 else None

            rating = porn_star.xpath('./div[@class="thumbnail__info thumbnail__info--transparent"]/'
                                     'span[@class="thumbnail__info__right"]/i')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].tail)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               additional_data=additional_info,
                                               rating=rating,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tree = self.parser.parse(tmp_request.text)
        raw_script = [x for x in tree.xpath('.//script') if x.text is not None and 'pC3' in x.text]
        video_id = re.findall(r'(?:"*video_id"*: *)(\d+)', raw_script[0].text)[0]
        pc3 = re.findall(r'(?:"*pC3"*: *\'*)([\d|,]*)', raw_script[0].text)[0]
        params = {'param': video_id + ',' + pc3}

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Cache-Control': 'max-age=0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': video_data.url,
            'Origin': self.base_url[:-1],
            'Sec-Fetch-Mode': 'nested-navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        request = self.session.post(self.video_data_request_url, headers=headers, data=params)
        video_url = re.findall(r'(?:"*video_url"*: *")(.*?)(?:")', request.text)[0]
        video_url = re.sub(r'\\u\d{3}[a-e0-9]', lambda x: x.group(0).encode('utf-8').decode('unicode-escape'),
                           video_url)
        true_video_url = self._get_video_url_from_raw_url(video_url)
        video_url = [VideoSource(link=true_video_url)]

        return VideoNode(video_sources=video_url)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        return max(pages) if len(pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(self._clear_text(x.text).replace(' ', '')) for x in tree.xpath('.//ul[@id="pagination-list"]/li/*')
                if x.text is not None and self._clear_text(x.text).replace(' ', '').isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        video_preview_url = dict(
            re.findall(r'(?:\[)(\d+)(?:\])(?:.*?)(https://cdn\d+.ahacdn.me/c\d+/videos)', page_request.text))
        videos = (tree.xpath('.//div[@id="list_videos2_common_videos_list_items"]/article/a') +
                  tree.xpath('.//div[@id="sphinx_list_cat_videos_videos_list_items"]/article/a') +
                  tree.xpath('.//div[@id="list_videos_videos_list_search_result_items"]/article/a'))
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./img')
            assert len(image_data) == 1
            video_id = image_data[0].attrib['data-video-id']
            image = image_data[0].attrib['src']
            flix_image = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                          for d in range(1, self.number_of_flip_images + 1)]
            video_source = image_data[0].attrib['data-sgid'].split(':')[-1]
            preview_link = (video_preview_url[video_source] +
                            '/{vid_prefix}/{vid}/{vid}_tr.mp4'
                            ''.format(vid_prefix=video_id[:-3]+'000', vid=video_id)) \
                if video_source in video_preview_url else None
            additional_info = {'video_id': video_id}

            video_length = video_tree_data.xpath('./div[@class="thumbnail__info"]/'
                                                 'div[@class="thumbnail__info__right"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            title = video_tree_data.xpath('./div[@class="thumbnail__info"]/div[@class="thumbnail__info__left"]/h5')
            assert len(title) == 1
            title = title[0].text

            rating = video_tree_data.xpath('./div[@class="thumbnail__info__left"]/i')
            rating = self._clear_text(rating[0].tail) if len(rating) == 1 else None

            number_of_views = video_tree_data.xpath('./div[@class="thumbnail__info thumbnail__info--hover"]/'
                                                    'div[@class="thumbnail__info__right"]/i')
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].tail)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  preview_video_link=preview_link,
                                                  additional_data=additional_info,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  number_of_views=number_of_views,
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
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if true_object.object_type == PornCategories.VIDEO:
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request

        if self.general_filter.current_filters.general.value is not None:
            self.session.cookies.set(name='category_group_id',
                                     value=self.general_filter.current_filters.general.value,
                                     domain=urlparse(self.base_url).netloc,
                                     )

        if page_number is None:
            page_number = 1
        conditions = self.get_proper_filter(page_data).conditions
        sort_filter_type = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id
        params.update({
            'mode': 'async',
            'action': 'get_block',
            'from': str(page_number).zfill(2)
        })
        if self.get_proper_filter(page_data).filters.sort_order[sort_filter_type].value is not None:
            params.update(parse_qs(self.get_proper_filter(page_data).filters.sort_order[sort_filter_type].value))

        if split_url[-2].isdigit():
            split_url.pop(-2)
        if page_number > 1:
            split_url.insert(-1, str(page_number))

        if true_object.object_type == PornCategories.CATEGORY_MAIN:
            params['block_id'] = ['list_categories_categories_list']
            params.pop('from')
        elif true_object.object_type == PornCategories.TAG_MAIN:
            params = None
            page_request = self.session.post(fetch_base_url, headers=headers, data=params)
            return page_request
        elif true_object.object_type == PornCategories.PORN_STAR_MAIN:
            params['block_id'] = ['list_models_sphinx_models_list']
        elif true_object.object_type == PornCategories.CHANNEL_MAIN:
            params['block_id'] = ['list_content_sources2_sponsors_list']
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            params['block_id'] = ['list_videos_videos_list_search_result']
            params.pop('from')
            params['from_videos'] = str(page_number).zfill(2)
        elif true_object.object_type in (PornCategories.CATEGORY, PornCategories.TAG):
            params['block_id'] = ['sphinx_list_cat_videos_videos_list']
            params['category'] = split_url[4]
        else:
            params['block_id'] = ['list_videos2_common_videos_list']

        if page_filter.period.value is not None and sort_filter_type in conditions.period.sort_order:
            params['sort_by'][0] += ('_' + page_filter.period.value)
        if page_filter.quality.value is not None:
            params.update(parse_qs(page_filter.quality.value))
        if page_filter.length.value is not None:
            params.update(parse_qs(page_filter.length.value))

        program_fetch_url = '/'.join(split_url)
        page_request = self.session.post(program_fetch_url, headers=headers, data=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote(query))


class HDZog(UPornia):
    number_of_flip_images = 15

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://hdzog.com/categories/',
            PornCategories.CHANNEL_MAIN: 'https://hdzog.com/channels/',
            PornCategories.PORN_STAR_MAIN: 'https://hdzog.com/models/',
            PornCategories.LONGEST_VIDEO: 'https://hdzog.com/longest/',
            PornCategories.LATEST_VIDEO: 'https://hdzog.com/new/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://hdzog.com/popular/',
            PornCategories.SEARCH_MAIN: 'https://hdzog.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://hdzog.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        _, video_filters, search_filter, categories_filters, porn_stars_filters, channels_filters = \
            self._prepare_filters()

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=categories_filters,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filter,
                                         )

    def _prepare_filters(self):
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Latest', 'sortby=post_date'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'sortby=video_viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'sortby=rating'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'sortby=duration'),
                                        (PornFilterTypes.CommentsOrder, 'Most Commented', 'sortby=most_commented'),
                                        (PornFilterTypes.FavorOrder, 'Most Favorite', 'sortby=most_favourited'),
                                        ),
                         'period_filters': (((PornFilterTypes.AllDate, 'All time', None),
                                             (PornFilterTypes.TwoDate, 'Week', 'week'),
                                             (PornFilterTypes.OneDate, 'Month', 'month'),
                                             (PornFilterTypes.ThreeDate, 'Today', 'day'),
                                             ),
                                            (('sort_order', [PornFilterTypes.ViewsOrder,
                                                             PornFilterTypes.RatingOrder]),
                                             ),
                                            ),
                         'length_filters': ((PornFilterTypes.AllLength, 'Any duration', None),
                                            (PornFilterTypes.OneLength, '0-8 min', 'duration_from=&duration_to=480'),
                                            (PornFilterTypes.TwoLength, '10-40 min.',
                                             'duration_from=481&duration_to=1200'),
                                            (PornFilterTypes.ThreeLength, '40+ min.',
                                             'duration_from=1200&duration_to=1201'),
                                            ),
                         }
        categories_filters = \
            {'sort_order': ((PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sortby=title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Video Count', 'sortby=total_videos'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'sortby=avg_videos_rating'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'sortby=avg_videos_popularity'),
                            ),
             }
        porn_stars_filters = \
            {'sort_order': ((PornFilterTypes.RatingOrder, 'Model Rating', 'sortby=rating'),
                            (PornFilterTypes.ViewsOrder, 'Model Viewed', 'sortby=model_viewed'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Total Videos', 'sortby=total_videos'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sortby=title'),
                            (PornFilterTypes.DateOrder, 'Date Added', 'sortby=added_date'),
                            (PornFilterTypes.CommentsOrder, 'Most Comments', 'sortby=comments_count'),
                            (PornFilterTypes.SubscribersOrder, 'Most Subscribers', 'sortby=subscribers_count'),
                            ),
             }
        channels_filters = \
            {'sort_order': ((PornFilterTypes.VideosRatingOrder, 'Top Rated', 'sortby=avg_videos_rating'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Video Count', 'sortby=total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'sortby=avg_videos_popularity'),
                            (PornFilterTypes.ChannelViewsOrder, 'Recently Updated', 'sortby=cs_viewed'),
                            (PornFilterTypes.DateOrder, 'Recently Updated', 'sortby=last_content_date'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sortby=title'),
                            ),
             }
        return None, video_filters, video_filters, categories_filters, porn_stars_filters, channels_filters

    def __init__(self, source_name='HDZog', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HDZog, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                    session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, './/div[@class="thumbs-categories"]/ul/li/a',
                                                  PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channels.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(channel_data, './/div[@class="thumbs-channels"]/ul/li/a',
                                                  PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data, './/div[@class="thumbs-models"]/ul/li/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_base_object(self, object_data, xpath, object_type):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="thumb"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="thumb"]/span[@class="videos-count"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            country = category.xpath('./div[@class="thumb"]/span[@class="country"]/i')
            additional_info = {'country': re.findall(r'(?:flag-)(\w*$)',
                                                     country[0].attrib['class'])[0]} if len(country) == 1 else None

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               additional_data=additional_info,
                                               object_type=object_type,
                                               super_object=object_data,
                                               ))

        object_data.add_sub_objects(res)
        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        return max(pages) if len(pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(self._clear_text(x.text)) for x in tree.xpath('.//div[@class="pagination"]/ul/li/*')
                if x.text is not None and self._clear_text(x.text).isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        if (
                page_data.page_number is not None and page_data.page_number != 1 and
                page_data.super_object.object_type in (PornCategories.PORN_STAR, PornCategories.CHANNEL,)
        ):
            tree = self.parser.parse(tree.xpath('.//script[2]')[0].text)

        video_preview_url = dict(
            re.findall(r'(?:\[)(\d+)(?:\])(?:.*?)(https://cdn\d+.ahacdn.me/c\d+/videos)', page_request.text))
        videos = tree.xpath('.//div[@class="thumbs-videos"]/ul/li/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./div[@class="thumb thumb-paged"]/img')
            assert len(image_data) == 1
            video_id = image_data[0].attrib['data-video-id']
            image = image_data[0].attrib['src']
            flix_image = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                          for d in range(1, self.number_of_flip_images + 1)]
            video_source = image_data[0].attrib['data-sgid'].split(':')[-1]
            preview_link = (video_preview_url[video_source] +
                            '/{vid_prefix}/{vid}/{vid}_tr.mp4'
                            ''.format(vid_prefix=video_id[:-3]+'000', vid=video_id)) \
                if video_source in video_preview_url else None
            additional_info = {'video_id': video_id}

            video_length = video_tree_data.xpath('./div[@class="thumb thumb-paged"]/span[@class="time"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            rating = video_tree_data.xpath('./div[@class="thumb thumb-paged"]/span[@class="rating rating-gray"]')
            rating = rating[0].text if len(rating) == 1 else None

            added_before = video_tree_data.xpath('./div[@class="thumb-data"]/span[@class="added"]')
            assert len(added_before) == 1
            added_before = added_before[0].text

            title = video_tree_data.xpath('./div[@class="thumb-data"]/span[@class="title"]')
            assert len(title) == 1
            title = title[0].text if title[0].text is not None else ''

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  preview_video_link=preview_link,
                                                  additional_data=additional_info,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  added_before=added_before,
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
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if true_object.object_type == PornCategories.VIDEO:
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request

        if page_number is not None and page_number != 1:
            if true_object.object_type in (PornCategories.PORN_STAR, PornCategories.CHANNEL,):
                params['mode'] = 'async'
                params['mode2'] = 'najax'
                params['action'] = 'get_block'
                params['from'] = page_number
                if page_data.super_object.object_type == PornCategories.PORN_STAR:
                    params['block_id'] = 'list_videos_model_videos'
                elif page_data.super_object.object_type == PornCategories.CHANNEL:
                    params['block_id'] = 'list_videos_channel_videos'
                return self.session.get(fetch_base_url, headers=headers, params=params)

            else:
                if split_url[-2].isdigit():
                    split_url.pop(-2)
                split_url.insert(-1, str(page_number))

        conditions = self.get_proper_filter(page_data).conditions
        sort_filter_type = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id
        params.update(parse_qs(self.get_proper_filter(page_data).filters.sort_order[sort_filter_type].value))

        if page_filter.period.value is not None and sort_filter_type in conditions.period.sort_order:
            params['sortby'][0] += ('_' + page_filter.period.value)
        if page_filter.length.value is not None:
            params.update(parse_qs(page_filter.length.value))

        program_fetch_url = '/'.join(split_url)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote(query))


class HotMovs(UPornia):
    number_of_flip_images = 15

    @property
    def object_urls(self):
        res = super(HotMovs, self).object_urls
        res[PornCategories.TAG_MAIN] = urljoin(self.base_url, '/categories/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://hotmovs.com/'

    def _prepare_filters(self):
        _, video_filters, video_filters, categories_filters, porn_stars_filters, channels_filters = \
            super(HotMovs, self)._prepare_filters()
        general_filters = {'general_filters': ((PornFilterTypes.StraightType, 'Heterosexual', '66'),
                                               (PornFilterTypes.GayType, 'Gay', '67'),
                                               (PornFilterTypes.ShemaleType, 'Transgender', '68'),
                                               ),
                           }
        return general_filters, video_filters, video_filters, categories_filters, porn_stars_filters, channels_filters

    def __init__(self, source_name='HotMovs', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HotMovs, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(self._clear_text(x.text).replace(' ', ''))
                for x in tree.xpath('.//ul[@class="pagination pagination-lg"]/li/*')
                if x.text is not None and self._clear_text(x.text).replace(' ', '').isdigit()]

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        links = tree.xpath('.//ul[@class="list-categories list-group list-group--minimalism"]//'
                           'li[@class="list-group-item"]/a/@href')
        titles = tree.xpath('.//ul[@class="list-categories list-group list-group--minimalism"]//'
                            'li[@class="list-group-item"]/a/text()')
        number_of_videos = [int(x.text.replace(',', ''))
                            for x in tree.xpath('.//ul[@class="list-categories list-group list-group--minimalism"]//'
                                                'li[@class="list-group-item"]//'
                                                'span[@class="list-group-item__action__count"]')]
        assert len(titles) == len(links)
        assert len(titles) == len(number_of_videos)

        return links, titles, number_of_videos

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        video_preview_url = dict(
            re.findall(r'(?:\[)(\d+)(?:\])(?:.*?)(https://cdn\d+.ahacdn.me/c\d+/videos)', page_request.text))
        videos = (tree.xpath('.//div[@id="list_videos2_common_videos_list_items"]/article/a') +
                  tree.xpath('.//div[@id="sphinx_list_cat_videos_videos_list_items"]/article/a') +
                  tree.xpath('.//div[@id="list_videos_videos_list_search_result_items"]/article/a'))
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            video_id = video_tree_data.xpath('./div[@class="thumbnail__label thumbnail__label--watch-later"]')
            assert len(video_id) == 1
            video_id = video_id[0].attrib['data-video-id']

            image_data = video_tree_data.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            flix_image = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                          for d in range(1, self.number_of_flip_images + 1)]
            video_source = image_data[0].attrib['data-custom3'].split(':')[-1]
            preview_link = (video_preview_url[video_source] +
                            '/{vid_prefix}/{vid}/{vid}_tr.mp4'
                            ''.format(vid_prefix=video_id[:-3]+'000', vid=video_id)) \
                if video_source in video_preview_url else None
            additional_info = {'video_id': video_id}

            video_length = video_tree_data.xpath('./div[@class="thumbnail__info"]/'
                                                 'div[@class="thumbnail__info__right"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            title = video_tree_data.xpath('./div[@class="thumbnail__info"]/div[@class="thumbnail__info__left"]/h5')
            assert len(title) == 1
            title = title[0].text

            rating = (video_tree_data.xpath('./div[@class="thumbnail__info__left"]/i'))
            rating = rating[0].tail if len(rating) == 1 else None

            number_of_views = (video_tree_data.xpath('./div[@class="thumbnail__info thumbnail__info--hover"]/'
                                                     'div[@class="thumbnail__info__right"]/i'))
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].tail)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  preview_video_link=preview_link,
                                                  additional_data=additional_info,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  number_of_views=number_of_views,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res


class VoyeurHit(UPornia):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://voyeurhit.com/categories/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://voyeurhit.com/most-popular/',
            PornCategories.TOP_RATED_VIDEO: 'https://voyeurhit.com/top-rated/',
            PornCategories.LATEST_VIDEO: 'https://voyeurhit.com/latest-updates/',
            PornCategories.LONGEST_VIDEO: 'https://voyeurhit.com/longest/',
            PornCategories.SEARCH_MAIN: 'https://voyeurhit.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://voyeurhit.com/'

    def _set_video_filter(self):
        return super(Txxx, self)._set_video_filter()

    def __init__(self, source_name='VoyeurHit', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(VoyeurHit, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="block-thumb"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span[@class="image"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            title_data = category.xpath('./span[@class="item-info"]/span')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos = category.xpath('./span[@class="date"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text.replace(' ', ''))
                for x in (tree.xpath('.//div[@class="pagination"]/ul/li') +
                          tree.xpath('.//div[@class="pagination"]/ul/li/*'))
                if x.text is not None and x.text.replace(' ', '').isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        video_preview_url = dict(
            re.findall(r'(?:\[)(\d+)(?:\])(?:.*?)(https://[\w./-]*/videos)', page_request.text))
        videos = tree.xpath('.//div[@class="list-videos"]div/div/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./div[@class="img"]/img')
            assert len(image_data) == 1
            video_id = image_data[0].attrib['data-video-id'] if 'data-video-id' in image_data[0].attrib else None
            image = image_data[0].attrib['src']
            if video_id is None:
                # We get it from the image link
                video_id = image.split('/')[-3]
            flix_image = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                          for d in range(1, self.number_of_flip_images + 1)]
            video_source = image_data[0].attrib['data-sgid'].split(':')[-1] \
                if 'data-sgid' in image_data[0].attrib else image_data[0].attrib['data-custom3'].split(':')[-1]
            preview_link = (video_preview_url[video_source] +
                            '/{vid_prefix}/{vid}/{vid}_tr.mp4'
                            ''.format(vid_prefix=video_id[:-3]+'000', vid=video_id)) \
                if video_source in video_preview_url else None
            additional_info = {'video_id': video_id}

            title = video_tree_data.xpath('./strong[@class="title"]')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            video_length = video_tree_data.xpath('./div[@class="wrap"]/div[@class="duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            rating = (video_tree_data.xpath('./div[@class="wrap"]/div[@class="rating positive"]') +
                      video_tree_data.xpath('./div[@class="wrap"]/div[@class="rating negative"]'))
            rating = self._clear_text(rating[0].text) if len(rating) == 1 else None

            added_before = (video_tree_data.xpath('./div[@class="wrap"]/div[@class="added"]/em') +
                            video_tree_data.xpath('./div[@class="wrap date-views__wrap"]/div[@class="added"]/em'))
            assert len(added_before) == 1
            added_before = added_before[0].text

            number_of_views = (video_tree_data.xpath('./div[@class="wrap"]/div[@class="views ico ico-eye"]') +
                               video_tree_data.xpath('./div[@class="wrap date-views__wrap"]/'
                                                     'div[@class="views ico ico-eye"]'))
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  preview_video_link=preview_link,
                                                  additional_data=additional_info,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  number_of_views=number_of_views,
                                                  added_before=added_before,
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
        if true_object.object_type in self._default_sort_by:
            split_url = fetch_base_url.split('/')
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3',
                'Cache-Control': 'max-age=0',
                'Referer': self.base_url,
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }
            # if true_object.object_type == PornCategories.VIDEO:
            #     page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            #     return page_request

            if self.general_filter.current_filters.general.value is not None:
                self.session.cookies.set(name='category_group_id',
                                         value=self.general_filter.current_filters.general.value,
                                         domain=urlparse(self.base_url).netloc,
                                         )

            if page_number is None:
                page_number = 1
            if split_url[-2].isdigit():
                split_url.pop(-2)
            if page_number > 1:
                split_url.insert(-1, str(page_number))

            program_fetch_url = '/'.join(split_url)
            page_request = self.session.post(program_fetch_url, headers=headers, data=params)
            return page_request
        else:
            return super(VoyeurHit, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                  page_filter, fetch_base_url)


class TubePornClassic(UPornia):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
        }

    def _prepare_filters(self):
        _, video_filters, video_filters, categories_filters, porn_stars_filters, _ = \
            super(TubePornClassic, self)._prepare_filters()
        video_filters.pop('quality_filters')
        return None, video_filters, video_filters, categories_filters, porn_stars_filters, None

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        _, video_filters, search_filter, categories_filters, porn_stars_filters, _ = \
            self._prepare_filters()

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=categories_filters,
                                         porn_stars_args=porn_stars_filters,
                                         single_porn_star_args=video_filters,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filter,
                                         )

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://tubepornclassic.com/'

    def __init__(self, source_name='TubePornClassic', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(TubePornClassic, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                              session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, './/div[@class="list-categories"]/div/a',
                                                  PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data, './/div[@class="list-models"]/div/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_base_object(self, object_data, xpath, object_type):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            title_data = (category.xpath('./strong[@class="title"]') +
                          category.xpath('./div[@class="item__title clearfix"]/strong[@class="model-name"]'))
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos = category.xpath('./div[@class="wrap"]/div[@class="videos"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            rating = (category.xpath('./div[@class="wrap"]/div[@class="rating positive"]') +
                      category.xpath('./div[@class="wrap"]/div[@class="rating negative"]')
                      )
            assert len(rating) == 1
            rating = self._clear_text(rating[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               rating=rating,
                                               object_type=object_type,
                                               super_object=object_data,
                                               ))

        object_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return ([int(self._clear_text(x.text))
                for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/*')
                if x.text is not None and self._clear_text(x.text).isdigit()] +
                [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0])
                 for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a')
                 if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0])

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        video_preview_url = dict(
            re.findall(r'(?:\[)(\d+)(?:\])(?:.*?)(https://[\w./-]*/videos)', page_request.text))
        videos = tree.xpath('.//div[@class="list-videos"]div/div/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./div[@class="img"]/img')
            assert len(image_data) == 1
            video_id = image_data[0].attrib['data-video-id']
            image = image_data[0].attrib['src']
            flix_image = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                          for d in range(1, self.number_of_flip_images + 1)]
            video_source = image_data[0].attrib['data-sgid'].split(':')[-1]
            preview_link = (video_preview_url[video_source] +
                            '/{vid_prefix}/{vid}/{vid}_tr.mp4'
                            ''.format(vid_prefix=video_id[:-3]+'000', vid=video_id)) \
                if video_source in video_preview_url else None
            additional_info = {'video_id': video_id}

            title = video_tree_data.xpath('./strong[@class="title"]')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            video_length = video_tree_data.xpath('./div[@class="wrap"]/div[@class="duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            rating = (video_tree_data.xpath('./div[@class="wrap"]/div[@class="rating positive"]') +
                      video_tree_data.xpath('./div[@class="wrap"]/div[@class="rating negative"]'))
            rating = self._clear_text(rating[0].text) if len(rating) == 1 else None

            added_before = (video_tree_data.xpath('./div[@class="wrap"]/div[@class="added"]/em') +
                            video_tree_data.xpath('./div[@class="wrap date-views__wrap"]/div[@class="added"]/em'))
            assert len(added_before) == 1
            added_before = added_before[0].text

            number_of_views = (video_tree_data.xpath('./div[@class="wrap"]/div[@class="views ico ico-eye"]') +
                               video_tree_data.xpath('./div[@class="wrap date-views__wrap"]/'
                                                     'div[@class="views ico ico-eye"]'))
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  preview_video_link=preview_link,
                                                  additional_data=additional_info,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  number_of_views=number_of_views,
                                                  added_before=added_before,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw number, i.e. '7m:58s'.
        :return:
        """
        res = 0
        hours = re.findall(r'(\d+)(?:h)', raw_duration)
        if len(hours) > 0:
            res += 3600 * int(hours[0])
        minutes = re.findall(r'(\d+)(?:m)', raw_duration)
        if len(minutes) > 0:
            res += 60 * int(minutes[0])
        seconds = re.findall(r'(\d+)(?:s)', raw_duration)
        if len(seconds) > 0:
            res += int(seconds[0])
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        split_url = fetch_base_url.split('/')
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if true_object.object_type == PornCategories.VIDEO:
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request

        if page_number is None:
            page_number = 1
        conditions = self.get_proper_filter(page_data).conditions
        sort_filter_type = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id
        params.update({
            'mode': 'async',
            'action': 'get_block',
            'from': str(page_number).zfill(2)
        })
        params.update(parse_qs(self.get_proper_filter(page_data).filters.sort_order[sort_filter_type].value))

        if split_url[-2].isdigit():
            split_url.pop(-2)
        if page_number > 1:
            split_url.insert(-1, str(page_number))

        if true_object.object_type == PornCategories.CATEGORY_MAIN:
            params['block_id'] = ['list_categories_categories_list']
            params.pop('from')
        elif true_object.object_type == PornCategories.PORN_STAR_MAIN:
            params['block_id'] = ['list_models2_models_list']
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            params['block_id'] = ['list_videos_videos_list_search_result']
            params.pop('from')
            params['from_videos'] = str(page_number).zfill(2)
        elif true_object.object_type == PornCategories.CATEGORY:
            params['block_id'] = ['list_videos2_videos_list']
        elif true_object.object_type == PornCategories.PORN_STAR:
            params['block_id'] = ['list_videos2_common_videos_list']
        else:
            params['block_id'] = ['list_videos2_common_videos_list']

        if page_filter.period.value is not None and sort_filter_type in conditions.period.sort_order:
            params['sort_by'][0] += ('_' + page_filter.period.value)
        if page_filter.quality.value is not None:
            params.update(parse_qs(page_filter.quality.value))
        if page_filter.length.value is not None:
            params.update(parse_qs(page_filter.length.value))

        program_fetch_url = '/'.join(split_url)
        page_request = self.session.post(program_fetch_url, headers=headers, data=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote(query))


class VJav(TubePornClassic):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://vjav.com/'

    def __init__(self, source_name='VJav', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(VJav, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                   session_id)


class TheGay(TubePornClassic):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://thegay.com/'

    def __init__(self, source_name='TheGay', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(TheGay, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _prepare_filters(self):
        general_filters, video_filters, video_filters, categories_filters, porn_stars_filters, channels_filters = \
            super(TheGay, self)._prepare_filters()
        general_filters = {'general_filters': [(PornFilterTypes.GayType, 'Gay', None),
                                               ],
                           }
        return general_filters, video_filters, video_filters, categories_filters, porn_stars_filters, channels_filters


class Shemalez(UPornia):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://shemalez.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://shemalez.com/models/',
            PornCategories.TOP_RATED_VIDEO: 'https://shemalez.com/top-rated/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://shemalez.com/most-popular/',
            PornCategories.LATEST_VIDEO: 'https://shemalez.com/latest-updates/',
            PornCategories.LONGEST_VIDEO: 'https://shemalez.com/latest-updates/?sort_by=duration',
            PornCategories.MOST_DISCUSSED_VIDEO: 'https://shemalez.com/latest-updates/?sort_by=most_commented',
            PornCategories.FAVORITE_VIDEO: 'https://shemalez.com/latest-updates/?sort_by=most_favourited',
            PornCategories.SEARCH_MAIN: 'https://shemalez.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
            PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://shemalez.com/'

    def _prepare_filters(self):
        _, video_filters, video_filters, categories_filters, porn_stars_filters, _ = \
            super(Shemalez, self)._prepare_filters()
        general_filters = {'general_filters': [(PornFilterTypes.ShemaleType, 'Shemale', None),
                                               ],
                           }
        channels_filters = \
            {'sort_order': ((PornFilterTypes.VideosRatingOrder, 'Top Rated', 'sort_by=avg_videos_rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sort_by=title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'sort_by=total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'sort_by=avg_videos_popularity'),
                            ),
             }
        video_filters['quality_filters'] = ((PornFilterTypes.AllQuality, 'All quality', None),
                                            (PornFilterTypes.HDQuality, 'HD quality', 'is_hd=1'),
                                            )
        search_filters = {'length_filters': video_filters['length_filters']}
        return general_filters, video_filters, search_filters, categories_filters, porn_stars_filters, channels_filters

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        _, video_filters, search_filter, categories_filters, porn_stars_filters, channels_filters = \
            self._prepare_filters()

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=categories_filters,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filter,
                                         )

    def __init__(self, source_name='Shemalez', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Shemalez, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@id="list_categories_list"]//'
                                                  'div[@class="thumb-category"]',
                                                  PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@id="list_models_list_items"]//'
                                                  'div[@class="thumb-model"]',
                                                  PornCategories.PORN_STAR)

    def _update_available_base_object(self, object_data, xpath, object_type):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            rating = category.xpath('./span[@class="thumb__rating rating"]/i')
            rating = self._clear_text(rating[0].tail) if len(rating) == 1 else None

            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = category.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = (category.xpath('./span[@class="thumb__amount amount"]/i') +
                                category.xpath('./a/span[@class="thumb__amount amount"]/i') +
                                category.xpath('./span[@class="thumb__amount"]/i') +
                                category.xpath('./a/span[@class="thumb__amount"]/i'))
            assert len(number_of_videos) == 1
            number_of_videos = int(''.join(re.findall(r'\d+', number_of_videos[0].tail)))

            number_of_views = category.xpath('./div[@class="thumb__info"]/div[@class="thumb__row"]/'
                                             'span[@class="thumb__view"]/i')
            number_of_views = int(''.join(re.findall(r'\d+', number_of_views[0].tail))) \
                if len(number_of_views) == 1 else None

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               number_of_views=number_of_views,
                                               rating=rating,
                                               object_type=object_type,
                                               super_object=object_data,
                                               ))

        object_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(self._clear_text(x.text).replace(' ', ''))
                for x in tree.xpath('.//ul[@class="pagination__list"]/li/*')
                if x.text is not None and self._clear_text(x.text).replace(' ', '').isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        video_preview_url = dict(
            re.findall(r'(?:\[)(\d+)(?:\])(?:.*?)(https://[\w./-]*/videos)', page_request.text))
        videos = (tree.xpath('.//div[@id="list_videos_list_items"]/div[@class="thumb"]') +
                  tree.xpath('.//div[@id="list_videos_videos_items"]/div[@class="thumb"]'))
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a[@class="thumb__link"]')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            video_id = image_data[0].attrib['data-video-id']
            image = image_data[0].attrib['src']
            flix_image = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                          for d in range(1, self.number_of_flip_images + 1)]
            video_source = image_data[0].attrib['data-sgid'].split(':')[-1]
            preview_link = (video_preview_url[video_source] +
                            '/{vid_prefix}/{vid}/{vid}_tr.mp4'
                            ''.format(vid_prefix=video_id[:-3]+'000', vid=video_id)) \
                if video_source in video_preview_url else None
            additional_info = {'video_id': video_id}

            video_length = video_tree_data.xpath('./a/span[@class="thumb__duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            title = video_tree_data.xpath('./div[@class="thumb__info"]/a')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            rating = video_tree_data.xpath('./div[@class="thumb__info"]//div[@class="thumb__row"]/'
                                           'span[@class="thumb__rating"]/i')
            rating = self._clear_text(rating[0].tail) if len(rating) == 1 else None

            number_of_views = video_tree_data.xpath('./div[@class="thumb__info"]//div[@class="thumb__row"]/'
                                                    'span[@class="thumb__view"]/i')
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].tail)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  preview_video_link=preview_link,
                                                  additional_data=additional_info,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  number_of_views=number_of_views,
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
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if true_object.object_type == PornCategories.VIDEO:
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request

        # if self.general_filter.current_filters.general.value is not None:
        #     self.session.cookies.set(name='category_group_id',
        #                              value=self.general_filter.current_filters.general.value,
        #                              domain=urlparse(self.base_url).netloc,
        #                              )

        if page_number is None:
            page_number = 1
        conditions = self.get_proper_filter(page_data).conditions
        sort_filter_type = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id
        params.update(parse_qs(self.get_proper_filter(page_data).filters.sort_order[sort_filter_type].value))

        if split_url[-2].isdigit():
            split_url.pop(-2)
        if page_number > 1:
            split_url.insert(-1, str(page_number))

        if true_object.object_type in (PornCategories.CATEGORY, PornCategories.PORN_STAR,
                                       PornCategories.CHANNEL, PornCategories.SEARCH_MAIN):
            params.update({
                'mode': 'async',
                'action': 'get_block',
                'from': str(page_number).zfill(2)
            })

            if true_object.object_type == PornCategories.SEARCH_MAIN:
                params['block_id'] = ['list_videos_list']
                params.pop('from')
                params['from_videos'] = str(page_number).zfill(2)
            elif true_object.object_type == PornCategories.CATEGORY:
                params['block_id'] = ['list_videos_list']
                params['category'] = split_url[4]
            elif true_object.object_type == PornCategories.CHANNEL:
                params['block_id'] = ['list_videos_videos']
                params['cs'] = split_url[4]
            elif true_object.object_type == PornCategories.PORN_STAR:
                params['block_id'] = ['list_videos_videos']
                params['model'] = split_url[4]

        if page_filter.period.value is not None and sort_filter_type in conditions.period.sort_order:
            params['sort_by'][0] += ('_' + page_filter.period.value)
        if page_filter.quality.value is not None:
            params.update(parse_qs(page_filter.quality.value))
        if page_filter.length.value is not None:
            params.update(parse_qs(page_filter.length.value))

        program_fetch_url = '/'.join(split_url)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request


if __name__ == '__main__':
    # cat_id = IdGenerator.make_id('/categories/arab/?sort_by=rating_month')
    cat_id = IdGenerator.make_id('/categories/czech/?sort_by=rating_month')
    # module = Txxx()
    # module = HClips()
    # module = UPornia()
    # module = HDZog()
    # module = HotMovs()
    # module = VoyeurHit()
    module = TubePornClassic()
    # module = VJav()
    # module = TheGay()
    # module = Shemalez()
    # module.get_available_categories()
    # module.download_object(None, cat_id, verbose=1)
    module.download_category_input_from_user(use_web_server=False)
