import re
from .... import urljoin, parse_qs

from ....catalogs.base_catalog import VideoSource, VideoNode
from ....catalogs.porn_catalog import PornFilter, PornCatalogCategoryNode, PornCategories, PornCatalogVideoPageNode
from .pornktube import PornKTube


class PornKy(PornKTube):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornky.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters, single_category_filters, _, categories_filters, _, _ = self._prepare_filters()
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=categories_filters,
                                         single_category_args=single_category_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='PornKy', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornKy, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)

        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="block_content"]/div[@class="item"]')
        res = []
        for category in categories:
            link = category.xpath('./div[@class="image"]/a')
            assert len(link) == 1

            image = category.xpath('./div[@class="image"]/a/img')
            assert len(image) == 1

            title = category.xpath('./h2/a')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            number_of_videos = category.xpath('./h2/a/span[@class="info"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=title,
                                                  image_link=image[0].attrib['src'],
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        video_raw_data = self.external_fetchers.get_video_link_from_fapmedia(video_data.url)
        video_links = sorted((VideoSource(link=x[0], resolution=x[1]) for x in video_raw_data),
                             key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=video_links)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//div[@class="pages"]/*/text()') if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="video_content"]/div[@class="video"]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./div[@class="image "]/a')
            assert len(link) == 1

            image_data = video_tree_data.xpath('./div[@class="image "]/a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            number_of_flip_images = int(re.findall(r'(\d+)(?:\))', image_data[0].attrib['onmouseover'])[0])
            flip_image = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                          for i in range(1, number_of_flip_images+1)]

            video_length = video_tree_data.xpath('./div[@class="image "]/div[@class="duration"]')
            assert len(video_length) == 1

            rating = video_tree_data.xpath('./div[@class="image "]/div[@class="thumbsup"]')
            assert len(rating) == 1

            title = video_tree_data.xpath('./div[@class="info"]/h2/a')
            assert len(title) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=title[0].attrib['title'],
                                                  image_link=image,
                                                  flip_images_link=flip_image,
                                                  duration=self._format_duration(video_length[0].text),
                                                  rating=rating[0].text,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        if true_object.object_type not in (PornCategories.CATEGORY_MAIN, ):
            return super(PornKy, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                               page_filter, fetch_base_url)

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_filter.sort_order.value is not None:
            params.update(parse_qs(page_filter.sort_order.value))
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        if not page_request.ok:
            # Sometimes we try another fetch
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(PornKy, self)._version_stack + [self.__version]
