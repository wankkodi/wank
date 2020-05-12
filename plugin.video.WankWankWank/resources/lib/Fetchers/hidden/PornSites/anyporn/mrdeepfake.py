import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories
from .boundhub import BoundHub


class MrDeepFake(BoundHub):
    flip_number = 10

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    @property
    def object_urls(self):
        res = super(MrDeepFake, self).object_urls
        res.pop(PornCategories.CHANNEL_MAIN)
        res[PornCategories.LATEST_VIDEO] = urljoin(self.base_url, '/videos')
        res[PornCategories.ACTRESS_MAIN] = urljoin(self.base_url, '/celebrities')
        res[PornCategories.PORN_STAR_MAIN] = urljoin(self.base_url, '/pornstars')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://mrdeepfakes.com/'

    def _prepare_filters(self):
        """
        Prepares the filters
        :return:
        """
        (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
         search_params) = super(MrDeepFake, self)._prepare_filters()
        actress_params = porn_stars_params
        return (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
                search_params)

    def __init__(self, source_name='MrDeepFake', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(MrDeepFake, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        xpath = './/div[@class="pagination"]/div/ul/li/a'
        return ([int(x.attrib['data-parameters'].split(':')[-1])
                for x in tree.xpath(xpath)
                if 'data-parameters' in x.attrib and x.attrib['data-parameters'].split(':')[-1].isdigit()] +
                [int(re.findall(r'(?:from.*?:)(\d+)', x.attrib['href'])[0])
                for x in tree.xpath(xpath)
                if 'href' in x.attrib and len(re.findall(r'(?:from.*?:)(\d+)', x.attrib['href'])) > 0]
                )

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(MrDeepFake, self)._version_stack + [self.__version]
