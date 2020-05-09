import re
from .... import urljoin, quote_plus

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .anyporn import AnyPorn


class HellPorno(AnyPorn):
    max_flip_images = 10

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://hellporno.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://hellporno.com/models/',
            PornCategories.CHANNEL_MAIN: 'https://hellporno.com/channels/',
            PornCategories.TOP_RATED_VIDEO: 'https://hellporno.com/',
            PornCategories.SEARCH_MAIN: 'https://hellporno.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """

        general_filter_params = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', ''),
                                                     (PornFilterTypes.LesbianType, 'Lesbian', 'lesbian'),
                                                     (PornFilterTypes.ShemaleType, 'Shemale', 'shemale'),
                                                     (PornFilterTypes.GayType, 'Gay', 'gay'),
                                                     ],
                                 }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         )

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://hellporno.com/'

    def __init__(self, source_name='HellPorno', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HellPorno, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="block-categories-videos"]/div[@class="categories-holder-videos"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span[@class="image"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            title = category.xpath('./span[@class="title"]') + category.xpath('./span[@class="title long-title"]')
            assert len(title) == 1
            title = title[0].text

            # number_of_videos_data = (category.xpath('./span[@class="cat-info"]/span') +
            #                          category.xpath('./span[@class="cat-info long-cat-info"]/span'))
            # assert len(number_of_videos_data) > 0
            # number_of_videos = re.findall(r'\d+', number_of_videos_data[0].text)[0]
            # number_of_pictures = re.findall(r'\d+', number_of_videos_data[1].text)[0] \
            #     if len(re.findall(r'\d+', number_of_videos_data[1].text)) > 0 else None

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(category_data.url, link),
                                                      title=title,
                                                      image_link=image,
                                                      # number_of_videos=number_of_videos,
                                                      # number_of_photos=number_of_pictures,
                                                      object_type=PornCategories.CATEGORY,
                                                      super_object=category_data,
                                                      )
            res.append(sub_object_data)
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@class="block-inner"]/ul/li/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="block-inner"]/ul/li/a',
                                                  PornCategories.CHANNEL)

    def _update_available_base_object(self, object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link = category.attrib['href']
            title = category.text

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(object_data.url, link),
                                                      title=title,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        if is_sort:
            res.sort(key=lambda x: x.title)
        object_data.add_sub_objects(res)
        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN, PornCategories.PORN_STAR_MAIN):
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
        return [int(x) for x in tree.xpath('.//div[@class="pagination"]/*/text()') if x.isdigit()]

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        return self._get_video_links_from_video_data3(video_data)

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        res = []
        videos = tree.xpath('.//div[@class="videos-holder"]/div[@class="video-thumb"]')
        if len(videos) > 0:
            # Method 1
            for video_tree_data in videos:
                link_data = video_tree_data.xpath('./a')
                assert len(link_data) == 1
                link = link_data[0].attrib['href']
                title = link_data[0].text

                image_data = video_tree_data.xpath('./span[@class="image"]/img')
                assert len(image_data) == 1
                image = image_data[0].attrib['src']
                flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                               for d in range(1, self.max_flip_images + 1)]

                preview_data = video_tree_data.xpath('./span[@class="image"]/video')
                assert len(preview_data) == 1
                preview_link = preview_data[0].attrib['src']

                video_length = video_tree_data.xpath('./span[@class="image"]/span[@class="time"]')
                assert len(video_length) == 1
                video_length = video_length[0].text

                rating_data = video_tree_data.xpath('./span[@class="video-rating"]/span')
                assert len(rating_data) == 1
                rating = re.findall(r'\d+%', rating_data[0].attrib['style'])

                number_of_views_data = video_tree_data.xpath('./span[@class="info"]/span')
                assert len(number_of_views_data) == 1
                number_of_views = number_of_views_data[0].text
                added_before = number_of_views_data[0].tail

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(page_data.url, link),
                                                      title=title,
                                                      image_link=image,
                                                      flip_images_link=flip_images,
                                                      preview_video_link=preview_link,
                                                      duration=self._format_duration(video_length),
                                                      rating=rating,
                                                      number_of_views=number_of_views,
                                                      added_before=added_before,
                                                      object_type=PornCategories.VIDEO,
                                                      super_object=page_data,
                                                      )
                res.append(video_data)
        else:
            # Method 2
            videos = tree.xpath('.//div[@class="videos-holder"]/a')
            for video_tree_data in videos:
                link = video_tree_data.attrib['href']

                image_data = video_tree_data.xpath('./div[@class="image"]/img')
                assert len(image_data) == 1
                image = image_data[0].attrib['src']
                flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                               for d in range(1, int(re.findall(r'(\d+)(?:\)$)',
                                                                image_data[0].attrib['onmouseover'])[0]) + 1)]

                title_data = video_tree_data.xpath('./div[@class="title"]/span')
                assert len(title_data) == 1
                title = self._clear_text(title_data[0].tail)
                video_length = self._clear_text(title_data[0].text)

                number_of_views_data = video_tree_data.xpath('./div[@class="info"]/span')
                assert len(number_of_views_data) == 1
                number_of_views = number_of_views_data[0].text
                added_before = number_of_views_data[0].tail

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(page_data.url, link),
                                                      title=title,
                                                      image_link=image,
                                                      flip_images_link=flip_images,
                                                      duration=self._format_duration(video_length),
                                                      number_of_views=number_of_views,
                                                      added_before=added_before,
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
        if page_number is None:
            page_number = 1

        if true_object.object_type not in (PornCategories.PORN_STAR_MAIN, PornCategories.PORN_STAR):
            if self.general_filter.current_filters.general.filter_id != PornFilterTypes.AllType:
                # params['t'] = self._video_filters.current_filter_values['type'].value
                params['t'] = self.general_filter.current_filters.general.value

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Referer': page_data.url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_number is not None and page_number > 1:
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
