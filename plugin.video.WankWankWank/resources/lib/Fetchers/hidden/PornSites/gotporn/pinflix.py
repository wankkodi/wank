from ....catalogs.porn_catalog import PornCategories, PornFilterTypes
from .pornhd import PornHD


class PinFlix(PornHD):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.pinflix.com/category',
            PornCategories.PORN_STAR_MAIN: 'https://www.pinflix.com/pornstars',
            PornCategories.RECOMMENDED_VIDEO: 'https://www.pinflix.com/?order=featured',
            PornCategories.LATEST_VIDEO: 'https://www.pinflix.com/?order=newest',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.pinflix.com/?order=most-popular',
            PornCategories.LONGEST_VIDEO: 'https://www.pinflix.com/?order=longest',
            PornCategories.TOP_RATED_VIDEO: 'https://www.pinflix.com/?order=top-rated',
            # PornCategories.LIVE_VIDEO: 'https://www.pinflix.com/live-sex',
            PornCategories.SEARCH_MAIN: 'https://www.pinflix.com/search',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.RECOMMENDED_VIDEO: PornFilterTypes.RecommendedOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LIVE_VIDEO: PornFilterTypes.LiveOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pinflix.com/'

    def __init__(self, source_name='PinFlix', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PinFlix, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type == PornCategories.LIVE_VIDEO:
            return self._binary_search_max_number_of_live_pages(category_data, last_available_number_of_pages)
        # We perform binary search
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
        tmp_res = [int(x.attrib['data-last-page']) for x in tree.xpath('.//div[@class="button-wrapper text-center"]/a')
                   if 'data-last-page' in x.attrib]
        return tmp_res
