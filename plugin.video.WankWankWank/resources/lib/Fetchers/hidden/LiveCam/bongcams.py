# -*- coding: UTF-8 -*-
from ...fetchers.porn_fetcher import PornFetcher

# Internet tools
from ... import urljoin, quote_plus

# from requests import cookies

# Regex
import re

# Nodes
from ...catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, \
    VideoSource, VideoTypes
from ...catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# # json
# import json

# m3u8
import m3u8

# Math
import math

# Generator id
from ...id_generator import IdGenerator


class BongCams(PornFetcher):
    number_of_videos_per_page = 18
    page_request_json_url = 'https://en.bongacams.com/tools/listing_v3.php'
    video_request_json_url = 'https://en.bongacams.com/tools/amf.php'
    playlist_template = 'https:{srv}/hls/stream_{usr}/playlist.m3u8'

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://en.bongacams.com/',
            PornCategories.PORN_STAR_MAIN: 'https://en.bongacams.com/all-models',
            PornCategories.MOST_VIEWED_VIDEO: 'https://en.bongacams.com/',
            PornCategories.TOP_RATED_VIDEO: 'https://en.bongacams.com/',
            PornCategories.FAVORITE_VIDEO: 'https://en.bongacams.com/',
            PornCategories.JUST_LOGGED_IN_VIDEO: 'https://en.bongacams.com/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
            PornCategories.JUST_LOGGED_IN_VIDEO: PornFilterTypes.LoginOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': ((PornFilterTypes.GirlType, 'Females', 'female'),
                                                     (PornFilterTypes.CoupleType, 'Couples', 'couples'),
                                                     (PornFilterTypes.GuyType, 'Guy', 'male'),
                                                     (PornFilterTypes.ShemaleType, 'Transsexual', 'transsexual'),
                                                     (PornFilterTypes.NewType, 'Transsexual', 'transsexual'),
                                                     ),
                                 }
        video_params = {'sort_order': ((PornFilterTypes.DateOrder, 'Recent videos', 'most-recent'),
                                       (PornFilterTypes.LengthOrder, 'By duration', 'long-movies'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                       # (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                       (PornFilterTypes.QualityOrder, 'High definition', 'high-definition'),
                                       (PornFilterTypes.FavorOrder, 'Most favorite', 'mostfavorites'),
                                       ),
                        }
        search_params = {'sort_order': ((PornFilterTypes.RelevanceOrder, 'Most relevant', None),
                                        (PornFilterTypes.DateOrder, 'Most recent', 'most-recent'),
                                        (PornFilterTypes.LengthOrder, 'By duration', 'long-movies'),
                                        (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                        ),
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         video_args=video_params,
                                         search_args=search_params,
                                         )

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://en.bongacams.com/'

    def __init__(self, source_name='BongCams', source_id=0, store_dir='.', data_dir='../../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(BongCams, self).__init__(source_name, source_id, store_dir, data_dir, source_type,
                                       use_web_server, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//ul[@class="hbd_list js-spa_categories"]/li/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            title = self._clear_text(category.text)
            number_of_videos = category.xpath('./span[@class="hbd_s_live"]/text()')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0])[0])
            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        # js = json.loads(tree.xpath('.//script[@id="listingConfiguration"]/text()')[0])
        # res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
        #                                obj_id=x['code'],
        #                                url=urljoin(self.base_url, '/{c}'.format(c=x['code'])),
        #                                title=x['title'],
        #                                object_type=Category,
        #                                super_object=category_data,
        #                                ) for x in js['initData']['tagTitles']]
        #

        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        raw_data = page_request.json()
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x['username'],
                                       url=urljoin(self.base_url, x['username']),
                                       title=x['username'] + ' - ' + x['topic'],
                                       number_of_views=x['viewers'],
                                       raw_data=x,
                                       object_type=PornCategories.CATEGORY,
                                       super_object=porn_star_data,
                                       ) for x in raw_data['models']]

        porn_star_data.add_sub_objects(res)
        return res

    def _check_is_available_page(self, page_object, page_request=None):
        """
        In binary search performs test whether the current page is available.
        :param page_object: Page object.
        :param page_request: Page request.
        :return:
        """
        if page_object.true_object.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.VIDEO):
            return super(BongCams, self)._check_is_available_page(page_object, page_request)
        if page_request is None:
            page_request = self.get_object_request(page_object)
        raw_json = page_request.json()
        return raw_json['status'] == 'success'

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
        """
        params = [('method', ['getRoomData']), ('args[]', [video_data.raw_data['username'], 'false'])]
        page_request = self.get_object_request(video_data, override_params=params)
        raw_data = page_request.json()
        playlist_url = self.playlist_template.format(srv=raw_data['localData']['videoServerUrl'],
                                                     usr=raw_data['performerData']['username'])

        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            # 'Referer': video_data.url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': self.user_agent,
        }
        req = self.session.get(playlist_url, headers=headers)
        video_m3u8 = m3u8.loads(req.text)
        video_playlists = video_m3u8.playlists
        videos = sorted((VideoSource(link=urljoin(playlist_url, x.uri),
                                     video_type=VideoTypes.VIDEO_SEGMENTS,
                                     quality=x.stream_info.bandwidth,
                                     resolution=x.stream_info.resolution[1],
                                     codec=x.stream_info.codecs)
                         for x in video_playlists),
                        key=lambda x: x.quality, reverse=True)

        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1

        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        raw_data = page_request.json()

        return int(math.ceil(raw_data['online_count'] / self.number_of_videos_per_page))

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        videos = page_request.json()
        res = [PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                        obj_id=x['chat_url'],
                                        url=urljoin(self.base_url, x['chat_url']),
                                        title=x['display_name'],
                                        image_link=x['thumb_image'],
                                        number_of_views=x['viewers'],
                                        raw_data=x,
                                        object_type=PornCategories.VIDEO,
                                        super_object=page_data,
                                        ) for x in videos['models']]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        if page_data.super_object.object_type == PornCategories.CATEGORY_MAIN:
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
            page_request = self.session.get(page_data.url, headers=headers, params=params)
            return page_request
        elif page_data.super_object.object_type == PornCategories.VIDEO:
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                'Host': self.host_name,
                'Referer': page_data.url,
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
            page_request = self.session.post(page_data.url, headers=headers, data=params)
            return page_request

        # Here we are preparing the true request
        if page_data.super_object.object_type == PornCategories.PORN_STAR_MAIN:
            params['model_search[base_sort]'] = ['popular']
            raw_cookie = '{{"sorting":"camscore","th_type":"live","limit":{npp}}}' \
                         ''.format(npp=self.number_of_videos_per_page)
        elif page_data.super_object.object_type == PornCategories.TOP_RATED_VIDEO:
            raw_cookie = '{{"sorting":"camscore","th_type":"live","limit":{npp},"c_limit":12}}' \
                         ''.format(npp=self.number_of_videos_per_page)
        elif page_data.super_object.object_type == PornCategories.MOST_VIEWED_VIDEO:
            raw_cookie = '{{"sorting":"popular","th_type":"live","limit":{npp},"c_limit":12}}' \
                         ''.format(npp=self.number_of_videos_per_page)
        elif page_data.super_object.object_type == PornCategories.FAVORITE_VIDEO:
            raw_cookie = '{{"sorting":"lovers","th_type":"live","limit":{npp},"c_limit":12}}' \
                         ''.format(npp=self.number_of_videos_per_page)
        elif page_data.super_object.object_type == PornCategories.JUST_LOGGED_IN_VIDEO:
            raw_cookie = '{{"sorting":"logged","th_type":"live","limit":{npp},"c_limit":12}}' \
                         ''.format(npp=self.number_of_videos_per_page)
        elif page_data.super_object.object_type == PornCategories.NEW_MODEL_VIDEO:
            raw_cookie = '{{"sorting":"new","th_type":"live","limit":{npp},"c_limit":12}}' \
                         ''.format(npp=self.number_of_videos_per_page)
        elif page_data.super_object.object_type == PornCategories.GENERAL_MAIN:
            # Regular request
            raw_cookie = '{{"sorting":"popular","th_type":"live","limit":{npp},"c_limit":12}}' \
                         ''.format(npp=self.number_of_videos_per_page)
        else:
            raise RuntimeError('Unknown object type {ot}'.format(ot=page_data.super_object.object_type))

        # new_cookie = cookies.create_cookie(name='ls01',
        #                                    value=quote_plus(raw_cookie),
        #                                    domain='.bongacams.com'
        #                                    )
        self.session.cookies.set(name='ls01', value=quote_plus(raw_cookie), domain='.bongacams.com')
        self.session.cookies.set(name='warning18', value=quote_plus('["en_GB"]'), domain='.bongacams.com')
        self.session.cookies.set(name='reg_ver2', value='3', domain='.bongacams.com')
        self.session.cookies.set(name='ts_type2', value='1', domain='.bongacams.com')
        # self.session.cookies.set(name='bonga20120608', value='e77cd0f91bb0e9453742957b5f7a11af',
        #                          domain='.bongacams.com')
        # self.session.cookies.set(name='sg', value=695, domain='.bongacams.com')

        params['offset'] = [self.number_of_videos_per_page * (page_number - 1)]
        params['livetab'] = [self.general_filter.current_filters.general.value]
        params['online_only'] = ['true']

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        page_request = self.session.get(self.page_request_json_url, headers=headers, params=params)
        return page_request


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    module = BongCams()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=False)
