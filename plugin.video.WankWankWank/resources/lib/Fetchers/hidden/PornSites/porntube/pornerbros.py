from ....catalogs.porn_catalog import PornCategories
from .porntube import PornTube


class PornerBros(PornTube):
    @property
    def object_urls(self):
        res = super(PornerBros, self).object_urls
        res.pop(PornCategories.TAG_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornerbros.com/'

    def __init__(self, source_name='PornerBros', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornerBros, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)
