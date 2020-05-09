import re

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes
from .madthumbs import MadThumbs
from .pervertsluts import PervertSluts


class VQTube(MadThumbs):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://vqtube.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://vqtube.com/models/',
            PornCategories.TAG_MAIN: 'https://vqtube.com/tags/',
            PornCategories.LATEST_VIDEO: 'https://vqtube.com/latest-updates/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://vqtube.com/most-popular/',
            PornCategories.TOP_RATED_VIDEO: 'https://vqtube.com/top-rated/',
            PornCategories.SEARCH_MAIN: 'https://vqtube.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://vqtube.com/'

    @property
    def number_of_videos_per_page(self):
        """
        Base site url.
        :return:
        """
        return 30  # 5*6

    def __init__(self, source_name='VQTube', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(VQTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _update_available_tags(self, tag_data):
        return super(PervertSluts, self)._update_available_tags(tag_data)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        page_request = self._get_object_request_no_exception_check(category_data) if fetched_request is None \
            else fetched_request
        if not self._check_is_available_page(category_data, page_request):
            return 1
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        xpath = './/div[@class="pagination-holder"]/ul/li/a'
        return ([int(x.attrib['href'].split('/')[-2]) for x in tree.xpath(xpath)
                if 'href' in x.attrib and len(x.attrib['href'].split('/')) > 2 and
                 x.attrib['href'].split('/')[-2].isdigit()]
                ) + \
               ([int(x.attrib['data-parameters'].split(':')[-1])
                for x in tree.xpath(xpath)
                if 'data-parameters' in x.attrib and x.attrib['data-parameters'].split(':')[-1].isdigit()] +
                [int(re.findall(r'(?:from.*?:)(\d+)', x.attrib['href'])[0])
                for x in tree.xpath(xpath)
                if 'href' in x.attrib and len(re.findall(r'(?:from.*?:)(\d+)', x.attrib['href'])) > 0]
                )

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//div[@class="list-tags"]/div[@class="margin-fix"]/ul/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, None)
                                                for x in raw_data])
        return links, titles, number_of_videos

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        if fetch_base_url == 'https://vqtube.com/categories/1/':
            # ad-hoc solution for the problematic category
            fetch_base_url += '1/'
        if true_object.object_type in (PornCategories.TAG_MAIN, ):
            # New
            headers = {
                'Accept': '*.*',
                'Cache-Control': 'max-age=0',
                'Referer': self.base_url,
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
            if page_number is None:
                page_number = 1
            params.update({
                    'mode': 'async',
                    'function': 'get_block',
                })
            if page_number > 1:
                params['from'] = str(page_number).zfill(2)
            if true_object.object_type == PornCategories.TAG_MAIN:
                params['block_id'] = 'list_tags_tags_list'
                params['sort_by'] = 'tag'

                page_request = self.session.get(fetch_base_url, headers=headers, params=params)
                return page_request
        else:
            return super(VQTube, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                               page_filter, fetch_base_url)
