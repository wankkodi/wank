import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .anyporn import AnyPorn


class PornoDep(AnyPorn):
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://pornodep.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://pornodep.com/models/',
            PornCategories.TAG_MAIN: 'https://pornodep.com/tags/',
            PornCategories.CHANNEL_MAIN: 'https://pornodep.com/sites/',
            PornCategories.LATEST_VIDEO: 'https://pornodep.com/',
            PornCategories.SEARCH_MAIN: 'https://pornodep.com/search/',
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
        return 'https://pornodep.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_sort_order = [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                            ]
        search_sort_order = video_sort_order
        porn_stars_params = \
            {'sort_order': [(PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            ],
             }
        video_params = {'sort_order': video_sort_order,
                        }
        search_params = {'sort_order': search_sort_order,
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         # categories_args=category_params,
                                         channels_args=porn_stars_params,
                                         porn_stars_args=porn_stars_params,
                                         single_category_args=video_params,
                                         single_tag_args=video_params,
                                         single_channel_args=video_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='PornoDep', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornoDep, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="category-list"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="card-box"]/div[@class="img-box"]/img')
            if len(image_data) != 1:
                continue
            image = image_data[0].attrib['src']

            title_data = category.xpath('./div[@class="card-box"]/div[@class="title"]')
            assert len(image_data) == 1
            title = title_data[0].text

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channels.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="video-block channel"]/div[@class="heading"]')
        res = []
        for category in categories:
            title_data = category.xpath('./div[@class="title"]')
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].xpath('./span')[0].text)
            image = title_data[0].xpath('./i/img')
            image = image[0].attrib['src'] if len(image) > 0 else None
            link = category.xpath('./a')[0].attrib['href']

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ))

        channel_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="card-list models_list"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            ranking_data = category.xpath('./div[@class="card-top"]/span[@class="info"]/div')
            assert len(ranking_data) == 1
            ranking = self._clear_text(ranking_data[0].text)

            image_data = category.xpath('./div[@class="card-top"]/span[@class="wrap-img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None

            number_of_videos = category.xpath('./div[@class="card-top"]/div[@class="count"]/'
                                              'div[@class="count-box"]/span')
            assert len(number_of_videos) == 1
            number_of_videos = self._clear_text(number_of_videos[0].text)

            title_data = category.xpath('./div[@class="card-bottom"]/div/span[@class="title"]')
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               rating=ranking,
                                               number_of_videos=number_of_videos,
                                               image_link=image,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    def _add_tag_sub_pages(self, tag_data, sub_object_type):
        """
        Adds sub pages to the tags according to the first letter of the title. Stores all the tags to the proper pages.
        Notice that the current method contradicts with the _get_tag_properties method, thus you must use either of
        them, according to the way you want to implement the parsing (Use the _make_tag_pages_by_letter property to
        indicate which of the methods you are about to use...)
        :param tag_data: Tag data.
        :param sub_object_type: Object types of the sub pages (either Page or VideoPage).
        :return:
        """
        return super(AnyPorn, self)._add_tag_sub_pages(tag_data, sub_object_type)

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//div[@class="tags-wrap"]/div/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'],
                                                 self._clear_text(x.xpath('./div[@class="name"]')[0].text),
                                                 self._clear_text(x.xpath('./div[@class="count"]')[0].text))
                                                for x in raw_data])
        return links, titles, number_of_videos

    def _add_category_sub_pages(self, category_data, sub_object_type, page_request=None, clear_sub_elements=True):
        """
        Adds category sub pages.
        :param category_data: Category data object (PornCatalogCategoryNode).
        :param sub_object_type: Sub object type.
        :param page_request: Page request if such exist. In case it doesn't exist we fetch the object's url.
        :param clear_sub_elements: Flag that indicates whether we clear previous sub elements.
        :return:
        """
        if category_data.object_type == PornCategories.CATEGORY:
            # We add additional categories as well
            if clear_sub_elements is True:
                category_data.clear_sub_objects()
            if category_data.super_object.object_type != PornCategories.CATEGORY:
                self._update_available_categories(category_data)
            return super(PornoDep, self)._add_category_sub_pages(category_data, sub_object_type, page_request, False)
        else:
            return super(PornoDep, self)._add_category_sub_pages(category_data, sub_object_type, page_request,
                                                                 clear_sub_elements)

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        return self._get_video_links_from_video_data2(video_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(re.findall(r'(?:from.*?:)(\d+)', x.attrib['data-parameters'])[0])
                for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a')
                if len(re.findall(r'(?:from.*?:)(\d+)', x.attrib['data-parameters'])) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="card-list"]/div[@class="card item"]/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./div[@class="card-top"]/span[@class="wrap-img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] if 'data:image' not in image_data[0].attrib['src'] \
                else image_data[0].attrib['data-original']
            preview = image_data[0].attrib['data-preview'] if 'data-preview' in image_data[0].attrib else None
            flip_image = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                          for i in range(1, int(image_data[0].attrib['data-cnt']) + 1)]

            title = image_data[0].attrib['alt'] if 'alt' in image_data[0].attrib else video_tree_data.attrib['title']

            uploader = video_tree_data.xpath('./div[@class="card-top"]/span[@class="autor"]/div')
            additional_data = {'name': self._clear_text(uploader[0].text)} if len(uploader) == 1 else None

            video_length = video_tree_data.xpath('./div[@class="card-top"]/div[@class="time"]')
            assert len(video_length) == 1
            video_length = self._format_duration(self._clear_text(video_length[0].text))

            rating = video_tree_data.xpath('./div[@class="card-bottom"]/div/div[@class="rait"]/span')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].text)

            number_of_views = video_tree_data.xpath('./div[@class="card-bottom"]/div/div[@class="views"]')
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  preview_video_link=preview,
                                                  flip_images_link=flip_image,
                                                  additional_data=additional_data,
                                                  duration=video_length,
                                                  rating=rating,
                                                  number_of_views=number_of_views,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
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
        if (
                true_object.object_type in (PornCategories.CATEGORY_MAIN, ) or
                page_data.object_type in (PornCategories.CATEGORY, )
        ):
            params = {}
        elif true_object.object_type == PornCategories.LATEST_VIDEO:
            params['block_id'] = 'list_videos_most_recent_videos'
            params['sort_by'] = 'post_date'
            params['from'] = str(page_number).zfill(2)
        elif true_object.object_type == PornCategories.TAG:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = page_filter.sort_order.value
            params['from'] = str(page_number).zfill(2)
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            params['block_id'] = 'list_videos_videos_list_search_result'
            params['q'] = self._search_query
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            if page_filter.sort_order.filter_id in (PornFilterTypes.RatingOrder, PornFilterTypes.ViewsOrder):
                params['sort_by'] += page_filter.period.value
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
        else:
            return super(PornoDep, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                 page_filter, fetch_base_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw number, i.e. '7m:58s'.
        :return:
        """
        return super(AnyPorn, self)._format_duration(raw_duration)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(PornoDep, self)._version_stack + [self.__version]
