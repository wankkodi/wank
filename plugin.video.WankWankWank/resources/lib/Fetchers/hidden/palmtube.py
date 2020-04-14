# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError

# Internet tools
from .. import urljoin, quote_plus, parse_qs

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# Generator id
from ..id_generator import IdGenerator


class PalmTube(PornFetcher):
    _watch_url = 'https://palmtube.com/watch/'

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
            PornCategories.CATEGORY_MAIN: 'https://palmtube.com/all_categories/',
            PornCategories.PORN_STAR_MAIN: 'https://palmtube.com/pornstars/',
            PornCategories.LATEST_VIDEO: 'https://palmtube.com/?s=2',
            PornCategories.TOP_RATED_VIDEO: 'https://palmtube.com/?s=3',
            PornCategories.FAVORITE_VIDEO: 'https://palmtube.com/?s=4',
            PornCategories.LONGEST_VIDEO: 'https://palmtube.com/?s=1',
            PornCategories.SEARCH_MAIN: 'https://palmtube.com/channel/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://palmtube.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'New', '2'),
                                        (PornFilterTypes.RatingOrder, 'Rating', '3'),
                                        (PornFilterTypes.FavorOrder, 'Votes', '4'),
                                        (PornFilterTypes.LengthOrder, 'Duration', '1'),
                                        ],
                         }
        video_filters = {'sort_order': ([(PornFilterTypes.PopularityOrder, 'Most popular', '')] +
                                        video_filters['sort_order']),
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         video_args=video_filters,
                                         search_args=video_filters,
                                         )

    def __init__(self, source_name='PalmTube', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PalmTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="Thumb Thumb_Category"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@class="Thumb Thumb_Category"]/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_base_object(self, object_data, xpath, object_type):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt'] \
                if 'alt' in image_data[0].attrib else category.xpath('./span[@class="Thumb_Title"]')[0].text

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               object_type=object_type,
                                               super_object=object_data,
                                               ))

        object_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)

        videos = tmp_tree.xpath('.//video/source')
        assert len(videos) > 0
        videos = [VideoSource(link=x.attrib['src']) for x in videos]
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        start_page = category_data.page_number if category_data.page_number is not None else 1
        try:
            page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        except PornFetchUrlError:
            return 1

        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        max_page = max(pages)
        if (max_page - start_page) < self._binary_search_page_threshold:
            return max_page
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 3

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//div[@class="Pagination"]/*') if x.text.isdigit()]

    def _check_is_available_page(self, page_request):
        """
        In binary search performs test whether the current page is available.
        :param page_request: Page request.
        :return:
        """
        if not page_request.ok:
            return False
        if len(page_request.history) > 0:
            if len(page_request.history) != 1 or page_request.history[0].url.split('?')[0] != self._watch_url:
                return False
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        args = parse_qs(page_request.url.split('?')[-1])
        if 'page' in args and len(pages) == 0:
            return False
        return True

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="Thumbs_Block"]/div[@class="Thumb"]/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt'] \
                if 'alt' in image_data[0].attrib else video_tree_data.xpath('./span[@class="Thumb_Title"]')[0].text

            video_info = video_tree_data.xpath('./div[@class="Thumb_Rating"]/span')
            assert len(video_info) == 3
            rating = video_info[1]
            additional_info = {'number_of_votes': video_info[2]}

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  rating=rating,
                                                  additional_data=additional_info,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            # 'Referer': self.base_url,
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        if (
                true_object.object_type not in self._default_sort_by and page_filter.sort_order.value is not None and
                len(page_filter.sort_order.value) > 0
        ):
            params['s'] = page_filter.sort_order.value
        if page_number is not None and page_number != 1:
            params['page'] = str(page_number)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    # module = HDTubePorn()
    # module = SexVid()
    # module = PornID()
    module = PalmTube()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=False)
