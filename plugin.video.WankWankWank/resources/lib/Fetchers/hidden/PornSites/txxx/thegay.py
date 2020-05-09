from ....catalogs.porn_catalog import PornFilterTypes
from .tubepornclassic import TubePornClassic


class TheGay(TubePornClassic):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://thegay.com/'

    def __init__(self, source_name='TheGay', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(TheGay, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _prepare_filters(self):
        general_filters, video_filters, video_filters, categories_filters, porn_stars_filters, channels_filters = \
            super(TheGay, self)._prepare_filters()
        general_filters = {'general_filters': [(PornFilterTypes.GayType, 'Gay', None),
                                               ],
                           }
        return general_filters, video_filters, video_filters, categories_filters, porn_stars_filters, channels_filters
