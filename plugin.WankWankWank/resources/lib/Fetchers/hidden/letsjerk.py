# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher
from ..tools.external_fetchers import ExternalFetcher

# Internet tools
from .. import urlparse, urljoin, quote_plus

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode
from ..catalogs.porn_catalog import PornCategories, VideoNode, VideoSource

# Generator id
from ..id_generator import IdGenerator

# Warnings
import warnings


class LetsJerk(PornFetcher):
    number_of_thumbnails = 20

    @property
    def object_urls(self):
        # fixme: search temporarily disabled.
        return {
            PornCategories.CATEGORY_MAIN: 'http://www.letsjerk.is/category-page/',
            PornCategories.CHANNEL_MAIN: 'http://www.letsjerk.is/studios/',
            PornCategories.LATEST_VIDEO: 'http://www.letsjerk.is/?orderby=modified&order=desc',
            PornCategories.MOST_VIEWED_VIDEO: 'http://www.letsjerk.is/?v_sortby=views&v_orderby=desc',
            # PornCategories.SEARCH_MAIN: 'http://www.letsjerk.is/',
        }

    @property
    def _default_sort_by(self):
        return {}

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.letsjerk.is/'

    def __init__(self, source_name='LetsJerk', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(LetsJerk, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)
        self.external_fetchers = ExternalFetcher(session=self.session, user_agent=self.user_agent, parser=self.parser)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_objects(category_data,
                                                   './/ul[@class="latestVideos"]/li',
                                                   PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channels.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_objects(channel_data,
                                                   './/ul[@class="latestVideos"]/li',
                                                   PornCategories.CHANNEL)

    def _update_available_base_objects(self, base_object_data, sub_object_xpath, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(sub_object_xpath)
        res = []
        for category in categories:
            title = category.xpath('./h3/a')
            if len(title) == 0:
                # We have empty sequence, just skip it...
                continue

            image = category.xpath('./a/div[@class="thumbnail"]/img')
            assert len(image) == 1
            number_of_videos = category.xpath('./div[@class="buttons"]/a')
            assert len(number_of_videos) == 1
            number_of_videos = re.findall(r'(?:All )(\d+)(?: videos)', number_of_videos[0].text)
            number_of_videos = int(number_of_videos[0]) if len(number_of_videos) > 0 else None

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=title[0].attrib['href'],
                                                  url=urljoin(self.base_url, title[0].attrib['href']),
                                                  title=title[0].text,
                                                  image_link=image[0].attrib['src'],
                                                  number_of_videos=number_of_videos,
                                                  object_type=object_type,
                                                  super_object=base_object_data
                                                  )
            res.append(object_data)
        base_object_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """

        tmp_request = self.get_object_request(video_data)
        videos = self._get_video_links_from_video_data_method1(tmp_request)
        if len(videos) == 0:
            # We try another method
            videos = self._get_video_links_from_video_data_method2(tmp_request)

        return VideoNode(video_sources=videos)

    def _get_video_links_from_video_data_method1(self, page_request):
        """
        # Method 1 of fetching the videos.
        """
        tmp_tree = self.parser.parse(page_request.text)
        request_data = tmp_tree.xpath('.//form[@id="form1"]//option/@value')
        videos = []
        if len(request_data) > 0:
            for new_url in request_data:
                if urlparse(new_url).hostname == 'streamcherry.com':
                    videos.extend(self.external_fetchers.get_video_link_from_streamcherry(new_url))
                if urlparse(new_url).hostname == 'openload.co':
                    videos.extend(self.external_fetchers.get_video_link_from_openload(new_url))
                else:
                    warnings.warn('Unknown host {h}'.format(h=urlparse(new_url).hostname))

        videos = sorted((VideoSource(link=x[0], resolution=x[1]) for x in videos),
                        key=lambda x: x.resolution, reverse=True)
        return videos

    def _get_video_links_from_video_data_method2(self, page_request):
        """
        # Method 2 of fetching the videos.
        """
        tmp_tree = self.parser.parse(page_request.text)
        request_data = tmp_tree.xpath('.//video/source')
        res = sorted((VideoSource(link=x.attrib['src'],
                                  resolution=720 if 'title' in x.attrib and 'HD' == x.attrib['title'] else 360)
                      for x in request_data),
                     key=lambda x: x.resolution, reverse=True)

        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        Finds the number of pages for the given parsed object.
        :param tree: Page tree.
        :return: number of pages (int).
        """
        pages = [int(re.findall(r'(\d+)(?:/*\?|/*$)', x.attrib['href'])[0])
                 for x in tree.xpath('.//ul[@class="pagination"]/li/a')
                 if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*\?|/*$)', x.attrib['href'])) > 0]
        return pages

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//ul[@class="video_list"]/li[@class="video"]/a')
        res = []
        for video_tree_data in videos:
            image_data = video_tree_data.xpath('./img')
            image = image_data[0].attrib['data-src'] \
                if 'data-src' in image_data[0].attrib else image_data[0].attrib['src']

            added_before = video_tree_data.xpath('./span[@class="box"]/span[@class="time"]')
            assert len(added_before) == 1

            number_of_viewers = video_tree_data.xpath('./span[@class="box"]/span[@class="views"]')
            assert len(number_of_viewers) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['href'],
                                                  url=urljoin(self.base_url, video_tree_data.attrib['href']),
                                                  title=video_tree_data.attrib['title'],
                                                  image_link=image,
                                                  added_before=added_before[0].text,
                                                  number_of_views=number_of_viewers[0].text,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')

        if page_number is not None and page_number != 1:
            if len(split_url[-1]) > 0:
                split_url.append('')
            split_url.insert(-1, 'page')
            split_url.insert(-1, str(page_number))
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


if __name__ == '__main__':
    category_id = IdGenerator.make_id('http://www.letsjerk.is/categoriesHD9/21naturals-hd/')
    channel_id = IdGenerator.make_id('http://www.letsjerk.is/categoriesHD/bangbros-hd1')
    module = LetsJerk()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['channels']['obj'], (channel_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user()
