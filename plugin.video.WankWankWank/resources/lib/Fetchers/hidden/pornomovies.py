# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError, PornNoVideoError, PornErrorModule

# Internet tools
from .. import urljoin, parse_qs, quote

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# Generator id
from ..id_generator import IdGenerator

# Math
import math


class PornoMovies(PornFetcher):
    # Very similar to ShesFreaky
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
            PornCategories.CATEGORY_MAIN: 'https://www.pornomovies.com/categories/',
            PornCategories.LATEST_VIDEO: 'https://www.pornomovies.com/most-recent/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.pornomovies.com/most-viewed/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.pornomovies.com/top-rated/',
            PornCategories.LONGEST_VIDEO: 'https://www.pornomovies.com/longest/',
            PornCategories.SEARCH_MAIN: 'https://www.pornomovies.com/search/',
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
        return 'https://www.pornomovies.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Newest', 'most-recent'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        ),
                         'period_filters': ([(PornFilterTypes.AllDate, 'All time', None),
                                             (PornFilterTypes.TwoDate, 'Week', 'week'),
                                             (PornFilterTypes.OneDate, 'Month', 'month'),
                                             (PornFilterTypes.ThreeDate, 'Today', 'day'),
                                             ],
                                            [('sort_order', [PornFilterTypes.RatingOrder,
                                                             PornFilterTypes.ViewsOrder])]),
                         'length_filters': ([(PornFilterTypes.AllLength, 'Any duration', None),
                                             (PornFilterTypes.OneLength, 'Short (0-5 min.)', 'duration=short'),
                                             (PornFilterTypes.TwoLength, 'Medium (5-20 min.)', 'duration=medium'),
                                             (PornFilterTypes.ThreeLength, 'Long (20+ min.)', 'duration=long'),
                                             ],
                                            [('sort_order', [PornFilterTypes.DateOrder,
                                                             PornFilterTypes.RatingOrder,
                                                             PornFilterTypes.ViewsOrder])]
                                            ),
                         }
        search_filters = {'sort_order': ((PornFilterTypes.RelevanceOrder, 'Relevance', None),
                                         (PornFilterTypes.DateOrder, 'Newest', 'most-recent'),
                                         (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                         (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                         ),
                          'period_filters': video_filters['period_filters'],
                          'length_filters': video_filters['length_filters'],
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='PornoMovies', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornoMovies, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                          session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//main//div[@class="inner-block"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            title = category.attrib['title']

            image = category.xpath('./span[@class="image"]/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(category_data.url, link),
                                               image_link=image,
                                               title=title,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
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
        tmp_request = self.session.get(video_data.url, headers=headers)
        if not self._check_is_available_page(tmp_request):
            server_data = PornErrorModule(self.data_server, self.source_name, video_data.url,
                                          'Cannot fetch video links from the url {u}'.format(u=tmp_request.url),
                                          None, None)
            raise PornNoVideoError('No Video link for url {u}'.format(u=tmp_request.url), server_data)

        tree = self.parser.parse(tmp_request.text)
        videos = [VideoSource(link=x) for x in tree.xpath('.//video/source/@src')]
        assert len(videos) > 0
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
        start_page = category_data.page_number if category_data.page_number is not None else 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            # We have no pages at all!
            return 1
        max_page = max(pages)
        if max_page - start_page < self._binary_search_page_threshold:
            return max_page
        # We perform binary search
        return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

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
            else math.ceil((right_page + left_page) / 2)
        while 1:
            if right_page == left_page:
                return left_page
            elif left_page > right_page:
                # We had a mistake on the previous measurement
                right_page = 2 * (right_page - left_page) + left_page
            try:
                page_request = self.get_object_request(category_data, override_page_number=page, send_error=False)
                tree = self.parser.parse(page_request.text)
                pages = self._get_available_pages_from_tree(tree)
                if len(pages) == 0:
                    # We also moved too far...
                    right_page = page - 1
                else:
                    max_page = max(pages)
                    if max_page - page < self._binary_search_page_threshold:
                        return max_page

                    left_page = max_page
            except PornFetchUrlError:
                # We moved too far...
                right_page = page - 1
            page = math.ceil((right_page + left_page) / 2)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//div[@id="pagination"]/div/*')
                if x.text is not None and x.text.isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 10

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="item-block item-normal col"]/div/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']
            title = video_tree_data.attrib['title']

            number_of_flip_images = video_tree_data.xpath('./span[@class="image"]/script')
            if len(number_of_flip_images) == 0:
                # gallery
                continue

            number_of_flip_images = len(re.findall(r'(?:Array\()(.*?)(?:\))',
                                                   number_of_flip_images[-1].text)[-1].split(','))

            image_data = video_tree_data.xpath('./span[@class="image"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-src']
            flip_images = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                           for i in range(1, number_of_flip_images + 1)]

            added_before = video_tree_data.xpath('./span[@class="image"]/span[@class="vidinfo"]/'
                                                 'span[@class="icon i-calendar"]')
            assert len(added_before) == 1
            added_before = self._clear_text(re.sub(r' \| ', '', added_before[0].tail))

            video_length = video_tree_data.xpath('./span[@class="image"]/span[@class="vidinfo"]/'
                                                 'span[@class="icon i-time"]')
            assert len(video_length) == 1
            video_length = self._clear_text(re.sub(r' \| ', '', video_length[0].tail))

            number_of_views = video_tree_data.xpath('./span[@class="image"]/span[@class="vidinfo"]/'
                                                    'span[@class="icon i-time"]')
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(re.sub(r' \| ', '', number_of_views[0].tail))

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  added_before=added_before,
                                                  number_of_views=number_of_views,
                                                  duration=self._format_duration(video_length),
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

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
        if len(re.findall(r'page\d+.html', split_url[-1])) > 0:
            split_url[-1] = ''

        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            split_url.insert(-1, page_filter.sort_order.value)
        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            split_url.insert(-1, page_filter.period.value)

        if (
                page_filter.length.value is not None and
                conditions.length.sort_order is not None and true_sort_filter_id in conditions.length.sort_order
        ):
            params.update(parse_qs(page_filter.length.value))

        if page_number is not None and page_number > 1:
            split_url[-1] = 'page{p}.html'.format(p=page_number)

        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote(query.replace(' ', '-')))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    module = PornoMovies()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=False)
