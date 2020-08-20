# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher, PornValueError

# Internet tools
from .... import urljoin, quote

# Regex
import re

# Math
import math

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


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
            return int(math.ceil(number_of_videos / self.number_of_channels_per_page))
        elif category_data.object_type in (PornCategories.PORN_STAR_MAIN, ):
            return int(math.ceil(number_of_videos / self.number_of_porn_stars_per_page))
        else:
            return min(int(math.ceil(number_of_videos / self.number_of_videos_per_page)), self._max_pages)

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
            raw_video_url = re.sub(r'[^\u0410\u0412\u0421\u0415\u041CA-Za-z0-9.,~]', '', raw_video_url)

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

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Txxx, self)._version_stack + [self.__version]
