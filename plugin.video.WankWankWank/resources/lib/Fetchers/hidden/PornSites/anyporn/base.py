# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher, PornNoVideoError

# Internet tools
from .... import quote_plus, parse_qsl

# Regex
import re

# Json
from ....tools.text_json_manioulations import prepare_json_from_not_formatted_text

# Nodes
from ....catalogs.porn_catalog import VideoNode, VideoSource, VideoTypes
from ....catalogs.porn_catalog import PornCategories

# External Fetchers
from ....tools.external_fetchers import KTMoviesFetcher, NoVideosException

# Heritages
from abc import ABCMeta


class Base(PornFetcher):
    metaclass = ABCMeta
    video_quality_index = {'UHD': 2160, 'HQ': 720, 'LQ': 360}
    max_search_pages = 250

    def __init__(self, source_name, source_id, store_dir, data_dir, source_type, use_web_server, session_id):
        """
        C'tor
        :param source_name: save directory
        """
        super(Base, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                   session_id)
        self.kt_fetcher = KTMoviesFetcher(self.session, self.user_agent, self.parser)

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
        if len(videos) == 0:
            error_module = self._prepare_porn_error_module_for_video_page(video_data, tmp_request.url)
            raise PornNoVideoError(error_module.message, error_module)
        elif len(videos) > 1:
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
        try:
            videos, resolutions = self.kt_fetcher.get_video_link(video_data.url)
        except NoVideosException as err:
            error_module = self._prepare_porn_error_module_for_video_page(video_data, err.error_module.url,
                                                                          err.error_module.message)
            raise PornNoVideoError(error_module.message, error_module)

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
        if len(videos) == 0:
            error_module = self._prepare_porn_error_module_for_video_page(video_data, tmp_request.url)
            raise PornNoVideoError(error_module.message, error_module)
        elif len(videos) > 1:
            videos = sorted(((VideoSource(link=x.attrib['src'],
                                          resolution=re.findall(r'\d+', x.attrib['title'])[0],
                                          video_type=VideoTypes.VIDEO_REGULAR)
                              ) for x in videos),
                            key=lambda x: x.resolution, reverse=True)
        else:
            videos = [VideoSource(link=videos[0].attrib['src'], video_type=VideoTypes.VIDEO_REGULAR)]
        return VideoNode(video_sources=videos)

    def _get_video_links_from_video_data4(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        request_data = re.findall(r'(?:var flashvars = )({.*?})(?:;)', tmp_request.text, re.DOTALL)
        raw_data = prepare_json_from_not_formatted_text(request_data[0])

        videos = [VideoSource(link=raw_data['video_url'])]
        return VideoNode(video_sources=videos, verify=False)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN):
            return 1
        page_request = self._get_object_request_no_exception_check(category_data) if fetched_request is None \
            else fetched_request
        if not self._check_is_available_page(category_data, page_request):
            return 1
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return (max(available_pages)
                if category_data.object_type not in (PornCategories.TAG, PornCategories.SEARCH_MAIN)
                else min(self.max_search_pages, max(available_pages))) if len(available_pages) > 0 else 1

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        # todo: to make more generic
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

        elif true_object.object_type in (PornCategories.SEARCH_MAIN, PornCategories.TAG):
            params['block_id'] = 'list_videos_v2_videos_list_search_result'
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            if 'from' in params:
                params.pop('from')
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
            params['q'] = self._search_query if true_object.object_type == PornCategories.SEARCH_MAIN \
                else fetch_base_url.split('/')[-2]

        elif true_object.object_type in (PornCategories.CATEGORY, PornCategories.CHANNEL,
                                         PornCategories.PORN_STAR, PornCategories.ACTRESS):
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = page_filter.sort_order.value
        elif true_object.object_type in (PornCategories.MOST_VIEWED_VIDEO, PornCategories.POPULAR_VIDEO):
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
            raise ValueError('Wrong category type {c}'.format(c=true_object.object_type))

        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            params['sort_by'] += page_filter.period.value
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    @staticmethod
    def _format_duration1(raw_duration):
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
