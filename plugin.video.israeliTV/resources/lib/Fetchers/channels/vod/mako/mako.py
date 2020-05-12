from .... import urljoin

# Regex
import re

# JSON
import json

from ....catalogs.vod_catalog import VODCategories, VODCatalogNode
from .base import Base


class Mako(Base):
    def __init__(self, vod_name='Mako', vod_id=-1, store_dir='.', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(Mako, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        return NotImplementedError

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        return NotImplementedError

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
                                                    url=urljoin(self.base_url, x['url']),
                                                    image_link=x['logoPicVOD']
                                                    if (x['logoPicVOD'] is not None and len(x['logoPicVOD']) > 0
                                                        and x['logoPicVOD'] != 'null')
                                                    else x['logoPic'],
                                                    super_object=base_object,
                                                    subtitle=x['subtitle'],
                                                    description=x['brief'],
                                                    object_type=VODCategories.SHOW,
                                                    raw_data=x)
                                     for x in raw_data['root']['allPrograms']])

        # with open(self.available_shows_data_filename, 'wb') as fl:
        #     pickle.dump(self.available_categories, fl)

    def _update_live_page_data(self):
        """
        Updates the live page data.
        :return:
        """
        video_fetch_url = self.video_fetch_url
        params = {
            'jspName': 'FlashVODMakolivePopup.jsp',
            'type': 'service',
            'device': 'desktop',
            'orderingName': 'VODPopup24/7',
            'contentTypeName': 'RelLinks',
        }
        req = self.session.get(video_fetch_url, params=params)
        res = req.json()
        self.live_data['raw_data'] = res
        # We check whether the page has the right structure.
        if (
                'makolive' not in self.live_data['raw_data'] or 'list' not in self.live_data['raw_data']['makolive'] or
                len(self.live_data['raw_data']['makolive']['list']) == 0
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

        link = urljoin(self.base_url, self.live_data['raw_data']['makolive']['list'][0]['link'])
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.mako.co.il/mako-vod?partner=NavBar',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        params = {
            'partner': 'headerNav',
        }
        req = self.session.get(link, headers=headers, params=params)
        data = re.findall(r'(?:var videoJson =\')(.*?)(?:\';)', req.text)
        self.live_data['live_show_data'] = json.loads(data[0])

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Mako, self)._version_stack + [self.__version]
