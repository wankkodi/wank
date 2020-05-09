import re
from .... import urljoin, quote_plus

from ....catalogs.porn_catalog import PornFilter, PornCatalogCategoryNode, PornCategories, PornCatalogVideoPageNode
from .pornktube import PornKTube


class TubeXXPorn(PornKTube):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.tubxporn.com/'

    def __init__(self, source_name='TubeXXPorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(TubeXXPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters, single_category_filters, _, _, _, _ = self._prepare_filters()
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=single_category_filters,
                                         video_args=video_filters,
                                         )

    def _update_available_categories(self, category_data):
        """
        Fetches all the available category.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="list_categories"]//div[@class="item"]')
        res = []
        for category in categories:
            link_data = category.xpath('./div[@class="image"]/a')
            assert len(link_data) == 1

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1

            info_data = category.xpath('./h2/a')
            assert len(info_data) == 1
            title = re.findall(r'([\w ]+?)(?: *\(\d+\))', info_data[0].text)[0]
            number_of_videos = int(re.findall(r'(?:\()(\d+)(?:\))', info_data[0].text)[0])

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(category_data.url, link_data[0].attrib['href']),
                                                  image_link=image_data[0].attrib['src'],
                                                  title=title,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)

        category_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in (tree.xpath('.//div[@class="pagination"]/div[@class="block_content"]/*/text()') +
                                 tree.xpath('.//div[@class="pagination"]/div[@class="block_content"]/*/*/text()'))
                if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="block_content"]/div[@class="item"]/div[@class="inner"]')
        res = []
        for video_tree_data in videos:
            # We skip vip title
            link = video_tree_data.xpath('./div[@class="image "]/a')
            assert len(link) == 1

            image_data = video_tree_data.xpath('./div[@class="image "]/a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            number_of_flip_images = int(re.findall(r'(\d+)(?:\))', image_data[0].attrib['onmouseover'])[0])
            flip_image = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                          for i in range(1, number_of_flip_images + 1)]

            video_length = video_tree_data.xpath('./div[@class="image "]/div[@class="length"]/text()')
            assert len(video_length) == 1

            video_likes = video_tree_data.xpath('./div[@class="image "]/div[@class="likes"]/text()')
            assert len(video_likes) == 1

            video_dislikes = video_tree_data.xpath('./div[@class="image "]/div[@class="dislikes"]/text()')
            assert len(video_dislikes) == 1

            title = video_tree_data.xpath('./div[@class="info"]/a/@title')
            assert len(title) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=re.findall(r'\d+', link[0].attrib['href'])[0],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=title[0],
                                                  image_link=image,
                                                  flip_images_link=flip_image,
                                                  duration=self._format_duration(video_length[0]),
                                                  pos_rating=video_likes[0],
                                                  neg_rating=video_dislikes[0],
                                                  rating=str(int(video_likes[0]) /
                                                             (int(video_likes[0]) + int(video_dislikes[0]))),
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))
