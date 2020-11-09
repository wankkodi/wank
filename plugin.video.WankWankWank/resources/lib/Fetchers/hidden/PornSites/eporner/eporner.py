# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher, PornNoVideoError

# Internet tools
from .... import urljoin, quote_plus

# Regex
import re

# JSON
from ....tools.text_json_manioulations import prepare_json_from_not_formatted_text

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource, \
    VideoTypes
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter


class EPorner(PornFetcher):
    sd_resolutions = ('480p', '360p', '240p')
    max_flip_image = 15

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 100000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.eporner.com/cats/',
            PornCategories.TAG_MAIN: 'https://www.eporner.com/cats/',
            PornCategories.PORN_STAR_MAIN: 'https://www.eporner.com/pornstar-list/',
            PornCategories.POPULAR_VIDEO: 'https://www.eporner.com/best-videos/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.eporner.com/cat/all/SORT-top-rated/',
            PornCategories.LATEST_VIDEO: 'https://www.eporner.com/cat/all/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.eporner.com/cat/all/SORT-most-viewed/',
            PornCategories.LONGEST_VIDEO: 'https://www.eporner.com/cat/all/SORT-longest/',
            PornCategories.SHORTEST_VIDEO: 'https://www.eporner.com/shortest/',
            PornCategories.SEARCH_MAIN: 'https://www.eporner.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.SHORTEST_VIDEO: PornFilterTypes.LengthOrder2,
        }

    @property
    def possible_empty_pages(self):
        """
        Defines whether it is possible to have empty pages in the site.
        :return:
        """
        return True

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.eporner.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        category_filter = {'sort_order': [(PornFilterTypes.DateOrder, 'Most recent', ''),
                                          (PornFilterTypes.PopularityOrder, 'Weekly top', 'SORT-top-weekly'),
                                          (PornFilterTypes.PopularityOrder2, 'Monthly top', 'SORT-top-monthly'),
                                          (PornFilterTypes.ViewsOrder, 'Most viewed', 'SORT-most-viewed'),
                                          (PornFilterTypes.RatingOrder, 'Top rated', 'SORT-top-rated'),
                                          (PornFilterTypes.LengthOrder, 'Longest', 'SORT-longest'),
                                          ],
                           }
        porn_star_filter = {'sort_order': [(PornFilterTypes.PopularityOrder2, 'Monthly top', ''),
                                           (PornFilterTypes.DateOrder, 'Most recent', 'recent'),
                                           (PornFilterTypes.PopularityOrder, 'Weekly top', 'top-weekly'),
                                           (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                           (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                           (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                           (PornFilterTypes.LengthOrder2, 'Shortest', 'shortest'),
                                           ],
                            }
        search_filter = {'sort_order': [(PornFilterTypes.DateOrder, 'Most recent', ''),
                                        (PornFilterTypes.PopularityOrder, 'Weekly top', 'top-weekly'),
                                        (PornFilterTypes.PopularityOrder2, 'Monthly top', 'monthly-weekly'),
                                        (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        (PornFilterTypes.LengthOrder2, 'Shortest', 'shortest'),
                                        ],
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=category_filter,
                                         single_porn_star_args=porn_star_filter,
                                         search_args=search_filter,
                                         )

    def __init__(self, source_name='Eporner', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(EPorner, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="categoriesbox"]/div')
        res = []
        #
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            img = category.xpath('./a/div/div/img/@src')
            assert len(img) == 1

            title = category.xpath('./a/h2/text()')
            assert len(title) == 1

            # Total number of videos per category
            num_of_videos = [x for x in tree.xpath('.//div[@id="categories-list-left"]/ul/li/div[2]')
                             if 'href' in x.xpath('./a')[0].attrib and
                             x.xpath('./a')[0].attrib['href'] == link_data[0].attrib['href']]
            # assert len(num_of_videos) == 1
            if len(num_of_videos) == 1:
                num_of_videos = num_of_videos[0].xpath('./div[@class="cllnumber"]/text()')
                num_of_videos = int(re.sub(r'[(),]', '', str(num_of_videos[0])))
            else:
                num_of_videos = None

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(self.base_url, link_data[0].attrib['href']),
                                                  image_link=img[0],
                                                  title=title[0],
                                                  number_of_videos=num_of_videos,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available pornstar.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = tree.xpath('.//div[@class="mbprofile"]')
        res = []
        for porn_star in porn_stars:
            link = porn_star.xpath('./a')
            assert len(link) == 1
            title = link[0].attrib['title']

            img = porn_star.xpath('./a/div/div/img/@src')
            assert len(img) == 1

            # Total number of videos per category
            num_of_videos = porn_star.xpath('./div[@class="mbtim"]/span')
            assert len(num_of_videos) == 1

            # Total number of videos per category
            num_of_photos = porn_star.xpath('./div[@class="mbvie"]/span')
            assert len(num_of_photos) == 1
            number_of_photos = int(num_of_photos[0].tail)

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(porn_star_data.url, link[0].attrib['href']),
                                                  image_link=urljoin(porn_star_data.url, img[0]),
                                                  title=title,
                                                  number_of_videos=int(num_of_videos[0].tail),
                                                  number_of_photos=number_of_photos,
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
        link_objects = tree.xpath('.//ul[@class="allcatslist"]/li/a')
        number_of_videos_objects = tree.xpath('.//ul[@class="allcatslist"]/li/span')
        assert len(link_objects) == len(number_of_videos_objects)
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text,
                                                 int(re.sub(r'[,+]', '', y.text)))
                                                for x, y in zip(link_objects, number_of_videos_objects)])
        return links, titles, number_of_videos

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """

        def base_n(num, b, numerals="0123456789abcdefghijklmnopqrstuvwxyz"):
            return ((num == 0) and numerals[0]) or (
                    base_n(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])

        def _get_hash(a):
            return base_n(int(a[0:8], 16), 36) + base_n(int(a[8:16], 16), 36) + base_n(int(a[16:24], 16), 36) + \
                   base_n(int(a[24:32], 16), 36)

        headers = {
            'Accept': '*/*',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_data.url, headers=headers)
        if not self._check_is_available_page(video_data, tmp_request):
            error_module = self._prepare_porn_error_module_for_video_page(video_data, tmp_request.url)
            raise PornNoVideoError(error_module.message, error_module)

        tmp_tree = self.parser.parse(tmp_request.text)

        request_data = re.findall(r'(?:\'EPvideo\', )( *{.*} *)(?:, function)',
                                  [x for x in tmp_tree.xpath('.//script/text()') if 'EPinitPlayerVR' in x][0],
                                  re.DOTALL)
        request_data = prepare_json_from_not_formatted_text(request_data[0])
        request_hash = request_data['plugins']['EP']['hash']
        request_hash = _get_hash(request_hash)

        query = {
            'hash': request_hash,
            'device': 'generic',
            'domain': self.host_name,
            'fallback': False,
            'embed': False,
            'supportedFormats': 'dash,mp4',
            'tech': 'htmml5',
        }
        video_web_id = video_data.url.split('/')[-3]
        fetch_url = 'https://www.eporner.com/xhr/video/{vid}'.format(vid=video_web_id)

        page_request = self.session.get(fetch_url, headers=headers, params=query)
        video_data = page_request.json()
        if not self._check_is_available_page(video_data, page_request) or video_data['available'] is False:
            error_module = self._prepare_porn_error_module_for_video_page(
                video_data, tmp_request.url,
                'Cannot fetch video {t} from url {u}.'.format(t=video_data['title'], u=video_data.url)
                                                                          )
            raise PornNoVideoError(error_module.message, error_module)

        # mp4 support
        res = []
        if 'mp4' in video_data['sources']:
            res.extend([VideoSource(link=v['src'], resolution=re.findall(r'(\d*)(?:p)', k)[0])
                        for k, v in video_data['sources']['mp4'].items()
                        ])
        # dash support
        if 'dash' in video_data['sources']:
            res.append(VideoSource(link=video_data['sources']['dash']['auto']['src'],
                                   video_type=VideoTypes.VIDEO_DASH,
                                   resolution=max((int(x)
                                                   for x in re.findall(r'(?:,)([\d,]+)(?:,p)',
                                                                       video_data['sources']['dash']['auto']['src'])
                                                  [0].split(',')))
                                   ))
        res.sort(key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=res)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Get number of pages from category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN):
            return 1
        return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 5

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//div[@class="numlist2"]//span/text()') if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = [x for x in tree.xpath('.//div[@id="vidresults"]/div')
                  if 'class' in x.attrib and 'mb' in x.attrib['class']]
        res = []
        for video_tree_data in videos:
            resolution = video_tree_data.xpath('./div[@class="mvhdico"]/*/text()')
            assert len(resolution) >= 1
            if len(resolution) == 2:
                is_hd = True
                is_vr = True
                resolution = resolution[1]
            elif len(resolution) == 1:
                is_hd = resolution[0] in self.sd_resolutions
                is_vr = False
                resolution = resolution[0]
            else:
                raise RuntimeError('Cannot fetch the resolution!')

            link_data = video_tree_data.xpath('./div/div/a')
            assert len(link_data) == 1
            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if len(image) == 0 or 'data:image' in image:
                # We try alternative path
                image = image_data[0].attrib['data-src']
            # flip_start = image_data[0].attrib['data-st']
            flip_end = image_data[0].attrib['data-stdef'] if 'data-stdef' in image_data[0].attrib \
                else self.max_flip_image
            flip_images = [re.sub(r'{e}_240.jpg'.format(e=flip_end), '{i}_240.jpg'.format(i=i), image)
                           for i in range(1, int(flip_end) + 1)]

            link = link_data[0].attrib['href']

            data_tree = video_tree_data.xpath('./div[@class="mbunder"]')
            assert len(data_tree) == 1

            title = data_tree[0].xpath('./p[@class="mbtit"]/a')
            assert len(title) == 1
            title = title[0].text

            stats_tree = data_tree[0].xpath('./p[@class="mbstats"]')
            assert len(stats_tree) == 1

            video_length = stats_tree[0].xpath('./span[@class="mbtim"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            rating = stats_tree[0].xpath('./span[@class="mbrate"]')
            assert len(rating) == 1
            rating = rating[0].text

            viewers = stats_tree[0].xpath('./span[@class="mbvie"]')
            assert len(viewers) == 1
            viewers = viewers[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  resolution=resolution,
                                                  is_hd=is_hd,
                                                  is_vr=is_vr,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  title=title,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  number_of_views=viewers,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        # program_fetch_url = urljoin(self.base_url, object_data.url)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        if page_number is not None and page_number > 1:
            fetch_base_url = urljoin(fetch_base_url, str(page_number)) + '/'
        if true_object.object_type == PornCategories.CATEGORY:
            if page_filter.sort_order.filter_id != PornFilterTypes.DateOrder:
                fetch_base_url = urljoin(fetch_base_url, page_filter.sort_order.value)
        elif true_object.object_type == PornCategories.PORN_STAR:
            if page_filter.sort_order.filter_id != PornFilterTypes.PopularityOrder2:
                fetch_base_url = urljoin(fetch_base_url, page_filter.sort_order.value)
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            if page_filter.sort_order.filter_id != PornFilterTypes.DateOrder:
                fetch_base_url = urljoin(fetch_base_url, page_filter.sort_order.value)

        if fetch_base_url[-1] != '/':
            fetch_base_url += '/'

        page_request = self.session.get(fetch_base_url, headers=headers)
        return page_request

    def search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        res = super(EPorner, self).search_query(query)
        # First run for cookie purpose
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        self.session.get(self.objects[PornCategories.SEARCH_MAIN].url, headers=headers)
        return res

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query.replace(' ', '-')))

    @property
    def __version(self):
        return 2

    @property
    def _version_stack(self):
        return super(EPorner, self)._version_stack + [self.__version]
