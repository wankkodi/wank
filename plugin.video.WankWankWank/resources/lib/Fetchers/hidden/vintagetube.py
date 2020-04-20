# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urlparse, quote, quote_plus

# Regex
import re

# Math
import math

# Warnings
import warnings

# External fetchers
from ..tools.external_fetchers import ExternalFetcher

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# Generator id
from ..id_generator import IdGenerator


class VintageTube(PornFetcher):
    # todo: fix search
    porn_stars_api_url = 'https://api.vintagetube.xxx/api/v1/models'
    porn_star_api_url_template = 'https://api.vintagetube.xxx/api/v1/models/{ps}'
    search_api_url_template = 'https://api.vintagetube.xxx/api/v1/search'
    categories_api_url = 'https://api.vintagetube.xxx/api/v1/categories'
    category_api_template = 'https://api.vintagetube.xxx/api/v1/categories/{cat}'
    videos_api_url = 'https://api.vintagetube.xxx/api/v1/videos'
    video_api_url_template = 'https://api.vintagetube.xxx/api/v1/videos/{vid}'

    items_per_page = 100
    max_flip_images = 35

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://vintagetube.xxx/categories',
            PornCategories.PORN_STAR_MAIN: 'https://vintagetube.xxx/models',
            PornCategories.LATEST_VIDEO: 'https://vintagetube.xxx/latest',
            PornCategories.MOST_VIEWED_VIDEO: 'https://vintagetube.xxx/most-viewed',
            PornCategories.TOP_RATED_VIDEO: 'https://vintagetube.xxx/top-rated',
            PornCategories.SEARCH_MAIN: 'https://vintagetube.xxx/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://vintagetube.xxx/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Latest', 'latest'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        ),
                         'period_filters': ([(PornFilterTypes.AllAddedBefore, 'All time', 'all-time'),
                                             (PornFilterTypes.OneAddedBefore, 'Today', 'today'),
                                             (PornFilterTypes.TwoAddedBefore, 'This week', 'this-week'),
                                             (PornFilterTypes.ThreeAddedBefore, 'This month', 'this-month'),
                                             ],
                                            [('sort_order', [PornFilterTypes.RatingOrder,
                                                             PornFilterTypes.ViewsOrder])]
                                            ),
                         }
        search_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Latest', 'latest'),
                                         (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                         (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                         ),
                          }
        porn_stars_filters = \
            {'sort_order': ((PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Viewed', 'most-viewed'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'abc'),
                            ),
             }
        category_filters = \
            {'sort_order': ((PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'most-videos'),
                            (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'abc'),
                            ),
             }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filters,
                                         categories_args=category_filters,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='VintageTube', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(VintageTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                          session_id)
        self.external_fetchers = ExternalFetcher(session=self.session, user_agent=self.user_agent,
                                                 parser=self.parser)
        self.host_name = urlparse(self.porn_stars_api_url).hostname

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        raw_data = page_request.json()
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x['id'],
                                       url=self.category_api_template.format(cat=x['slug']),
                                       title=x['title'],
                                       image_link=x['thumb'],
                                       number_of_videos=x['videos'],
                                       rating=x['rating'],
                                       raw_data=x,
                                       object_type=PornCategories.CATEGORY,
                                       super_object=category_data,
                                       ) for x in raw_data['data']]
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
                                       obj_id=x['id'],
                                       url=self.category_api_template.format(cat=x['slug']),
                                       title=x['title'],
                                       image_link=x['thumb'],
                                       number_of_videos=x['videos'],
                                       number_of_views=x['viewed'],
                                       raw_data=x,
                                       object_type=PornCategories.PORN_STAR,
                                       super_object=porn_star_data,
                                       ) for x in raw_data['data']]
        porn_star_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        page_request = self.get_object_request(video_data)
        raw_data = page_request.json()
        videos = []
        if 'files' in raw_data:
            videos.extend((VideoSource(link=x['link'], resolution=x['w']) for x in raw_data['files'].values()))
        if 'embed' in raw_data:
            tree = self.parser.parse(raw_data['embed'])
            sources = [x.attrib['src'] for x in tree.xpath('.//script') if 'src' in x.attrib]
            for source in sources:
                if urlparse(source).hostname == 'pt.protoawe.com':
                    res = self.external_fetchers.get_video_link_from_protoawe(source)
                    videos.append(VideoSource(link=res[0][0], resolution=res[0][1]))
                else:
                    warnings.warn('Unknown source {s}'.format(s=urlparse(source).hostname))

        videos.sort(key=lambda x: x.resolution, reverse=True)

        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.number_of_videos is not None:
            return math.ceil(category_data.number_of_videos / self.items_per_page)
        page_request = self._get_object_request_no_exception_check(category_data) if fetched_request is None \
            else fetched_request
        if not self._check_is_available_page(category_data, page_request):
            return 1
        tree = page_request.json()
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, json_data):
        """
        In binary looks for the available pages from current page tree.
        :param json_data: Current page json data.
        :return: List of available trees
        """
        return [math.ceil(json_data['total'] / self.items_per_page)]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        raw_data = page_request.json()
        if page_data.super_object.object_type in (PornCategories.CATEGORY, PornCategories.PORN_STAR):
            data = raw_data['videos']['data']
        else:
            data = raw_data['data']
        res = [PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                        obj_id=x['id'],
                                        url=x['link'],
                                        title=x['title'],
                                        image_link=x['thumb'],
                                        flip_images_link=[re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), x['thumb'])
                                                          for i in range(1, self.max_flip_images + 1)],
                                        preview_video_link=x['vthumb']['link'] if x['vthumb'] is not None else None,
                                        added_before=x['post_date'],
                                        duration=x['duration'],
                                        raw_data=x,
                                        object_type=PornCategories.VIDEO,
                                        super_object=page_data,
                                        ) for x in data]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        split_url = fetch_base_url.split('/')
        page_number = page_number if page_number is not None else 1
        params = {'offset': (page_number - 1) * 100, 'c': self.items_per_page}
        if true_object.object_type == PornCategories.CATEGORY_MAIN:
            params['sort'] = page_filter.sort_order.value,
            params['min_videos'] = 50
            program_fetch_url = self.categories_api_url
        elif true_object.object_type == PornCategories.CATEGORY:
            params['sort'] = page_filter.sort_order.value,
            program_fetch_url = \
                self.category_api_template.format(cat=split_url[-1] if split_url[-1] != '' else split_url[-2])
        elif true_object.object_type == PornCategories.PORN_STAR_MAIN:
            params['sort'] = page_filter.sort_order.value,
            params['min_videos'] = 50
            program_fetch_url = self.porn_stars_api_url
        elif true_object.object_type == PornCategories.PORN_STAR:
            # params['sort'] = page_filter.sort_order.value,
            program_fetch_url = \
                self.porn_star_api_url_template.format(ps=split_url[-1] if split_url[-1] != '' else split_url[-2])
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            params['sort'] = page_filter.sort_order.value,
            params['query'] = quote_plus(split_url[-1]),
            params['from'] = params.pop('offset'),
            params['size'] = params.pop('c'),
            program_fetch_url = self.search_api_url_template
        elif true_object.object_type in self._default_sort_by:
            conditions = self.get_proper_filter(page_data).conditions
            true_sort_filter_id = self._default_sort_by[true_object.object_type] \
                if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id
            params['sort'] = self.get_proper_filter(page_data).filters.sort_order[true_sort_filter_id].value,
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['tf'] = page_filter.period.value
            program_fetch_url = self.videos_api_url
        # elif true_object.object_type == PornCategories.LATEST_VIDEO:
        #     params['sort'] = 'latest',
        #     params['tf'] = 'all-time'
        #     program_fetch_url = self.videos_api_url
        # elif true_object.object_type == PornCategories.TOP_RATED_VIDEO:
        #     params['sort'] = 'top-rated',
        #     params['tf'] = 'all-time'
        #     program_fetch_url = self.videos_api_url
        # elif true_object.object_type == PornCategories.MOST_VIEWED_VIDEO:
        #     params['sort'] = 'most-viewed',
        #     params['tf'] = 'all-time'
        #     program_fetch_url = self.videos_api_url
        elif true_object.object_type == PornCategories.VIDEO:
            # We override params!
            params = None
            program_fetch_url = self.video_api_url_template.format(vid=page_data.raw_data['id'])
        else:
            raise RuntimeError('Unsupported object type {ot}'.format(ot=page_data.object_type))
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': self.host_name,
            'Origin': self.base_url,
            'Referer': page_data.url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}'.format(q=quote(query))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornky.com/categories/full-hd-porno/')
    module = VintageTube()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
