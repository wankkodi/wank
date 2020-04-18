# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError

# Internet tools
from .. import urljoin, quote_plus

# Regex
import re

# # Math
# import math

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# Generator id
from ..id_generator import IdGenerator


class WankGalore(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://wankgalore.com/channels',
            PornCategories.TRENDING_VIDEO: 'https://wankgalore.com/trending',
            PornCategories.LATEST_VIDEO: 'https://wankgalore.com/newest',
            PornCategories.POPULAR_VIDEO: 'https://wankgalore.com/popular',
            PornCategories.LONGEST_VIDEO: 'https://wankgalore.com/longest',
            PornCategories.SEARCH_MAIN: 'https://wankgalore.com/search',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://wankgalore.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'added_before_filters': [(PornFilterTypes.AllAddedBefore, 'Anytime', None),
                                                  (PornFilterTypes.OneAddedBefore, '1 Day', '1'),
                                                  (PornFilterTypes.TwoAddedBefore, '7 Days', '7'),
                                                  (PornFilterTypes.ThreeAddedBefore, '30 Days', '30'),
                                                  ],
                         }
        categories_filters = \
            {'sort_order': ((PornFilterTypes.PopularityOrder, 'Popularity', None),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'alphabetically'),
                            ),
             }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=categories_filters,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='WankGalore', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(WankGalore, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//ul[@class="gallery category"]/li')
        res = []
        for category in categories:
            link_data = category.xpath('./figure/a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title'].title()

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] \
                if 'src' in image_data[0].attrib else image_data[0].attrib['data-original']

            number_of_videos_data = category.xpath('./figcaption/a/span[@class="score"]')
            assert len(number_of_videos_data) == 1
            number_of_videos = int(number_of_videos_data[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(category_data.url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))
        category_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        page_request = self.get_object_request(video_data)
        videos = [VideoSource(link=x) for x in re.findall(r'(?:sources.*src: *\')(.*?)(?:\')', page_request.text)]
        return VideoNode(video_sources=videos)

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
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

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
        videos = tree.xpath('.//ul[@class="gallery"]/li/figure')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title'].title()
            video_preview = link_data[0].attrib['data-animation']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] \
                if 'src' in image_data[0].attrib else image_data[0].attrib['data-original']

            video_length = video_tree_data.xpath('./figcaption/ul[@class="properties"]/li[@class="dur"]/time')
            assert len(video_length) == 1
            video_length = video_length[0].text

            added_before = video_tree_data.xpath('./figcaption/ul[@class="properties"]/li[@class="pubtime"]')
            assert len(added_before) == 1
            added_before = added_before[0].text

            res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                obj_id=link,
                                                url=urljoin(self.base_url, link),
                                                title=title,
                                                image_link=image,
                                                preview_video_link=video_preview,
                                                duration=self._format_duration(video_length),
                                                added_before=added_before,
                                                object_type=PornCategories.VIDEO,
                                                super_object=page_data,
                                                ))
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            # 'Referer': page_data.url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if true_object.object_type == PornCategories.CATEGORY_MAIN:
            # We have only sort filter
            split_url = split_url[:4]
            if page_filter.sort_order.value is not None:
                split_url.append(page_filter.sort_order.value)
        elif true_object.object_type == PornCategories.CATEGORY:
            # We have video
            split_url = split_url[:5]
            if page_filter.added_before.value is not None:
                split_url[-2] += page_filter.added_before.value
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            if page_number is not None and page_number != 1:
                params['page'] = page_number
        else:
            split_url = split_url[:4]
            if page_filter.added_before.value is not None:
                split_url[-1] += page_filter.added_before.value
        if page_number is not None and page_number != 1 and 'page' not in params:
            split_url.append(str(page_number))
        program_fetch_url = '/'.join(split_url)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?query={q}'.format(q=quote_plus(query))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornky.com/categories/full-hd-porno/')
    module = WankGalore()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
