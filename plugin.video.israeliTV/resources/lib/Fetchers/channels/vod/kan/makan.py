from ....catalogs.vod_catalog import VODCategories
from .base import Base


class Makan(Base):
    schedule_url = 'https://www.kan.org.il/tv-guide/tv_guidePrograms.ashx'
    additional_content_page = 'https://www.makan.org.il/program/getMoreProgram.aspx'

    @property
    def schedule_index(self):
        return 2

    @property
    def main_channel_page(self):
        return None

    @property
    def station_id(self):
        return 3

    @property
    def object_urls(self):
        res = super(Makan, self).object_urls
        res[VODCategories.CHANNELS_MAIN] = 'https://www.makan.org.il/video/programs.aspx'
        res[VODCategories.LIVE_VIDEO] = 'https://www.makan.org.il/live/tv.aspx?stationid={sid}' \
                                        ''.format(sid=self.station_id)
        return res

    def __init__(self, vod_name='Makan', vod_id=-20, store_dir='.', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        """
        C'tor
        :param vod_name: save directory
        """
        super(Makan, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.makan.org.il/'

    def _update_base_categories(self, base_object):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'User-Agent': self.user_agent
        }

        req = self.session.get(base_object.url, headers=headers)
        tree = self.parser.parse(req.text)
        xpath = './/div[@id="moreProgram"]/div[@class="items sm_it_section"]/div[@class="it_small"]/' \
                'div[@class="it_small_pictgroup programs"]'
        shows = tree.xpath(xpath)
        sub_objects = self._get_show_objects_from_it_small_component_trees(shows, base_object)

        base_object.add_sub_objects(sub_objects)
        # with open(self.available_shows_data_filename, 'wb') as fl:
        #     pickle.dump(self.available_categories, fl)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Makan, self)._version_stack + [self.__version]
