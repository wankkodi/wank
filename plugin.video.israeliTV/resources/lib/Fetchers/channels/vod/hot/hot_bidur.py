from .base import Base
from ....catalogs.vod_catalog import VODCategories


class HotBidur(Base):
    @property
    def object_urls(self):
        return {
            VODCategories.CHANNELS_MAIN: 'http://hot.ynet.co.il/home/0,7340,L-7261,00.html',
        }

    def __init__(self, source_name='HotBidur', source_id=-9, store_dir='.\\Hot\\', data_dir='../../Data',
                 source_type='VOD', use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(HotBidur, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Base, self)._version_stack + [self.__version]
