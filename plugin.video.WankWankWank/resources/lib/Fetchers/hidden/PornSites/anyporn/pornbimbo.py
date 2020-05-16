import math
import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes
from .pornfd import PornFd


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
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornBimbo, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

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
            if right_page == left_page:
                return left_page

            page_request = self._get_object_request_no_exception_check(category_data, override_page_number=page,
                                                                       refetch_broken_page=False)
            if self._check_is_available_page(category_data, page_request):
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
            else:
                # We moved too far...
                right_page = page - 1
            page = int(math.ceil((right_page + left_page) / 2))

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

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
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
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 1

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url,
                                refetch_broken_page=True):
        if true_object.object_type in (PornCategories.CATEGORY, PornCategories.PORN_STAR, PornCategories.CHANNEL,
                                       PornCategories.TAG) + \
                tuple(self._default_sort_by.keys()):
            params['ipp'] = self.videos_per_video_page
        return super(PornBimbo, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                              page_filter, fetch_base_url, refetch_broken_page)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(PornBimbo, self)._version_stack + [self.__version]
