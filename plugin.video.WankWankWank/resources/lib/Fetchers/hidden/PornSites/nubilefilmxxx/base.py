# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urlparse, quote_plus

# Nodes
from ....catalogs.porn_catalog import VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories

# abstract
from abc import ABCMeta, abstractmethod


class BaseObject(PornFetcher):
    @property
    @abstractmethod
    def base_url(self):
        """
        Base site url.
        :return:
        """
        raise NotImplementedError

    metaclass = ABCMeta

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        videos = [VideoSource(link=x.attrib['src']) for x in tmp_tree.xpath('.//video/source')]
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'identity;q=1, *;q=0',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': urlparse(videos[0].link).hostname,
            'Range': 'bytes=0-',
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': self.user_agent
        }
        return VideoNode(video_sources=videos, headers=headers)

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
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
        if page_number is not None and page_number != 1:
            if len(split_url[-1]) > 0:
                split_url.append('')
            split_url.insert(-1, 'page')
            split_url.insert(-1, str(page_number))

        if page_filter.sort_order.value is not None:
            if true_object.object_type not in (PornCategories.LATEST_VIDEO, PornCategories.MOST_VIEWED_VIDEO,
                                               PornCategories.LONGEST_VIDEO, PornCategories.POPULAR_VIDEO,
                                               PornCategories.RANDOM_VIDEO):
                params['filter'] = [page_filter.sort_order.value]

        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?s={q}'.format(q=quote_plus(query))
