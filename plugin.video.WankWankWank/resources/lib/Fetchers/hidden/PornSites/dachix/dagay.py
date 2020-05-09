from .deviantclip import DeviantClip


class DaGay(DeviantClip):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.dagay.com/'

    def __init__(self, source_name='DaGay', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(DaGay, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                    session_id)