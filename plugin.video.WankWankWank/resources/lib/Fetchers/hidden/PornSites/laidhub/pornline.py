import re
from .... import urljoin

from .laidhub import LaidHub


class PornPine(LaidHub):
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 20000

    @property
    def object_urls(self):
        return {
            # CategoryMain: 'https://www.pornpine.com/channels/',
            TagMain: 'https://www.pornpine.com/tags/',
            VideoCategories.CHANNEL_MAIN: 'https://www.pornpine.com/channels/',
            PornStarMain: 'https://www.pornpine.com/models/',
            TopRatedVideo: 'https://www.pornpine.com/top-rated/',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornpine.com/'

    def __init__(self, source_name='StileProject', source_id=0, store_dir='.', data_dir='../Data'):
        """
        C'tor
        :param source_name: save directory
        """
        super().__init__(source_name, source_id, store_dir, data_dir)

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        links = tree.xpath('.//ul[@class="item list-tags"]/li[@class="box"]/a/@href')
        titles = tree.xpath('.//ul[@class="item list-tags"]/li[@class="box"]/a/span/b/text()')
        number_of_videos = [None] * len(titles)
        return links, titles, number_of_videos

    def _add_tag_sub_pages(self, tag_data, sub_object_type):
        return super(LaidHub, self)._add_tag_sub_pages(tag_data, sub_object_type)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channel.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_objects(channel_data,
                                                   './/div[@class="list-sponsors"]/div[@class="cards-list"]'
                                                   '/div[@class="card"]/a',
                                                   Channel)

    def _update_available_porn_stars(self, pornstar_data):
        """
        Fetches all the available channel.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_objects(pornstar_data,
                                                   './/div[@class="list-models"]/div[@class="cards-list"]'
                                                   '/div[@class="card"]/a',
                                                   PornStar)

    def _update_available_base_objects(self, base_object_data, sub_object_xpath, object_type):
        page_request = self.get_object_request(base_object_data)

        tree = self.parser.parse(page_request.text)
        sub_objects = tree.xpath(sub_object_xpath)
        res = []
        used_ids = set()
        for sub_object in sub_objects:
            img = sub_object.xpath('./div[@class="card-img"]/img')
            assert len(img) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=sub_object.attrib['href'],
                                                  url=urljoin(base_object_data.url, sub_object.attrib['href']),
                                                  title=sub_object.attrib['title'],
                                                  image_link=img[0].attrib['src'],
                                                  object_type=object_type,
                                                  super_object=base_object_data,
                                                  )
            if object_data.id in used_ids:
                continue
            res.append(object_data)
            used_ids.add(object_data.id)
        base_object_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        pages = [int(x) for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a/text()')
                 if x.isdigit()]
        return pages

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 4

    def get_videos_data(self, object_data):
        """
        Gets videos data for the given category.
        :param object_data: Page data.
        :return:
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="cards-list"]/div[@class="item card card-video  "]')
        res = []
        for video_tree_data in videos:
            sub_node = video_tree_data.xpath('./a')
            assert len(sub_node) >= 1
            sub_node = sub_node[0]
            link = sub_node.attrib['href']
            if 'title' in sub_node.attrib:
                title = sub_node.attrib['title']
            else:
                title = video_tree_data.xpath('./div[@class="card-footer noupp"]/strong[@class="card-name"]')
                assert len(title) == 1
                title = self._clear_text(title[0].text)

            additional_categories = video_tree_data.xpath('./div[@class="card-footer noupp"]/'
                                                          'div[@class="cols-tools"]/div/ul/li/a')
            additional_data = {'categories': [{'name': x.text, 'link': x.attrib['href']}
                                              for x in additional_categories]}
            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  additional_data=additional_data,
                                                  object_type=Video,
                                                  super_object=object_data,
                                                  )
            res.append(video_data)
        object_data.add_sub_objects(res)
        return res

    def get_object_request(self, object_data, override_page_number=None):
        """
        Fetches the page number with respect to base url.
        :param object_data: Page data.
        :param override_page_number: Override page number.
        :return: Page request
        """
        program_fetch_url = object_data.url.split('?')[0]
        if len(object_data.url.split('?')) > 1:
            params = object_data.url.split('?')[1]
            params = parse_qs(params)
        else:
            params = {}

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Referer': object_data.url,
            # 'Host': urlparse(object_data.url).hostname,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        page_number = object_data.page_number if override_page_number is None else override_page_number
        if page_number is not None and page_number != 1:
            program_fetch_url = re.sub(r'/(page\d+.html)*$', '', program_fetch_url)
            program_fetch_url += '/{d}/'.format(d=page_number)

        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(PornPine, self)._version_stack + [self.__version]
