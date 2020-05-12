from ....catalogs.porn_catalog import PornCategories, PornFilterTypes
from .base import BaseClass


class LaidHub(BaseClass):
    # todo: add types (a bit tricky)

    @property
    def object_urls(self):
        res = super(LaidHub, self).object_urls
        res.pop(PornCategories.TAG_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.laidhub.com/'

    def _prepare_filters(self):
        res = super(LaidHub, self)._prepare_filters()
        res['single_tag_args'] = None
        quality_filters = [(PornFilterTypes.AllQuality, 'All', (None, None)),
                           (PornFilterTypes.VRQuality, 'VR', ('vr-porn-categories', 'vr')),
                           (PornFilterTypes.HDQuality, 'HD', ('categories', 'hd')),
                           ]
        res['general_args'] = {'quality_filters': quality_filters}
        return res

    def __init__(self, source_name='LaidHub', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(LaidHub, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(LaidHub, self)._version_stack + [self.__version]
