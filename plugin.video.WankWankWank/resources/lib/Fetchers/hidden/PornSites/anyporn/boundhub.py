from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes
from .pornfd import PornFd


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

    # @property
    # def possible_empty_pages(self):
    #     """
    #     Defines whether it is possible to have empty pages in the site.
    #     :return:
    #     """
    #     return True

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.boundhub.com/'

    def __init__(self, source_name='BoundHub', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(BoundHub, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
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

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(BoundHub, self)._version_stack + [self.__version]
