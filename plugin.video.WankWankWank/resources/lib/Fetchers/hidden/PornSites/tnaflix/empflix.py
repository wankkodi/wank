from ....catalogs.porn_catalog import PornCategories
from .tnaflix import TnaFlix


class EmpFlix(TnaFlix):

    # Has the same structure as tnaflix
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        res = super(EmpFlix, self).object_urls
        res.pop(PornCategories.TAG_MAIN)
        res.pop(PornCategories.CHANNEL_MAIN)
        return res

    # @property
    # def object_urls(self):
    #     return {
    #         PornCategories.CATEGORY_MAIN: 'https://www.empflix.com/categories',
    #         # PornCategories.CHANNEL_MAIN: 'https://www.empflix.com/channels',
    #         PornCategories.PORN_STAR_MAIN: 'https://www.empflix.com/pornstars',
    #         PornCategories.TOP_RATED_VIDEO: 'https://www.empflix.com/toprated/',
    #         PornCategories.POPULAR_VIDEO: 'https://www.empflix.com/popular/',
    #         PornCategories.LATEST_VIDEO: 'https://www.empflix.com/new/',
    #         PornCategories.RECOMMENDED_VIDEO: 'https://www.empflix.com/featured/',
    #     }
    #     # return {
    #     #     CategoryMain: 'https://www.empflix.com/categories',
    #     #     # CHANNEL_MAIN: 'https://www.empflix.com/channels',
    #     #     PornStarMain: 'https://www.empflix.com/pornstars',
    #     #     TopRatedVideo: 'https://www.empflix.com/toprated/?d=all&period=all',
    #     #     PopularVideo: 'https://www.empflix.com/popular/?d=all&period=all',
    #     #     LatestVideo: 'https://www.empflix.com/new/?d=all&period=all',
    #     #     RecommendedVideo: 'https://www.empflix.com/featured/?d=all&period=all',
    #     # }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.empflix.com/'

    def __init__(self, source_name='EmpFlix', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(EmpFlix, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(EmpFlix, self)._version_stack + [self.__version]
