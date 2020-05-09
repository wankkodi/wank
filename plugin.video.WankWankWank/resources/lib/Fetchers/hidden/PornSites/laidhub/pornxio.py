from .... import urljoin

from ....catalogs.porn_catalog import PornCategories
from .base import BaseClass


class PornXio(BaseClass):
    @property
    def object_urls(self):
        res = super(PornXio, self).object_urls
        res[PornCategories.CATEGORY_MAIN] = urljoin(self.base_url, 'category/')
        res[PornCategories.CHANNEL_MAIN] = urljoin(self.base_url, 'studios/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://pornxio.com/'

    def __init__(self, source_name='PornXio', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornXio, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)
