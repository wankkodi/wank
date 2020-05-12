import re
from .... import urljoin, quote_plus

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .anyporn import AnyPorn


class BravoTeens(AnyPorn):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.bravoteens.com/cats/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.bravoteens.com/top/',
            PornCategories.LATEST_VIDEO: 'https://www.bravoteens.com/new/',
            PornCategories.POPULAR_VIDEO: 'https://www.bravoteens.com/popular/',
            PornCategories.SEARCH_MAIN: 'https://www.bravoteens.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.bravoteens.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_params = {'period_filters': [(PornFilterTypes.AllDate, 'All time', ''),
                                           (PornFilterTypes.OneDate, 'This Month', 'month'),
                                           (PornFilterTypes.TwoDate, 'This week', 'week'),
                                           (PornFilterTypes.ThreeDate, 'Today', 'today'),
                                           ],
                        }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='BravoTeens', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(BravoTeens, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="preview-item"]/div')

        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = category.xpath('./a/img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])

            title_data = category.xpath('./div[@class="thumb_meta"]/span[@class="video-title"]')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos = category.xpath('./div[@class="thumb_meta"]/span[@class="white"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))
        res.sort(key=lambda x: x.title)
        category_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//div[@class="pagination2 nopop"]/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="block-video-preview"]/div[@class="preview-item"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./div[@class="image-holder "]/a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']

            image_data = video_tree_data.xpath('./div[@class="image-holder "]/a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']
            if 'onmouseover' in image_data[0].attrib:
                max_flip_images = int(re.findall(r'(\d+)(?:\)$)', image_data[0].attrib['onmouseover'])[0])
                flix_image = [re.sub(r'\d.jpg$', '{d}.jpg'.format(d=d), image) for d in range(1, max_flip_images+1)]
            else:
                flix_image = None

            video_length = video_tree_data.xpath('./div[@class="image-holder "]/a/div[@class="video-info"]/'
                                                 'span[@class="time"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            added_before = video_tree_data.xpath('./div[@class="image-holder "]/a/div[@class="video-info"]/'
                                                 'span[@class="date"]')
            assert len(added_before) == 1
            added_before = added_before[0].text

            rating = video_tree_data.xpath('./div[@class="video-meta"]/span[@class="video-rating"]')
            assert len(rating) == 1
            rating = rating[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  added_before=added_before,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
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
        if page_data.object_type == PornCategories.VIDEO_PAGE and page_data.url != page_data.super_object.url:
            # We want to have original page url, without page index
            fetch_base_url = page_data.super_object.url.split('?')[0]
        if true_object.object_type in (PornCategories.POPULAR_VIDEO, PornCategories.TOP_RATED_VIDEO,):
            if page_filter.period.filter_id != PornFilterTypes.AllDate:
                fetch_base_url += page_filter.period.value + '/'

        if page_number is not None and page_number != 1:
            fetch_base_url += '{d}/'.format(d=page_number)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

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
        return super(BravoTeens, self)._version_stack + [self.__version]
