from ....catalogs.porn_catalog import PornCategories
from .boundhub import BoundHub


class CamUploads(BoundHub):
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
        res = super(CamUploads, self).object_urls
        res.pop(PornCategories.TAG_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.camuploads.com/'

    def __init__(self, source_name='CamUploads', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(CamUploads, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)
