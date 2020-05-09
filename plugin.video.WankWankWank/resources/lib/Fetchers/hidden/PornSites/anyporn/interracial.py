from .movisand import MoviesAnd


class Interracial(MoviesAnd):
    max_flip_images = 30
    videos_per_video_page = 31

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.interracial.com/'

    @property
    def max_pages(self):
        return 2000

    def __init__(self, source_name='Interracial', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Interracial, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                          session_id)
