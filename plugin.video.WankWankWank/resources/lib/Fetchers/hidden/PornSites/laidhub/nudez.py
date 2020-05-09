from .... import urljoin

from ....catalogs.porn_catalog import PornCategories
from .base import BaseClass


class Nudez(BaseClass):
    # todo: add types (a bit tricky)

    @property
    def object_urls(self):
        res = super(Nudez, self).object_urls
        res.pop(PornCategories.CHANNEL_MAIN)
        res.pop(PornCategories.TAG_MAIN)
        res[PornCategories.CATEGORY_MAIN] = urljoin(self.base_url, 'channels/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://nudez.com/'

    def _prepare_filters(self):
        res = super(Nudez, self)._prepare_filters()
        res['single_tag_args'] = None
        res['single_channel_args'] = None
        return res

    def __init__(self, source_name='Nudez', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Nudez, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                    session_id)
