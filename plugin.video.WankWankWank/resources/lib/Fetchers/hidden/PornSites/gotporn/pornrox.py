from ....catalogs.porn_catalog import PornCategories, PornFilterTypes
from .pornhd import PornHD


class PornRox(PornHD):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.pornrox.com/category',
            PornCategories.PORN_STAR_MAIN: 'https://www.pornrox.com/pornstars',
            PornCategories.CHANNEL_MAIN: 'https://www.pornrox.com/channel',
            PornCategories.RECOMMENDED_VIDEO: 'https://www.pornrox.com/?order=featured',
            PornCategories.LATEST_VIDEO: 'https://www.pornrox.com/?order=newest',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.pornrox.com/?order=most-popular',
            PornCategories.LONGEST_VIDEO: 'https://www.pornrox.com/?order=longest',
            PornCategories.TOP_RATED_VIDEO: 'https://www.pornrox.com/?order=top-rated',
            # PornCategories.LIVE_VIDEO: 'https://www.pornrox.com/live-sex',
            PornCategories.SEARCH_MAIN: 'https://www.pornrox.com/search',
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
        return 'https://www.pornrox.com/'

    def __init__(self, source_name='PornRox', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornRox, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)
