from ....catalogs.porn_catalog import PornCategories
from .base import BaseClass


class SinClips(BaseClass):
    @property
    def object_urls(self):
        res = super(SinClips, self).object_urls
        res.pop(PornCategories.CHANNEL_MAIN)
        res.pop(PornCategories.CATEGORY_MAIN)
        res.pop(PornCategories.PORN_STAR_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://sinclips.com/'

    def _prepare_filters(self):
        res = super(SinClips, self)._prepare_filters()
        res['single_channel_args'] = None
        res['single_category_args'] = None
        res['porn_stars_args'] = None
        return res

    def __init__(self, source_name='SinClips', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SinClips, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(SinClips, self)._version_stack + [self.__version]
