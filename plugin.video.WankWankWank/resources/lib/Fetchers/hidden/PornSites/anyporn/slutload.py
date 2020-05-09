from ....catalogs.porn_catalog import PornCategories, PornFilterTypes
from .madthumbs import MadThumbs


class SlutLoad(MadThumbs):
    @property
    def max_pages(self):
        return 8000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.slutload.com/categories/',
            # VideoCategories.CHANNEL_MAIN: 'https://www.slutload.com/sites/',
            # VideoCategories.PORN_STAR_MAIN: 'https://www.slutload.com/models/',
            # PornCategories.TAG_MAIN: 'https://www.slutload.com/tags/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.slutload.com/rating/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.slutload.com/view/',
            PornCategories.SEARCH_MAIN: 'https://www.slutload.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.slutload.com/'

    def __init__(self, source_name='SlutLoad', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SlutLoad, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)
