from .base import Base


class KanEducation(Base):
    @property
    def schedule_index(self):
        return 19

    @property
    def main_channel_page(self):
        return 1083

    @property
    def station_id(self):
        return 20

    @property
    def special_show_parsing(self):
        return {
            'https://www.kan.org.il/page.aspx?landingpageid=1113': self._fetch_show_data_1113,
            'https://www.kan.org.il/page.aspx?landingpageid=1137': self._fetch_show_data_1137,
        }

    def __init__(self, vod_name='KanEducation', vod_id=-5, store_dir='.', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(KanEducation, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server,
                                           session_id)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(KanEducation, self)._version_stack + [self.__version]
