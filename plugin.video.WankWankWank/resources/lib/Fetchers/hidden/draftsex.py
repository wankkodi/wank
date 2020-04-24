# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote

# Regex
import re

# JSON
from ..tools.text_json_manioulations import prepare_json_from_not_formatted_text

import base64

# Math
import math

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# Generator id
from ..id_generator import IdGenerator


class DraftSex(PornFetcher):
    # todo: change tag to playlist support: https://daftsex.com/browse

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://daftsex.com/categories',
            PornCategories.TAG_MAIN: 'https://daftsex.com/browse',
            PornCategories.PORN_STAR_MAIN: 'https://daftsex.com/pornstars',
            PornCategories.TOP_RATED_VIDEO: 'https://daftsex.com/hottest',
            PornCategories.LATEST_VIDEO: 'https://daftsex.com/video/',
            PornCategories.SEARCH_MAIN: 'https://daftsex.com/video/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'length_filters': [(PornFilterTypes.AllLength, 'Any durations', '2'),
                                            (PornFilterTypes.OneLength, 'Short', '1'),
                                            (PornFilterTypes.TwoLength, 'Medium (5-20 min.)', '0'),
                                            ],
                         'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', '0'),
                                             (PornFilterTypes.HDQuality, 'HD quality', '1'),
                                             ],
                         'sort_order': [(PornFilterTypes.DateOrder, 'Date added', '0'),
                                        (PornFilterTypes.LengthOrder, 'Duration', '1'),
                                        (PornFilterTypes.PopularityOrder, 'Most Popular', '2'),
                                        ],
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         search_args=video_filters,
                                         video_args=video_filters,
                                         )

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://daftsex.com/'

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    def __init__(self, source_name='DaftSex', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(DraftSex, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="video-item"]/a')
        res = []
        for category in categories:
            image = category.xpath('./div[@class="video-img"]/img/@src')
            assert len(image) == 1

            title = category.xpath('./div[@class="video-title"]/text()')
            assert len(title) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(category_data.url, category.attrib['href']),
                                                  title=title[0],
                                                  image_link=urljoin(category_data.url, image[0]),
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="pornstar"]/a')
        res = []
        for category in categories:
            image = category.xpath('./img/@src')
            assert len(image) == 1

            title = category.xpath('./span/text()')
            assert len(title) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(porn_star_data.url, category.attrib['href']),
                                                  title=title[0],
                                                  image_link=urljoin(porn_star_data.url, image[0]),
                                                  object_type=PornCategories.PORN_STAR,
                                                  super_object=porn_star_data,
                                                  )
            res.append(object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available tags.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="video-item pl-wrapper"]/a')
        res = []
        for category in categories:
            image = category.xpath('./div[@class="video-img"]/img/@src')
            assert len(image) == 1

            number_of_videos = category.xpath('./div[@class="video-img"]/div[@class="playlist-info"]/'
                                              'div[@class="pl-number"]/span/text()')
            assert len(number_of_videos) == 1
            if number_of_videos[0].isdigit():
                number_of_videos = int(number_of_videos[0])
            elif number_of_videos[0][-1] == 'k':
                number_of_videos = int(float(number_of_videos[0][:-1].replace(',', '.')) * 1000) + 99
            else:
                raise RuntimeError('Unknown suffix {s}!'.format(s=number_of_videos[0][:-1]))

            title = category.xpath('./div[@class="video-title"]/text()')
            assert len(title) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(tag_data.url, category.attrib['href']),
                                                  title=title[0],
                                                  image_link=urljoin(tag_data.url, image[0]),
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.TAG,
                                                  super_object=tag_data,
                                                  )
            res.append(object_data)
        tag_data.add_sub_objects(res)
        return res

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return False

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        video_url = re.findall(r'(?:\')(https://.*)(?:\')', video_data.raw_data)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'nested-navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_url[0], headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)
        script = [x for x in tmp_tree.xpath('.//script/text()') if 'window.globParams' in x]
        script = re.findall(r'(?:window.globParams *= *)({.*})', script[0], re.DOTALL)
        script = prepare_json_from_not_formatted_text(script[0])

        url_prefix = 'https://{s}/videos/{i1}/{i2}/'.format(s=base64.b64decode(script['server'][::-1]).decode(),
                                                            i1=script['video']['id'].split('_')[0],
                                                            i2=script['video']['id'].split('_')[1])
        video_links = sorted((VideoSource(link=urljoin(url_prefix, re.sub(r'\.', '.mp4?extra=', x)),
                                          resolution=re.findall(r'(?:mp4_)(\d+)', k)[0])
                              for k, x in script['video']['cdn_files'].items()),
                             key=lambda y: y.resolution, reverse=True)
        return VideoNode(video_sources=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        is_show_more = tree.xpath('.//div[@class="more"]')
        if len(is_show_more):
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)
        else:
            return max(available_pages) if len(available_pages) > 0 else 1

    def _binary_search_max_number_of_pages(self, category_data, last_available_number_of_pages):
        """
        Performs binary search in order to find the last available page.
        :param category_data: Category data.
        :param last_available_number_of_pages: Last available number of pages. Will be the pivot for our next search.
        By default is None, which mean the original pivot will be used...
        :return: Page request
        """
        left_page = 1
        right_page = self.max_pages
        page = last_available_number_of_pages if last_available_number_of_pages is not None \
            else int(math.ceil((right_page + left_page) / 2))
        while 1:
            if left_page == right_page:
                return left_page
            page_request = self._get_object_request_no_exception_check(category_data, override_page_number=page)
            if self._check_is_available_page(category_data, page_request):
                left_page = page
            else:
                # We moved too far...
                right_page = page - 1
            page = int(math.ceil((right_page + left_page) / 2))

    def _check_is_available_page(self, page_object, page_request=None):
        """
        In binary search performs test whether the current page is available.
        :param page_object: Page object.
        :param page_request: Page request.
        :return:
        """
        if page_request is None:
            page_request = self.get_object_request(page_object)
        if page_object.object_type == PornCategories.VIDEO:
            return page_request.ok
        if page_object.true_object.object_type in (PornCategories.TAG_MAIN, PornCategories.PORN_STAR_MAIN):
            tree = self.parser.parse(page_request.text)
            is_error = tree.xpath('.//div[@class="message-error"]')
            return len(is_error) == 0
        else:
            tree = self.parser.parse(page_request.text)
            is_show_more = tree.xpath('.//div[@class="more"]')
            videos = tree.xpath('.//div[@class="video-item"]')
        return len(is_show_more) > 0 or len(videos) > 0

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//ul[@class="pagination"]/li/*/text()') if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="video-item"]/a')

        res = []
        for video_tree_data in videos:

            video_raw_data = video_tree_data.xpath('./div[@class="video-show"]/@onclick')
            assert len(video_raw_data) == 1

            img = video_tree_data.xpath('./div[@class="video-img"]/img/@src')
            assert len(img) == 1

            added_before = video_tree_data.xpath('./div[@class="video-img"]//div[@class="video-info"]/'
                                                 'span[@class="video-date"]/text()')
            assert len(added_before) == 1

            number_of_views = video_tree_data.xpath('./div[@class="video-img"]//div[@class="video-info"]/'
                                                    'span[@class="video-view"]/text()')

            video_length = video_tree_data.xpath('./div[@class="video-img"]//div[@class="video-info"]/'
                                                 'span[@class="video-time"]/text()')
            assert len(video_length) == 1

            title = video_tree_data.xpath('.//div[@class="video-title"]/text()')
            if len(title) >= 1:
                title = title[0] if len(title) == 1 else ''.join(title)
            else:
                # AD-hoc solution
                title = 'Untitled_{s}'.format(s=re.findall(r'(?:.*/)(.*)(?:.jpg)', img[0])[0]) \
                    if len(re.findall(r'(?:.*/)(.*)(?:.jpg)', img[0])) > 0 else 'Untitled'
            labels = re.findall(r'(?:\[)(.*?)(?:\])', title)
            if len(labels) > 0:
                labels = labels[0].split(', ')
                pos_title = re.findall(r'(^.*)(?: +\[.*?\])', title)
                title = pos_title[0] if len(pos_title) > 0 else ', '.join(labels)

            resolution = [int(re.findall(r'(?:HD )(\d+)', x)[0])
                          for x in labels if len(re.findall(r'HD \d+', x)) > 0][0] \
                if any(re.findall(r'HD \d+', x) for x in labels) else 480

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['href'],
                                                  url=urljoin(self.base_url, video_tree_data.attrib['href']),
                                                  preview_video_link=video_tree_data.attrib['data-webm']
                                                  if 'data-webm' in video_tree_data.attrib else None,
                                                  image_link=img[0],
                                                  added_before=added_before[0],
                                                  number_of_views=number_of_views[0]
                                                  if len(number_of_views) == 1 else None,
                                                  duration=self._format_duration(video_length[0]),
                                                  title=title,
                                                  resolution=resolution,
                                                  is_hd=resolution > 480,
                                                  raw_data=video_raw_data[0],
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        headers = {
            'Accept': 'text/html, */*; q=0.01',
            'Cache-Control': 'max-age=0',
            'Origin': self.base_url,
            'Referer': page_data.url,
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        if true_object.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.PORN_STAR_MAIN,
                                       PornCategories.TAG, PornCategories.TAG_MAIN,):
            if page_number is not None:
                params.update({'page': [page_number]})
        else:
            params.update({
                'hd': [page_filter.quality.value],
                'sort': [page_filter.sort_order.value],
                'longer': [page_filter.length.value],
                'page': [page_number - 1 if page_number is not None else 0],
            })
        page_request = self.session.post(fetch_base_url, headers=headers, data=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}'.format(q=quote(query))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('/video/Big%20Tits')
    tag_id = IdGenerator.make_id('/playlist/127351/25401')
    module = DraftSex()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user()
