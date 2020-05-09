from .... import urljoin

from ....catalogs.porn_catalog import PornCategories
from .base import BaseClass


class HandJobHub(BaseClass):
    @property
    def object_urls(self):
        res = super(HandJobHub, self).object_urls
        res.pop(PornCategories.PORN_STAR_MAIN)
        res[PornCategories.CATEGORY_MAIN] = urljoin(self.base_url, 'category/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://handjobhub.com/'

    def _prepare_filters(self):
        res = super(HandJobHub, self)._prepare_filters()
        res['porn_stars_args'] = None
        return res

    def __init__(self, source_name='HandJobHub', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HandJobHub, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)
