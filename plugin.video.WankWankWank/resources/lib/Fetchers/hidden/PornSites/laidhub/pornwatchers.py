from .base import BaseClass2


class PornWatchers(BaseClass2):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornwatchers.com/'

    def __init__(self, source_name='PornWatchers', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornWatchers, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                           session_id)
