from . import Base1


class AssPoint(Base1):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.asspoint.com/'

    def __init__(self, source_name='AssPoint', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(AssPoint, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)