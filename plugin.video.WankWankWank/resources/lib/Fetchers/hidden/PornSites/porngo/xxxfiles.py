from .porngo import PornGo


class XXXFiles(PornGo):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.porngo.com/'

    def __init__(self, source_name='XXXFiles', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(XXXFiles, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        # return super(XXXFiles, self)._version_stack + [self.__version]
        return super(PornGo, self)._version_stack + [self.__version]
