# Nodes
from ....catalogs.porn_catalog import PornCategories
from .dachix import DaChix


class DeviantClip(DaChix):
    @property
    def object_urls(self):
        tmp_res = super(DeviantClip, self).object_urls
        tmp_res.pop(PornCategories.PORN_STAR_MAIN)
        return tmp_res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.deviantclip.com/'

    def __init__(self, source_name='DeviantClip', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(DeviantClip, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                          session_id)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(DeviantClip, self)._version_stack + [self.__version]
