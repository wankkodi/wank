from .... import urljoin

from ....catalogs.porn_catalog import PornCategories
from .boundhub import BoundHub


class CamVideosTv(BoundHub):
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
        res = super(CamVideosTv, self).object_urls
        res[PornCategories.LATEST_VIDEO] = urljoin(self.base_url, '/recent/')
        res[PornCategories.TOP_RATED_VIDEO] = urljoin(self.base_url, '/rated/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.camvideos.tv/'

    def __init__(self, source_name='CamVideosTv', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(CamVideosTv, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                          session_id)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(CamVideosTv, self)._version_stack + [self.__version]
