from . import Base1


class YoungPornVideos(Base1):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.youngpornvideos.com/'

    def __init__(self, source_name='YoungPornVideos', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(YoungPornVideos, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                              session_id)
