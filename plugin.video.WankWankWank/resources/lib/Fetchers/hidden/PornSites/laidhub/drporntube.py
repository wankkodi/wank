from .... import urljoin

from ....catalogs.porn_catalog import PornCategories
from .base import BaseClass


class DrPornTube(BaseClass):
    @property
    def object_urls(self):
        res = super(DrPornTube, self).object_urls
        res.pop(PornCategories.CHANNEL_MAIN)
        res[PornCategories.CATEGORY_MAIN] = urljoin(self.base_url, 'channels/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.drporntube.com/'

    def _prepare_filters(self):
        res = super(DrPornTube, self)._prepare_filters()
        res['single_channel_args'] = None
        return res

    def __init__(self, source_name='DrPornTube', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(DrPornTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(DrPornTube, self)._version_stack + [self.__version]
