from ....catalogs.porn_catalog import PornCategories
from .base import BaseFetcher


class Pornoxo(BaseFetcher):
    @property
    def object_urls(self):
        res = super(Pornoxo, self).object_urls
        res.pop(PornCategories.PORN_STAR_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornoxo.com/'

    def __init__(self, source_name='Pornoxo', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Pornoxo, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Pornoxo, self)._version_stack + [self.__version]
