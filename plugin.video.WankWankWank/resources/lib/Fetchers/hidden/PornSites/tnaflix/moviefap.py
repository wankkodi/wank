import re
from .... import urljoin, quote_plus

from ....catalogs.base_catalog import VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .tnaflix import TnaFlix


class MovieFap(TnaFlix):
    max_flip_images = 311

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.moviefap.com/categories/',
            PornCategories.BEING_WATCHED_VIDEO: 'https://www.moviefap.com/browse/bw/1',
            PornCategories.TOP_RATED_VIDEO: 'https://www.moviefap.com/browse/tr/1',
            PornCategories.LATEST_VIDEO: 'https://www.moviefap.com/browse/mr/1',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.moviefap.com/browse/mv/1',
            PornCategories.LONGEST_VIDEO: 'https://www.moviefap.com/browse/rd/1',
            PornCategories.SEARCH_MAIN: 'https://www.moviefap.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.BEING_WATCHED_VIDEO: PornFilterTypes.BeingWatchedOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.moviefap.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': ((PornFilterTypes.StraightType, 'Straight', 'type%3Dgay%2Ctranny'),
                                                     (PornFilterTypes.GayType, 'Gay', 'type%3Dstraight%2Ctranny'),
                                                     (PornFilterTypes.ShemaleType, 'Tranny', 'type%3Dstraight%2Cgay'),
                                                     ),
                                 }
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Most Recent', 'mr'),
                                        (PornFilterTypes.BeingWatchedOrder, 'Being Watched', 'bw'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'mv'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'tr'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'rd'),
                                        ),
                         }
        search_filters = {'sort_order': ((PornFilterTypes.RelevanceOrder, 'Relevancy', 'relevance'),
                                         (PornFilterTypes.DateOrder, 'Most Recent', 'adddate'),
                                         (PornFilterTypes.ViewsOrder, 'Most Viewed', 'viewnum'),
                                         (PornFilterTypes.RatingOrder, 'Top Rated', 'rate'),
                                         (PornFilterTypes.LengthOrder, 'Duration', 'duration'),
                                         ),
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='MovieFap', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(MovieFap, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="category_box"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = category.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-src'] \
                if 'data-src' in image_data[0].attrib else image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./em')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(category_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        if not page_request.ok:
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
        return [int(x.text) for x in tree.xpath('.//div[@class="pagination"]/*')
                if x.text is not None and x.text.isdigit()]

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        request_data = tmp_tree.xpath('.//form[@id="vid_info"]/input')
        request_data = {x.attrib['id']: x.attrib['value'] for x in request_data}

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            'Origin': self.base_url,
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'cors',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(request_data['config1'], headers=headers,)
        raw_text = re.sub(r'<!\[CDATA\[', '', re.sub(r']]>', '', tmp_request.text))
        tmp_tree = self.parser.parse(raw_text)
        # todo: could be videoLink instead of videoLinkDownload
        res = sorted((VideoSource(link=x.xpath('./*')[1].text,
                                  resolution=int(re.findall(r'\d+', x.xpath('./res')[0].text)[0]))
                      for x in tmp_tree.xpath('.//quality/item')),
                     key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=res)

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="videothumb"]')
        res = []
        for video_tree_data in videos:
            video_link = video_tree_data.xpath('./a')
            assert len(video_link) == 1
            link = video_link[0].attrib['href']

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']
            flip_images = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=x), image)
                           for x in range(1, self.max_flip_images, 10)]

            video_data = video_tree_data.xpath('./div[@class="videoleft"]')
            assert len(video_data) == 1
            video_length = video_data[0].text

            added_before_data = video_tree_data.xpath('./div[@class="videoleft"]/br')
            assert len(added_before_data) == 1
            added_before = added_before_data[0].text

            rating_data = video_tree_data.xpath('./div[@class="videoright"]/div[@class="rating"]/div/ul')
            assert len(rating_data) == 1
            rating = re.findall(r'(\d+)(?:px)', rating_data[0].attrib['style'])[0] + '%'

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  duration=self._format_duration(video_length),
                                                  added_before=added_before,
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        split_url = fetch_base_url.split('/')
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
        if page_number is None:
            page_number = 1
        self.session.cookies.set(name='content_filter',
                                 value=self.general_filter.current_filters.general.value,
                                 )
        if true_object.object_type == PornCategories.CATEGORY:
            # Delete previous filters
            if split_url[-2] in ('mr', 'tr', 'mv', 'bw', 'rd'):
                split_url = split_url[:-2]
            if split_url[-1] in ('mr', 'tr', 'mv', 'bw', 'rd'):
                split_url = split_url[:-1]
            if len(split_url[-1]) == 0:
                split_url.pop()
            split_url.append(page_filter.sort_order.value)
            split_url.append(str(page_number))
        elif true_object.object_type in self._default_sort_by:
            split_url[-1] = str(page_number)
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            # Delete previous filters
            if len(split_url) > 5:
                split_url = split_url[:5]
            split_url.append(page_filter.sort_order.value)
            split_url.append(str(page_number))
        program_fetch_url = '/'.join(split_url)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}'.format(q=quote_plus(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(MovieFap, self)._version_stack + [self.__version]
