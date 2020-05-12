# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote_plus, urlparse

# Regex
import re

# Math
import math

# # Request Exception
# import json

try:
    from json import \
        JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter


class PornHD(PornFetcher):
    prime_host_name = 'www.pornhdprime.com'
    max_flip_images = 53

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
            PornCategories.CATEGORY_MAIN: 'https://www.pornhd.com/category',
            PornCategories.CHANNEL_MAIN: 'https://www.pornhd.com/channel',
            PornCategories.PORN_STAR_MAIN: 'https://www.pornhd.com/pornstars',
            PornCategories.RECOMMENDED_VIDEO: 'https://www.pornhd.com/?order=featured',
            PornCategories.LATEST_VIDEO: 'https://www.pornhd.com/?order=newest',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.pornhd.com/?order=most-popular',
            PornCategories.LONGEST_VIDEO: 'https://www.pornhd.com/?order=longest',
            PornCategories.TOP_RATED_VIDEO: 'https://www.pornhd.com/?order=top-rated',
            # PornCategories.LIVE_VIDEO: 'https://www.pornhd.com/live-sex',
            PornCategories.SEARCH_MAIN: 'https://www.pornhd.com/search',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.RECOMMENDED_VIDEO: PornFilterTypes.RecommendedOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LIVE_VIDEO: PornFilterTypes.LiveOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornhd.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        categories_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most Popular', 'most-popular'),
                                             (PornFilterTypes.AlphabeticOrder, 'Alphabetical ', 'alphabetical'),
                                             (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'video-count'),
                                             ],
                              }
        porn_stars_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most Popular', 'most-popular'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'video-count'),
                                             (PornFilterTypes.AlphabeticOrder, 'Alphabetical ', 'alphabetical'),
                                             ],
                              }
        channels_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most Popular', 'most-popular'),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'video-count'),
                                           (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                                           (PornFilterTypes.AlphabeticOrder, 'Alphabetical ', 'alphabetical'),
                                           ],
                            }
        video_filters = {'sort_order': [(PornFilterTypes.RecommendedOrder, 'Featured', 'featured'),
                                        (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                                        (PornFilterTypes.ViewsOrder, 'Views', 'most-popular'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        (PornFilterTypes.RatingOrder, 'Rating', 'top-rated'),
                                        ],
                         }
        search_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Relevant', 'mostrelevant'),
                                         (PornFilterTypes.RecommendedOrder, 'Featured', 'featured'),
                                         (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                                         (PornFilterTypes.ViewsOrder, 'Views', 'most-popular'),
                                         (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                         (PornFilterTypes.RatingOrder, 'Rating', 'top-rated'),
                                         ],
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         channels_args=channels_filters,
                                         porn_stars_args=porn_stars_filters,
                                         categories_args=categories_filters,
                                         single_category_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         single_tag_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='PornHD', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornHD, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_object(category_data,
                                             './/section[@class="small-thumb-list lazy-load"]/article',
                                             PornCategories.CATEGORY)

    def _update_available_porn_stars(self, pornstar_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_object(pornstar_data,
                                             './/section[@class="section-margin small-thumb-list lazy-load"]/article',
                                             PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channels.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_object(channel_data,
                                             './/section[@class="section-margin small-thumb-list lazy-load"]/article',
                                             PornCategories.CHANNEL)

    def _update_available_object(self, object_data, page_xpath, object_type):
        """
        Fetches all the available object.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(page_xpath)
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            if len(link_data) == 0:
                # dummy node
                continue

            image_data = link_data[0].xpath('./picture/img')
            title = None
            image = None
            if len(image_data) > 0:
                image = urljoin(self.base_url, image_data[0].attrib['src'])
                if 'alt' in image_data[0].attrib:
                    title = image_data[0].attrib['alt']

            if title is None:
                title = link_data[0].xpath('./*[@class="thumb-title"]')
                assert len(title) == 1
                title = self._clear_text(title[0].text)

            # additional_info = category.xpath('./div[@class="info"]/div[@class="video-count"]')
            # number_of_videos = re.findall(r'\d+', additional_info[0].text) if len(additional_info) > 0 else None
            # number_of_videos = int(number_of_videos[0]) \
            #     if number_of_videos is not None and len(number_of_videos) > 0 else None
            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link_data[0].attrib['href'],
                                                      url=urljoin(self.base_url, link_data[0].attrib['href']),
                                                      title=title,
                                                      image_link=image,
                                                      # number_of_videos=number_of_videos,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        object_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        video_url = video_data.url
        if urlparse(video_url).hostname == self.prime_host_name:
            # In case of the prime video, we need to fetch it separately.
            return self._get_prime_video_links_from_video_data(video_data)

        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        videos = tmp_tree.xpath('.//video/source')
        video_links = sorted((VideoSource(link=urljoin(self.base_url, x.attrib['src']),
                                          resolution=int(x.attrib['res']))
                              for x in videos),
                             key=lambda x: x.resolution, reverse=True)

        return VideoNode(video_sources=video_links)

    def _get_prime_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        request_data = tmp_tree.xpath('.//video[@id="html5-player"]/source')
        video_links = sorted((VideoSource(link=x.attrib['src'], resolution=int(x.attrib['res'])) for x in request_data),
                             key=lambda y: y.resolution, reverse=True)

        return VideoNode(video_sources=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type == PornCategories.LIVE_VIDEO:
            return self._binary_search_max_number_of_live_pages(category_data, last_available_number_of_pages)
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

    def _binary_search_max_number_of_pages(self, category_data, last_available_number_of_pages):
        """
        Performs binary search in order to find the last available page.
        :param category_data: Category data.
        :param last_available_number_of_pages: Last available number of pages. Will be the pivot for our next search.
        By default is None, which mean the original pivot will be used...
        :return: Page request
        """
        left_page = 1
        right_page = self.max_pages
        page = last_available_number_of_pages if last_available_number_of_pages is not None \
            else int(math.ceil((right_page + left_page) / 2))
        use_max_page_flag = True
        while 1:
            page_request = self._get_object_request_no_exception_check(category_data, override_page_number=page)
            if self._check_is_available_page(category_data, page_request):
                tree = self.parser.parse(page_request.text)
                pages = self._get_available_pages_from_tree(tree)
                if len(pages) == 0:
                    # We also moved too far...
                    right_page = page - 1
                else:
                    max_page = max(pages) if use_max_page_flag is True else page
                    if max_page - page < self._binary_search_page_threshold:
                        return max_page

                    left_page = max_page
            else:
                # We moved too far...
                right_page = page - 1
                if left_page >= right_page:
                    use_max_page_flag = False
                    left_page = right_page - 1
            page = int(math.ceil((right_page + left_page) / 2))

    def _binary_search_max_number_of_live_pages(self, category_data, last_available_number_of_pages):
        """
        Override of super method with local modifications...
        Performs binary search in order to find the last available page.
        :param category_data: Category data.
        :param last_available_number_of_pages: Last available number of pages. Will be the pivot for our next search.
        By default is None, which mean the original pivot will be used...
        :return: Page request
        """
        left_page = 1
        right_page = self.max_pages
        page = last_available_number_of_pages if last_available_number_of_pages is not None \
            else int(math.ceil((right_page + left_page) / 2))
        while 1:
            page_request = self._get_object_request_no_exception_check(category_data, override_page_number=page)
            if self._check_is_available_page(category_data, page_request):
                tree = self.parser.parse(page_request.text)
                videos = tree.xpath('.//ul[@class="thumbs live-girls"]/li')
                if len(videos) == 0:
                    # We also moved too far...
                    right_page = page - 1
                else:
                    left_page = page

                if left_page == right_page:
                    return left_page
            else:
                # We moved too far...
                right_page = page - 1
                if left_page >= right_page:
                    left_page = right_page - 1

            page = int(math.ceil((right_page + left_page) / 2))

    # def _check_is_available_page(self, page_request):
    #     """
    #     In binary search performs test whether the current page is available.
    #     :param page_request: Page request.
    #     :return:
    #     """
    #     return page_request.ok
    #     # tree = self.parser.parse(page_request.text)
    #     # return len(self._get_available_pages_from_tree(tree)) > 0

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        tmp_res = [int(x.text) for x in tree.xpath('.//section[@class="section-margin pagination-wrapper"]/div/*')
                   if x.text.isdigit()]
        return tmp_res

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 6

    # # Obsolete
    # def get_videos_data(self, page_data):
    #     """
    #     Gets videos data for the given category.
    #     :param page_data: Page data.
    #     :return:
    #     """
    #     page_request = self.get_object_request(page_data)
    #     tree = self.parser.parse(page_request.text)
    #     videos = ([x for x in tree.xpath('.//ul[@class="thumbs"]/li') if 'data-video' in x.attrib] +
    #               [x for x in tree.xpath('.//ul[@class="thumbs live-girls"]/li')])
    #     res = []
    #     for video_tree_data in videos:
    #         preview_video = video_tree_data.attrib['data-webm'] if 'data-webm' in video_tree_data.attrib else None
    #         if preview_video is None:
    #             preview_video = video_tree_data.attrib['data-mp4'] if 'data-mp4' in video_tree_data.attrib else None
    #
    #         link_data = [x for x in video_tree_data.xpath('./a')
    #                      if 'class' in x.attrib and 'thumb' in x.attrib['class']]
    #         if len(link_data) == 0:
    #             # We want not to include premium content
    #             continue
    #             # link_data = video_tree_data.xpath('./a[@class="thumb videoThumb prime-video-thumb '
    #             #                                   'rotate-video-thumb popTrigger"]')
    #
    #         if 'data-thumbs' in link_data[0].attrib:
    #             flix_image = re.findall(r'(?:")(.*?)(?:")', link_data[0].attrib['data-thumbs'])
    #             flix_image = [urljoin(page_data.url, re.sub(r'\\/', '/', x)) for x in flix_image]
    #         else:
    #             flix_image = None
    #
    #         assert len(link_data) == 1
    #         link = link_data[0].attrib['href']
    #         url = urljoin(self.base_url, link)
    #
    #         img = link_data[0].xpath('./img/@src')
    #         assert len(img) == 1
    #         if 'data:image' in img[0]:
    #             img = link_data[0].xpath('./img/@data-original')
    #         assert len(img) == 1
    #         image = img[0]
    #
    #         video_length = link_data[0].xpath('./div[@class="meta"]/time/text()')
    #         if len(video_length) == 0:
    #             video_length = link_data[0].xpath('./div[@class="meta transition"]/time/text()')
    #         assert len(video_length) == 1
    #         video_length = self._clear_text(video_length[0])
    #
    #         title = video_tree_data.xpath('./a[@class="title"]/text()')
    #         assert len(title) == 1
    #         title = self._clear_text(title[0])
    #
    #         video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
    #                                               obj_id=link,
    #                                               url=url,
    #                                               title=title,
    #                                               image_link=image,
    #                                               flip_images_link=flix_image,
    #                                               preview_video_link=preview_video,
    #                                               duration=self._format_duration(video_length),
    #                                               object_type=PornCategories.VIDEO,
    #                                               super_object=page_data,
    #                                               )
    #         res.append(video_data)
    #     page_data.add_sub_objects(res)
    #     return res

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = ([x for x in tree.xpath('.//div[@class="video-list-container"]/article[@class="video-item "]')] +
                  [x for x in tree.xpath('.//div[@class="video-list-container live-sex"]/'
                                         'article[@class="video-item live-video-item"]')]
                  )
        res = []
        for video_tree_data in videos:
            title = video_tree_data.xpath('./a')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            main_section = video_tree_data.xpath('./section[@class="thumb-top"]')
            assert len(main_section) == 1
            link_data = main_section[0].xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./picture/source[@type="image/jpeg"]')
            if len(image_data) == 0:
                image_data = link_data[0].xpath('./picture/source[@type="image/webp"]')
            image = image_data[0].attrib['srcset'] \
                if 'srcset' in image_data[0].attrib else image_data[0].attrib['data-srcset']
            flip_images = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                           for i in range(1, self.max_flip_images + 1)] \
                if len(re.findall(r'\d+.jpg', image)) > 0 else None

            video_data = link_data[0].xpath('./picture/img')
            video_preview = urljoin(self.base_url, video_data[0].attrib['data-preview-url'].replace('webm', 'mp4'))

            video_length = main_section[0].xpath('.//span[@class="meta"]/*[@class="video-duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                obj_id=link,
                                                url=urljoin(self.base_url, link),
                                                title=title,
                                                image_link=image,
                                                flip_images_link=flip_images,
                                                preview_video_link=video_preview,
                                                duration=self._format_duration(video_length),
                                                object_type=PornCategories.VIDEO,
                                                super_object=page_data,
                                                ))
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            # 'Referer': self.base_url,
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_number is not None and page_number > 1:
            params['page'] = [page_number]

        if true_object.object_type not in self._default_sort_by:
            params['order'] = [page_filter.sort_order.value]

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        if (
                true_object.object_type == PornCategories.SEARCH_MAIN and len(page_request.history) > 0 and
                ((page_number is not None and page_number > 1) or
                 page_filter.sort_order.filter_id != PornFilterTypes.RelevanceOrder)
        ):
            # We have a redirection
            fetch_base_url = page_request.url
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)

        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?search={q}'.format(q=quote_plus(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(PornHD, self)._version_stack + [self.__version]
