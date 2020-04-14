# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError

# Internet tools
from .. import urljoin, quote

# Regex
import re

# Generator id
from ..id_generator import IdGenerator

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes, PornCatalogPageNode


class XFantazy(PornFetcher):
    category_template = 'https://xfantazy.com/category/{sub_cat}'
    channel_template = 'https://xfantazy.com/channel/{sub_ch}'
    tag_template = 'https://xfantazy.com/tag/{sub_tag}'
    category_videos_url = 'https://xfantazy.com/graphql'
    video_page_template = 'https://xfantazy.com/video/{vid}'
    number_of_thumbnails = 20

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://xfantazy.com/categories',
            PornCategories.CHANNEL_MAIN: 'https://xfantazy.com/channels',
            PornCategories.TAG_MAIN: 'https://xfantazy.com/tags',
            PornCategories.MOST_VIEWED_VIDEO: 'https://xfantazy.com/top',
            PornCategories.LONGEST_VIDEO: 'https://xfantazy.com/top',
            PornCategories.LATEST_VIDEO: 'https://xfantazy.com/top',
            PornCategories.RELEVANT_VIDEO: 'https://xfantazy.com/top',
            PornCategories.SEARCH_MAIN: 'https://xfantazy.com/search',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.RELEVANT_VIDEO: PornFilterTypes.RelevanceOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://xfantazy.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': ((PornFilterTypes.RelevanceOrder, 'Relevance', 'relevance'),
                                        (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'mostViewed'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        ),
                         'period_filters': ((PornFilterTypes.AllDate, 'All time', 'allTime'),
                                            (PornFilterTypes.OneDate, 'Last Month', 'lastMonth'),
                                            (PornFilterTypes.TwoDate, 'Last Week', 'lastWeek'),
                                            (PornFilterTypes.ThreeDate, 'Today', 'lastDay'),
                                            ),
                         }
        search_filters = {'period_filters': video_filters['period_filters']}
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=video_filters,
                                         single_channel_args=video_filters,
                                         single_tag_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='XFantazy', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(XFantazy, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        raw_data = page_request.json()
        new_channels = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                obj_id=x['id'],
                                                url=self.category_template.format(sub_cat=x['slug']),
                                                title=x['title'],
                                                image_link=urljoin(category_data.url, x['thumbnail']),
                                                number_of_videos=x['count'],
                                                raw_data=x,
                                                object_type=PornCategories.CATEGORY,
                                                super_object=category_data,
                                                ) for x in raw_data['data']['getCategories']]
        category_data.add_sub_objects(new_channels)
        return new_channels

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        raw_data = page_request.json()
        new_channels = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                obj_id=x['id'],
                                                url=self.category_template.format(sub_cat=x['slug']),
                                                title=x['title'],
                                                image_link=x['thumbnail'],
                                                number_of_videos=x['count'],
                                                raw_data=x,
                                                object_type=PornCategories.CHANNEL,
                                                super_object=channel_data,
                                                ) for x in raw_data['data']['getChannels']['channels']]
        channel_data.add_sub_objects(new_channels)
        return new_channels

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
        links, titles, numbers_of_videos, raw_data = self._get_tag_properties(page_request)
        partitioned_data = {
            chr(x): [(link, title, number_of_videos, raw_datum)
                     for link, title, number_of_videos, raw_datum in zip(links, titles, numbers_of_videos, raw_data)
                     if title[0].upper() == chr(x)]
            for x in range(ord('A'), ord('Z')+1)
        }
        partitioned_data['#'] = [(link, title, number_of_videos, raw_datum)
                                 for link, title, number_of_videos, raw_datum in
                                 zip(links, titles, numbers_of_videos, raw_data)
                                 if title[0].isdigit()]
        new_pages = [PornCatalogPageNode(catalog_manager=self.catalog_manager,
                                         obj_id=(IdGenerator.id_to_original_str(tag_data.id), k),
                                         title='{c} | Letter {p}'.format(c=tag_data.title, p=k),
                                         url=tag_data.url,
                                         page_number=k,
                                         raw_data=tag_data.raw_data,
                                         object_type=sub_object_type,
                                         super_object=tag_data,
                                         )
                     for k in sorted(partitioned_data.keys()) if len(partitioned_data[k]) > 0]
        for new_page in new_pages:
            sub_tags = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                obj_id=link,
                                                url=urljoin(tag_data.url, link),
                                                title=title,
                                                number_of_videos=number_of_videos,
                                                raw_data=raw_datum,
                                                object_type=PornCategories.TAG,
                                                super_object=new_page,
                                                )
                        for link, title, number_of_videos, raw_datum in partitioned_data[new_page.page_number]]
            new_page.add_sub_objects(sub_tags)

        tag_data.add_sub_objects(new_pages)

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles. The fetched objects MUST be sorted wrt title.
        :param page_request: Page request.
        :return:
        """
        raw_data = page_request.json()
        raw_tags = [(self.tag_template.format(sub_tag=x['slug'].replace(' ', '-')), x['name'], x['count'], x)
                    for x in raw_data['data']['getTags']]
        raw_tags.sort(key=lambda x: x[1])
        links, titles, numbers_of_videos, raw_data = zip(*raw_tags)
        return links, titles, numbers_of_videos, raw_data

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        page_request = self.get_object_request(video_data)
        raw_data = page_request.json()

        res = sorted((VideoSource(resolution=(int(re.findall(r'\d+', x['label'])[0])
                                              if x['label'] != 'original' else 1080),
                                  link=x['src'])
                      for x in raw_data['data']['getVideoSources']['sources'] if x['src'] != 'blocked'),
                     key=lambda x: x.resolution, reverse=True)
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
        raw_data = page_request.json()
        key = [k for k in raw_data['data'] if 'get' in k]
        if len(key) == 0:
            return 1
        return raw_data['data'][key[0]]['totalPages'] if 'totalPages' in raw_data['data'][key[0]] else 1

    def _prepare_params_for_video_list_page(self, category_data, page_number, sort_filter, period_filter):
        if category_data.true_object.object_type not in self._default_sort_by:
            object_type = category_data.raw_data['__typename'].lower()
            query = """query Query($page: Int, ${ob}: String!,
                                        $sort: AllowedSort, $uploaded: AllowedUploadedFilter,
                                        $tags: [String] = [], $limit: Int) {
                                            getThumbs(page: $page, {ob}: ${ob}, sort: $sort, uploaded: $uploaded,
                                                      tags: $tags, limit: $limit) {
                                                totalPages
                                                posts {
                                                  id
                                                  title
                                                  duration
                                                  thumbnail
                                                  userFileId
                                                  __typename
                                                }
                                                __typename
                                            }
                                        }"""
            query = re.sub(r'{ob}', object_type, query)
            params = {
                'operationName': "Query",
                'query': query,
                'variables': {'page': page_number,
                              'sort': sort_filter,
                              'tags': [],
                              object_type: category_data.raw_data['slug'],
                              'uploaded': period_filter}
            }
        else:
            sort_by = self._default_sort_by[category_data.true_object.object_type]
            sort_filter = self.get_proper_filter(category_data).filters.sort_order[sort_by].value
            query = """query Query($page: Int, $sort: AllowedSort, $uploaded: AllowedUploadedFilter, 
                        $tags: [String] = [], $limit: Int) {
                          getThumbs(page: $page, sort: $sort, uploaded: $uploaded, tags: $tags, limit: $limit) {
                            totalPages
                            posts {
                              id
                              title
                              duration
                              thumbnail
                              userFileId
                              resolution {
                                width
                                height
                                __typename
                              }
                              __typename
                            }
                            __typename
                          }
                        }
                        """
            params = {
                'operationName': "Query",
                'query': query,
                'variables': {'page': page_number,
                              'sort': sort_filter,
                              'tags': [],
                              'uploaded': period_filter}
            }
        return params

    @staticmethod
    def _prepare_params_for_search_page(search_query, page_number, period_filter):
        query = """query Query($page: Int, 
                                $search: String!, 
                                $sort: AllowedSort, 
                                $uploaded: AllowedUploadedFilter, 
                                $tags: [String] = [], 
                                $limit: Int) {
                                  getThumbs(page: $page, search: $search, sort: $sort, uploaded: $uploaded, 
                                            tags: $tags, limit: $limit) {
                                    totalPages
                                    posts {
                                      id
                                      title
                                      duration
                                      thumbnail
                                      userFileId
                                      __typename
                                    }
                                    __typename
                                  }
                                }
                """
        params = {
            'operationName': "Query",
            'query': query,
            'variables': {'page': page_number,
                          'search': search_query,
                          'sort': 'relevance',
                          'tags': [],
                          'uploaded': period_filter}
        }
        return params

    @staticmethod
    def _prepare_params_for_main_channel_page(page_number):
        params = {
            'operationName': "Query",
            'query': """query Query($page: Int) {
                              getChannels(page: $page) {
                                totalPages
                                channels {
                                  id
                                  title
                                  slug
                                  thumbnail
                                  count
                                  __typename
                                }
                                __typename
                              }
                            }
                            """,
            'variables': {'page': page_number,
                          }
        }
        return params

    @staticmethod
    def _prepare_params_for_main_category_page():
        params = {
            'operationName': "Query",
            'query': """query Query {
                          getCategories {
                            id
                            slug
                            title
                            thumbnail
                            cover
                            count
                            __typename
                          }
                        }
                        """,
            'variables': {}
        }
        return params

    @staticmethod
    def _prepare_params_for_main_tag_page():
        params = {
            'operationName': "Query",
            'query': """query Query {
                      getTags {
                        name
                        count
                        slug
                        __typename
                      }
                    }
                    """,
            'variables': {}
        }
        return params

    @staticmethod
    def _prepare_params_for_video_page(video_data):
        params = {
            'operationName': "Query",
            'query': "query Query($id: String!) {\n  getVideoSources(id: $id) {\n    free360DailyLimitExceeded\n    "
                     "sources {\n      type\n      label\n      src\n      blocked\n      durationLimit\n      __"
                     "typename\n    }\n    __typename\n  }\n}\n",
            'variables': {'id': video_data.raw_data['id']}
        }
        return params

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        raw_data = page_request.json()
        res = [PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                        obj_id=video_prepared_data['id'],
                                        url=self.video_page_template.format(vid=video_prepared_data['id']),
                                        title=video_prepared_data['title'],
                                        image_link=video_prepared_data['thumbnail'],
                                        duration=self._format_duration(video_prepared_data['duration']),
                                        raw_data=video_prepared_data,
                                        object_type=PornCategories.VIDEO,
                                        super_object=page_data,
                                        ) for video_prepared_data in raw_data['data']['getThumbs']['posts']]

        page_data.add_sub_objects(res)
        return res

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw duration.
        :return:
        """
        res = raw_duration
        minutes, seconds = raw_duration.split(':')
        if int(minutes) > 59:
            res = '{h}:{m}:{s}'.format(h=str(int(minutes) // 60).zfill(2),
                                       m=str(int(minutes) % 60).zfill(2),
                                       s=seconds)
        return super(XFantazy, self)._format_duration(res)

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
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
        url = self.category_videos_url
        sort_filter = page_filter.sort_order.value
        if page_number is None:
            page_number = 1
        period_filter = page_filter.period.value
        if true_object.object_type in (PornCategories.CHANNEL_MAIN, ):
            params = self._prepare_params_for_main_channel_page(page_number)
        elif true_object.object_type in (PornCategories.CATEGORY_MAIN, ):
            params = self._prepare_params_for_main_category_page()
        elif true_object.object_type in (PornCategories.TAG_MAIN, ):
            params = self._prepare_params_for_main_tag_page()
        elif (
                true_object.object_type in (PornCategories.VIDEO_PAGE, PornCategories.CHANNEL, PornCategories.CATEGORY,
                                            PornCategories.TAG) or
                true_object.object_type in self._default_sort_by
        ):
            params = self._prepare_params_for_video_list_page(page_data, page_number, sort_filter, period_filter)
        elif true_object.object_type in (PornCategories.SEARCH_MAIN,):
            params = self._prepare_params_for_search_page(self._search_query, page_number, period_filter)
        elif true_object.object_type in (PornCategories.VIDEO, ):
            params = self._prepare_params_for_video_page(page_data)
        else:
            raise RuntimeError('Unknown object_type {o}!'.format(o=page_data.object_type))
        page_request = self.session.post(url, headers=headers, json=params)
        # else:
        #     raise RuntimeError('Unknown object_type {o}!'.format(o=object_data.object_type))
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '/{q}'.format(q=quote(query))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('/category/bbw')
    module = XFantazy()
    # module.get_available_categories()
    # module.download_object(None, category_id, verbose=1)
    module.download_category_input_from_user(use_web_server=False)
