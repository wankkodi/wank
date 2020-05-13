from .... import urljoin, parse_qs

from ....catalogs.vod_catalog import VODCategories, VODCatalogNode
from .base import Base


class Channel24(Base):
    def __init__(self, source_name='Channel 24', source_id=-1, store_dir='.', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(Channel24, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        return NotImplementedError

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        return NotImplementedError

    @property
    def object_urls(self):
        res = super(Channel24, self).object_urls.copy()
        res[VODCategories.CHANNELS_MAIN] = 'https://www.mako.co.il/mako-vod-music24'
        return res

    def _update_base_categories(self, base_object):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        req = self.get_object_request(base_object)
        raw_data = req.json()
        base_object.add_sub_objects([VODCatalogNode(catalog_manager=self.catalog_manager,
                                                    obj_id=x['guid'],
                                                    title=x['title'],
                                                    url=urljoin(self.base_url, x['link']),
                                                    image_link=x['picUrl'],
                                                    subtitle=x['subtitle'],
                                                    object_type=VODCategories.SHOW,
                                                    super_object=base_object,
                                                    raw_data=x)
                                     for x in raw_data['root']['specialArea']['items'][1:]])
        # Update live shows
        self.live_data['raw_pre_data'] = raw_data['root']['specialArea']['items'][0]

    def _update_live_page_data(self):
        """
        Updates the live page data.
        :return:
        """
        if 'raw_pre_data' not in self.live_data:
            self._update_base_categories(self.objects[VODCategories.CHANNELS_MAIN])

        video_fetch_url = urljoin(self.object_urls[VODCategories.CHANNELS_MAIN], self.live_data['raw_pre_data']['link'])
        program_fetch_url = video_fetch_url.split('?')[0]
        if len(video_fetch_url.split('?')) > 1:
            params = video_fetch_url.split('?')[1]
            params = parse_qs(params)
        else:
            params = {}
        params.update({'type': ['service'], 'device': ['desktop']})

        req = self.session.get(program_fetch_url, params=params)
        res = req.json()
        self.live_data['raw_data'] = res
        # We check whether the page has the right structure.
        if (
                'root' not in self.live_data['raw_data'] or 'video' not in self.live_data['raw_data']['root'] or
                len(self.live_data['raw_data']['root']['video']) == 0
        ):
            raise RuntimeError('The structure of the live page has changed. Recheck the code!')

    def _update_live_show_data(self):
        """
        Updates the live page data.
        :return:
        """
        if 'raw_data' not in self.live_data:
            # We update the live page
            self._update_live_page_data()

        link = self.object_urls[VODCategories.LIVE_VIDEO]
        params = {
            'jspName': 'FlashVODMoreOnChannel.jsp',
            'type': 'service',
            'channelId': self.live_data['raw_data']['root']['channelId'],
            'device': 'desktop',
            'strto': 'true',
        }
        req = self.session.get(link, params=params)
        raw_data = req.json()
        live_data = [x for x in raw_data['moreOnChannel']
                     if 'Title' in x and x['Title'] == self.live_data['raw_data']['root']['video']['title']]
        assert len(live_data) == 1
        self.live_data['live_show_data'] = live_data[0]

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Channel24, self)._version_stack + [self.__version]
