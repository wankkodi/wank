# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError

# Internet tools
from .. import urljoin, quote_plus, parse_qsl

# Regex
import re

# Json
from ..tools.text_json_manioulations import prepare_json_from_not_formatted_text

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogPageNode, PornCatalogVideoPageNode, VideoNode, \
    VideoSource, VideoTypes
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# Math
import math

# External Fetchers
from ..tools.external_fetchers import KTMoviesFetcher

# ID generator
from ..id_generator import IdGenerator


class AnyPorn(PornFetcher):
    video_quality_index = {'UHD': 2160, 'HQ': 720, 'LQ': 360}

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://anyporn.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://anyporn.com/models/',
            PornCategories.TAG_MAIN: 'https://anyporn.com/categories/',
            PornCategories.CHANNEL_MAIN: 'https://anyporn.com/channels/',
            PornCategories.LATEST_VIDEO: 'https://anyporn.com/newest/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://anyporn.com/popular/',
            PornCategories.SEARCH_MAIN: 'https://anyporn.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://anyporn.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        # general_filter_params = {'general_filters': [(StraightType, 'Straight', ''),
        #                                              (GayType, 'Gay', 'gay'),
        #                                              (ShemaleType, 'Shemale', 'shemale'),
        #                                              ],
        #                          }
        category_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Recently updated', 'last_content_date'),
                                          (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'name'),
                                          (PornFilterTypes.ViewsOrder, 'Most viewed', 'avg_videos_popularity'),
                                          (PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          ],
                           }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       ],
                        'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', ''),
                                            (PornFilterTypes.HDQuality, 'HD quality', 'hd'),
                                            ],
                        }
        search_params = video_params.copy()
        search_params['sort_order'] = [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                                       (PornFilterTypes.DateOrder, 'Recent videos', 'most-recent'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                       (PornFilterTypes.LengthOrder, 'By duration', 'long-movies'),
                                       ]

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_params,
                                         channels_args=category_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='AnyPorn', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(AnyPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)
        self.kt_fetcher = KTMoviesFetcher(self.session, self.user_agent, self.parser)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="list-categories"]/div[@class="margin-fix"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="list-sponsors"]/div[@class="margin-fix"]/a',
                                                  PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@class="list-models"]/div[@class="margin-fix"]/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        tag_properties = self._get_tag_properties(page_request)
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=link,
                                       url=urljoin(tag_data.url, link),
                                       title=title,
                                       number_of_videos=number_of_videos,
                                       object_type=PornCategories.TAG,
                                       super_object=tag_data,
                                       )
               for link, title, number_of_videos in zip(*tag_properties)]
        tag_data.add_sub_objects(res)
        return res

    def _update_available_base_object(self, object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None
            title = category.attrib['title'] if 'title' in category.attrib else image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="wrap"]/div[@class="videos"]')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].text)[0]) if len(number_of_videos) > 0 else None

            rating = (category.xpath('./div[@class="wrap"]/div[@class="rating positive"]') +
                      category.xpath('./div[@class="wrap"]/div[@class="rating negative"]'))
            rating = re.findall(r'\d+%', rating[0].text, re.DOTALL)[0] if len(rating) > 0 else None

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      rating=rating,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        if is_sort:
            res.sort(key=lambda x: x.title)
        object_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//div[@class="tagslist"]/ul/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.attrib['title'], None)
                                                for x in raw_data])
        return links, titles, number_of_videos

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        return self._get_video_links_from_video_data1(video_data)

    def _get_video_links_from_video_data1(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        # new_video_data = json.loads([x for x in tmp_tree.xpath('.//script/text()') if 'gvideo' in x][0])
        # video_suffix = video_suffix = urlparse(tmp_data['contentUrl']).path

        videos = tmp_tree.xpath('.//video/source')
        assert len(videos) > 0
        if len(videos) > 1:
            videos = sorted((VideoSource(link=x.attrib['src'], resolution=self.video_quality_index[x.attrib['title']])
                             for x in videos),
                            key=lambda x: x.resolution, reverse=True)
        else:
            videos = VideoNode(video_sources=[VideoSource(link=videos[0].attrib['src'],
                                                          video_type=VideoTypes.VIDEO_REGULAR)])
        return VideoNode(video_sources=videos)

    def _get_video_links_from_video_data2(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        videos, resolutions = self.kt_fetcher.get_video_link(video_data.url)
        video_sources = [VideoSource(link=x, resolution=res) for x, res in zip(videos, resolutions)]
        if not all(x is None for x in resolutions):
            video_sources.sort(key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=video_sources)

    def _get_video_links_from_video_data3(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        # new_video_data = json.loads([x for x in tmp_tree.xpath('.//script/text()') if 'gvideo' in x][0])
        # video_suffix = video_suffix = urlparse(tmp_data['contentUrl']).path

        videos = tmp_tree.xpath('.//video/source')
        assert len(videos) > 0
        if len(videos) > 1:
            videos = VideoNode(video_sources=sorted(((VideoSource(link=x.attrib['src'],
                                                                  resolution=re.findall(r'\d+', x.attrib['title'])[0],
                                                                  video_type=VideoTypes.VIDEO_REGULAR)
                                                      ) for x in videos),
                                                    key=lambda x: x.resolution, reverse=True)
                               )
        else:
            videos = VideoNode(video_sources=[VideoSource(link=videos[0].attrib['src'],
                                                          video_type=VideoTypes.VIDEO_REGULAR)])
        return VideoNode(video_sources=videos)

    def _get_video_links_from_video_data4(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        request_data = re.findall(r'(?:var flashvars = )({.*?})(?:;)', tmp_request.text, re.DOTALL)
        assert len(request_data) == 1
        raw_data = prepare_json_from_not_formatted_text(request_data[0])

        videos = [VideoSource(link=raw_data['video_url'])]
        return VideoNode(video_sources=videos, verify=False)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN):
            return 1
        try:
            page_request = self.get_object_request(category_data, send_error=False) if fetched_request is None \
                else fetched_request
        except PornFetchUrlError:
            return 1
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.attrib['data-parameters'].split(':')[-1])
                for x in tree.xpath('.//div[@class="nopop pagination-holder"]/ul/li/a')
                if x.attrib['data-parameters'].split(':')[-1].isdigit()]

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        # New
        headers = {
            'Accept': '*.*',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        if page_number is None:
            page_number = 1
        params.update({
                'mode': 'async',
                'function': 'get_block',
            })
        if page_filter.length.value is not None:
            params.update(parse_qsl(page_filter.length.value))
        if page_number > 1:
            params['from'] = str(page_number).zfill(2)

        if true_object.object_type == PornCategories.CATEGORY_MAIN:
            params['block_id'] = 'list_categories_categories_list'
            params['sort_by'] = page_filter.sort_order.value
        elif true_object.object_type == PornCategories.CHANNEL_MAIN:
            params['block_id'] = 'list_content_sources_sponsors_list'
            params['sort_by'] = page_filter.sort_order.value
        elif true_object.object_type == PornCategories.PORN_STAR_MAIN:
            params['block_id'] = 'list_models_models_list'
            params['sort_by'] = page_filter.sort_order.value
            params['gender_id'] = page_filter.general.value
        elif true_object.object_type == PornCategories.ACTRESS_MAIN:
            params['block_id'] = 'list_models_models_list'
            params['sort_by'] = page_filter.sort_order.value
            params['gender_id'] = page_filter.general.value
        elif true_object.object_type == PornCategories.TAG_MAIN:
            # params['block_id'] = 'list_content_sources_sponsors_list'
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3*',
                'Cache-Control': 'max-age=0',
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }
            page_request = self.session.get(page_data.url, headers=headers)
            return page_request
        elif true_object.object_type == PornCategories.VIDEO:
            # Right now like TagMain,but could easily change...
            # params['block_id'] = 'list_content_sources_sponsors_list'
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3*',
                'Cache-Control': 'max-age=0',
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }
            page_request = self.session.get(page_data.url, headers=headers)
            return page_request

        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            params['block_id'] = 'list_videos_v2_videos_list_search_result'
            params['q'] = self._search_query
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            if 'from' in params:
                params.pop('from')
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
        elif true_object.object_type in (PornCategories.CATEGORY, PornCategories.CHANNEL,
                                         PornCategories.TAG, PornCategories.PORN_STAR, PornCategories.ACTRESS):
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = page_filter.sort_order.value
        elif true_object.object_type == PornCategories.MOST_VIEWED_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = 'video_viewed'
            if page_filter.period.value is not None:
                params['sort_by'] += page_filter.period.value
        elif true_object.object_type == PornCategories.LATEST_VIDEO:
            params['block_id'] = 'list_videos_latest_videos_list'
            params['sort_by'] = 'post_date'
        elif true_object.object_type == PornCategories.TOP_RATED_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = 'rating'
            if page_filter.period.value is not None:
                params['sort_by'] += page_filter.period.value
        elif true_object.object_type == PornCategories.LONGEST_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = 'duration'
        elif true_object.object_type == PornCategories.MOST_DISCUSSED_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = 'most_commented'
        elif true_object.object_type == PornCategories.FAVORITE_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = 'most_favourited'
        elif true_object.object_type == PornCategories.RECOMMENDED_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = 'last_time_view_date'
        else:
            raise ValueError('Wrong category type {c}'.format(c=page_data))

        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            params['sort_by'] += page_filter.period.value
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div[@class="margin-fix"]/div[@class="item  "]/'
                            'div[@class="thmbclck"]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1

            image = video_tree_data.xpath('./div[@class="img"]/a/img')
            assert len(image) == 1

            is_hd = video_tree_data.xpath('./div[@class="img"]/div[@class="hdpng"]')

            video_length = video_tree_data.xpath('./div[@class="wrap"]/div[@class="added"]/em/script')
            assert len(video_length) == 1

            rating = (video_tree_data.xpath('./div[@class="wrap"]/div[@class="rating positive"]/script') +
                      video_tree_data.xpath('./div[@class="wrap"]/div[@class="rating negative"]/script'))
            rating = re.findall(r'\d+%', rating[0].text) if len(rating) > 0 else '0'

            video_data = PornCatalogVideoPageNode(
                catalog_manager=self.catalog_manager,
                obj_id=re.findall(r'\d+', link[0].attrib['href'])[0],
                title=image[0].attrib['alt'],
                url=urljoin(self.base_url, link[0].attrib['href']),
                image_link=image[0].attrib['data-original'],
                preview_video_link=image[0].attrib['data-preview'] if 'data-preview' in image[0].attrib else None,
                is_hd=len(is_hd) > 0,
                duration=self._format_duration(video_length[0].text),
                rating=rating[0] if len(rating) > 0 else None,
                object_type=PornCategories.VIDEO,
                super_object=page_data,
            )
            res.append(video_data)

        page_filter = self.get_proper_filter(page_data).current_filters
        if page_filter.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
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

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query.replace(' ', '-')))


class PervertSluts(AnyPorn):
    # Some of the models we took from AnyPorn module (has thee same structure)
    flip_number = 11

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://pervertslut.com/categories/',
            PornCategories.TAG_MAIN: 'https://pervertslut.com/tags/',
            PornCategories.CHANNEL_MAIN: 'https://pervertslut.com/channels/',
            PornCategories.LATEST_VIDEO: 'https://pervertslut.com/latest-updates/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://pervertslut.com/most-popular/',
            PornCategories.TOP_RATED_VIDEO: 'https://pervertslut.com/top-rated/',
            PornCategories.SEARCH_MAIN: 'https://pervertslut.com/search/',
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
        return 'https://pervertslut.com/'

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return False

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', ''),
                                                     (PornFilterTypes.GayType, 'Gay', 'gay'),
                                                     (PornFilterTypes.ShemaleType, 'Shemale', 'shemale'),
                                                     ],
                                 }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       ],
                        }
        search_params = video_params.copy()
        search_params['sort_order'] = [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                                       (PornFilterTypes.DateOrder, 'Recent videos', 'most-recent'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                       (PornFilterTypes.LengthOrder, 'By duration', 'long-movies'),
                                       ]

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='AnyPorn', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PervertSluts, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available channels.
        :return: Object of all available shows (JSON).
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        page_request = self.session.get(tag_data.url, headers=headers)
        tree = self.parser.parse(page_request.text)
        tags = tree.xpath('.//div[@class="list-tags"]/div[@class="margin-fix"]/ul/li/a')
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x.attrib['href'],
                                       url=urljoin(self.base_url, x.attrib['href']),
                                       title=x.text,
                                       object_type=PornCategories.TAG,
                                       super_object=tag_data,
                                       ) for x in tags]
        tag_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        return self._get_video_links_from_video_data2(video_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        xpath = './/div[@class="pagination-holder"]/ul/li/a'
        return ([int(x.attrib['data-parameters'].split(':')[-1])
                for x in tree.xpath(xpath)
                if 'data-parameters' in x.attrib and x.attrib['data-parameters'].split(':')[-1].isdigit()] +
                [int(re.findall(r'(?:from.*?:)(\d+)', x.attrib['href'])[0])
                for x in tree.xpath(xpath)
                if 'href' in x.attrib and len(re.findall(r'(?:from.*?:)(\d+)', x.attrib['href'])) > 0]
                )

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        # Took from AnyPorn module with somme modifications...
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div[@class="margin-fix"]/div[@class="item  "]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1

            image = video_tree_data.xpath('./a/div[@class="img"]/img')
            assert len(image) == 1

            is_hd = video_tree_data.xpath('./a/div[@class="img"]/div[@class="hdpng"]')

            video_length = video_tree_data.xpath('./a/div[@class="img"]/div[@class="duration-overlay"]')
            assert len(video_length) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=re.findall(r'\d+', link[0].attrib['href'])[0],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=image[0].attrib['alt'],
                                                  image_link=image[0].attrib['src'],
                                                  duration=self._format_duration(video_length[0].text),
                                                  is_hd=len(is_hd) > 0,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query))


class Analdin(PervertSluts):
    # Belongs to the AnyPorn network
    # todo: add playlists, webcams
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.analdin.com/categories/',
            PornCategories.CHANNEL_MAIN: 'https://www.analdin.com/#popup-sponsors',
            PornCategories.PORN_STAR_MAIN: 'https://www.analdin.com/models/',
            PornCategories.LATEST_VIDEO: 'https://www.analdin.com/latest-updates/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.analdin.com/most-popular/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.analdin.com/top-rated/',
            PornCategories.SEARCH_MAIN: 'https://www.analdin.com/search/',
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
        return 'https://www.analdin.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': [(PornFilterTypes.AllType, 'All genders', ''),
                                                     (PornFilterTypes.GirlType, 'Girls', '0'),
                                                     (PornFilterTypes.GuyType, 'Guys', '1'),
                                                     (PornFilterTypes.OtherType, 'Other', '2'),
                                                     ],
                                 }
        category_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Recently updated', 'last_content_date'),
                                          (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'name'),
                                          (PornFilterTypes.ViewsOrder, 'Most viewed', 'avg_videos_popularity'),
                                          (PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          ],
                           }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       ],
                        'period_filters': ([(PornFilterTypes.AllDate, 'All time', ''),
                                            (PornFilterTypes.OneDate, 'This Month', '_month'),
                                            (PornFilterTypes.TwoDate, 'This week', '_week'),
                                            (PornFilterTypes.ThreeDate, 'Today', '_today'),
                                            ],
                                           [('sort_order', [PornFilterTypes.RatingOrder,
                                                            PornFilterTypes.ViewsOrder])]
                                           ),
                        'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', ''),
                                            (PornFilterTypes.HDQuality, 'HD quality', 'hd'),
                                            ],
                        }
        search_params = video_params.copy()
        search_params['sort_order'] = [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                                       (PornFilterTypes.DateOrder, 'Recent videos', 'most-recent'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                       (PornFilterTypes.LengthOrder, 'By duration', 'long-movies'),
                                       ]

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         categories_args=category_params,
                                         channels_args=category_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='Analdin', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Analdin, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_base_object(self, base_object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link = category.attrib['href']
            title = category.attrib['title']

            image = category.xpath('./div[@class="img"]/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            info_data = category.xpath('./*')[-1]
            number_of_videos = int(re.findall(r'(\d+)(?: video)', info_data.text)[0])
            rating = re.findall(r'(\d+%)', info_data.text)[0]

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(base_object_data.url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               rating=rating,
                                               object_type=object_type,
                                               super_object=base_object_data,
                                               ))
        if is_sort:
            res.sort(key=lambda x: x.title)
        base_object_data.add_sub_objects(res)
        return res

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        channels = tree.xpath('.//div[@class="wrap2"]/ul/li/a')
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x.attrib['href'],
                                       url=urljoin(channel_data.url, x.attrib['href']),
                                       title=x.attrib['title'],
                                       object_type=PornCategories.CHANNEL,
                                       super_object=channel_data,
                                       ) for x in channels]
        channel_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="wrap2"]/ul/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, None)
                                                for x in raw_objects])
        return links, titles, number_of_videos

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div[@class="margin-fix"]/div[@class="item  "]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1

            is_hd = 'class="hd"' in video_tree_data.xpath('./a/div[@class="img ithumb"]/*')[1].text

            video_length = video_tree_data.xpath('./a/div[@class="img ithumb"]/div[@class="duration"]')
            assert len(video_length) == 1

            title = video_tree_data.xpath('./a/strong')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            video_data = PornCatalogVideoPageNode(
                catalog_manager=self.catalog_manager,
                obj_id=re.findall(r'\d+', link[0].attrib['href'])[0],
                title=title,
                url=urljoin(self.base_url, link[0].attrib['href']),
                image_link=link[0].attrib['thumb'],
                preview_video_link=link[0].attrib['vthumb'] if 'vthumb' in link[0].attrib else None,
                is_hd=is_hd,
                duration=self._format_duration(video_length[0].text),
                object_type=PornCategories.VIDEO,
                super_object=page_data,
            )
            res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return super(PervertSluts, self)._prepare_new_search_query(query)


class Fapster(PervertSluts):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://fapster.xxx/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://fapster.xxx/models/',
            PornCategories.CHANNEL_MAIN: 'https://fapster.xxx/sites/',
            PornCategories.LATEST_VIDEO: 'https://fapster.xxx/latest-updates/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://fapster.xxx/most-popular/',
            PornCategories.SEARCH_MAIN: 'https://fapster.xxx/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://fapster.xxx/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': [(PornFilterTypes.AllType, 'All genders', ''),
                                                     (PornFilterTypes.LesbianType, 'Girls', '0'),
                                                     (PornFilterTypes.GayType, 'Guys', '1'),
                                                     (PornFilterTypes.ShemaleType, 'Other', '2'),
                                                     ],
                                 }
        category_params = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.ViewsOrder, 'Most viewed', 'avg_videos_popularity'),
                                          (PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          ],
                           }
        porn_stars_params = {'sort_order': [(PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                            (PornFilterTypes.ViewsOrder, 'Most viewed', 'avg_videos_popularity'),
                                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                            ],
                             }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                                       (PornFilterTypes.FavorOrder, 'Most Favourite', 'most_favourited'),
                                       ],
                        }
        search_params = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                                        (PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                        (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                                        (PornFilterTypes.FavorOrder, 'Most Favourite', 'most_favourited'),
                                        ],
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         categories_args=category_params,
                                         porn_stars_args=porn_stars_params,
                                         channels_args=porn_stars_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='Fapster', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Fapster, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div[@class="margin-fix"]/div[@class="item  "]/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./div[@class="img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            title = video_tree_data.attrib['title'] \
                if 'title' in video_tree_data.attrib else image_data[0].attrib['alt']

            is_hd = len(video_tree_data.xpath('./div[@class="img"]/span[@class="is-hd"]')) > 0

            video_length = video_tree_data.xpath('./div[@class="wrap"]/div[@class="duration"]')
            assert len(video_length) == 1

            rating = (video_tree_data.xpath('./div[@class="wrap"]/div[@class="rating positive"]') +
                      video_tree_data.xpath('./div[@class="wrap"]/div[@class="rating negative"]'))
            assert len(video_length) == 1
            rating = re.findall(r'\d+%', rating[0].text, re.DOTALL)

            added_before = video_tree_data.xpath('./div[@class="wrap"]/div[@class="added"]')
            assert len(added_before) == 1
            added_before = added_before[0].text

            number_of_views = video_tree_data.xpath('./div[@class="wrap"]/div[@class="views"]')
            number_of_views = number_of_views[0].text if len(number_of_views) == 1 else None

            video_data = PornCatalogVideoPageNode(
                catalog_manager=self.catalog_manager,
                obj_id=link,
                title=title,
                url=urljoin(page_data.url, link),
                image_link=image,
                is_hd=is_hd,
                duration=self._format_duration(video_length[0].text),
                rating=rating,
                added_before=added_before,
                number_of_views=number_of_views,
                object_type=PornCategories.VIDEO,
                super_object=page_data,
            )
            res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        if true_object.object_type == PornCategories.SEARCH_MAIN:
            headers = {
                'Accept': '*.*',
                'Cache-Control': 'max-age=0',
                'Referer': self.base_url,
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
            page_number = page_data.page_number if page_data.page_number is not None else 1
            params.update({
                'mode': 'async',
                'function': 'get_block',
            })
            page_filter = self.get_proper_filter(page_data).current_filters

            params['block_id'] = 'list_videos_videos_list_search_result'
            params['q'] = self._search_query
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            if page_filter.sort_order.filter_id in (PornFilterTypes.RatingOrder, PornFilterTypes.ViewsOrder):
                params['sort_by'] += page_filter.period.value
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            return super(PervertSluts, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                     page_filter, fetch_base_url)

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return super(PervertSluts, self)._prepare_new_search_query(query)


class PornRewind(PervertSluts):
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.pornrewind.com/categories/',
            PornCategories.TAG_MAIN: 'https://www.pornrewind.com/categories/',
            PornCategories.LATEST_VIDEO: 'https://www.pornrewind.com/videos/?sort_by=post_date',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.pornrewind.com/videos/?sort_by=video_viewed',
            PornCategories.TOP_RATED_VIDEO: 'https://www.pornrewind.com/videos/?sort_by=rating',
            PornCategories.SEARCH_MAIN: 'https://www.pornrewind.com/search/',
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
        return 'https://www.pornrewind.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        category_params = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          (PornFilterTypes.VideosPopularityOrder, 'Videos Popularity',
                                           'avg_videos_popularity'),
                                          (PornFilterTypes.VideosRatingOrder, 'Videos rating', 'avg_videos_rating'),
                                          ],
                           }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       ],
                        }
        search_params = video_params.copy()
        search_params['sort_order'] = [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                                       (PornFilterTypes.DateOrder, 'Recent videos', 'post_date'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.LengthOrder, 'By duration', 'duration'),
                                       ]

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_params,
                                         single_category_args=video_params,
                                         single_tag_args=video_params,
                                         video_args=video_params,
                                         search_args=search_params,
                                         )

    def __init__(self, source_name='PornRewind', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornRewind, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumbs-list"]/div[@class="th"]/a')
        res = []
        for category in categories:
            img = category.xpath('./span[@class="thumb-categories-img"]/img')
            assert len(img) == 1
            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=category.attrib['title'],
                                                  image_link=img[0].attrib['data-src'],
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="tags"]/ul[@class="tags-list"]/li/a')
        links = [x.attrib['href'] for x in raw_objects]
        titles = [x.text.title() for x in raw_objects]
        number_of_videos = [None] * len(titles)
        assert len(titles) == len(links)
        # assert len(titles) == len(number_of_videos)

        return links, titles, number_of_videos

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        return self._get_video_links_from_video_data4(video_data)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        if len(self._get_available_pages_from_tree(tree)) == 0:
            return 1
        else:
            return self._binary_search_max_number_of_pages(category_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//nav[@class="pagination"]/ul/li/*/text()') if x.isdigit()]

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
        videos = tree.xpath('.//div[@class="thumbs-list"]/div[@class="th "]/a[@class="thumb"]')
        res = []
        for video_tree_data in videos:
            image_data = video_tree_data.xpath('./span[@class="thumb-img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-src']
            flip_image = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                          for i in range(1, int(image_data[0].attrib['data-cnt']) + 1)]

            video_length = video_tree_data.xpath('./span[@class="thumb-desc"]/span[@class="thumb-info"]/'
                                                 'span[@class="thumb-label thumb-time"]/span/text()')
            assert len(video_length) == 1

            added_before = video_tree_data.xpath('./span[@class="thumb-desc"]/span[@class="thumb-info"]/'
                                                 'span[@class="thumb-label thumb-added"]/span/text()')
            assert len(added_before) == 1

            viewers = video_tree_data.xpath('./span[@class="thumb-desc"]/span[@class="thumb-info"]/'
                                            'span[@class="thumb-label thumb-viewed"]/span/text()')
            assert len(viewers) == 1

            rating = video_tree_data.xpath('./span[@class="thumb-desc"]/span[@class="thumb-info"]/'
                                           'span[@class="thumb-label thumb-rating"]/text()')
            assert len(rating) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['href'],
                                                  url=urljoin(self.base_url, video_tree_data.attrib['href']),
                                                  title=video_tree_data.attrib['title'],
                                                  image_link=image,
                                                  flip_images_link=flip_image,
                                                  duration=self._format_duration(video_length[0]),
                                                  added_before=added_before[0],
                                                  number_of_views=viewers[0],
                                                  rating=rating[0],
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        if true_object.object_type in (PornCategories.SEARCH_MAIN,):
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
            if len(split_url[-1]) != 0:
                split_url.append('')
            if page_number is not None and page_number != 1:
                if split_url[-2].isdigit():
                    split_url.pop(-2)
                split_url.insert(-1, str(page_number))
            params.update({
                'mode': 'async',
                'action': 'get_block',
                'block_id': 'list_videos_common_videos_list',
            })
            if len(page_filter.sort_order.value) > 0:
                params['sort_by'] = page_filter.sort_order.value

            fetch_base_url = '/'.join(split_url)
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            page_number = page_number if page_number is not None else 1
            return super(PornRewind, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                   page_filter, fetch_base_url)

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return super(PervertSluts, self)._prepare_new_search_query(query)


class HellPorno(AnyPorn):
    max_flip_images = 10

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://hellporno.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://hellporno.com/models/',
            PornCategories.CHANNEL_MAIN: 'https://hellporno.com/channels/',
            PornCategories.TOP_RATED_VIDEO: 'https://hellporno.com/',
            PornCategories.SEARCH_MAIN: 'https://hellporno.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """

        general_filter_params = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', ''),
                                                     (PornFilterTypes.LesbianType, 'Lesbian', 'lesbian'),
                                                     (PornFilterTypes.ShemaleType, 'Shemale', 'shemale'),
                                                     (PornFilterTypes.GayType, 'Gay', 'gay'),
                                                     ],
                                 }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         )

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://hellporno.com/'

    def __init__(self, source_name='HellPorno', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HellPorno, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="block-categories-videos"]/div[@class="categories-holder-videos"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span[@class="image"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            title = category.xpath('./span[@class="title"]') + category.xpath('./span[@class="title long-title"]')
            assert len(title) == 1
            title = title[0].text

            number_of_videos_data = (category.xpath('./span[@class="cat-info"]/span') +
                                     category.xpath('./span[@class="cat-info long-cat-info"]/span'))
            assert len(number_of_videos_data) > 0
            number_of_videos = re.findall(r'\d+', number_of_videos_data[0].text)[0]
            number_of_pictures = re.findall(r'\d+', number_of_videos_data[1].text)[0] \
                if len(re.findall(r'\d+', number_of_videos_data[1].text)) > 0 else None

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(category_data.url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      number_of_photos=number_of_pictures,
                                                      object_type=PornCategories.CATEGORY,
                                                      super_object=category_data,
                                                      )
            res.append(sub_object_data)
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@class="block-inner"]/ul/li/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="block-inner"]/ul/li/a',
                                                  PornCategories.CHANNEL)

    def _update_available_base_object(self, object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link = category.attrib['href']
            title = category.text

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(object_data.url, link),
                                                      title=title,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        if is_sort:
            res.sort(key=lambda x: x.title)
        object_data.add_sub_objects(res)
        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN, PornCategories.PORN_STAR_MAIN):
            return 1
        try:
            page_request = self.get_object_request(category_data, send_error=False) if fetched_request is None \
                else fetched_request
        except PornFetchUrlError:
            return 1
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//div[@class="pagination"]/*/text()') if x.isdigit()]

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        return self._get_video_links_from_video_data3(video_data)

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        res = []
        videos = tree.xpath('.//div[@class="videos-holder"]/div[@class="video-thumb"]')
        if len(videos) > 0:
            # Method 1
            for video_tree_data in videos:
                link_data = video_tree_data.xpath('./a')
                assert len(link_data) == 1
                link = link_data[0].attrib['href']
                title = link_data[0].text

                image_data = video_tree_data.xpath('./span[@class="image"]/img')
                assert len(image_data) == 1
                image = image_data[0].attrib['src']
                flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                               for d in range(1, self.max_flip_images + 1)]

                preview_data = video_tree_data.xpath('./span[@class="image"]/video')
                assert len(preview_data) == 1
                preview_link = preview_data[0].attrib['src']

                video_length = video_tree_data.xpath('./span[@class="image"]/span[@class="time"]')
                assert len(video_length) == 1
                video_length = video_length[0].text

                rating_data = video_tree_data.xpath('./span[@class="video-rating"]/span')
                assert len(rating_data) == 1
                rating = re.findall(r'\d+%', rating_data[0].attrib['style'])

                number_of_views_data = video_tree_data.xpath('./span[@class="info"]/span')
                assert len(number_of_views_data) == 1
                number_of_views = number_of_views_data[0].text
                added_before = number_of_views_data[0].tail

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(page_data.url, link),
                                                      title=title,
                                                      image_link=image,
                                                      flip_images_link=flip_images,
                                                      preview_video_link=preview_link,
                                                      duration=self._format_duration(video_length),
                                                      rating=rating,
                                                      number_of_views=number_of_views,
                                                      added_before=added_before,
                                                      object_type=PornCategories.VIDEO,
                                                      super_object=page_data,
                                                      )
                res.append(video_data)
        else:
            # Method 2
            videos = tree.xpath('.//div[@class="videos-holder"]/a')
            for video_tree_data in videos:
                link = video_tree_data.attrib['href']

                image_data = video_tree_data.xpath('./div[@class="image"]/img')
                assert len(image_data) == 1
                image = image_data[0].attrib['src']
                flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                               for d in range(1, int(re.findall(r'(\d+)(?:\)$)',
                                                                image_data[0].attrib['onmouseover'])[0]) + 1)]

                title_data = video_tree_data.xpath('./div[@class="title"]/span')
                assert len(title_data) == 1
                title = self._clear_text(title_data[0].tail)
                video_length = self._clear_text(title_data[0].text)

                number_of_views_data = video_tree_data.xpath('./div[@class="info"]/span')
                assert len(number_of_views_data) == 1
                number_of_views = number_of_views_data[0].text
                added_before = number_of_views_data[0].tail

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(page_data.url, link),
                                                      title=title,
                                                      image_link=image,
                                                      flip_images_link=flip_images,
                                                      duration=self._format_duration(video_length),
                                                      number_of_views=number_of_views,
                                                      added_before=added_before,
                                                      object_type=PornCategories.VIDEO,
                                                      super_object=page_data,
                                                      )
                res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        if page_number is None:
            page_number = 1

        if true_object.object_type not in (PornCategories.PORN_STAR_MAIN, PornCategories.PORN_STAR):
            if self.general_filter.current_filters.general.filter_id != PornFilterTypes.AllType:
                # params['t'] = self._video_filters.current_filter_values['type'].value
                params['t'] = self.general_filter.current_filters.general.value

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Referer': page_data.url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_number is not None and page_number > 1:
            fetch_base_url += '{d}/'.format(d=page_number)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


class AlphaPorno(HellPorno):
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.alphaporno.com/categories/',
            PornCategories.CHANNEL_MAIN: 'https://www.alphaporno.com/channels/',
            PornCategories.PORN_STAR_MAIN: 'https://www.alphaporno.com/pornstars/',
            PornCategories.TAG_MAIN: 'https://www.alphaporno.com/tags/',
            PornCategories.LATEST_VIDEO: 'https://www.alphaporno.com/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.alphaporno.com/most-popular/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.alphaporno.com/top-rated/',
            PornCategories.LONGEST_VIDEO: 'https://www.alphaporno.com/longest/',
            PornCategories.SEARCH_MAIN: 'https://www.alphaporno.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        porn_stars_params = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Popularity', 'popularity'),
                                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'name'),
                                            (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total-videos'),
                                            ],
                             }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       ],
                        'period_filters': [(PornFilterTypes.AllDate, 'All time', ''),
                                           (PornFilterTypes.OneDate, 'This Month', '_month'),
                                           (PornFilterTypes.TwoDate, 'This week', '_week'),
                                           (PornFilterTypes.ThreeDate, 'Today', '_today'),
                                           ],
                        }
        search_params = video_params.copy()
        search_params['sort_order'] = [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                                       (PornFilterTypes.DateOrder, 'Recent videos', 'most-recent'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                       (PornFilterTypes.LengthOrder, 'By duration', 'long-movies'),
                                       ]

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.alphaporno.com/'

    def __init__(self, source_name='AlphaPorno', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(AlphaPorno, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="movies-block"]/ul/li')
        res = []
        for category in categories:
            link = category.xpath('./a')
            assert len(link) == 1
            link = link[0].attrib['href']

            image = category.xpath('./a/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            title_data = category.xpath('./a/span[@class="cat-title"]')
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].text)

            number_of_videos = category.xpath('./a/span[@class="cat-title"]/em')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(category_data.url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        channels = tree.xpath('.//div[@class="movies-block"]/ul/li')
        res = []
        for channel in channels:
            link_data = channel.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']

            image = channel.xpath('./a/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            title_data = channel.xpath('./a/b')
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].text)

            number_of_videos = channel.xpath('./em')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            related_categories = channel.xpath('./span/a')

            additional_data = {'site_link': link_data[1].attrib['href'],
                               'related_categories': {x.attrib['title']: x.attrib['href'] for x in related_categories}}

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(channel_data.url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               additional_data=additional_data,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ))

        channel_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = tree.xpath('.//div[@class="models-block"]/ul/li')
        res = []
        for porn_star in porn_stars:
            link_data = porn_star.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']

            image = porn_star.xpath('./a/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            title_data = porn_star.xpath('./a/span')
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].text)

            number_of_videos = porn_star.xpath('./span[@class="count"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(porn_star_data.url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        tree = self.parser.parse(page_request.text)
        tags = tree.xpath('.//div[@class="wrap"]/ul/li')
        res = []
        for tag in tags:
            link_data = tag.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']

            title_data = tag.xpath('./a/em')
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].text)

            number_of_videos = tag.xpath('./a/span')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(tag_data.url, link),
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.TAG,
                                               super_object=tag_data,
                                               ))

        tag_data.add_sub_objects(res)
        return res

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return False

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN,):
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
        return [int(x.text) for x in tree.xpath('.//ul[@class="pagination-list"]/li/a')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//ul[@class="movies-list"]/li[@class="thumb"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']
            max_flip_images = int(re.findall(r'(\d+)(?:\)$)', image_data[0].attrib['onmouseover'])[0])
            flix_image = [re.sub(r'\d.jpg$', '{d}.jpg'.format(d=d), image) for d in range(1, max_flip_images+1)]

            added_before = video_tree_data.xpath('./meta[@itemprop="datePublished"]')
            assert len(added_before) == 1
            added_before = added_before[0].attrib['content']

            video_length = video_tree_data.xpath('./span[@class="duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  added_before=added_before,
                                                  duration=self._format_duration(video_length),
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        if true_object.object_type in (PornCategories.TOP_RATED_VIDEO, PornCategories.MOST_VIEWED_VIDEO,):
            if self.video_filters.videos_filters.current_filters.period.filter_id != PornFilterTypes.AllDate:
                fetch_base_url += self.video_filters.videos_filters.current_filters.period.value + '/'
        if true_object.object_type == PornCategories.PORN_STAR_MAIN:
            if self.video_filters.porn_stars_filters.current_filters.sort_order.filter_id != PornFilterTypes.DateOrder:
                fetch_base_url += self.video_filters.porn_stars_filters.current_filters.sort_order.value + '/'

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Referer': page_data.url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        if page_number is not None and page_number != 1:
            if fetch_base_url == self.base_url:
                fetch_base_url += 'latest-updates/'
            fetch_base_url += '{d}/'.format(d=page_number)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request


class MegaTubeXXX(PervertSluts):
    # Belongs to the AnyPorn network
    # todo: add playlists, webcams
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/porn-review'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/pornstars'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/new-videos'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/popular-videos'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-videos'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
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
        return 'https://www.megatube.xxx/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        channels_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Recently updated', 'last_content_date'),
                                          (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.ViewsOrder, 'Most viewed', 'avg_videos_popularity'),
                                          (PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          ],
                           }
        porn_stars_params = {'general_filters': [(PornFilterTypes.GirlType, 'Females', '0'),
                                                 (PornFilterTypes.GuyType, 'Males', '1'),
                                                 (PornFilterTypes.AllType, 'All', ''),
                                                 ],
                             'sort_order': [(PornFilterTypes.RatingOrder, 'Top Rated', 'avg_videos_rating'),
                                            (PornFilterTypes.ViewsOrder, 'Most Viewed', 'avg_videos_popularity'),
                                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                            ],
                             }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       ],
                        'period_filters': ([(PornFilterTypes.AllDate, 'All time', ''),
                                            (PornFilterTypes.OneDate, 'This Month', '_month'),
                                            (PornFilterTypes.TwoDate, 'This week', '_week'),
                                            (PornFilterTypes.ThreeDate, 'Today', '_today'),
                                            ],
                                           [('sort_order', [PornFilterTypes.RatingOrder,
                                                            PornFilterTypes.ViewsOrder])]
                                           ),
                        'length_filters': [(PornFilterTypes.AllLength, 'Any length', None),
                                           (PornFilterTypes.OneLength, '0-10', 'duration_to=600'),
                                           (PornFilterTypes.TwoLength, '10-40', 'duration_from=600&duration_to=2400'),
                                           (PornFilterTypes.ThreeLength, '40+', 'duration_from=2400'),
                                           ],
                        }
        search_params = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Most Relevant', ''),
                                        (PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'video_viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        ],
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_params,
                                         channels_args=channels_params,
                                         single_category_args=video_params,
                                         single_porn_star_args=video_params,
                                         single_channel_args=video_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='MegaTubeXXX', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(MegaTubeXXX, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        return self._get_video_links_from_video_data4(video_data)

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div/div[@class="item  "]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1

            image_data = link_data[0].xpath('./div[@class="img js-videoPreview"]')
            assert len(image_data) == 1
            image = image_data[0].xpath('./img')[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].xpath('./img')[0].attrib['data-original']
            flip_images = [x.attrib['data-src']
                           for x in image_data[0].xpath('./ul[@class="thumb-slider-screenshots"]/li')]
            video_preview = image_data[0].xpath('./div[@class="thumb-video-info"]')[0].attrib['data-mediabook']

            video_length = image_data[0].xpath('./div[@class="item__flags"]/span[@class="item__flag--duration"]')
            assert len(video_length) >= 1

            title = link_data[0].attrib['title']

            number_of_views = video_tree_data.xpath('./div[@class="wrap last-wrap"]/div[@class="views"]/i')
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].tail)

            added_before = video_tree_data.xpath('./div[@class="wrap last-wrap"]/div[@class="added"]')
            assert len(added_before) == 1
            added_before = self._clear_text(added_before[0].text)

            porn_stars = [{'name': x.text, 'url': x.attrib['href']}
                          for x in video_tree_data.xpath('./div[@class="wrap"]/div[@class="model-name"]/a')]
            channel = [{'name': x.text, 'url': x.attrib['href']}
                       for x in video_tree_data.xpath('./div[@class="wrap"]/div[@class="paysite-name"]/a')]
            channel = channel[0] if len(channel) > 0 else None
            additional_data = {'porn_stars': porn_stars, 'channel': channel}

            video_data = PornCatalogVideoPageNode(
                catalog_manager=self.catalog_manager,
                obj_id=re.findall(r'\d+', link_data[0].attrib['href'])[0],
                title=title,
                url=urljoin(self.base_url, link_data[0].attrib['href']),
                image_link=image,
                flip_images_link=flip_images,
                preview_video_link=video_preview,
                duration=self._format_duration(video_length[-1].text),
                additional_data=additional_data,
                added_before=added_before,
                number_of_views=number_of_views,
                object_type=PornCategories.VIDEO,
                super_object=page_data,
            )
            res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        if true_object.object_type == PornCategories.SEARCH_MAIN:
            headers = {
                'Accept': '*.*',
                'Cache-Control': 'max-age=0',
                'Referer': self.base_url,
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
            conditions = self.get_proper_filter(page_data).conditions
            true_sort_filter_id = self._default_sort_by[true_object.object_type] \
                if true_object.object_type in self._default_sort_by \
                else page_filter.sort_order.filter_id

            if page_number is None:
                page_number = 1
            params.update({
                    'mode': 'async',
                    'function': 'get_block',
                })
            if page_filter.length.value is not None:
                params.update(parse_qsl(page_filter.length.value))

            params['block_id'] = 'list_videos_videos_list_search_result'
            params['q'] = self._search_query
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            return super(MegaTubeXXX, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                    page_filter, fetch_base_url)

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        res = super(MegaTubeXXX, self)._prepare_new_search_query(query.replace(' ', '-'))
        self._search_query = query
        return res


class TubeWolf(AlphaPorno):
    max_flip_images = 10
    videos_per_video_page = 100

    @property
    def object_urls(self):
        return {
            PornCategories.PORN_STAR_MAIN: 'https://www.tubewolf.com/pornstars/',
            PornCategories.LATEST_VIDEO: 'https://www.tubewolf.com/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.tubewolf.com/top-rated/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.tubewolf.com/most-popular/',
            PornCategories.LONGEST_VIDEO: 'https://www.tubewolf.com/longest/',
            PornCategories.SEARCH_MAIN: 'https://www.tubewolf.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
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
        return 'https://www.tubewolf.com/'

    @property
    def max_pages(self):
        return 200

    def __init__(self, source_name='TubeWolf', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(TubeWolf, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//ul[@class="pagination"]/li/a')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumb-list"]/div[@class="thumb"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']
            max_flip_images = int(re.findall(r'(\d+)(?:\)$)', image_data[0].attrib['onmouseover'])[0])
            flix_image = [re.sub(r'\d.jpg$', '{d}.jpg'.format(d=d), image) for d in range(1, max_flip_images+1)]

            added_before = video_tree_data.xpath('./meta[@itemprop="datePublished"]')
            assert len(added_before) == 1
            added_before = added_before[0].attrib['content']

            video_length = video_tree_data.xpath('./span[@class="duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  added_before=added_before,
                                                  duration=self._format_duration(video_length),
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res


class XBabe(AnyPorn):
    max_flip_images = 10
    videos_per_video_page = 100

    @property
    def object_urls(self):
        return {
            PornCategories.TAG_MAIN: 'https://xbabe.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://xbabe.com/models/',
            PornCategories.LATEST_VIDEO: 'https://xbabe.com/videos/',
            PornCategories.BEING_WATCHED_VIDEO: 'https://xbabe.com/videos/watched-now/',
            PornCategories.TOP_RATED_VIDEO: 'https://xbabe.com/videos/top-rated/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://xbabe.com/videos/most-viewed/',
            PornCategories.LONGEST_VIDEO: 'https://xbabe.com/videos/longest/',
            PornCategories.SEARCH_MAIN: 'https://xbabe.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.BEING_WATCHED_VIDEO: PornFilterTypes.BeingWatchedOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        model_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Recently updated', 'last_content_date'),
                                       (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'model_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       ],
                        }
        video_params = {'period_filters': [(PornFilterTypes.ThreeDate, 'Today', '_today'),
                                           (PornFilterTypes.TwoDate, 'This week', '_week'),
                                           (PornFilterTypes.OneDate, 'This Month', '_month'),
                                           (PornFilterTypes.AllDate, 'All time', ''),
                                           ],
                        }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=model_params,
                                         video_args=video_params,
                                         )

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://xbabe.com/'

    @property
    def max_pages(self):
        return 2000

    def __init__(self, source_name='XBabe', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(XBabe, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//div[@class="categories-paragraph"]/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, None)
                                                for x in raw_data])
        return links, titles, number_of_videos

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="item-ourgirls ourgirls-thumb"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].text

            image_data = category.xpath('./em/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(porn_star_data.url, link),
                                                      title=title,
                                                      image_link=image,
                                                      object_type=PornCategories.PORN_STAR,
                                                      super_object=porn_star_data,
                                                      )
            res.append(sub_object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        return self._get_video_links_from_video_data3(video_data)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN,):
            return 1
        try:
            page_request = self.get_object_request(category_data, send_error=False) if fetched_request is None \
                else fetched_request
        except PornFetchUrlError:
            return 1
        tree = self.parser.parse(page_request.text)
        if category_data.object_type in (PornCategories.TAG, PornCategories.PORN_STAR):
            available_pages = self._get_available_pages_from_tree(tree)
            return max(available_pages) if len(available_pages) > 0 else 1
        # elif category_data.object_type in (LatestVideo, BeingWatchedVideo, TopRatedVideo, MostViewedVideo,
        #                                    LongestVideo):
        #     total_number_of_videos = tree.xpath('.//ul[@class="site-stats"]/li[2]/a/span')
        #     total_number_of_videos = (int(total_number_of_videos[0].text) +
        #                               (int(total_number_of_videos[1].text[1:])
        #                                if len(total_number_of_videos[1].text[1:]) > 0 else 0)
        #                               )
        #     return math.ceil(total_number_of_videos / self.videos_per_video_page)
        else:
            # We have a porn star page
            return self._binary_search_max_number_of_pages(category_data)

    def _binary_search_max_number_of_pages(self, category_data):
        """
        Performs binary search in order to find the last available page.
        :param category_data: Category data.
        :return: Page request
        """
        left_page = 1
        right_page = self.max_pages
        while 1:
            page = math.ceil((right_page + left_page) / 2)
            try:
                self.get_object_request(category_data, override_page_number=page, send_error=False)
                left_page = page
                if left_page == right_page:
                    return left_page
            except PornFetchUrlError:
                # We moved too far...
                right_page = page - 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text)
                for x in tree.xpath('.//div[@class="pagination"]/*') +
                tree.xpath('.//div[@class="pagination-bar"]/ul/li/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        res = []
        videos = tree.xpath('.//div[@class="thumb-big"]')
        method = 1
        if len(videos) == 0:
            method = 2
            videos = tree.xpath('.//div[@class="videos-related-holder"]/div[@class="block_content"]/a')
        if len(videos) == 0:
            method = 3
            videos = tree.xpath('.//div[@class="block_content"]/a')
        if len(videos) == 0:
            method = 4
            videos = tree.xpath('.//div[@class="thumb-holder"]/div')

        if method == 1:
            # Method 1
            for video_tree_data in videos:
                link_data = video_tree_data.xpath('./a')
                assert len(link_data) == 1
                link = link_data[0].attrib['href']
                title = link_data[0].text

                image_data = video_tree_data.xpath('./div[@class="image"]/span[@class="image-holder"]/img')
                assert len(image_data) == 1
                image = image_data[0].attrib['src']
                flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                               for d in range(1, int(re.findall(r'(\d+)(?:\)$)',
                                                                image_data[0].attrib['onmouseover'])[0]) + 1)] \
                    if 'onmouseover' in image_data[0].attrib else None

                video_length = video_tree_data.xpath('./div[@class="image"]/span[@class="duration"]')
                assert len(video_length) == 1
                video_length = video_length[0].text

                added_before = video_tree_data.xpath('./div[@class="info"]/span[@class="added"]')
                assert len(added_before) == 1
                added_before = added_before[0].text

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(page_data.url, link),
                                                      title=title,
                                                      image_link=image,
                                                      flip_images_link=flip_images,
                                                      duration=self._format_duration(video_length),
                                                      added_before=added_before,
                                                      object_type=PornCategories.VIDEO,
                                                      super_object=page_data,
                                                      )
                res.append(video_data)
        elif method in (2, 3):
            # Method 2
            for video_tree_data in videos:
                link = video_tree_data.attrib['href']

                image_data = video_tree_data.xpath('./span[@class="image"]/span[@class="image-holder"]/img')
                assert len(image_data) == 1
                image = image_data[0].attrib['src']
                flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                               for d in range(1, int(re.findall(r'(\d+)(?:\)$)',
                                                                image_data[0].attrib['onmouseover'])[0]) + 1)]

                video_length = video_tree_data.xpath('./span[@class="image"]/span[@class="duration"]')
                assert len(video_length) == 1
                video_length = video_length[0].text

                title = video_tree_data.xpath('./span[@class="info"]/h3')
                assert len(title) == 1
                title = title[0].text

                added_before = video_tree_data.xpath('./span[@class="info"]/span[@class="added"]')
                assert len(added_before) == 1
                added_before = added_before[0].text

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(page_data.url, link),
                                                      title=title,
                                                      image_link=image,
                                                      flip_images_link=flip_images,
                                                      duration=self._format_duration(video_length),
                                                      added_before=added_before,
                                                      object_type=PornCategories.VIDEO,
                                                      super_object=page_data,
                                                      )
                res.append(video_data)

        elif method == 4:
            # Method 3
            for video_tree_data in videos:
                link_data = video_tree_data.xpath('./a')
                assert len(link_data) == 1
                link = link_data[0].attrib['href']

                title_data = video_tree_data.xpath('./a/span')
                assert len(title_data) == 1
                title = title_data[0].text

                image_data = video_tree_data.xpath('./span[@class="img"]/img')
                assert len(image_data) == 1
                image = image_data[0].attrib['src']
                description = image_data[0].attrib['alt']

                preview_data = video_tree_data.xpath('./span[@class="video"]/video')
                assert len(preview_data) == 1
                preview_link = preview_data[0].attrib['src']

                number_of_views = video_tree_data.xpath('./span[@class="info"]/span[@class="views"]')
                assert len(number_of_views) == 1
                number_of_views = number_of_views[0].text

                rating = video_tree_data.xpath('./span[@class="info"]/span[@class="rating"]')
                assert len(rating) == 1
                rating = rating[0].text

                is_hd = video_tree_data.xpath('./span[@class="info"]/span[@class="quality"]')
                assert len(is_hd) == 1
                is_hd = is_hd[0].text == 'HD'

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(page_data.url, link),
                                                      title=title,
                                                      description=description,
                                                      image_link=image,
                                                      preview_video_link=preview_link,
                                                      number_of_views=number_of_views,
                                                      is_hd=is_hd,
                                                      rating=rating,
                                                      object_type=PornCategories.VIDEO,
                                                      super_object=page_data,
                                                      )
                res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        if true_object.object_type in (PornCategories.TAG, PornCategories.TAG_MAIN,
                                       PornCategories.SEARCH_MAIN, PornCategories.VIDEO):
            # params['block_id'] = 'list_content_sources_sponsors_list'
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3*',
                'Cache-Control': 'max-age=0',
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }
            if page_number is not None and page_number > 1:
                fetch_base_url = (fetch_base_url + ('/' if fetch_base_url[-1] != '/' else '') +
                                  '{d}/'.format(d=page_number))

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        elif true_object.object_type in (PornCategories.PORN_STAR, PornCategories.PORN_STAR_MAIN,
                                         PornCategories.MOST_VIEWED_VIDEO, PornCategories.LONGEST_VIDEO,
                                         PornCategories.LATEST_VIDEO, PornCategories.BEING_WATCHED_VIDEO,
                                         PornCategories.TOP_RATED_VIDEO,):
            # return super(XBabe, self).get_object_request(object_data, override_page)
            # Slight change: instead of the 'function' param, here it is 'action'...
            conditions = self.get_proper_filter(page_data).conditions
            true_sort_filter_id = self._default_sort_by[true_object.object_type] \
                if true_object.object_type in self._default_sort_by \
                else page_filter.sort_order.filter_id

            headers = {
                'Accept': '*.*',
                'Cache-Control': 'max-age=0',
                'Referer': self.base_url,
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
            if page_number is None:
                page_number = 1
            params.update({
                'mode': 'async',
                'action': 'get_block',
            })
            if page_number > 1:
                params['from'] = str(page_number).zfill(2)

            fetch_base_url = 'https://xbabe.com/content_load.php'
            if true_object.object_type == PornCategories.PORN_STAR:
                params['block_id'] = 'list_videos_model_videos'
                params['dir'] = page_data.url.split('/')[-2]
                fetch_base_url = 'https://xbabe.com/view_model_2.php'
            elif true_object.object_type == PornCategories.PORN_STAR_MAIN:
                params['block_id'] = 'list_models_models_list'
                params['sort_by'] = page_filter.sort_order.value
            elif true_object.object_type == PornCategories.LONGEST_VIDEO:
                params['block_id'] = 'list_videos_common_videos_list'
                params['sort_by'] = 'duration'
            elif true_object.object_type == PornCategories.LATEST_VIDEO:
                params['block_id'] = 'list_videos_common_videos_list'
                params['sort_by'] = 'post_date'
            elif true_object.object_type == PornCategories.BEING_WATCHED_VIDEO:
                params['block_id'] = 'list_videos_common_videos_list'
                params['sort_by'] = 'last_time_view_date'
            elif true_object.object_type == PornCategories.TOP_RATED_VIDEO:
                params['block_id'] = 'list_videos_common_videos_list'
                params['sort_by'] = 'rating'
            elif true_object.object_type == PornCategories.MOST_VIEWED_VIDEO:
                params['block_id'] = 'list_videos_common_videos_list'
                params['sort_by'] = 'video_viewed'

            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            raise ValueError('Wrong object type {ot}!'.format(ot=true_object.object_type))

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


class BravoPorn(AnyPorn):
    more_categories_url = 'https://www.bravoporn.com/v/devbmg_desktop_categories_helper.php?sort_by=sort_id'

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.bravoporn.com/c/',
            PornCategories.TAG_MAIN: 'https://www.bravoporn.com/c/',
            PornCategories.PORN_STAR_MAIN: 'https://www.bravoporn.com/models/',
            PornCategories.LATEST_VIDEO: 'https://www.bravoporn.com/latest-updates/',
            PornCategories.POPULAR_VIDEO: 'https://www.bravoporn.com/most-popular/',
            PornCategories.SEARCH_MAIN: 'https://www.bravoporn.com/s/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.bravoporn.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        category_params = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          (PornFilterTypes.VideosPopularityOrder, 'Videos Popularity',
                                           'avg_videos_popularity'),
                                          (PornFilterTypes.VideosRatingOrder, 'Videos Rating', 'avg_videos_rating'),
                                          ],
                           }
        single_category_params = {'sort_order': [(PornFilterTypes.ViewsOrder, 'Most Viewed First', None),
                                                 (PornFilterTypes.RecommendedOrder, 'Recommended first', 'recommended'),
                                                 (PornFilterTypes.VideosRatingOrder, 'Top Rated first', 'top-rated'),
                                                 (PornFilterTypes.DateOrder, 'Recent first', 'latest'),
                                                 ],
                                  }
        model_params = {'sort_order': [(PornFilterTypes.VideosPopularityOrder, 'Videos Popularity',
                                        'avg_videos_popularity'),
                                       (PornFilterTypes.VideosRatingOrder, 'Videos rating', 'avg_videos_rating'),
                                       (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                       (PornFilterTypes.PopularityOrder, 'Popularity', 'model_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                       (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                       ],
                        }
        video_params = {'period_filters': ([(PornFilterTypes.ThreeDate, 'Today', 'today'),
                                            (PornFilterTypes.TwoDate, 'This week', 'week'),
                                            (PornFilterTypes.OneDate, 'This Month', 'month'),
                                            (PornFilterTypes.AllDate, 'All time', 'alltime'),
                                            ],
                                           [('sort_order', [PornFilterTypes.PopularityOrder])]
                                           ),
                        }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_params,
                                         single_category_args=single_category_params,
                                         # single_tag_args=single_category_params,
                                         porn_stars_args=model_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='BravoPorn', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(BravoPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories1 = tree.xpath('.//div[@class="th-wrap"]/a')

        headers = {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        page_request2 = self.session.get(self.more_categories_url, headers=headers)
        tree2 = self.parser.parse(page_request2.text)
        categories2 = tree2.xpath('./body/a')

        categories = categories1 + categories2
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="in-mod"]/strong/span')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].tail)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))
        res.sort(key=lambda x: x.title)
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="th-wrap"]/a')

        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="in-mod"]/strong/span')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].tail)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="list-tags"]/ul/li/a')
        links = [x.attrib['href'] for x in raw_objects]
        titles = [x.text for x in raw_objects]
        number_of_videos = [None] * len(titles)
        assert len(titles) == len(links)
        # assert len(titles) == len(number_of_videos)

        return links, titles, number_of_videos

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN,):
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
        return [int(x.text) for x in tree.xpath('.//div[@class="pager"]/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="th-wrap"]/div[@class="video_block"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']
            if 'onmouseover' in image_data[0].attrib:
                max_flip_images = int(re.findall(r'(\d+)(?:\)$)', image_data[0].attrib['onmouseover'])[0])
                flix_image = [re.sub(r'\d.jpg$', '{d}.jpg'.format(d=d), image) for d in range(1, max_flip_images+1)]
            else:
                flix_image = None
            is_hd = video_tree_data.xpath('./div[@class="hd"]')
            is_hd = len(is_hd) == 1

            video_length = video_tree_data.xpath('./div[@class="on"]/span')
            assert len(video_length) == 1
            video_length = video_length[0].text

            rating = video_tree_data.xpath('./em')
            assert len(rating) == 1
            rating = rating[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  is_hd=is_hd,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id
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

        if true_object.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.PORN_STAR_MAIN,):
            params['sort_by'] = page_filter.sort_order.value
        if true_object.object_type in (PornCategories.CATEGORY, PornCategories.TAG):
            if page_filter.sort_order.value is not None:
                fetch_base_url += page_filter.sort_order.value + '/'
        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            fetch_base_url += page_filter.period.value + '/'
        if page_number is not None and page_number != 1:
            fetch_base_url = re.sub(r'/*\d*/$', '/{d}/'.format(d=page_number), fetch_base_url)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


class XCum(XBabe):
    max_flip_images = 6

    @property
    def object_urls(self):
        return {
            PornCategories.TAG_MAIN: 'https://xcum.com/t/',
            PornCategories.LATEST_VIDEO: 'https://xcum.com/',
            PornCategories.SEARCH_MAIN: 'https://xcum.com/q/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://xcum.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        return super(AnyPorn, self)._set_video_filter()

    def __init__(self, source_name='XCum', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(XCum, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="block_content"]/ul/li/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            title = category.xpath('./span')
            assert len(title) == 1
            title = title[0].text

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               object_type=PornCategories.TAG,
                                               super_object=tag_data,
                                               ))
        tag_data.add_sub_objects(res)
        return res

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return False

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN,):
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
        return [int(x.text) for x in tree.xpath('.//nav[@class="pagination pignr"]/div/*') +
                tree.xpath('.//div[@class="pagination"]/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        method = 1
        videos = tree.xpath('.//div[@class="thumbs"]/div/div[@class="thumb"]/a')
        if len(videos) == 0:
            method = 2
            videos = tree.xpath('.//div[@class="thumbs"]/div[@class="thumb"]')
        res = []
        if method == 1:
            for video_tree_data in videos:
                link = video_tree_data.attrib['href']

                image_data = video_tree_data.xpath('./picture/img')
                assert len(image_data) == 1
                image = image_data[0].attrib['data-original']
                description = image_data[0].attrib['alt']
                flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                               for d in range(1, self.max_flip_images + 1)]

                preview_data = video_tree_data.xpath('./video')
                assert len(preview_data) == 1
                preview_video = preview_data[0].attrib['src']

                info_data = video_tree_data.xpath('./span[@class="inf"]/span')
                assert len(info_data) == 4
                title = info_data[0].text
                video_length = info_data[2].text
                number_of_likes = info_data[3].text

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      description=description,
                                                      image_link=image,
                                                      flip_images_link=flip_images,
                                                      preview_video_link=preview_video,
                                                      duration=self._format_duration(video_length),
                                                      number_of_likes=number_of_likes,
                                                      object_type=PornCategories.VIDEO,
                                                      super_object=page_data,
                                                      )
                res.append(video_data)
        elif method == 2:
            for video_tree_data in videos:
                link_data = video_tree_data.xpath('./a')
                assert len(link_data) == 1
                link = link_data[0].attrib['href']

                image_data = video_tree_data.xpath('./a/img')
                assert len(image_data) == 1
                image = image_data[0].attrib['data-original']
                description = image_data[0].attrib['alt']
                flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                               for d in range(1, int(re.findall(r'(\d+)(?:\)$)',
                                                                image_data[0].attrib['onmouseover'])[0]) + 1)] \
                    if 'onmouseover' in image_data[0].attrib else None

                preview_data = video_tree_data.xpath('./a/video')
                assert len(preview_data) == 1
                preview_video = preview_data[0].attrib['src']

                title_data = video_tree_data.xpath('./div[@class="btn-info btn-trailer"]/div/b')
                assert len(title_data) == 1
                title = title_data[0].text

                info_data = video_tree_data.xpath('./div[@class="btn-info btn-trailer"]/div/span[@class="thumb-info"]/'
                                                  'span')
                assert len(info_data) == 2
                video_length = info_data[0].text
                number_of_likes = info_data[1].text

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      description=description,
                                                      image_link=image,
                                                      flip_images_link=flip_images,
                                                      preview_video_link=preview_video,
                                                      duration=self._format_duration(video_length),
                                                      number_of_likes=number_of_likes,
                                                      object_type=PornCategories.VIDEO,
                                                      super_object=page_data,
                                                      )
                res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
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
        if page_number is not None and page_number != 1:
            fetch_base_url = re.sub(r'/$', '', fetch_base_url)
            fetch_base_url += '/{d}/'.format(d=page_number)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query))


class HellMoms(XBabe):
    max_flip_images = 11

    @property
    def object_urls(self):
        return {
            PornCategories.TAG_MAIN: 'https://hellmoms.com/',
            PornCategories.LATEST_VIDEO: 'https://hellmoms.com/',
            PornCategories.SEARCH_MAIN: 'https://hellmoms.com/q/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://hellmoms.com/'

    def __init__(self, source_name='HellMoms', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HellMoms, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="block-menu"]/ul/li/a')
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x.attrib['href'],
                                       url=urljoin(tag_data.url, x.attrib['href']),
                                       title=x.text,
                                       object_type=PornCategories.TAG,
                                       super_object=tag_data,
                                       ) for x in categories]
        tag_data.add_sub_objects(res)
        return res

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return False

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN,):
            return 1
        try:
            page_request = self.get_object_request(category_data, send_error=False) if fetched_request is None \
                else fetched_request
        except PornFetchUrlError:
            return 1
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//div[@class="pagination"]/*/text()') if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        res = []
        videos = tree.xpath('.//div[@class="thumb-holder"]/div[@class="thumb"]')
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            title_data = video_tree_data.xpath('./a/span')
            assert len(title_data) == 1
            title = title_data[0].text

            image_data = video_tree_data.xpath('./span[@class="img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            description = image_data[0].attrib['alt']
            flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                           for d in range(1, self.max_flip_images + 1)]

            preview_data = video_tree_data.xpath('./span[@class="video"]/video')
            assert len(preview_data) == 1
            preview_link = preview_data[0].attrib['src']

            video_length = video_tree_data.xpath('./span[@class="duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            rating_data = video_tree_data.xpath('./span[@class="video-rating "]/span')
            assert len(rating_data) == 1
            rating = re.findall(r'\d+%', rating_data[0].attrib['style'])

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  description=description,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=preview_link,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Referer': page_data.url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_number is not None and page_number != 1:
            fetch_base_url = (fetch_base_url + ('/' if fetch_base_url[-1] != '/' else '') +
                              '{d}/'.format(d=page_number))

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query))


class PornPlus(HellMoms):
    max_flip_images = 10

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.porn-plus.com/c/',
            PornCategories.TAG_MAIN: 'https://www.porn-plus.com/c/',
            PornCategories.PORN_STAR_MAIN: 'https://www.porn-plus.com/p/',
            PornCategories.LATEST_VIDEO: 'https://www.porn-plus.com/fresh/',
            PornCategories.TRENDING_VIDEO: 'https://www.porn-plus.com/trending/',
            PornCategories.SEARCH_MAIN: 'https://www.porn-plus.com/s/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.TRENDING_VIDEO: PornFilterTypes.TrendingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.porn-plus.com/'

    def __init__(self, source_name='PornPlus', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornPlus, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="thmbclck"]/div[@class="thmb"]/a',
                                                  PornCategories.CATEGORY,
                                                  True)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@class="thmbclck"]/div[@class="thmb"]/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_base_object(self, object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        for category in categories:
            link = category.attrib['href']
            title = category.attrib['title']

            image_data = category.xpath('./img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(object_data.url, link),
                                                      title=title,
                                                      image_link=image,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        if is_sort:
            res.sort(key=lambda x: x.title)
        object_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="tagslist"]/ul/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.attrib['title'], None) for x in raw_objects])

        return links, titles, number_of_videos

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN, PornCategories.CATEGORY_MAIN):
            return 1
        try:
            page_request = self.get_object_request(category_data, send_error=False) if fetched_request is None \
                else fetched_request
        except PornFetchUrlError:
            return 1
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(re.findall(r'(\d+)(?:/\?*)', x.attrib['href'])[-1])
                for x in tree.xpath('.//div[@class="pgntn-hlder"]/ul/li/a')
                if len(re.findall(r'(\d+)(?:/\?*)', x.attrib['href'])) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        res = []
        videos = tree.xpath('.//div[@class="thmbclck"]/div[@class="thmb"]/a')
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            # title_data = video_tree_data.xpath('./h3')
            # assert len(title_data) == 1
            # title = title_data[0].text

            image_data = video_tree_data.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            description = image_data[0].attrib['alt']
            flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                           for d in range(1, self.max_flip_images + 1)]
            title = image_data[0].attrib['alt']

            video_length = video_tree_data.xpath('./div[@class="video_time"]/span')
            assert len(video_length) == 1
            video_length = video_length[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  description=description,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  duration=self._format_duration(video_length),
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


class TropicTube(PervertSluts):
    # Some of the models we took from AnyPorn module (has thee same structure)
    flip_number = 30

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/c/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/sites/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/longest/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.tropictube.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        category_params = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            ],
             }
        porn_stars_params = \
            {'sort_order': [(PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            ],
             }
        search_params = \
            {'sort_order': [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                            (PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                            (PornFilterTypes.ViewsOrder, 'Most Viewed', 'video_viewed'),
                            (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                            (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                            (PornFilterTypes.FavorOrder, 'Most Favourite', 'most_favourited'),
                            ],
             }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_params,
                                         channels_args=category_params,
                                         porn_stars_args=porn_stars_params,
                                         search_args=search_params,
                                         )

    def __init__(self, source_name='TropicTube', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(TropicTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="list-videos"]/div[@class="margin-fix"]/div/a',
                                                  PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="list-videos"]/div[@class="margin-fix"]/div/a',
                                                  PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="list-albums list-models"]/div[@class="margin-fix"]/a')
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None
            title = category.xpath('./div[@class="img"]/div[@class="name"]')[0].text

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      object_type=PornCategories.PORN_STAR,
                                                      super_object=porn_star_data,
                                                      )
            res.append(sub_object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_base_object(self, object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None
            title = category.attrib['title'].title() \
                if 'title' in category.attrib else image_data[0].attrib['alt'].title()

            number_of_videos = category.xpath('./span[@class="img"]/span[@class="bottom_info"]/span[@class="title"]/'
                                              'span[@class="videos_count"]')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].text)[0]) if len(number_of_videos) > 0 else None

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        if is_sort:
            res.sort(key=lambda x: x.title)
        object_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        return self._get_video_links_from_video_data2(video_data)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN,):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        elif max(pages) - 1 < self._binary_search_page_threshold:
            return max(pages)
        else:
            return self._binary_search_max_number_of_pages(category_data)

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
        # Took from AnyPorn module with somme modifications...
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div[@class="margin-fix"]/div[@class="item  "]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title'] if 'title' in link_data[0].attrib else None

            image_data = link_data[0].xpath('./span[@class="img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, self.flip_number + 1)]
            if title is None:
                title = image_data[0].attrib['alt']

            data_info = link_data[0].xpath('./span[@class="img"]/span[@class="big-info"]')
            assert len(data_info) == 1

            video_length = data_info[0].xpath('./span[@class="video_title"]/span[@class="duration"]')
            assert len(video_length) == 1
            video_length = self._format_duration(self._clear_text(video_length[0].text))

            rating = data_info[0].xpath('./span[@class="video_title"]/span[@class="rating"]')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].text)

            additional_data = data_info[0].xpath('./span[@class="thumb_info"]/em')
            assert len(additional_data) == 3
            number_of_views = int(additional_data[1].text.replace(' ', ''))
            added_before = additional_data[2].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  duration=video_length,
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
        if true_object.object_type == PornCategories.SEARCH_MAIN:
            headers = {
                'Accept': '*.*',
                'Cache-Control': 'max-age=0',
                'Referer': self.base_url,
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
            conditions = self.get_proper_filter(page_data).conditions
            true_sort_filter_id = self._default_sort_by[true_object.object_type] \
                if true_object.object_type in self._default_sort_by \
                else page_filter.sort_order.filter_id

            if page_number is None:
                page_number = 1
            params.update({
                    'mode': 'async',
                    'function': 'get_block',
                })
            if page_filter.length.value is not None:
                params.update(parse_qsl(page_filter.length.value))

            params['block_id'] = 'list_videos_videos_list_search_result'
            params['q'] = self._search_query
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            return super(TropicTube, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                   page_filter, fetch_base_url)

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw number, i.e. '7m:58s'.
        :return:
        """
        return super(AnyPorn, self)._format_duration(raw_duration)

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query.replace(' ', '-')))


class ZedPorn(AnyPorn):
    max_flip_images = 10
    videos_per_video_page = 100

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/longest/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       ],
                        'period_filters': ([(PornFilterTypes.AllDate, 'All time', None),
                                            (PornFilterTypes.OneDate, 'This Month', 'month'),
                                            (PornFilterTypes.TwoDate, 'This week', 'week'),
                                            (PornFilterTypes.ThreeDate, 'Today', 'today'),
                                            ],
                                           [('sort_order', [PornFilterTypes.RatingOrder,
                                                            PornFilterTypes.ViewsOrder])]
                                           ),
                        }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         video_args=video_params,
                                         )

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://zedporn.com/'

    @property
    def max_pages(self):
        return 2000

    def __init__(self, source_name='ZedPorn', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(ZedPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="smovies-list"]/ul/li/a')
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('span[@class="img-shadow"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None
            title = category.attrib['title'].title() \
                if 'title' in category.attrib else image_data[0].attrib['alt'].title()

            number_of_videos = category.xpath('./i')
            number_of_videos = int(number_of_videos[0].text) if len(number_of_videos) > 0 else None

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      object_type=PornCategories.CATEGORY,
                                                      super_object=category_data,
                                                      )
            res.append(sub_object_data)
        category_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        return self._get_video_links_from_video_data3(video_data)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN,):
            return 1
        try:
            page_request = self.get_object_request(category_data, send_error=False) if fetched_request is None \
                else fetched_request
        except PornFetchUrlError:
            return 1
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text)
                for x in tree.xpath('.//ul[@class="pagination-list"]/li/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        res = []
        videos = tree.xpath('.//div[@class="smovies-list"]/ul/li')
        # Method 1
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title']

            image_data = link_data[0].xpath('./span[@class="img-shadow"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                           for d in range(1, int(re.findall(r'(\d+)(?:\)$)',
                                                            image_data[0].attrib['onmouseover'])[0]) + 1)] \
                if 'onmouseover' in image_data[0].attrib else None

            video_length = video_tree_data.xpath('./div[@class="intro_th"]/span[@class="duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            rating = [x for x in video_tree_data.xpath('./div[@class="intro_th"]/span')
                      if 'class' in x.attrib and 'rate' in x.attrib['class']]
            rating = rating[0].text if len(rating) == 1 else None

            additional_data = video_tree_data.xpath('./div[@class="info_th"]/p[2]/*')
            assert len(additional_data) == 2
            added_before = additional_data[0].text
            number_of_views = additional_data[1].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  duration=self._format_duration(video_length),
                                                  added_before=added_before,
                                                  rating=rating,
                                                  number_of_views=number_of_views,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id
        if true_object.object_type not in self._default_sort_by:
            if page_filter.sort_order.value is not None:
                split_url.insert(-1, page_filter.sort_order.value)
        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            split_url.insert(-1, page_filter.period.value)

        if page_number is not None and page_number > 1:
            split_url.insert(-1, str(page_number))
        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


class PornFd(PervertSluts):
    # Some of the models we took from AnyPorn module (has thee same structure)
    flip_number = 15

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.pornfd.com/'

    def _prepare_filters(self):
        """
        Prepares the filters
        :return:
        """
        video_sort_order = [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                            (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                            (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                            (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                            (PornFilterTypes.FavorOrder, 'Most Favorite', 'most_favourited'),
                            ]
        search_sort_order = [(PornFilterTypes.RelevanceOrder, 'Most Relevant', '')] + video_sort_order
        video_period = ([(PornFilterTypes.AllDate, 'All time', ''),
                         (PornFilterTypes.OneDate, 'This Month', '_month'),
                         (PornFilterTypes.TwoDate, 'This week', '_week'),
                         (PornFilterTypes.ThreeDate, 'Today', '_today'),
                         ],
                        [('sort_order', [PornFilterTypes.RatingOrder,
                                         PornFilterTypes.ViewsOrder])]
                        )
        category_params = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            ],
             }
        porn_stars_params = \
            {'sort_order': [(PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            ],
             }
        actress_params = None
        channel_params = porn_stars_params
        tag_params = None
        video_params = {'sort_order': video_sort_order,
                        'period_filters': video_period,
                        }
        search_params = {'sort_order': search_sort_order,
                         'period_filters': video_period,
                         }

        return (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
                search_params)

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
         search_params) = self._prepare_filters()
        self._video_filters = \
            PornFilter(data_dir=self.fetcher_data_dir,
                       categories_args=category_params if PornCategories.CATEGORY_MAIN in self.object_urls else None,
                       channels_args=channel_params if PornCategories.CHANNEL_MAIN in self.object_urls else None,
                       porn_stars_args=porn_stars_params
                       if PornCategories.PORN_STAR_MAIN in self.object_urls else None,
                       actresses_args=actress_params if PornCategories.ACTRESS_MAIN in self.object_urls else None,
                       single_category_args=video_params if PornCategories.CATEGORY_MAIN in self.object_urls else None,
                       single_channel_args=video_params if PornCategories.CHANNEL_MAIN in self.object_urls else None,
                       single_porn_star_args=video_params
                       if PornCategories.PORN_STAR_MAIN in self.object_urls else None,
                       single_tag_args=video_params if PornCategories.TAG_MAIN in self.object_urls else None,
                       video_args=video_params,
                       search_args=search_params,
                       )

    def __init__(self, source_name='PornFd', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornFd, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="list-categories"]/div[@class="margin-fix"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="list-channels"]/div[@class="margin-fix"]/div/a',
                                                  PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@class="list-models"]/div[@class="margin-fix"]/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_actresses(self, actress_data):
        return self._update_available_base_object(actress_data,
                                                  './/div[@class="list-models"]/div[@class="margin-fix"]/a',
                                                  PornCategories.ACTRESS)

    def _update_available_base_object(self, object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('div[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None
            title = category.attrib['title'].title() \
                if 'title' in category.attrib else image_data[0].attrib['alt'].title()

            number_of_videos = category.xpath('./div[@class="wrap"]/div[@class="videos"]')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].text)[0]) if len(number_of_videos) > 0 else None

            rating = (category.xpath('./div[@class="wrap"]/div[@class="rating positive"]') +
                      category.xpath('./div[@class="wrap"]/div[@class="rating negative"]'))
            assert len(rating) == 1
            rating = self._clear_text(rating[0].text)

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      rating=rating,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        if is_sort:
            res.sort(key=lambda x: x.title)
        object_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//div[@class="list-tags"]/div[@class="margin-fix"]/ul/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, None)
                                                for x in raw_data])
        return links, titles, number_of_videos

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        return self._get_video_links_from_video_data2(video_data)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        elif max(pages) - 1 < self._binary_search_page_threshold:
            return max(pages)
        else:
            return self._binary_search_max_number_of_pages(category_data)

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
        # Took from AnyPorn module with somme modifications...
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div[@class="margin-fix"]/div[@class="item  "]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title'] if 'title' in link_data[0].attrib else None

            image_data = link_data[0].xpath('./div[@class="img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, self.flip_number + 1)]
            if title is None:
                title = image_data[0].attrib['alt']
            preview = image_data[0].attrib['data-preview'] if 'data-preview' in image_data[0].attrib else None

            is_hd = link_data[0].xpath('./div[@class="img"]/span[@class="is-hd"]')
            is_hd = len(is_hd) > 0 and is_hd[0] == 'HD'

            if title is None:
                title = self._clear_text(link_data[0].xpath('./span[@class="title"]')[0].text)

            data_info = link_data[0].xpath('./div[@class="wrap"]')
            assert len(data_info) == 2

            video_length = data_info[0].xpath('./div[@class="duration"]')
            assert len(video_length) == 1
            video_length = self._format_duration(self._clear_text(video_length[0].text))

            rating = (data_info[0].xpath('./div[@class="rating positive"]') +
                      data_info[0].xpath('./div[@class="rating negative"]') +
                      data_info[0].xpath('./div[@class="rating positive}"]') +
                      data_info[0].xpath('./div[@class="rating negative}"]')
                      )
            assert len(rating) == 1
            rating = self._clear_text(rating[0].text)

            added_before = data_info[1].xpath('./div[@class="added"]/*')[0].text
            number_of_views = int(''.join(re.findall(r'\d+', data_info[1].xpath('./div[@class="views"]')[0].text)))

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=preview,
                                                  is_hd=is_hd,
                                                  duration=video_length,
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
        headers = {
            'Accept': '*.*',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        if page_number is None:
            page_number = 1
        params.update({
            'mode': 'async',
            'function': 'get_block',
        })
        if page_filter.length.value is not None:
            params.update(parse_qsl(page_filter.length.value))
        if page_number > 1:
            params['from'] = str(page_number).zfill(2)

        if true_object.object_type == PornCategories.SEARCH_MAIN:
            params['block_id'] = 'list_videos_videos_list_search_result'
            params['q'] = self._search_query
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            if 'from' in params:
                params.pop('from')
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

        elif true_object.object_type == PornCategories.CHANNEL_MAIN:
            params['block_id'] = 'list_dvds_channels_list'
            params['sort_by'] = page_filter.sort_order.value
        else:
            return super(PornFd, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                               page_filter, fetch_base_url)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw number, i.e. '7m:58s'.
        :return:
        """
        return super(AnyPorn, self)._format_duration(raw_duration)

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query.replace(' ', '-')))


class ZeroDaysPorn(PornFd):
    max_flip_images = 30
    videos_per_video_page = 31

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://0dayporn.com/'

    @property
    def max_pages(self):
        return 2000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    def _prepare_filters(self):
        """
        Prepares the filters
        :return:
        """
        video_sort_order = [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                            (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                            (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                            (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                            (PornFilterTypes.FavorOrder, 'Most Favorite', 'most_favourited'),
                            ]
        search_sort_order = [(PornFilterTypes.RelevanceOrder, 'Most Relevant', '')] + video_sort_order
        video_period = ([(PornFilterTypes.AllDate, 'All time', ''),
                         (PornFilterTypes.OneDate, 'This Month', '_month'),
                         (PornFilterTypes.TwoDate, 'This week', '_week'),
                         (PornFilterTypes.ThreeDate, 'Today', '_today'),
                         ],
                        [('sort_order', [PornFilterTypes.RatingOrder,
                                         PornFilterTypes.ViewsOrder])]
                        )
        category_params = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            ],
             }
        porn_stars_params = \
            {'sort_order': [(PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            ],
             }
        actress_params = None
        channel_params = porn_stars_params
        tag_params = None
        video_params = {'sort_order': video_sort_order,
                        'period_filters': video_period,
                        }
        search_params = {'sort_order': search_sort_order,
                         'period_filters': video_period,
                         }

        return (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
                search_params)

    def __init__(self, source_name='ZeroDaysPorn', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(ZeroDaysPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)


class PornBimbo(PornFd):
    # Some of the models we took from AnyPorn module (has thee same structure)

    flip_number = 15
    videos_per_video_page = 60

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://pornbimbo.com/'

    def __init__(self, source_name='PornBimbo', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornBimbo, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _binary_search_max_number_of_pages(self, category_data):
        """
        Performs binary search in order to find the last available page.
        :param category_data: Category data.
        :return: Page request
        """
        left_page = 1
        right_page = self.max_pages
        while 1:
            if right_page == left_page:
                return left_page

            page = math.ceil((right_page + left_page) / 2)
            try:
                page_request = self.get_object_request(category_data, override_page_number=page, send_error=False)
                tree = self.parser.parse(page_request.text)
                pages = self._get_available_pages_from_tree(tree)
                if len(pages) == 0:
                    # We just found the final page
                    return page
                else:
                    max_page = max(pages)
                    if max_page - page < self._binary_search_page_threshold:
                        return max_page

                    left_page = max_page
            except PornFetchUrlError:
                # We moved too far...
                right_page = page - 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        xpath = './/div[@class="load-more"]/a'
        return [int(re.findall(r'(?:from.*?:)(\d+)', x.attrib['data-parameters'])[0])
                for x in tree.xpath(xpath)
                if 'data-parameters' in x.attrib and
                len(re.findall(r'(?:from.*?:)(\d+)', x.attrib['data-parameters'])) > 0]

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN,
                                         PornCategories.PORN_STAR_MAIN,):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        elif max(pages) - 1 < self._binary_search_page_threshold:
            return max(pages)
        else:
            return self._binary_search_max_number_of_pages(category_data)

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 1

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        if true_object.object_type in (PornCategories.CATEGORY, PornCategories.PORN_STAR, PornCategories.CHANNEL,
                                       PornCategories.TAG) + \
                tuple(self._default_sort_by.keys()):
            params['ipp'] = self.videos_per_video_page
        return super(PornBimbo, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                              page_filter, fetch_base_url)


class BoundHub(PornFd):
    # Some of the models we took from AnyPorn module (has thee same structure)

    flip_number = 10

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.boundhub.com/'

    def __init__(self, source_name='BoundHub', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(BoundHub, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        return max(pages) if len(pages) > 0 else 1


class EroClips(BoundHub):
    # Some of the models we took from AnyPorn module (has thee same structure)

    flip_number = 10

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.eroclips.org/'

    def __init__(self, source_name='EroClips', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(EroClips, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)


class CamVideosTv(BoundHub):
    flip_number = 10

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        res = super(CamVideosTv, self).object_urls
        res[PornCategories.LATEST_VIDEO] = urljoin(self.base_url, '/recent/')
        res[PornCategories.TOP_RATED_VIDEO] = urljoin(self.base_url, '/rated/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.camvideos.tv/'

    def __init__(self, source_name='CamVideosTv', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(CamVideosTv, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)


class AnonV(BoundHub):
    flip_number = 10

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        res = super(AnonV, self).object_urls
        res.pop(PornCategories.TAG_MAIN)
        res.pop(PornCategories.CHANNEL_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://anon-v.com/'

    def __init__(self, source_name='AnonV', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(AnonV, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)


class MrDeepFake(BoundHub):
    flip_number = 10

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    @property
    def object_urls(self):
        res = super(MrDeepFake, self).object_urls
        res.pop(PornCategories.CHANNEL_MAIN)
        res[PornCategories.LATEST_VIDEO] = urljoin(self.base_url, '/videos')
        res[PornCategories.ACTRESS_MAIN] = urljoin(self.base_url, '/celebrities')
        res[PornCategories.PORN_STAR_MAIN] = urljoin(self.base_url, '/pornstars')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://mrdeepfakes.com/'

    def _prepare_filters(self):
        """
        Prepares the filters
        :return:
        """
        (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
         search_params) = super(MrDeepFake, self)._prepare_filters()
        actress_params = porn_stars_params
        return (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
                search_params)

    def __init__(self, source_name='MrDeepFake', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(MrDeepFake, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        xpath = './/div[@class="pagination"]/div/ul/li/a'
        return ([int(x.attrib['data-parameters'].split(':')[-1])
                for x in tree.xpath(xpath)
                if 'data-parameters' in x.attrib and x.attrib['data-parameters'].split(':')[-1].isdigit()] +
                [int(re.findall(r'(?:from.*?:)(\d+)', x.attrib['href'])[0])
                for x in tree.xpath(xpath)
                if 'href' in x.attrib and len(re.findall(r'(?:from.*?:)(\d+)', x.attrib['href'])) > 0]
                )


class Ebony8(BoundHub):
    flip_number = 10

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    @property
    def object_urls(self):
        res = super(Ebony8, self).object_urls
        res.pop(PornCategories.CHANNEL_MAIN)
        res[PornCategories.CHANNEL_MAIN] = urljoin(self.base_url, '/sites/')
        return res

    def _prepare_filters(self):
        """
        Prepares the filters
        :return:
        """
        (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
         search_params) = super(Ebony8, self)._prepare_filters()
        channel_params = \
            {'sort_order': [(PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'cs_viewed'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            ],
             }
        return (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
                search_params)

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.ebony8.com/'

    def __init__(self, source_name='Ebony8', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Ebony8, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_channels(self, channel_data):
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="list-sponsors"]/div[@class="margin-fix"]/a',
                                                  PornCategories.CHANNEL)

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        headers = {
            'Accept': '*.*',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        if page_number is None:
            page_number = 1
        params.update({
            'mode': 'async',
            'function': 'get_block',
        })
        if page_filter.length.value is not None:
            params.update(parse_qsl(page_filter.length.value))
        if page_number > 1:
            params['from'] = str(page_number).zfill(2)

        if true_object.object_type == PornCategories.CHANNEL_MAIN:
            params['block_id'] = 'list_content_sources_sponsors_list'
            params['sort_by'] = page_filter.sort_order.value
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            return super(Ebony8, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                               page_filter, fetch_base_url)


class CamUploads(BoundHub):
    flip_number = 10

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        res = super(CamUploads, self).object_urls
        res.pop(PornCategories.TAG_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.camuploads.com/'

    def __init__(self, source_name='CamUploads', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(CamUploads, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)


class Porn7(PornBimbo):
    max_flip_images = 10
    videos_per_video_page = 40

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/studios/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/pornstars/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.RECOMMENDED_VIDEO: urljoin(self.base_url, '/featured/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/new/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/popular/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/rated/'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/longest/'),
            PornCategories.MOST_DISCUSSED_VIDEO: urljoin(self.base_url, '/featured/?sort_by=most_commented'),
            PornCategories.FAVORITE_VIDEO: urljoin(self.base_url, '/featured/?sort_by=most_favourited'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.RECOMMENDED_VIDEO: PornFilterTypes.RecommendedOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
            PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
        }

    def _prepare_filters(self):
        """
        Prepares the filters
        :return:
        """
        video_sort_order = [(PornFilterTypes.RecommendedOrder, 'Featured', 'ctr'),
                            (PornFilterTypes.DateOrder, 'New', 'post_date'),
                            (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                            (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                            (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                            (PornFilterTypes.FavorOrder, 'Most Favorite', 'most_favourited'),
                            ]
        video_period = ([(PornFilterTypes.AllDate, 'All time', ''),
                         (PornFilterTypes.OneDate, 'This Month', '_month'),
                         (PornFilterTypes.TwoDate, 'This week', '_week'),
                         (PornFilterTypes.ThreeDate, 'Today', '_today'),
                         ],
                        [('sort_order', [PornFilterTypes.RatingOrder,
                                         PornFilterTypes.ViewsOrder])]
                        )
        search_sort_order = [(PornFilterTypes.RelevanceOrder, 'Most Relevant', '')] + video_sort_order

        category_params = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.PopularityOrder, 'Popular', 'max_videos_ctr'),
                            (PornFilterTypes.DateOrder, 'Last Update', 'today_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            ],
             }
        porn_stars_params = \
            {'sort_order': [(PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.DateOrder, 'Last Update', 'today_videos'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            ]
             }
        actress_params = None
        channel_params = porn_stars_params
        tag_params = None
        video_params = {'sort_order': video_sort_order,
                        'period_filters': video_period,
                        }
        search_params = {'sort_order': search_sort_order,
                         'period_filters': video_period,
                         }

        return (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
                search_params)

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.porn7.xxx/'

    @property
    def max_pages(self):
        return 2000

    def __init__(self, source_name='Porn7', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Porn7, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="list-categories"]/div[@class="margin-fix"]/div')
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = link_data[0].xpath('div[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None

            number_of_videos = category.xpath('./div[@class="wrap"]/div[@class="views"]')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].text)[0]) if len(number_of_videos) > 0 else None
            number_of_photos = category.xpath('./div[@class="wrap"]/div[@class="added"]/*')
            number_of_photos = \
                int(re.findall(r'\d+', number_of_photos[0].text)[0]) if len(number_of_photos) > 0 else None

            rating = link_data[0].xpath('./strong[@class="title"]/*')
            rating = self._clear_text(rating[0].text) if len(rating) == 1 else None

            title = category.xpath('./strong[@class="title"]/*')
            assert len(title) == 1
            title = self._clear_text(title[0].text)
            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      number_of_photos=number_of_photos,
                                                      rating=rating,
                                                      object_type=PornCategories.CATEGORY,
                                                      super_object=category_data,
                                                      )
            res.append(sub_object_data)
        category_data.add_sub_objects(res)

    def _update_available_channels(self, channel_data):
        res = []
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="list-sponsors"]/div[@class="margin-fix"]/a')
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('div[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None

            number_of_videos = category.xpath('./div[@class="wrap pr-first"]/div[@class="rating"]')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].text)[0]) if len(number_of_videos) > 0 else None

            title = category.xpath('./strong[@class="title"]')
            assert len(title) == 1
            title = self._clear_text(title[0].text)
            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      object_type=PornCategories.CHANNEL,
                                                      super_object=channel_data,
                                                      )
            res.append(sub_object_data)
        channel_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        res = []
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="list-models"]/div[@class="margin-fix"]/a')
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('div[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None

            number_of_videos = category.xpath('./div[@class="wrap pr-first"]/div[@class="rating"]')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].text)[0]) if len(number_of_videos) > 0 else None

            rating = category.xpath('./strong[@class="title"]/*')
            rating = self._clear_text(rating[0].text) if len(rating) == 1 else None

            title = category.xpath('./strong[@class="title"]')
            assert len(title) == 1
            title = self._clear_text(title[0].text)
            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      rating=rating,
                                                      object_type=PornCategories.PORN_STAR,
                                                      super_object=porn_star_data,
                                                      )
            res.append(sub_object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN, ):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        if category_data.object_type == PornCategories.SEARCH_MAIN:
            return max(pages)
        else:
            if max(pages) - 1 < self._binary_search_page_threshold:
                return max(pages)
            else:
                return self._binary_search_max_number_of_pages(category_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        res = ([int(x.attrib['data-parameters'].split(':')[-1])
                for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a')
                if 'data-parameters' in x.attrib and x.attrib['data-parameters'].split(':')[-1].isdigit()] +
               [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0])
                for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a')
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0]
               )
        if len(res) == 0:
            xpath = './/div[@class="link_show_more"]/a'
            res = [int(re.findall(r'(?:from.*?:)(\d+)', x.attrib['data-parameters'])[0])
                   for x in tree.xpath(xpath)
                   if 'data-parameters' in x.attrib and
                   len(re.findall(r'(?:from.*?:)(\d+)', x.attrib['data-parameters'])) > 0]
        return res

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        # Took from AnyPorn module with somme modifications...
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div[@class="margin-fix"]/div[@class="item  "]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title'] if 'title' in link_data[0].attrib else None
            preview = link_data[0].attrib['data-mp4'] if 'data-mp4' in link_data[0].attrib else None

            image_data = link_data[0].xpath('./div[@class="img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, self.flip_number + 1)]
            if title is None:
                title = image_data[0].attrib['alt']

            video_length = video_tree_data.xpath('./div[@class="wrap pr-first"]/div[@class="duration"]')
            assert len(video_length) == 1
            video_length = self._format_duration(self._clear_text(video_length[0].text))

            if title is None:
                title = self._clear_text(link_data[0].xpath('./p[@class="title"]')[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=preview,
                                                  duration=video_length,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        headers = {
            'Accept': '*.*',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        if page_number is None:
            page_number = 1
        params.update({
            'mode': 'async',
            'function': 'get_block',
        })
        if page_filter.length.value is not None:
            params.update(parse_qsl(page_filter.length.value))
        params['from'] = str(page_number).zfill(2)

        if true_object.object_type == PornCategories.SEARCH_MAIN:
            conditions = self.get_proper_filter(page_data).conditions
            true_sort_filter_id = self._default_sort_by[true_object.object_type] \
                if true_object.object_type in self._default_sort_by \
                else page_filter.sort_order.filter_id

            params['block_id'] = 'list_videos_videos_list_search_result'
            params['sort_by'] = page_filter.sort_order.value
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value
            params.pop('from')
            params['from2'] = str(page_number).zfill(2)
        elif true_object.object_type == PornCategories.CHANNEL_MAIN:
            params['block_id'] = 'list_content_sources_sponsors_list'
            params['sort_by'] = page_filter.sort_order.value
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

        else:
            return super(Porn7, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                              page_filter, fetch_base_url)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request


class AdultCartoons(PornBimbo):
    max_flip_images = 30
    videos_per_video_page = 31

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/longest/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    def _prepare_filters(self):
        """
        Prepares the filters
        :return:
        """
        video_sort_order = [(PornFilterTypes.DateOrder, 'New', 'post_date'),
                            (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                            (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                            ]
        video_period = ([(PornFilterTypes.AllDate, 'All time', ''),
                         (PornFilterTypes.OneDate, 'This Month', '_month'),
                         (PornFilterTypes.TwoDate, 'This week', '_week'),
                         (PornFilterTypes.ThreeDate, 'Today', '_today'),
                         ],
                        [('sort_order', [PornFilterTypes.RatingOrder,
                                         PornFilterTypes.ViewsOrder])]
                        )
        search_sort_order = [(PornFilterTypes.RelevanceOrder, 'Most Relevant', '')] + video_sort_order

        category_params = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            ],
             }
        porn_stars_params = None
        actress_params = None
        channel_params = porn_stars_params
        tag_params = None
        video_params = {'sort_order': video_sort_order,
                        'period_filters': video_period,
                        }
        search_params = {'sort_order': search_sort_order,
                         'period_filters': video_period,
                         }

        return (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
                search_params)

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.adultcartoons.com/'

    @property
    def max_pages(self):
        return 2000

    def __init__(self, source_name='AdultCartoons', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(AdultCartoons, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="thumbs category_list"]/'
                                                  'div[@class="thumb grid item"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_base_object(self, object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('div[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None
            title = category.attrib['title'] if 'title' in category.attrib else \
                (image_data[0].attrib['alt'] if 'alt' in image_data[0].attrib else
                 image_data[0].xpath('./span[@class="author uppercase"]')[0].text)

            category_data = category.xpath('./span[@class="sub_info"]/span/span')
            if len(category_data) == 1:
                number_of_views = None
                number_of_videos = int(re.findall(r'\d+', category_data[0].text)[0])
                number_of_photos = None
            elif len(category_data) == 3:
                number_of_views = int(re.findall(r'\d+', category_data[0].text)[0])
                number_of_videos = int(re.findall(r'\d+', category_data[1].text)[0])
                number_of_photos = int(re.findall(r'\d+', category_data[2].text)[0])
            else:
                number_of_views = None
                number_of_videos = None
                number_of_photos = None

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_views=number_of_views,
                                                      number_of_videos=number_of_videos,
                                                      number_of_photos=number_of_photos,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        object_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//div[@class="tags-holder"]//div[@class="item"]/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.xpath('./strong')[0].text,
                                                 int(re.findall(r'\d+', x.xpath('./span')[0].text)[0]))
                                                for x in raw_data])
        return links, titles, number_of_videos

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN, PornCategories.CATEGORY_MAIN, ):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        if category_data.object_type in (PornCategories.SEARCH_MAIN, PornCategories.PORN_STAR_MAIN):
            return max(pages)
        else:
            if max(pages) - 1 < self._binary_search_page_threshold:
                return max(pages)
            else:
                return self._binary_search_max_number_of_pages(category_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        res = ([int(x.attrib['data-parameters'].split(':')[-1])
                for x in tree.xpath('.//ul[@class="pagination"]/li/a')
                if 'data-parameters' in x.attrib and x.attrib['data-parameters'].split(':')[-1].isdigit()] +
               [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0])
                for x in tree.xpath('.//ul[@class="pagination"]/li/a')
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0]
               )
        if len(res) == 0:
            xpath = './/div[@class="load-more"]/a'
            return [int(re.findall(r'(?:from.*?:)(\d+)', x.attrib['data-parameters'])[0])
                    for x in tree.xpath(xpath)
                    if 'data-parameters' in x.attrib and
                    len(re.findall(r'(?:from.*?:)(\d+)', x.attrib['data-parameters'])) > 0]
        return res

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        # Took from AnyPorn module with somme modifications...
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumbs videos_list"]/div[@class="item thumb"]/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']
            title = video_tree_data.attrib['title'] if 'title' in video_tree_data.attrib else None

            image_data = video_tree_data.xpath('./div[@class="img wrap_image"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, self.flip_number + 1)]
            if title is None:
                title = image_data[0].attrib['alt']

            video_length = video_tree_data.xpath('./div[@class="img wrap_image"]/div[@class="sticky"]/'
                                                 'div[@class="time"]')
            assert len(video_length) == 1
            video_length = self._format_duration(self._clear_text(video_length[0].text))

            is_hd = video_tree_data.xpath('./div[@class="img wrap_image"]/div[@class="sticky"]/div[@class="quality"]')
            is_hd = len(is_hd) == 1 and is_hd[0].text == 'HD'

            if title is None:
                title = self._clear_text(video_tree_data.xpath('./div[@class="tools"]/div[@class="title"]')[0].text)

            uploader = self._clear_text(video_tree_data.xpath('./div[@class="tools"]/div[@class="columns"]/'
                                                              'div[@class="column"]/div[@class="name"]')[0].text)
            additional_data = {'uploader': uploader}
            rating = self._clear_text(video_tree_data.xpath('./div[@class="tools"]/div[@class="columns"]/'
                                                            'div[@class="column second"]/div[@class="rate"]/'
                                                            'span')[0].text)
            count_data = video_tree_data.xpath('./div[@class="tools"]/div[@class="info"]/div[@class="count"]')
            assert len(count_data) == 2
            number_of_views = int(''.join(re.findall(r'\d+', count_data[0].text)))
            added_before = count_data[1].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  is_hd=is_hd,
                                                  duration=video_length,
                                                  number_of_views=number_of_views,
                                                  additional_data=additional_data,
                                                  rating=rating,
                                                  added_before=added_before,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        headers = {
            'Accept': '*.*',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        if page_number is None:
            page_number = 1
        params.update({
            'mode': 'async',
            'function': 'get_block',
        })
        if page_filter.length.value is not None:
            params.update(parse_qsl(page_filter.length.value))
        if page_number > 1:
            params['from'] = str(page_number).zfill(2)
        if true_object.object_type == PornCategories.LATEST_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = page_filter.sort_order.value
            params['ipp'] = self.videos_per_video_page
        else:
            return super(AdultCartoons, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                      page_filter, fetch_base_url)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request


class MoviesAnd(AdultCartoons):
    max_flip_images = 30
    videos_per_video_page = 56

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/longest/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    def _prepare_filters(self):
        """
        Prepares the filters
        :return:
        """
        video_sort_order = [(PornFilterTypes.DateOrder, 'New', 'post_date'),
                            (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                            (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                            ]
        video_period = ([(PornFilterTypes.AllDate, 'All time', ''),
                         (PornFilterTypes.OneDate, 'This Month', '_month'),
                         (PornFilterTypes.TwoDate, 'This week', '_week'),
                         (PornFilterTypes.ThreeDate, 'Today', '_today'),
                         ],
                        [('sort_order', [PornFilterTypes.RatingOrder,
                                         PornFilterTypes.ViewsOrder])]
                        )
        search_sort_order = [(PornFilterTypes.RelevanceOrder, 'Most Relevant', '')] + video_sort_order

        category_params = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            ],
             }
        porn_stars_params = \
            {'sort_order': [(PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.DateOrder, 'Last Update', 'today_videos'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            ]
             }
        actress_params = None
        channel_params = porn_stars_params
        tag_params = None
        video_params = {'sort_order': video_sort_order,
                        'period_filters': video_period,
                        }
        search_params = {'sort_order': search_sort_order,
                         'period_filters': video_period,
                         }

        return (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
                search_params)

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.moviesand.com/'

    @property
    def max_pages(self):
        return 2000

    def __init__(self, source_name='MoviesAnd', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(MoviesAnd, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="thumbs category_list"]/'
                                                  'div[@class="thumb grid item"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@class="thumbs models_list"]/'
                                                  'div[@class="thumb grid item"]/a',
                                                  PornCategories.PORN_STAR)


class Interracial(MoviesAnd):
    max_flip_images = 30
    videos_per_video_page = 31

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.interracial.com/'

    @property
    def max_pages(self):
        return 2000

    def __init__(self, source_name='Interracial', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Interracial, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)


class Deviants(MoviesAnd):
    max_flip_images = 30
    videos_per_video_page = 31

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.deviants.com/'

    @property
    def max_pages(self):
        return 2000

    def __init__(self, source_name='Devaints', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Deviants, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)


class PunishBang(PervertSluts):
    # Some of the models we took from AnyPorn module (has thee same structure)
    flip_number = 2

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/videos/?sort_by=post_date'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/videos/?sort_by=video_viewed'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/videos/?sort_by=rating'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/videos/?sort_by=duration'),
            PornCategories.MOST_DISCUSSED_VIDEO: urljoin(self.base_url, '/videos/?sort_by=most_commented'),
            PornCategories.FAVORITE_VIDEO: urljoin(self.base_url, '/videos/?sort_by=most_favourited'),
            PornCategories.RECOMMENDED_VIDEO: urljoin(self.base_url, '/videos/?sort_by=last_time_view_date'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
                PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
                PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
                PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
                PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
                PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
                PornCategories.RECOMMENDED_VIDEO: PornFilterTypes.RecommendedOrder,
                }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.punishbang.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_sort_order = [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                            (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                            (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                            (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                            (PornFilterTypes.FavorOrder, 'Most Favorite', 'most_favourited'),
                            (PornFilterTypes.RecommendedOrder, 'Most Favorite', 'last_time_view_date'),
                            ]
        search_sort_order = [(PornFilterTypes.RelevanceOrder, 'Most Relevant', '')] + video_sort_order
        category_params = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            ],
             }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                                       (PornFilterTypes.FavorOrder, 'Most Favorite', 'most_favourited'),
                                       (PornFilterTypes.RecommendedOrder, 'Most Favorite', 'last_time_view_date'),
                                       ],
                        'period_filters': ([(PornFilterTypes.AllDate, 'All time', ''),
                                            (PornFilterTypes.OneDate, 'This Month', '_month'),
                                            (PornFilterTypes.TwoDate, 'This week', '_week'),
                                            (PornFilterTypes.ThreeDate, 'Today', '_today'),
                                            ],
                                           [('sort_order', [PornFilterTypes.RatingOrder,
                                                            PornFilterTypes.ViewsOrder])]
                                           ),
                        }
        search_params = {'sort_order': search_sort_order,
                         'period_filters': video_params['period_filters']
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_params,
                                         channels_args=category_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         single_porn_star_args=video_params,
                                         single_tag_args=video_params,
                                         video_args=video_params,
                                         search_args=search_params,
                                         )

    def __init__(self, source_name='PunishBang', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PunishBang, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="cards__list"]/'
                                                  'div[@class="cards__item cards__item--small js-item"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="cards__list"]/'
                                                  'div[@class="cards__item cards__item--small js-item"]/a',
                                                  PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        links, titles, numbers_of_videos = self._get_tag_properties(page_request)
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=link,
                                       url=urljoin(self.base_url, link),
                                       title=title,
                                       number_of_videos=number_of_videos,
                                       object_type=PornCategories.PORN_STAR,
                                       super_object=porn_star_data,
                                       )
               for link, title, number_of_videos in zip(links, titles, numbers_of_videos)]
        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_base_object(self, object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None
            title = category.attrib['title'].title() \
                if 'title' in category.attrib else image_data[0].attrib['alt'].title()

            tmp_data = category.xpath('./span[@class="card__footer"]/span[@class="card__action"]/'
                                      'span[@class="card__col"]/span[@class="card__text"]')
            if object_type == PornCategories.CATEGORY:
                number_of_videos = int(tmp_data[0].text) if len(tmp_data) > 0 else None
                rating = None
            elif object_type == PornCategories.CHANNEL:
                number_of_videos = None
                rating = tmp_data[0].text if len(tmp_data) > 0 else None
            else:
                raise ValueError('Unsupported type {t}'.format(t=object_type))

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      rating=rating,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        if is_sort:
            res.sort(key=lambda x: x.title)
        object_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//ol[@class="list-column"]/li[@class="list-column__item"]/div/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'],
                                                 x.attrib['title'] if 'title' in x.attrib else x.text,
                                                 x.xpath('./strong')[0].text)
                                                for x in raw_data])
        return links, titles, number_of_videos

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        return self._get_video_links_from_video_data2(video_data)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN,):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        elif max(pages) - 1 < self._binary_search_page_threshold:
            return max(pages)
        else:
            return self._binary_search_max_number_of_pages(category_data)

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 4

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        xpath = './/div[@class="pagination"]/ul[@class="pagination__list"]/li/a'
        return ([int(x.attrib['data-parameters'].split(':')[-1]) for x in tree.xpath(xpath)
                if 'data-parameters' in x.attrib and x.attrib['data-parameters'].split(':')[-1].isdigit()
                 and 'class' in x.attrib and 'is-disabled' not in x.attrib['class']] +
                [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0]) for x in tree.xpath(xpath)
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0
                 and 'class' in x.attrib and 'is-disabled' not in x.attrib['class']]
                )

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        # Took from AnyPorn module with somme modifications...
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="cards__list"]/div[@class="cards__item js-item"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title'] if 'title' in link_data[0].attrib else None

            video_preview = link_data[0].xpath('./span[@class="card__content"]')
            assert len(video_preview) == 1
            video_preview = video_preview[0].attrib['data-preview'] \
                if 'data-preview' in video_preview[0].attrib else None

            image_data = link_data[0].xpath('./span[@class="card__content"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-src']
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, self.flip_number + 1)]
            if title is None and 'alt' in image_data[0].attrib:
                title = image_data[0].attrib['alt']

            is_hd = link_data[0].xpath('./span[@class="card__content"]/span[@class="flag-group"]/'
                                       'span[@class="flag flag--primary"]')
            is_hd = len(is_hd) > 0 and is_hd[0] == 'HD'

            video_length = link_data[0].xpath('./span[@class="card__content"]/span[@class="flag-group"]/'
                                              'span[@class="flag"]')
            video_length = self._format_duration(video_length[0].text)

            if title is None:
                title = link_data[0].xpath('./span[@class="card__footer"]/span[@class="card__title"]')
                if len(title) > 0:
                    title = title[0].attrib['title'] if'title' in title[0].attrib else self._clear_text(title[0].text)
                else:
                    raise ValueError('Cannot find title!')

            video_data = link_data[0].xpath('./span[@class="card__footer"]/span[@class="card__action"]/'
                                            'span[@class="card__col"]/span[@class="card__col"]/'
                                            'span[@class="card__text"]')
            assert len(video_data) == 2

            number_of_views = self._clear_text(video_data[0].text)
            rating = self._clear_text(video_data[1].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  duration=video_length,
                                                  is_hd=is_hd,
                                                  rating=rating,
                                                  number_of_views=number_of_views,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        headers = {
            'Accept': '*.*',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        if page_number is None:
            page_number = 1
        params.update({
            'mode': 'async',
            'function': 'get_block',
        })
        if page_filter.length.value is not None:
            params.update(parse_qsl(page_filter.length.value))
        if page_number > 1:
            params['from'] = str(page_number).zfill(2)
        if true_object.object_type == PornCategories.SEARCH_MAIN:
            conditions = self.get_proper_filter(page_data).conditions
            true_sort_filter_id = self._default_sort_by[true_object.object_type] \
                if true_object.object_type in self._default_sort_by \
                else page_filter.sort_order.filter_id

            params['block_id'] = 'list_videos_videos_list_search_result'
            # params['q'] = self._search_query
            # params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

        elif true_object.object_type == PornCategories.LATEST_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = page_filter.sort_order.value
        elif true_object.object_type in (PornCategories.TAG_MAIN, PornCategories.PORN_STAR_MAIN):
            # params['block_id'] = 'list_content_sources_sponsors_list'
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3*',
                'Cache-Control': 'max-age=0',
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }
            page_request = self.session.get(page_data.url, headers=headers)
            return page_request
        else:
            return super(PunishBang, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                   page_filter, fetch_base_url)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw number, i.e. '7m:58s'.
        :return:
        """
        return super(AnyPorn, self)._format_duration(raw_duration)

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query.replace(' ', '-')))


class BravoTeens(AnyPorn):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.bravoteens.com/cats/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.bravoteens.com/top/',
            PornCategories.LATEST_VIDEO: 'https://www.bravoteens.com/new/',
            PornCategories.POPULAR_VIDEO: 'https://www.bravoteens.com/popular/',
            PornCategories.SEARCH_MAIN: 'https://www.bravoteens.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.bravoteens.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_params = {'period_filters': [(PornFilterTypes.AllDate, 'All time', ''),
                                           (PornFilterTypes.OneDate, 'This Month', 'month'),
                                           (PornFilterTypes.TwoDate, 'This week', 'week'),
                                           (PornFilterTypes.ThreeDate, 'Today', 'today'),
                                           ],
                        }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='BravoTeens', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(BravoTeens, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="preview-item"]/div')

        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = category.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            title_data = category.xpath('./div[@class="thumb_meta"]/span[@class="video-title"]')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos = category.xpath('./div[@class="thumb_meta"]/span[@class="white"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))
        res.sort(key=lambda x: x.title)
        category_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//div[@class="pagination2 nopop"]/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="block-video-preview"]/div[@class="preview-item"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./div[@class="image-holder "]/a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']

            image_data = video_tree_data.xpath('./div[@class="image-holder "]/a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']
            if 'onmouseover' in image_data[0].attrib:
                max_flip_images = int(re.findall(r'(\d+)(?:\)$)', image_data[0].attrib['onmouseover'])[0])
                flix_image = [re.sub(r'\d.jpg$', '{d}.jpg'.format(d=d), image) for d in range(1, max_flip_images+1)]
            else:
                flix_image = None

            video_length = video_tree_data.xpath('./div[@class="image-holder "]/a/div[@class="video-info"]/'
                                                 'span[@class="time"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            added_before = video_tree_data.xpath('./div[@class="image-holder "]/a/div[@class="video-info"]/'
                                                 'span[@class="date"]')
            assert len(added_before) == 1
            added_before = added_before[0].text

            rating = video_tree_data.xpath('./div[@class="video-meta"]/span[@class="video-rating"]')
            assert len(rating) == 1
            rating = rating[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  added_before=added_before,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
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
        if true_object.object_type in (PornCategories.POPULAR_VIDEO, PornCategories.TOP_RATED_VIDEO,):
            if page_filter.period.filter_id != PornFilterTypes.AllDate:
                fetch_base_url += page_filter.period.value + '/'

        if page_number is not None and page_number != 1:
            fetch_base_url = re.sub(r'/*\d*/$', '/{d}/'.format(d=page_number), fetch_base_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


class MadThumbs(Fapster):
    @property
    def max_pages(self):
        return 8000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'http://www.madthumbs.com/categories/',
            PornCategories.CHANNEL_MAIN: 'http://www.madthumbs.com/sites/',
            PornCategories.PORN_STAR_MAIN: 'http://www.madthumbs.com/models/',
            PornCategories.TAG_MAIN: 'http://www.madthumbs.com/tags/',
            PornCategories.TOP_RATED_VIDEO: 'http://www.madthumbs.com/top-rated/',
            PornCategories.POPULAR_VIDEO: 'http://www.madthumbs.com/most-popular/',
            PornCategories.SEARCH_MAIN: 'http://www.madthumbs.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.madthumbs.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        category_params = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.ViewsOrder, 'Most viewed', 'avg_videos_popularity'),
                                          (PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          ],
                           }
        porn_stars_params = {'sort_order': [(PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                            (PornFilterTypes.ViewsOrder, 'Most viewed', 'avg_videos_popularity'),
                                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                            ],
                             }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                                       (PornFilterTypes.FavorOrder, 'Most Favourite', 'most_favourited'),
                                       ],
                        }
        search_params = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                                        (PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                        (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                                        (PornFilterTypes.FavorOrder, 'Most Favourite', 'most_favourited'),
                                        ],
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_params,
                                         porn_stars_args=porn_stars_params,
                                         channels_args=porn_stars_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='MadThumbs', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(MadThumbs, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="list-tags"]/div[@class="margin-fix"]/ul/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, None)
                                                for x in raw_objects]) if len(raw_objects) > 0 else ([], [], [])
        return links, titles, number_of_videos

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True


class VQTube(MadThumbs):

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://vqtube.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://vqtube.com/models/',
            PornCategories.TAG_MAIN: 'https://vqtube.com/tags/',
            PornCategories.LATEST_VIDEO: 'https://vqtube.com/latest-updates/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://vqtube.com/most-popular/',
            PornCategories.TOP_RATED_VIDEO: 'https://vqtube.com/top-rated/',
            PornCategories.SEARCH_MAIN: 'https://vqtube.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://vqtube.com/'

    @property
    def number_of_videos_per_page(self):
        """
        Base site url.
        :return:
        """
        return 30  # 5*6

    def __init__(self, source_name='VQTube', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(VQTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_tags(self, tag_data):
        return super(PervertSluts, self)._update_available_tags(tag_data)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
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
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//div[@class="list-tags"]/div[@class="margin-fix"]/ul/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, None)
                                                for x in raw_data])
        return links, titles, number_of_videos

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        # New
        headers = {
            'Accept': '*.*',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        if page_number is None:
            page_number = 1
        params.update({
                'mode': 'async',
                'function': 'get_block',
            })
        if page_number > 1:
            params['from'] = str(page_number).zfill(2)
        if true_object.object_type == PornCategories.TAG_MAIN:
            params['block_id'] = 'list_tags_tags_list'
            params['sort_by'] = 'tag'

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            return super(VQTube, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                               page_filter, fetch_base_url)


class Xozilla(MadThumbs):
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.xozilla.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://www.xozilla.com/models/',
            PornCategories.CHANNEL_MAIN: 'https://www.xozilla.com/channels/',
            PornCategories.LATEST_VIDEO: 'https://www.xozilla.com/latest-updates/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.xozilla.com/most-popular/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.xozilla.com/top-rated/',
            PornCategories.SEARCH_MAIN: 'https://www.xozilla.com/search/',
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
        return 'https://www.xozilla.com/'

    @property
    def number_of_videos_per_page(self):
        """
        Base site url.
        :return:
        """
        return 30  # 5*6

    def __init__(self, source_name='Xozilla', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Xozilla, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div[@class="margin-fix"]/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']
            video_preview = video_tree_data.attrib['vthumb'] if 'vthumb' in video_tree_data.attrib else None

            image_data = video_tree_data.xpath('./div[@class="img ithumb"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            title = video_tree_data.attrib['title'] \
                if 'title' in video_tree_data.attrib else image_data[0].attrib['alt']

            is_hd = 'class="hd-label"' in video_tree_data.xpath('./div[@class="img ithumb"]/*')[1].text

            video_length = video_tree_data.xpath('./div[@class="img ithumb"]/div[@class="duration"]')
            assert len(video_length) == 1

            res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                obj_id=link,
                                                title=title,
                                                url=urljoin(page_data.url, link),
                                                image_link=image,
                                                preview_video_link=video_preview,
                                                is_hd=is_hd,
                                                duration=self._format_duration(video_length[0].text),
                                                object_type=PornCategories.VIDEO,
                                                super_object=page_data,
                                                ))

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res


class SlutLoad(MadThumbs):
    @property
    def max_pages(self):
        return 8000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.slutload.com/categories/',
            # VideoCategories.CHANNEL_MAIN: 'https://www.slutload.com/sites/',
            # VideoCategories.PORN_STAR_MAIN: 'https://www.slutload.com/models/',
            PornCategories.TAG_MAIN: 'https://www.slutload.com/tags/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.slutload.com/top-rated/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.slutload.com/view/',
            PornCategories.SEARCH_MAIN: 'https://www.slutload.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.slutload.com/'

    def __init__(self, source_name='SlutLoad', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SlutLoad, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)


class Sex3(BravoPorn):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://sex3.com/categories/',
            PornCategories.CHANNEL_MAIN: 'https://sex3.com/channels/',
            PornCategories.PORN_STAR_MAIN: 'https://sex3.com/stars/',
            PornCategories.POPULAR_VIDEO: 'https://sex3.com/most-popular/',
            PornCategories.LATEST_VIDEO: 'https://sex3.com/latest-updates/',
            PornCategories.SEARCH_MAIN: 'https://sex3.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://sex3.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        single_category_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Recent first', 'latest'),
                                                 (PornFilterTypes.VideosRatingOrder, 'Top Rated first', 'top-rated'),
                                                 (PornFilterTypes.ViewsOrder, 'Most Viewed First', 'most-viewed'),
                                                 (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                                 ],
                                  }
        model_params = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Popularity', 'model_viewed'),
                                       (PornFilterTypes.VideosPopularityOrder, 'Videos Popularity',
                                        'avg_videos_popularity'),
                                       (PornFilterTypes.VideosRatingOrder, 'Videos rating', 'avg_videos_rating'),
                                       (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                       (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                       (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                       ],
                        }
        video_params = {'period_filters': ([(PornFilterTypes.ThreeDate, 'Today', 'today'),
                                            (PornFilterTypes.TwoDate, 'This week', 'week'),
                                            (PornFilterTypes.OneDate, 'This Month', 'month'),
                                            (PornFilterTypes.AllDate, 'All time', None),
                                            ],
                                           [('sort_order', [PornFilterTypes.PopularityOrder])]
                                           ),
                        }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=single_category_params,
                                         single_tag_args=single_category_params,
                                         porn_stars_args=model_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='Sex3', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Sex3, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_base_object(self, base_object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = category.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            title_data = (category.xpath('./div[@class="thumb_meta"]/a') +
                          category.xpath('./div[@style="position:absolute; color:#FFF; top:135px; left:0; '
                                         'padding: 0 3px; width:194px; height:15px; '
                                         'background: url(/images/sex3/pngbg.png); '
                                         'float:left; overflow: hidden;"]'))
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].text)

            number_of_videos = title_data[0].xpath('./span[@class="white"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(base_object_data.url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=object_type,
                                               super_object=base_object_data,
                                               ))
        if is_sort is True:
            res.sort(key=lambda x: x.title)
        base_object_data.add_sub_objects(res)
        return res

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/ul[@class="thumbs thumbs200 cat_link_list"]/li',
                                                  PornCategories.CATEGORY,
                                                  True)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/ul[@class="thumbs thumbs200"]/li',
                                                  PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="th-wrap"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            title = category.attrib['title']

            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            description = image_data[0].attrib['alt']

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
                                               description=description,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ))
        res.sort(key=lambda x: x.title)
        channel_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//div[@class="pagination nopop"]/div/*/text()') if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = (tree.xpath('.//div[@class="thumbs thumbs200"]/div[@class="fuck"]') +
                  tree.xpath('.//ul[@class="thumbs thumbs200"]/li'))
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']
            if 'onmouseover' in image_data[0].attrib:
                max_flip_images = int(re.findall(r'(\d+)(?:\)$)', image_data[0].attrib['onmouseover'])[0])
                flix_image = [re.sub(r'\d.jpg$', '{d}.jpg'.format(d=d), image) for d in range(1, max_flip_images+1)]
            else:
                flix_image = None

            video_length = video_tree_data.xpath('./div[@class="time"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            added_before = video_tree_data.xpath('./div[@class="thumb_meta"]/span[@class="left"]')
            assert len(added_before) == 1
            added_before = self._clear_text(added_before[0].text)

            rating = video_tree_data.xpath('./div[@class="thumb_meta"]/span[@class="right"]/em')
            assert len(rating) == 1
            rating = rating[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  duration=self._format_duration(video_length),
                                                  added_before=added_before,
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        if true_object.object_type in (PornCategories.CATEGORY,):
            conditions = self.get_proper_filter(page_data).conditions
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

            if (
                    page_filter.sort_order.value is not None and
                    (conditions.period.sort_order is None or
                     page_filter.sort_order.filter_id in conditions.period.sort_order)
            ):
                fetch_base_url += page_filter.sort_order.value + '/'

            if page_number is not None and page_number != 1:
                fetch_base_url = re.sub(r'/*\d*/$', '/{d}/'.format(d=page_number), fetch_base_url)

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            return super(Sex3, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                             page_filter, fetch_base_url)

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


class AnySex(Sex3):
    max_flip_image = 72

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://anysex.com/'

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://anysex.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://anysex.com/models/',
            PornCategories.LATEST_VIDEO: 'https://anysex.com/new-movies/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://anysex.com/most-popular/',
            PornCategories.TOP_RATED_VIDEO: 'https://anysex.com/top-rated/',
            PornCategories.SEARCH_MAIN: 'https://anysex.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        category_params = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'total_videos'),
                                          (PornFilterTypes.VideosPopularityOrder, 'Videos Popularity',
                                           'avg_videos_popularity'),
                                          (PornFilterTypes.VideosRatingOrder, 'Videos rating', 'avg_videos_rating'),
                                          ],
                           }
        single_category_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Recent first', 'latest'),
                                                 (PornFilterTypes.VideosRatingOrder, 'Top Rated first', 'top-rated'),
                                                 (PornFilterTypes.ViewsOrder, 'Most Viewed first', 'most-viewed'),
                                                 (PornFilterTypes.LengthOrder, 'Longest first', 'longest'),
                                                 ],
                                  }
        model_params = {'sort_order': [(PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                       (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                       (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'total_videos'),
                                       (PornFilterTypes.VideosPopularityOrder, 'Videos Popularity',
                                        'avg_videos_popularity'),
                                       (PornFilterTypes.VideosRatingOrder, 'Videos rating', 'avg_videos_rating'),
                                       ],
                        }
        video_params = {'period_filters': [(PornFilterTypes.ThreeDate, 'Today', 'today'),
                                           (PornFilterTypes.TwoDate, 'This week', 'week'),
                                           (PornFilterTypes.OneDate, 'This Month', 'month'),
                                           (PornFilterTypes.AllDate, 'All time', None),
                                           ],
                        }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_params,
                                         single_category_args=single_category_params,
                                         single_tag_args=single_category_params,
                                         porn_stars_args=model_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='AnySex', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(AnySex, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_general_category(category_data,
                                                       './/div[@class="list_categories"]//ul[@class="box"]/li',
                                                       PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_general_category(porn_star_data,
                                                       './/div[@class="modelleft"]//ul[@class="box"]/li',
                                                       PornCategories.PORN_STAR)

    def _update_available_general_category(self, category_data, xpath, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        for category in categories:
            link = category.xpath('./div[@class="img"]/a')
            assert len(link) == 1

            image = category.xpath('./div[@class="img"]/a/img/@src')
            assert len(image) == 1

            title = category.xpath('./div[@class="img"]/a/span/text()')
            assert len(title) == 1

            number_of_videos = category.xpath('./div[@class="desc"]/span[@class="views"]/text()')
            assert len(title) == 1
            number_of_videos = re.findall(r'\d+', number_of_videos[0])
            number_of_videos = number_of_videos[0] if len(number_of_videos) > 0 else None

            sub_category_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                        obj_id=link[0].attrib['href'],
                                                        url=urljoin(category_data.url, link[0].attrib['href']),
                                                        title=title[0],
                                                        image_link=image[0],
                                                        number_of_videos=number_of_videos,
                                                        object_type=object_type,
                                                        super_object=category_data,
                                                        )
            res.append(sub_category_data)
        category_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        return self._get_video_links_from_video_data3(video_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//div[@class="pagination"]/div[@class="block_content"]/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//ul[@class="box"]/li[@class="item "]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            image = video_tree_data.xpath('./a/div/img')
            assert len(image) == 1
            image = urljoin(self.base_url, image[0].attrib['src'])

            video_length = video_tree_data.xpath('./span[@class="time"]')
            assert len(video_length) == 1

            video_data = PornCatalogVideoPageNode(
                catalog_manager=self.catalog_manager,
                obj_id=re.findall(r'\d+', link_data[0].attrib['href'])[0],
                title=link_data[0].attrib['title'],
                url=urljoin(self.base_url, link_data[0].attrib['href']),
                image_link=image,
                flip_images_link=[re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                                  for i in range(self.max_flip_image + 1)],
                duration=self._format_duration(self._clear_text(video_length[0].text)),
                object_type=PornCategories.VIDEO,
                super_object=page_data,
            )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res


class CrocoTube(Sex3):
    flip_number = 5

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 5000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://crocotube.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://crocotube.com/pornstars/',
            PornCategories.TOP_RATED_VIDEO: 'https://crocotube.com/top-rated/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://crocotube.com/most-popular/',
            PornCategories.LONGEST_VIDEO: 'https://crocotube.com/longest/',
            PornCategories.LATEST_VIDEO: 'https://crocotube.com/',
            PornCategories.SEARCH_MAIN: 'https://crocotube.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
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
        return 'https://crocotube.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        model_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Last Added', ''),
                                       (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-popular'),
                                       (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                       ],
                        }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=model_params,
                                         single_porn_star_args=model_params,
                                         )

    def __init__(self, source_name='CrocoTube', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(CrocoTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        # page_request = self.get_object_request(category_data)
        # tree = self.parser.parse(page_request.text)
        # categories = tree.xpath('.//div[@class="smovies-list categories-list"]/ul/li/a')
        # res = []
        # for category in categories:
        #     link = category.attrib['href']
        #
        #     image_data = category.xpath('./span[@class="img-shadow"]/img')
        #     assert len(image_data) == 1
        #     image = image_data[0].attrib['src']
        #     title = image_data[0].attrib['alt']
        #
        #     number_of_videos = category.xpath('./strong/em')
        #     assert len(number_of_videos) == 1
        #     number_of_videos = int(self._clear_text(number_of_videos[0].text))
        #
        #     res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
        #                                        obj_id=link,
        #                                        url=urljoin(self.base_url, link),
        #                                        image_link=image,
        #                                        title=title,
        #                                        number_of_videos=number_of_videos,
        #                                        object_type=Category,
        #                                        super_object=category_data,
        #                                        ))
        #
        # category_data.add_sub_objects(res)
        # return res
        return self._update_available_base_object(category_data, None, PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        # page_request = self.get_object_request(porn_star_data)
        # tree = self.parser.parse(page_request.text)
        # porn_stars = tree.xpath('.//div[@class="models-block"]/ul/li/a')
        # res = []
        # for porn_star in porn_stars:
        #     link = porn_star.attrib['href']
        #
        #     image_data = porn_star.xpath('./img')
        #     assert len(image_data) == 1
        #     image = image_data[0].attrib['src']
        #
        #     title_data = porn_star.xpath('./span[@class="model-name"]')
        #     assert len(title_data) == 1
        #     title = title_data[0].text
        #
        #     number_of_videos = porn_star.xpath('./span[@class="count"]')
        #     assert len(number_of_videos) == 1
        #     number_of_videos = int(self._clear_text(number_of_videos[0].text))
        #
        #     res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
        #                                        obj_id=link,
        #                                        url=urljoin(self.base_url, link),
        #                                        image_link=image,
        #                                        title=title,
        #                                        number_of_videos=number_of_videos,
        #                                        object_type=PornStar,
        #                                        super_object=porn_star_data,
        #                                        ))
        #
        # porn_star_data.add_sub_objects(res)
        # return res
        return self._update_available_base_object(porn_star_data, None, PornCategories.PORN_STAR)

    def _update_available_base_object(self, base_object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//a[@class="ct-az-list-item"]')
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=category.attrib['href'],
                                       url=urljoin(self.base_url, category.attrib['href']),
                                       title=category.text,
                                       object_type=object_type,
                                       super_object=base_object_data,
                                       ) for category in categories]
        base_object_data.add_sub_objects(res)
        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN,):
            return 1

        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        return self._binary_search_max_number_of_pages(category_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//div[@class="ct-pagination"]/a')
                if x.text is not None and x.text.isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 2

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="ct-videos-list"]/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./div[@class="ct-video-thumb-image"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']
            video_data = video_tree_data.xpath('./div[@class="ct-video-thumb-image"]/video')
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, self.flip_number + 1)]
            preview_link = video_data[0].attrib['src'] if len(video_data) == 1 else None

            is_hd = video_tree_data.xpath('./div[@class="ct-video-thumb-image"]/div[@class="ct-video-thumb-icons"]/'
                                          'div[@class="ct-video-thumb-hd-icon"]')
            is_hd = len(is_hd) > 0

            video_length = video_tree_data.xpath('./div[@class="ct-video-thumb-image"]/'
                                                 'div[@class="ct-video-thumb-icons"]/'
                                                 'div[@class="ct-video-thumb-duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            rating = video_tree_data.xpath('./div[@class="ct-video-thumb-stats"]/'
                                           'div[@class="ct-video-thumb-rating"]/em')
            assert len(rating) == 1
            rating = rating[0].text

            number_of_views = video_tree_data.xpath('./div[@class="ct-video-thumb-stats"]/'
                                                    'div[@class="ct-video-thumb-views"]/em')
            assert len(number_of_views) == 1
            number_of_views = int(number_of_views[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=preview_link,
                                                  is_hd=is_hd,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  number_of_views=number_of_views,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
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

        if true_object.object_type in (PornCategories.CATEGORY, PornCategories.PORN_STAR):
            if page_filter.sort_order.filter_id != PornFilterTypes.DateOrder:
                fetch_base_url += page_filter.sort_order.value + '/'

        if page_number is not None and page_number != 1:
            fetch_base_url += '{d}/'.format(d=page_number)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request


class WatchMyGfTv(AnyPorn):
    # Some of the models we took from AnyPorn module (has thee same structure)
    flip_number = 11

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, ''),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, ''),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://watchmygf.tv/'

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return False

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'New', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most Viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                                       (PornFilterTypes.CommentsOrder, 'Most Favourite', 'most_favourited'),
                                       ],
                        }
        search_params = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'video_viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                                        (PornFilterTypes.FavorOrder, 'Most Favourite', 'most_favourited'),
                                        ]
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=video_params,
                                         search_args=search_params,
                                         # video_args=video_params,
                                         )

    def __init__(self, source_name='WatchMyGfTv', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(WatchMyGfTv, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="menu-container"]/ul/li/a')
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=category.attrib['href'],
                                       url=urljoin(self.base_url, category.attrib['href']),
                                       title=self._clear_text(category.text),
                                       object_type=PornCategories.CATEGORY,
                                       super_object=category_data,
                                       ) for category in categories
               if category.attrib['href'].split('/')[2].split('.')[1:] == self.base_url.split('/')[2].split('.')]
        category_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        return self._get_video_links_from_video_data3(video_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return ([int(x.attrib['data-parameters'].split(':')[-1])
                for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a')
                if 'data-parameters' in x.attrib and x.attrib['data-parameters'].split(':')[-1].isdigit()] +
                [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0])
                for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a')
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0]
                )

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        # Took from AnyPorn module with somme modifications...
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="item-list"]/div[@class="item video"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1

            image_data = link_data[0].xpath('./div[@class="thumb-container"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            title = image_data[0].attrib['alt']
            flip_images = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                           for i in range(1, self.flip_number + 1)]
            video_preview = image_data[0].attrib['data-preview']
            if title is None:
                title = link_data[0].xpath('./div[@class="thumb-container"]/div[@class="name"]')
                assert len(title) == 1
                title = title[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=re.findall(r'\d+', link_data[0].attrib['href'])[0],
                                                  url=urljoin(self.base_url, link_data[0].attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        # New
        headers = {
            'Accept': '*.*',
            'Cache-Control': 'max-age=0',
            'Referer': page_data.url,
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        if page_number is None:
            page_number = 1
        params.update({
                'mode': 'async',
                'function': 'get_block',
            })
        if page_filter.length.value is not None:
            params.update(parse_qsl(page_filter.length.value))
        if page_number > 1:
            params['from'] = str(page_number).zfill(2)
        if true_object.object_type == PornCategories.SEARCH_MAIN:
            params['block_id'] = 'list_videos_videos_list_search_result'
            params['q'] = self._search_query
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            if 'from' in params:
                params.pop('from')
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value
        elif true_object.object_type == PornCategories.CATEGORY_MAIN:
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
            page_request = self.session.get(page_data.url, headers=headers)
            return page_request
        elif true_object.object_type == PornCategories.CATEGORY:
            if page_number is None:
                page_number = 1
                params['from'] = str(page_number).zfill(2)
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = page_filter.sort_order.value
        elif true_object.object_type == PornCategories.LATEST_VIDEO:
            params['block_id'] = 'list_videos_most_recent_videos'
            params['sort_by'] = 'ctr'
        else:
            return super(WatchMyGfTv, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                    page_filter, fetch_base_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query.replace(' ', '-')))


class WatchMyExGf(PervertSluts):
    # Some of the models we took from AnyPorn module (has thee same structure)
    flip_number = 11

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/porn/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.watchmyexgf.net/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        channels_params = {'sort_order': [(PornFilterTypes.ViewsOrder, 'Most Viewed', 'avg_videos_popularity'),
                                          (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          ],
                           }
        category_params = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.ViewsOrder, 'Most viewed', 'avg_videos_popularity'),
                                          (PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          ],
                           }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       ],
                        'period_filters': ([(PornFilterTypes.AllDate, 'All time', ''),
                                            (PornFilterTypes.OneDate, 'This Month', '_month'),
                                            (PornFilterTypes.TwoDate, 'This week', '_week'),
                                            (PornFilterTypes.ThreeDate, 'Today', '_today'),
                                            ],
                                           [('sort_order', [PornFilterTypes.RatingOrder,
                                                            PornFilterTypes.ViewsOrder])]
                                           ),
                        }
        single_channel_params = {'sort_order': video_params['sort_order']}
        search_params = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Most Relevant', ''),
                                        (PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'video_viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        ],
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_params,
                                         channels_args=channels_params,
                                         single_category_args=single_channel_params,
                                         single_porn_star_args=video_params,
                                         single_tag_args=single_channel_params,
                                         single_channel_args=single_channel_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='WatchMyExGf', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(WatchMyExGf, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="thumbs"]/div[@class="thumb category"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="thumbs"]/div[@class="thumb sponsor"]/a',
                                                  PornCategories.CHANNEL)

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        tag_properties = self._get_tag_properties(page_request)
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=link,
                                       url=urljoin(tag_data.url, link),
                                       title=title,
                                       number_of_videos=number_of_videos,
                                       object_type=PornCategories.TAG,
                                       super_object=tag_data,
                                       )
               for link, title, number_of_videos in zip(*tag_properties)]
        tag_data.add_sub_objects(res)
        return res

    def _update_available_base_object(self, object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None
            title = category.attrib['title'] if 'title' in category.attrib else image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="thumb-container"]/div[@class="thumb-info"]/'
                                              'span[@class="thumb-videos"]/i')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].tail)[0]) if len(number_of_videos) > 0 else None

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        if is_sort:
            res.sort(key=lambda x: x.title)
        object_data.add_sub_objects(res)
        return res

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//div[@class="width-wrap"]/ul/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], self._clear_text(x.xpath('./i')[0].tail), None)
                                                for x in raw_data])
        return links, titles, number_of_videos

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        return self._get_video_links_from_video_data3(video_data)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        elif max(pages) - 1 < self._binary_search_page_threshold:
            return max(pages)
        else:
            return self._binary_search_max_number_of_pages(category_data)

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 4

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return ([int(x.attrib['data-parameters'].split(':')[-1])
                for x in tree.xpath('.//ul[@class="paginator"]/li/a')
                if 'data-parameters' in x.attrib and x.attrib['data-parameters'].split(':')[-1].isdigit()] +
                [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0])
                for x in tree.xpath('.//ul[@class="paginator"]/li/a')
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0]
                )

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        # Took from AnyPorn module with somme modifications...
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumbs list-videos"]/div[@class="thumb item"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            title = link_data[0].attrib['title'] if 'title' in link_data[0].attrib else None

            image_data = link_data[0].xpath('./div[@class="thumb-container"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'load.gif' in image:
                image = image_data[0].attrib['data-original']
            if title is None:
                title = image_data[0].attrib['alt'] if 'alt' in image_data[0].attrib else None
            flip_images = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                           for i in range(1, self.flip_number + 1)]
            video_preview = image_data[0].attrib['data-preview'] if 'data-preview' in image_data[0].attrib else None
            if title is None:
                title = link_data[0].xpath('./div[@class="thumb-description"]')
                assert len(title) == 1
                title = title[0].text

            info_data = link_data[0].xpath('./div[@class="thumb-container"]/div[@class="thumb-info"]')
            assert len(info_data) == 1
            video_length = info_data[0].xpath('./span[@class="thumb-duration"]/i')
            video_length = self._format_duration(video_length[0].tail)
            number_of_views = info_data[0].xpath('./span[@class="thumb-views"]/i')
            number_of_views = self._clear_text(number_of_views[0].tail)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=re.findall(r'\d+', link_data[0].attrib['href'])[0],
                                                  url=urljoin(self.base_url, link_data[0].attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  duration=video_length,
                                                  number_of_views=number_of_views,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        if true_object.object_type == PornCategories.SEARCH_MAIN:
            headers = {
                'Accept': '*.*',
                'Cache-Control': 'max-age=0',
                'Referer': self.base_url,
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
            conditions = self.get_proper_filter(page_data).conditions
            true_sort_filter_id = self._default_sort_by[true_object.object_type] \
                if true_object.object_type in self._default_sort_by \
                else page_filter.sort_order.filter_id

            if page_number is None:
                page_number = 1
            params.update({
                    'mode': 'async',
                    'function': 'get_block',
                })
            if page_filter.length.value is not None:
                params.update(parse_qsl(page_filter.length.value))

            params['block_id'] = 'list_videos_videos_list_search_result'
            params['q'] = self._search_query
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            return super(WatchMyExGf, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                    page_filter, fetch_base_url)

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query.replace(' ', '-')))


class PornoDep(AnyPorn):
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://pornodep.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://pornodep.com/models/',
            PornCategories.TAG_MAIN: 'https://pornodep.com/tags/',
            PornCategories.CHANNEL_MAIN: 'https://pornodep.com/sites/',
            PornCategories.LATEST_VIDEO: 'https://pornodep.com/',
            PornCategories.SEARCH_MAIN: 'https://pornodep.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://pornodep.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_sort_order = [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                            ]
        search_sort_order = video_sort_order
        porn_stars_params = \
            {'sort_order': [(PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            ],
             }
        video_params = {'sort_order': video_sort_order,
                        }
        search_params = {'sort_order': search_sort_order,
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         # categories_args=category_params,
                                         channels_args=porn_stars_params,
                                         porn_stars_args=porn_stars_params,
                                         single_category_args=video_params,
                                         single_tag_args=video_params,
                                         single_channel_args=video_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='PornoDep', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornoDep, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="category-list"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="card-box"]/div[@class="img-box"]/img')
            if len(image_data) != 1:
                continue
            image = image_data[0].attrib['src']

            title_data = category.xpath('./div[@class="card-box"]/div[@class="title"]')
            assert len(image_data) == 1
            title = title_data[0].text

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
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
        categories = tree.xpath('.//div[@class="video-block channel"]/div[@class="heading"]')
        res = []
        for category in categories:
            title_data = category.xpath('./div[@class="title"]')
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].xpath('./span')[0].text)
            image = title_data[0].xpath('./i/img')
            image = image[0].attrib['src'] if len(image) > 0 else None
            link = category.xpath('./a')[0].attrib['href']

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ))

        channel_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="card-list models_list"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            ranking_data = category.xpath('./div[@class="card-top"]/span[@class="info"]/div')
            assert len(ranking_data) == 1
            ranking = self._clear_text(ranking_data[0].text)

            image_data = category.xpath('./div[@class="card-top"]/span[@class="wrap-img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None

            number_of_videos = category.xpath('./div[@class="card-top"]/div[@class="count"]/'
                                              'div[@class="count-box"]/span')
            assert len(number_of_videos) == 1
            number_of_videos = self._clear_text(number_of_videos[0].text)

            title_data = category.xpath('./div[@class="card-bottom"]/div/span[@class="title"]')
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               rating=ranking,
                                               number_of_videos=number_of_videos,
                                               image_link=image,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//div[@class="tags-wrap"]/div/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'],
                                                 self._clear_text(x.xpath('./div[@class="name"]')[0].text),
                                                 self._clear_text(x.xpath('./div[@class="count"]')[0].text))
                                                for x in raw_data])
        return links, titles, number_of_videos

    def _add_category_sub_pages(self, category_data, sub_object_type, page_request=None, clear_sub_elements=True):
        """
        Adds category sub pages.
        :param category_data: Category data object (PornCatalogCategoryNode).
        :param sub_object_type: Sub object type.
        :param page_request: Page request if such exist. In case it doesn't exist we fetch the object's url.
        :param clear_sub_elements: Flag that indicates whether we clear previous sub elements.
        :return:
        """
        if category_data.object_type == PornCategories.CATEGORY:
            # We add additional categories as well
            if clear_sub_elements is True:
                category_data.clear_sub_objects()
            if category_data.super_object.object_type != PornCategories.CATEGORY:
                self._update_available_categories(category_data)
            return super(PornoDep, self)._add_category_sub_pages(category_data, sub_object_type, page_request, False)
        else:
            return super(PornoDep, self)._add_category_sub_pages(category_data, sub_object_type, page_request,
                                                                 clear_sub_elements)

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        return self._get_video_links_from_video_data2(video_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(re.findall(r'(?:from.*?:)(\d+)', x.attrib['data-parameters'])[0])
                for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a')
                if len(re.findall(r'(?:from.*?:)(\d+)', x.attrib['data-parameters'])) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="card-list"]/div[@class="card item"]/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./div[@class="card-top"]/span[@class="wrap-img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            preview = image_data[0].attrib['data-preview'] if 'data-preview' in image_data[0].attrib else None
            flip_image = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                          for i in range(1, int(image_data[0].attrib['data-cnt']) + 1)]

            title = image_data[0].attrib['alt'] if 'alt' in image_data[0].attrib else video_tree_data.attrib['title']

            uploader = video_tree_data.xpath('./div[@class="card-top"]/span[@class="autor"]/div')
            additional_data = {'name': self._clear_text(uploader[0].text)} if len(uploader) == 1 else None

            video_length = video_tree_data.xpath('./div[@class="card-top"]/div[@class="time"]')
            assert len(video_length) == 1
            video_length = super(AnyPorn, self)._format_duration(self._clear_text(video_length[0].text))

            rating = video_tree_data.xpath('./div[@class="card-bottom"]/div/div[@class="rait"]/span')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].text)

            number_of_views = video_tree_data.xpath('./div[@class="card-bottom"]/div/div[@class="views"]')
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  preview_video_link=preview,
                                                  flip_images_link=flip_image,
                                                  additional_data=additional_data,
                                                  duration=video_length,
                                                  rating=rating,
                                                  number_of_views=number_of_views,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        headers = {
            'Accept': '*.*',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        if page_number is None:
            page_number = 1
        params.update({
            'mode': 'async',
            'function': 'get_block',
        })
        if (
                true_object.object_type in (PornCategories.CATEGORY_MAIN, ) or
                page_data.object_type in (PornCategories.CATEGORY, )
        ):
            page_request = self.session.get(fetch_base_url, headers=headers)
            return page_request
        elif true_object.object_type == PornCategories.LATEST_VIDEO:
            params['block_id'] = 'list_videos_most_recent_videos'
            params['sort_by'] = 'post_date'
            params['from'] = str(page_number).zfill(2)
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            params['block_id'] = 'list_videos_videos_list_search_result'
            params['q'] = self._search_query
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            if page_filter.sort_order.filter_id in (PornFilterTypes.RatingOrder, PornFilterTypes.ViewsOrder):
                params['sort_by'] += page_filter.period.value
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request

        else:
            return super(PornoDep, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                 page_filter, fetch_base_url)


class WatchMyGfMe(AnyPorn):
    max_flip_images = 30
    videos_per_video_page = 56

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/girls/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/new/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/popular/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/rated/'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/longest/'),
            PornCategories.MOST_DISCUSSED_VIDEO: urljoin(self.base_url, '/commented/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_sort_order = [(PornFilterTypes.DateOrder, 'New', 'post_date'),
                            (PornFilterTypes.ViewsOrder, 'Most Viewed', 'video_viewed'),
                            (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                            (PornFilterTypes.FeaturedOrder, 'Recently Featured', 'last_time_view_date'),
                            ]
        video_period = ([(PornFilterTypes.AllDate, 'All time', ''),
                         (PornFilterTypes.OneDate, 'This Month', '_month'),
                         (PornFilterTypes.TwoDate, 'This week', '_week'),
                         (PornFilterTypes.ThreeDate, 'Today', '_today'),
                         ],
                        [('sort_order', [PornFilterTypes.RatingOrder,
                                         PornFilterTypes.ViewsOrder])]
                        )
        video_quality = [(PornFilterTypes.AllQuality, 'All', '0'),
                         (PornFilterTypes.HDQuality, 'HD', '1'),
                         ]
        search_sort_order = [(PornFilterTypes.RelevanceOrder, 'Most Relevant', '')] + video_sort_order

        category_params = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.VideosPopularityOrder, 'Popular Categories', 'avg_videos_popularity'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            ],
             }
        porn_stars_params = \
            {'sort_order': [(PornFilterTypes.VideosPopularityOrder, 'Most Popular', 'model_viewed'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.SubscribersOrder, 'Most Subscribed', 'subscribers_count'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            ]
             }
        channel_params = porn_stars_params
        video_params = {'sort_order': video_sort_order,
                        'period_filters': video_period,
                        'quality_filters': video_quality,
                        }
        search_params = {'sort_order': search_sort_order,
                         'period_filters': video_period,
                         }

        self._video_filters = \
            PornFilter(data_dir=self.fetcher_data_dir,
                       categories_args=category_params if PornCategories.CATEGORY_MAIN in self.object_urls else None,
                       channels_args=channel_params if PornCategories.CHANNEL_MAIN in self.object_urls else None,
                       porn_stars_args=porn_stars_params
                       if PornCategories.PORN_STAR_MAIN in self.object_urls else None,
                       single_category_args=video_params if PornCategories.CATEGORY_MAIN in self.object_urls else None,
                       single_channel_args=video_params if PornCategories.CHANNEL_MAIN in self.object_urls else None,
                       single_porn_star_args=video_params
                       if PornCategories.PORN_STAR_MAIN in self.object_urls else None,
                       single_tag_args=video_params if PornCategories.TAG_MAIN in self.object_urls else None,
                       video_args=video_params,
                       search_args=search_params,
                       )

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.watchmygf.me/'

    @property
    def max_pages(self):
        return 10000

    def __init__(self, source_name='WatchMyGfMe', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(WatchMyGfMe, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="video-box-body categories item"]/div[@class="video-box-card"]/a')
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="video-box-img more"]/img')
            image = image_data[0].attrib['data-src'] if len(image_data) == 1 else None
            title = image_data[0].attrib['alt'] if len(image_data) == 1 else None

            if title is None:
                title = category.xpath('./div[@class="video-box-img more"]/'
                                       'div[@class="video-box-description second"]/'
                                       'div[@class="video-box-text"]')
                assert len(title) > 0
                title = title[0].text

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      object_type=PornCategories.CATEGORY,
                                                      super_object=category_data,
                                                      )
            res.append(sub_object_data)
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="video-box-body for-client"]/div[@class="video-box-card"]/a')
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="video-box-img"]/img')
            image = image_data[0].attrib['data-src'] if len(image_data) == 1 else None
            title = image_data[0].attrib['alt'] if len(image_data) == 1 else None

            rating = category.xpath('./div[@class="video-box-img"]/div[@class="time"]/span')
            assert len(rating) > 0
            rating = rating[0].text

            number_of_videos = category.xpath('./div[@class="video-box-description"]/div[@class="video-box-likes"]/'
                                              'div/span[@class="like"]')
            assert len(number_of_videos) > 0
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            if title is None:
                title = category.xpath('./div[@class="video-box-description"]/div[@class="video-box-likes"]/'
                                       'div[@class="title-video-box-likes"]')
                assert len(title) > 0
                title = title[0].text

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      rating=rating,
                                                      object_type=PornCategories.PORN_STAR,
                                                      super_object=porn_star_data,
                                                      )
            res.append(sub_object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="video-box-card channels-page"]/a')
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="video-box-img channels-page"]/img')
            image = image_data[0].attrib['data-src'] if len(image_data) == 1 else None
            title = image_data[0].attrib['alt'] if len(image_data) == 1 else None

            rating = category.xpath('./div[@class="video-box-img channels-page"]/'
                                    'div[@class="time channels-page"]/span')
            assert len(rating) > 0
            rating = rating[0].text

            number_of_videos = category.xpath('./div[@class="video-box-img channels-page"]/'
                                              'div[@class="video-box-description channels-page"]/'
                                              'div[@class="video-box-likes"]/div/span[@class="like"]')
            assert len(number_of_videos) > 0
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            if title is None:
                title = category.xpath('./div[@class="video-box-img channels-page"]/'
                                       'div[@class="video-box-description channels-page"]/'
                                       'div[@class="video-box-likes"]/div[@class="title-video-box-likes"]')
                assert len(title) > 0
                title = title[0].text

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      rating=rating,
                                                      object_type=PornCategories.CHANNEL,
                                                      super_object=channel_data,
                                                      )
            res.append(sub_object_data)
        channel_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        tag_properties = self._get_tag_properties(page_request)
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=link,
                                       url=urljoin(tag_data.url, link),
                                       title=title,
                                       number_of_videos=number_of_videos,
                                       object_type=PornCategories.TAG,
                                       super_object=tag_data,
                                       )
               for link, title, number_of_videos in zip(*tag_properties)]
        tag_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//ul[@class="channels-list-letter"]/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.xpath('./div')[0].text,
                                                 int(x.xpath('./span')[0].text) if len(x.xpath('./span')) > 0 else None)
                                                for x in raw_data if len(x.attrib['href'].split('/')) > 4])
        return links, titles, number_of_videos

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
        new_pages = [PornCatalogPageNode(catalog_manager=self.catalog_manager,
                                         obj_id=(IdGenerator.id_to_original_str(tag_data.id), chr(x)),
                                         title='{c} | Letter {p}'.format(c=tag_data.title, p=chr(x)),
                                         url=urljoin(tag_data.url,
                                                     '{x}/'.format(x=chr(x).lower() if chr(x) != '#' else 'symbol')),
                                         additional_data={'letter': chr(x)},
                                         object_type=sub_object_type,
                                         super_object=tag_data,
                                         )
                     for x in (ord('#'),) + tuple(range(ord('A'), ord('Z')+1))]
        tag_data.add_sub_objects(new_pages)

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        return self._get_video_links_from_video_data2(video_data)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        if len(self._get_available_pages_from_tree(tree)) == 0:
            return 1
        else:
            return self._binary_search_max_number_of_pages(category_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//ul[@class="pagination-list"]/li/*/text()') if x.isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 4

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div/div[@class="video-box-card item"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            preview_data = link_data[0].xpath('./div[@class="video-box-img"]')
            assert len(preview_data) == 1
            preview = preview_data[0].attrib['data-preview'] if 'data-preview' in preview_data[0].attrib else None
            image_data = preview_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-src']
            title = image_data[0].attrib['alt'] if 'alt' in image_data[0].attrib else None
            flip_image = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                          for i in range(1, int(image_data[0].attrib['data-cnt']) + 1)]

            video_length = preview_data[0].xpath('./div[@class="time"]')
            assert len(video_length) == 1
            video_length = self._format_duration(video_length[0].text)

            info_data = link_data[0].xpath('./div[@class="video-box-description"]')
            assert len(info_data) == 1
            if title is None:
                title = info_data[0].attrib['title']

            rating = info_data[0].xpath('./div[@class="video-box-likes"]/span[@class="like"]')
            rating = re.findall(r'\d+%', rating[0].text) if len(rating) > 0 else '0'

            number_of_views = info_data[0].xpath('./div[@class="video-box-likes"]/span[@class="eye"]')
            number_of_views = re.findall(r'\d+%', number_of_views[0].text) if len(number_of_views) > 0 else '0'

            uploader = info_data[0].xpath('./div[@class="video-box-info"]/object/a')
            additional_data = {'uploader': uploader[0].text, 'link': uploader[0].attrib['href']} \
                if len(uploader) > 0 else None

            video_data = PornCatalogVideoPageNode(
                catalog_manager=self.catalog_manager,
                obj_id=link,
                title=title,
                url=urljoin(self.base_url, link),
                image_link=image,
                flip_images_link=flip_image,
                preview_video_link=preview,
                duration=video_length,
                rating=rating,
                number_of_views=number_of_views,
                additional_data=additional_data,
                object_type=PornCategories.VIDEO,
                super_object=page_data,
            )
            res.append(video_data)

        # page_filter = self.get_proper_filter(page_data).current_filters
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        headers = {
            'Accept': '*.*',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        if page_number is None:
            page_number = 1
        params.update({
            'mode': 'async',
            'function': 'get_block',
        })
        if page_filter.quality.value is not None:
            params['is_hd'] = [page_filter.quality.value]
        if page_number > 1:
            params['from'] = str(page_number).zfill(2)

        if true_object.object_type == PornCategories.TAG_MAIN:
            params = {}
        elif true_object.object_type == PornCategories.LATEST_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = page_filter.sort_order.value
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            params['block_id'] = 'list_videos_videos_list_search_result'
            params['q'] = self._search_query
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            if 'from' in params:
                params.pop('from')
            params['from_videos'] = str(page_number).zfill(2)
        else:
            return super(WatchMyGfMe, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                    page_filter, fetch_base_url)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw number, i.e. '7m:58s'.
        :return:
        """
        return super(AnyPorn, self)._format_duration(raw_duration)


if __name__ == '__main__':
    # category_id = '/search/biggest-tits/'  # 'Japanese'
    # category_id = IdGenerator.make_id('/categories/milf/')  # 'Japanese'
    # channel_id = IdGenerator.make_id('/channel/exxxtra-small/')  # 'Japanese'
    # module = AnyPorn()
    # module = AlphaPorno()
    # module = TubeWolf()
    # module = PervertSluts()
    # module = Analdin()
    # module = Fapster()
    # module = HellPorno()
    # module = XBabe()
    # module = BravoPorn()
    # module = XCum()
    # module = HellMoms()
    # module = PornPlus()
    # module = BravoTeens()
    # module = MadThumbs()
    # module = VQTube()
    # module = Xozilla()
    # module = SlutLoad()
    # module = Sex3()
    # module = AnySex()
    module = CrocoTube()
    # module.get_available_categories()
    # module.download_category(category_id, verbose=1)
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['channels']['obj'], (channel_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
