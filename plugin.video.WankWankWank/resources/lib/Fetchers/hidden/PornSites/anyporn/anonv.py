from ....catalogs.porn_catalog import PornCategories
from .boundhub import BoundHub


class AnonV(BoundHub):
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
        res = super(AnonV, self).object_urls
        res.pop(PornCategories.TAG_MAIN)
        res.pop(PornCategories.CHANNEL_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://anon-v.com/'

    def __init__(self, source_name='AnonV', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(AnonV, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                    session_id)
