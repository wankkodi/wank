import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories
from .base import BaseClass


class WetSins(BaseClass):
    @property
    def object_urls(self):
        res = super(WetSins, self).object_urls
        res.pop(PornCategories.CHANNEL_MAIN)
        res[PornCategories.CATEGORY_MAIN] = urljoin(self.base_url, 'channels/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.wetsins.com/'

    def _prepare_filters(self):
        res = super(WetSins, self)._prepare_filters()
        res['single_channel_args'] = None
        return res

    def __init__(self, source_name='WetSins', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(WetSins, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="textpage-inner-col inner-col"]/'
                                 'div[@style="width: 25%; min-width: 250px; float: left;"]/span/a')
        raw_numbers = tree.xpath('.//div[@class="textpage-inner-col inner-col"]/'
                                 'div[@style="width: 25%; min-width: 250px; float: left;"]/span/span')
        assert len(raw_objects) == len(raw_numbers)
        links, titles, number_of_videos = \
            zip(*[(x.attrib['href'], x.text, int(re.findall(r'\d+', y.text)[0]))
                  for x, y in zip(raw_objects, raw_numbers)])
        return links, titles, number_of_videos

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(WetSins, self)._version_stack + [self.__version]
