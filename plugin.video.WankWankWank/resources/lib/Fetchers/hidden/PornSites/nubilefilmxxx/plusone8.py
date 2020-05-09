from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornCatalogCategoryNode, PornCatalogVideoPageNode
from .nubilefilmxxx import NubileFilmXXX


class PlusOne8(NubileFilmXXX):
    max_flip_image = 16

    @property
    def object_urls(self):
        res = super(PlusOne8, self).object_urls
        res.pop(PornCategories.CHANNEL_MAIN)
        res[PornCategories.CATEGORY_MAIN] = urljoin(self.base_url, '/porn-categories/')
        res[PornCategories.TAG_MAIN] = urljoin(self.base_url, '/porn-tags/')
        res[PornCategories.PORN_STAR_MAIN] = urljoin(self.base_url, '/pornstars/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://plusone8.com/'

    def __init__(self, source_name='PlusOne8', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PlusOne8, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page = 1
        max_page = None
        res = []
        while 1:
            page_request = self._get_object_request_no_exception_check(category_data, override_page_number=page)
            if not self._check_is_available_page(category_data, page_request):
                break
            tree = self.parser.parse(page_request.text)
            if max_page is None:
                available_pages = self._get_available_pages_from_tree(tree)
                max_page = max(available_pages) if len(available_pages) > 0 else 1

            categories = tree.xpath('.//div[@class="videos-list"]/article/a')
            for category in categories:
                image = category.xpath('./div/img')
                assert len(image) == 1

                object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=category.attrib['href'],
                                                      url=urljoin(self.base_url, category.attrib['href']),
                                                      title=category.attrib['title'],
                                                      image_link=image[0].attrib['src'],
                                                      object_type=PornCategories.CATEGORY,
                                                      super_object=category_data,
                                                      )
                res.append(object_data)
            if page == max_page:
                # We reached the last page
                break
            page += 1
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="videos-list"]/article/a')
        res = []
        for category in categories:
            image = category.xpath('./div/img')
            assert len(image) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=category.attrib['title'],
                                                  image_link=image[0].attrib['src'],
                                                  raw_data=image[0].attrib,
                                                  object_type=PornCategories.PORN_STAR,
                                                  super_object=porn_star_data,
                                                  )
            res.append(object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//main/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, None) for x in raw_objects])
        assert len(titles) == len(links)
        assert len(titles) == len(number_of_videos)

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
        return set(([int(x.split('/')[-2]) for x in (tree.xpath('.//div[@class="pagination"]/ul/li/a/@href'))
                     if x.split('/')[-2].isdigit()] +
                    [int(x) for x in (tree.xpath('.//div[@class="pagination"]/ul/li/a/text()'))
                     if x.isdigit()]))

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div/article/a')
        res = []
        for video_tree_data in videos:
            title = video_tree_data.attrib['title']
            flip_image = video_tree_data.xpath('./div[@class="post-thumbnail thumbs-rotation"]')
            assert len(flip_image) == 1
            flip_image = flip_image[0].attrib['data-thumbs'].split(',')

            image_data = video_tree_data.xpath('./div[@class="post-thumbnail thumbs-rotation"]/img')
            if len(image_data) == 0:
                # Empty link, skip it...
                continue
            image = image_data[0].attrib['data-src'] if 'data-src' in image_data[0].attrib \
                else image_data[0].attrib['src']
            image = urljoin(self.base_url, image)

            video_length = video_tree_data.xpath('./div[@class="post-thumbnail thumbs-rotation"]/'
                                                 'span[@class="duration"]/i')
            video_length = \
                self._format_duration(self._clear_text(video_length[0].tail)) if len(video_length) == 1 else None

            rating = video_tree_data.xpath('./div[@class="rating-bar"]/span')
            rating = self._clear_text(rating[0].text) if len(rating) > 0 else None

            video_data = PornCatalogVideoPageNode(
                catalog_manager=self.catalog_manager,
                obj_id=video_tree_data.attrib['href'],
                url=urljoin(self.base_url, video_tree_data.attrib['href']),
                title=title,
                image_link=image,
                flip_images_link=flip_image,
                duration=video_length,
                rating=rating,
                object_type=PornCategories.VIDEO,
                super_object=page_data,
            )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res
