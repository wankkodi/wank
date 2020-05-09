import re
from .... import urljoin, quote_plus

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .bravoporn import BravoPorn


class Sex3(BravoPorn):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://sex3.com/categories/',
            PornCategories.CHANNEL_MAIN: 'https://sex3.com/channels/',
            PornCategories.PORN_STAR_MAIN: 'https://sex3.com/stars/',
            PornCategories.POPULAR_VIDEO: 'https://sex3.com/most-popular/',
            PornCategories.LATEST_VIDEO: 'https://sex3.com/latest-updates/',
            PornCategories.SEARCH_MAIN: 'https://sex3.com/search/',
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
        return 'https://sex3.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        single_category_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Recent first', 'latest'),
                                                 (PornFilterTypes.VideosRatingOrder, 'Top Rated first', 'top-rated'),
                                                 (PornFilterTypes.ViewsOrder, 'Most Viewed First', 'most-viewed'),
                                                 (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                                 ],
                                  }
        model_params = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Popularity', 'model_viewed'),
                                       (PornFilterTypes.VideosPopularityOrder, 'Videos Popularity',
                                        'avg_videos_popularity'),
                                       (PornFilterTypes.VideosRatingOrder, 'Videos rating', 'avg_videos_rating'),
                                       (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                       (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                       (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                       ],
                        }
        video_params = {'period_filters': ([(PornFilterTypes.ThreeDate, 'Today', 'today'),
                                            (PornFilterTypes.TwoDate, 'This week', 'week'),
                                            (PornFilterTypes.OneDate, 'This Month', 'month'),
                                            (PornFilterTypes.AllDate, 'All time', None),
                                            ],
                                           [('sort_order', [PornFilterTypes.PopularityOrder])]
                                           ),
                        }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=single_category_params,
                                         single_tag_args=single_category_params,
                                         porn_stars_args=model_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='Sex3', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Sex3, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                   session_id)

    def _update_available_base_object(self, base_object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = category.xpath('./a/img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])

            title_data = (category.xpath('./div[@class="thumb_meta"]/a') +
                          category.xpath('./div[@style="position:absolute; color:#FFF; top:135px; left:0; '
                                         'padding: 0 3px; width:194px; height:15px; '
                                         'background: url(/images/sex3/pngbg.png); '
                                         'float:left; overflow: hidden;"]'))
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].text)

            number_of_videos = title_data[0].xpath('./span[@class="white"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(base_object_data.url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=object_type,
                                               super_object=base_object_data,
                                               ))
        if is_sort is True:
            res.sort(key=lambda x: x.title)
        base_object_data.add_sub_objects(res)
        return res

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/ul[@class="thumbs thumbs200 cat_link_list"]/li',
                                                  PornCategories.CATEGORY,
                                                  True)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/ul[@class="thumbs thumbs200"]/li',
                                                  PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="th-wrap"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            title = category.attrib['title']

            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])
            description = image_data[0].attrib['alt']

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
                                               description=description,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ))
        res.sort(key=lambda x: x.title)
        channel_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//div[@class="pagination nopop"]/div/*/text()') if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = (tree.xpath('.//div[@class="thumbs thumbs200"]/div[@class="fuck"]') +
                  tree.xpath('.//ul[@class="thumbs thumbs200"]/li'))
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])
            title = image_data[0].attrib['alt']
            if 'onmouseover' in image_data[0].attrib:
                max_flip_images = int(re.findall(r'(\d+)(?:\)$)', image_data[0].attrib['onmouseover'])[0])
                flix_image = [re.sub(r'\d.jpg$', '{d}.jpg'.format(d=d), image) for d in range(1, max_flip_images+1)]
            else:
                flix_image = None

            video_length = video_tree_data.xpath('./div[@class="time"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            added_before = video_tree_data.xpath('./div[@class="thumb_meta"]/span[@class="left"]')
            assert len(added_before) == 1
            added_before = self._clear_text(added_before[0].text)

            rating = video_tree_data.xpath('./div[@class="thumb_meta"]/span[@class="right"]/em')
            assert len(rating) == 1
            rating = rating[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  duration=self._format_duration(video_length),
                                                  added_before=added_before,
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
        if true_object.object_type in (PornCategories.CATEGORY,):
            conditions = self.get_proper_filter(page_data).conditions
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

            if (
                    page_filter.sort_order.value is not None and
                    (conditions.period.sort_order is None or
                     page_filter.sort_order.filter_id in conditions.period.sort_order)
            ):
                fetch_base_url += page_filter.sort_order.value + '/'

            if page_number is not None and page_number != 1:
                fetch_base_url = re.sub(r'/*\d*/$', '/{d}/'.format(d=page_number), fetch_base_url)

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            return super(Sex3, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                             page_filter, fetch_base_url)

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))
