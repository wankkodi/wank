import re
from .... import urljoin, quote_plus

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornCatalogCategoryNode, PornCatalogVideoPageNode
from .anyporn import AnyPorn
from .xbabe import XBabe


class XCum(XBabe):
    max_flip_images = 6

    @property
    def object_urls(self):
        return {
            PornCategories.TAG_MAIN: 'https://xcum.com/',
            PornCategories.LATEST_VIDEO: 'https://xcum.com/',
            PornCategories.SEARCH_MAIN: 'https://xcum.com/q/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://xcum.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        return super(AnyPorn, self)._set_video_filter()

    def __init__(self, source_name='XCum', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(XCum, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                   session_id)

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="block_content"]/ul/li/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            title = category.xpath('./span')
            assert len(title) == 1
            title = title[0].text

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               object_type=PornCategories.TAG,
                                               super_object=tag_data,
                                               ))
        tag_data.add_sub_objects(res)
        return res

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return False

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN,):
            return 1

        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        return max(pages) if len(pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//nav[@class="pagination pignr"]/div/*') +
                tree.xpath('.//div[@class="pagination"]/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        method = 1
        videos = tree.xpath('.//div[@class="thumbs"]/div/div[@class="thumb"]/a')
        if len(videos) == 0:
            method = 2
            videos = tree.xpath('.//div[@class="thumbs"]/div[@class="thumb"]')
        res = []
        if method == 1:
            for video_tree_data in videos:
                link = video_tree_data.attrib['href']

                image_data = video_tree_data.xpath('./picture/img')
                assert len(image_data) == 1
                image = image_data[0].attrib['data-original']
                description = image_data[0].attrib['alt']
                flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                               for d in range(1, self.max_flip_images + 1)]

                preview_data = video_tree_data.xpath('./video')
                assert len(preview_data) == 1
                preview_video = preview_data[0].attrib['src']

                info_data = video_tree_data.xpath('./span[@class="inf"]/span')
                assert len(info_data) == 4
                title = info_data[0].text
                video_length = info_data[2].text
                number_of_likes = info_data[3].text

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      description=description,
                                                      image_link=image,
                                                      flip_images_link=flip_images,
                                                      preview_video_link=preview_video,
                                                      duration=self._format_duration(video_length),
                                                      number_of_likes=number_of_likes,
                                                      object_type=PornCategories.VIDEO,
                                                      super_object=page_data,
                                                      )
                res.append(video_data)
        elif method == 2:
            for video_tree_data in videos:
                link_data = video_tree_data.xpath('./a')
                assert len(link_data) == 1
                link = link_data[0].attrib['href']

                image_data = video_tree_data.xpath('./a/img')
                assert len(image_data) == 1
                image = image_data[0].attrib['data-original']
                description = image_data[0].attrib['alt']
                flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                               for d in range(1, int(re.findall(r'(\d+)(?:\)$)',
                                                                image_data[0].attrib['onmouseover'])[0]) + 1)] \
                    if 'onmouseover' in image_data[0].attrib else None

                preview_data = video_tree_data.xpath('./a/video')
                assert len(preview_data) == 1
                preview_video = preview_data[0].attrib['src']

                title_data = video_tree_data.xpath('./div[@class="btn-info btn-trailer"]/div/b')
                assert len(title_data) == 1
                title = title_data[0].text

                info_data = video_tree_data.xpath('./div[@class="btn-info btn-trailer"]/div/span[@class="thumb-info"]/'
                                                  'span')
                assert len(info_data) == 2
                video_length = info_data[0].text
                number_of_likes = info_data[1].text

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      description=description,
                                                      image_link=image,
                                                      flip_images_link=flip_images,
                                                      preview_video_link=preview_video,
                                                      duration=self._format_duration(video_length),
                                                      number_of_likes=number_of_likes,
                                                      object_type=PornCategories.VIDEO,
                                                      super_object=page_data,
                                                      )
                res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
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
        if page_number is not None and page_number != 1:
            fetch_base_url = re.sub(r'/$', '', fetch_base_url)
            fetch_base_url += '/{d}/'.format(d=page_number)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query))
