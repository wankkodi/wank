from .base import Base


class Kan(Base):
    @property
    def schedule_index(self):
        return 1

    @property
    def main_channel_page(self):
        return 1039

    @property
    def station_id(self):
        return 2

    @property
    def special_show_parsing(self):
        return {
            'https://www.kan.org.il/page.aspx?landingpageid=1135': self._fetch_show_data_1135,
            'https://www.kan.org.il/page.aspx?landingPageId=1135': self._fetch_show_data_1135,
            'https://www.kan.org.il/program/?catId=1274': self._fetch_show_data_1135,
            'https://www.kan.org.il/page.aspx?landingPageId=1274': self._fetch_show_data_1135,
        }

    def __init__(self, vod_name='Kan', vod_id=-4, store_dir='.', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(Kan, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Kan, self)._version_stack + [self.__version]
