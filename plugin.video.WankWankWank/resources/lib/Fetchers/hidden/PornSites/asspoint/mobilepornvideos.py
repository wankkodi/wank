from . import Base3


class MobilePornMovies(Base3):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.mobilepornmovies.com/'

    def __init__(self, source_name='MobilePornMovies', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(MobilePornMovies, self).__init__(source_name, source_id, store_dir, data_dir, source_type,
                                               use_web_server, session_id)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(MobilePornMovies, self)._version_stack + [self.__version]
