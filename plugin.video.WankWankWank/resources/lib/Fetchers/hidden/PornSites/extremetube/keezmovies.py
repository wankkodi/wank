import re
from .... import urljoin

from ....catalogs.base_catalog import VideoNode, VideoSource
from ....catalogs.porn_catalog import PornCategories, PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    PornFilter, PornFilterTypes

from .extremetube import ExtremeTube


class KeezMoovies(ExtremeTube):
    video_request_format = 'https://www.spankwire.com/api/video/{vid}.json'

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 50000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/pornstar'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/videos'),
            PornCategories.BEING_WATCHED_VIDEO: urljoin(self.base_url, '/videos?o=bw'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/videos?o=mv'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/videos?o=tr'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/videos?o=lg'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/video'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.BEING_WATCHED_VIDEO: PornFilterTypes.BeingWatchedOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.keezmovies.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Most recent', 'mr'),
                                        (PornFilterTypes.ViewsOrder, 'Most viewed', 'mv'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'tr'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'lg'),
                                        ],
                         'period_filters': ([(PornFilterTypes.AllDate, 'All time', None),
                                             (PornFilterTypes.OneDate, 'This Week', 'week'),
                                             (PornFilterTypes.TwoDate, 'This Month', 'month'),
                                             ],
                                            [('sort_order', [PornFilterTypes.RatingOrder,
                                                             PornFilterTypes.ViewsOrder])]
                                            ),

                         }
        porn_stars_filter = {'sort_order': [(PornFilterTypes.RatingOrder, 'Top ranked', None),
                                            (PornFilterTypes.AlphabeticOrder, 'Alphabetic', 'name'),
                                            ],
                             }

        search_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Most relevant', None),
                                         (PornFilterTypes.DateOrder, 'Most recent', 'mr'),
                                         (PornFilterTypes.ViewsOrder, 'Most viewed', 'mv'),
                                         (PornFilterTypes.RatingOrder, 'Top rated', 'tr'),
                                         (PornFilterTypes.LengthOrder, 'Longest', 'lg'),
                                         ],
                          }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filter,
                                         single_category_args=video_filters,
                                         single_tag_args=video_filters,
                                         search_args=search_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='KeezMoovies', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(KeezMoovies, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                          session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)

        headers = tree.xpath('.//div[@class="block_heading"]//h2[@class="h2cat"]')
        bodies = tree.xpath('.//div[@class="float-left"]/a[@class="category_img"]')
        assert len(headers) == len(bodies)
        res = []
        for header, body in zip(headers, bodies):
            title = self._clear_text(header.text)

            number_of_videos = header.xpath('./span[@class="inhsp"]/text()')
            assert len(number_of_videos) == 1
            number_of_videos = re.findall(r'(?:\()(\d*,*\d*)(?: Videos\))', number_of_videos[0])
            assert len(number_of_videos) == 1
            number_of_videos = int(re.sub(',', '', number_of_videos[0]))

            link = urljoin(self.base_url, body.attrib['href'])
            cat_id = body.attrib['href']
            image = body.xpath('./img/@src')
            assert len(image) == 1
            image = image[0]

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=cat_id,
                                                  url=link,
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = [x for x in tree.xpath('.//ul[@class="all-ps-list main_pornst_block"]/li')
                      if 'class' in x.attrib and 'allpornstars' in x.attrib['class']]
        res = []
        for porn_star in porn_stars:
            link_data = porn_star.xpath('./a')
            assert len(link_data)

            image_data = porn_star.xpath('./a/div/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'blank_pornstarimage.jpg' in image and 'data-srcsmall' in image_data[0].attrib:
                # We fetch another image
                image = image_data[0].attrib['data-srcsmall']
            image = urljoin(porn_star_data.url, image)

            additional_info = porn_star.xpath('./div[@class="pornstar_item_bottom"]/div/span')
            assert len(additional_info) == 6
            number_of_videos = int(additional_info[3].text)
            number_of_photos = int(additional_info[1].text)
            number_of_views = int(re.sub(',', '', additional_info[5].text))

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(porn_star_data.url, link_data[0].attrib['href']),
                                                  title=link_data[0].attrib['title'],
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  number_of_photos=number_of_photos,
                                                  number_of_views=number_of_views,
                                                  object_type=PornCategories.PORN_STAR,
                                                  super_object=porn_star_data,
                                                  )
            res.append(object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def _add_tag_sub_pages(self, tag_data, sub_object_type):
        return super(ExtremeTube, self)._add_tag_sub_pages(tag_data, sub_object_type)

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles. The fetched objects MUST be sorted wrt title.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        links = tree.xpath('.//div[@style="padding:10px;"]/ul[@class="auto"]/a/@href')
        titles = [x.title() for x in tree.xpath('.//div[@style="padding:10px;"]/ul[@class="auto"]/a/li/text()')]
        assert len(links) == len(titles)
        numbers_of_videos = [None] * len(titles)
        return links, titles, numbers_of_videos

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        page_request = self.get_object_request(video_data)
        raw_url = re.findall(r'(?:var htmlStr.*ArticleId=")(\d+?)(?:[&"])', page_request.text)
        if len(raw_url) == 0:
            raise RuntimeError('Could not fetch video from page {p}!'.format(p=video_data.url))
        data_url = self.video_request_format.format(vid=raw_url[0])
        headers = {
            'Accept': 'application/json, text/plain, */*, image/webp',
            'Cache-Control': 'max-age=0',
            'Host': 'www.spankwire.com',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(data_url, headers=headers)
        video_data = tmp_request.json()
        if video_data is False:
            raise RuntimeError('Could not fetch video from page {p}!'.format(p=video_data.url))

        video_sources = sorted((VideoSource(link=v, quality=int(re.findall(r'(?:quality_)(\d*)(?:p)', k)[0]))
                                for k, v in video_data['videos'].items()),
                               key=lambda y: y.quality, reverse=True)
        return VideoNode(video_sources=video_sources)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        start_page = category_data.page_number if category_data.page_number is not None else 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        max_page = max(pages)
        if (max_page - start_page) < self._binary_search_page_threshold:
            return max_page
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        pages = (tree.xpath('.//ul[@class="pagination"]/li/*/text()') +
                 tree.xpath('.//ul[@class="pagination"]/li/text()'))
        return [int(x) for x in pages if x.isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 5

    def get_videos_data(self, object_data):
        """
        Gets videos data for the given category.
        :param object_data: Page data.
        :return:
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        videos = [x for x in tree.xpath('.//ul/li') if 'id' in x.attrib and 'video' in x.attrib['id']]
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./div[@class="hoverab"]/a')
            assert len(link_data) >= 1
            link = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) >= 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])
            flip_images = [image_data[0].attrib['data-flipbook'].format(index=i)
                           for i in image_data[0].attrib['data-flipbook-values'].split(',')]

            vd_data = video_tree_data.xpath('./div[@class="hoverab"]/div[@class="vd_dr"]/span')
            is_hd = [x for x in vd_data if 'class' in x.attrib]
            is_hd = len(is_hd) > 0 and is_hd[0].attrib['class'] == 'vdIsHD'

            video_length = [x for x in vd_data if 'class' not in x.attrib]
            assert len(video_length) == 1
            video_length = video_length[0].text

            title = video_tree_data.xpath('./div[@class="video_name"]/a')
            assert len(title) == 1
            title = title[0].text if title[0].text is not None else ''

            rating = video_tree_data.xpath('./div[@class="video_extra"]/span[@class="liked_span"]')
            assert len(rating) == 1
            rating = rating[0].text

            viewers = video_tree_data.xpath('./div[@class="video_extra"]/span[@class="views"]')
            assert len(viewers) == 1
            viewers = viewers[0].text

            additional_data = {'id': video_tree_data.attrib['id']}

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  is_hd=is_hd,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  number_of_views=viewers,
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=object_data,
                                                  )
            res.append(video_data)
        object_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url,
                                page_type='regular'):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :param params: Page params.
        :param page_number: Page number.
        :param true_object: True object.
        :param page_filter: Page filter.
        :param fetch_base_url: Page base url.
        :param page_type: Page type.
        :return: Page request
        """
        if page_type == 'json':
            url, additional_params = self._prepare_request_params(page_data)
            headers = {
                'Accept': '*/*',
                'Cache-Control': 'max-age=0',
                # 'Host': self.host_name,
                'Referer': page_data.url,
                # 'Sec-Fetch-Mode': 'navigate',
                # 'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
        else:
            url = page_data.url
            additional_params = {}
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3',
                'Cache-Control': 'max-age=0',
                # 'Host': self.host_name,
                'Referer': page_data.url,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }
        params.update(additional_params)

        if true_object.object_type == PornCategories.VIDEO:
            page_request = self.session.get(url, headers=headers, params=params)
            return page_request

        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        if true_object.object_type in (PornCategories.PORN_STAR_MAIN,):
            if page_filter.sort_order.value is not None:
                params['sort'] = page_filter.sort_order.value
        else:
            if page_filter.sort_order.value is not None:
                params['o'] = page_filter.sort_order.value
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['t'] += page_filter.period.value

        if page_number is not None and page_number != 1:
            params['page'] = [page_number]

        page_request = self.session.get(url, headers=headers, params=params)
        return page_request

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(KeezMoovies, self)._version_stack + [self.__version]
