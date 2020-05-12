import re
from .... import urljoin, quote_plus

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornCatalogCategoryNode, PornCatalogVideoPageNode
from .hellmoms import HellMoms


class PornPlus(HellMoms):
    max_flip_images = 10

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.porn-plus.com/c/',
            PornCategories.TAG_MAIN: 'https://www.porn-plus.com/c/',
            PornCategories.PORN_STAR_MAIN: 'https://www.porn-plus.com/p/',
            PornCategories.LATEST_VIDEO: 'https://www.porn-plus.com/fresh/',
            PornCategories.TRENDING_VIDEO: 'https://www.porn-plus.com/trending/',
            PornCategories.SEARCH_MAIN: 'https://www.porn-plus.com/s/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.TRENDING_VIDEO: PornFilterTypes.TrendingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.porn-plus.com/'

    def __init__(self, source_name='PornPlus', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornPlus, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="thmbclck"]/div[@class="thmb"]/a',
                                                  PornCategories.CATEGORY,
                                                  True)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@class="thmbclck"]/div[@class="thmb"]/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_base_object(self, object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        for category in categories:
            link = category.attrib['href']
            title = category.attrib['title']

            image_data = category.xpath('./img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(object_data.url, link),
                                                      title=title,
                                                      image_link=image,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        if is_sort:
            res.sort(key=lambda x: x.title)
        object_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="tagslist"]/ul/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.attrib['title'], None) for x in raw_objects])

        return links, titles, number_of_videos

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN, PornCategories.CATEGORY_MAIN):
            return 1
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
        return [int(re.findall(r'(\d+)(?:/\?*)', x.attrib['href'])[-1])
                for x in tree.xpath('.//div[@class="pgntn-hlder"]/ul/li/a')
                if len(re.findall(r'(\d+)(?:/\?*)', x.attrib['href'])) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        res = []
        videos = tree.xpath('.//div[@class="thmbclck"]/div[@class="thmb"]/a')
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            # title_data = video_tree_data.xpath('./h3')
            # assert len(title_data) == 1
            # title = title_data[0].text

            image_data = video_tree_data.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            description = image_data[0].attrib['alt']
            flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                           for d in range(1, self.max_flip_images + 1)]
            title = image_data[0].attrib['alt']

            video_length = video_tree_data.xpath('./div[@class="video_time"]/span')
            assert len(video_length) == 1
            video_length = video_length[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  description=description,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  duration=self._format_duration(video_length),
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(PornPlus, self)._version_stack + [self.__version]
