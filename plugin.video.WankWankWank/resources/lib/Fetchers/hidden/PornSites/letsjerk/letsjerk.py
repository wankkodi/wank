# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher
from ....tools.external_fetchers import ExternalFetcher

# Internet tools
from .... import urlparse, urljoin, quote_plus

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, PornFilter, PornFilterTypes
from ....catalogs.porn_catalog import PornCategories, VideoNode, VideoSource

# Warnings
import warnings


class LetsJerk(PornFetcher):
    number_of_thumbnails = 20

    @property
    def object_urls(self):
        # fixme: search temporarily disabled.
        return {
            PornCategories.CATEGORY_MAIN: 'http://letsjerk.to/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://letsjerk.to/pornstars/',
            # PornCategories.CHANNEL_MAIN: 'http://letsjerk.to/studios/',
            PornCategories.LATEST_VIDEO: 'https://letsjerk.to/?order=newest',
            PornCategories.TOP_RATED_VIDEO: 'https://letsjerk.to/?order=rating',
            PornCategories.MOST_VIEWED_VIDEO: 'https://letsjerk.to/?order=views',
            PornCategories.MOST_DISCUSSED_VIDEO: 'https://letsjerk.to/?order=comments',
            PornCategories.SEARCH_MAIN: 'http://letsjerk.is/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://letsjerk.to/'

    def __init__(self, source_name='LetsJerk', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(LetsJerk, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)
        self.external_fetchers = ExternalFetcher(session=self.session, user_agent=self.user_agent, parser=self.parser)

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Newest', 'comments'),
                                        (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                        (PornFilterTypes.ViewsOrder, 'Views', 'views'),
                                        (PornFilterTypes.CommentsOrder, 'Comments', 'comments'),
                                        ),
                         'period_filters': ([(PornFilterTypes.AllDate, 'All time', None),
                                             (PornFilterTypes.OneDate, 'This Month', '_month'),
                                             (PornFilterTypes.TwoDate, 'This week', '_week'),
                                             (PornFilterTypes.ThreeDate, 'Today', '_today'),
                                             ],
                                            [('sort_order', [PornFilterTypes.RatingOrder,
                                                             PornFilterTypes.ViewsOrder,
                                                             PornFilterTypes.CommentsOrder])]
                                            ),

                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         video_args=video_filters,
                                         )

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumbs"]/ul/li')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-original'] \
                if 'data-original' in image_data[0].attrib else image_data[0].attrib['src']
            title = image_data[0].attrib['alt'] if 'alt' in image_data[0].attrib else None

            if title is None:
                title = link_data[0].xpath('./div[@class="taxonomy-name"]')
                if len(title) == 0:
                    # We have empty sequence, just skip it...
                    continue
                else:
                    title = title[0].text

            number_of_videos = category.xpath('./div[@class="taxonomy-videos"]/a/div[@class="number"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text) if len(number_of_videos) > 0 else None

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available channels.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = tree.xpath('.//div[@class="items"]/div[@class="performer-item"]')
        res = []
        for porn_star in porn_stars:
            link_data = porn_star.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-original'] \
                if 'data-original' in image_data[0].attrib else image_data[0].attrib['src']
            title = image_data[0].attrib['alt'] if 'alt' in image_data[0].attrib else None

            if title is None:
                title = link_data[0].xpath('./span[@class="performer-name"]')
                if len(title) == 0:
                    # We have empty sequence, just skip it...
                    continue
                else:
                    title = title[0].text

            number_of_videos = porn_star.xpath('./span[@class="performer-videos"]/span[@class="count"]')
            number_of_videos = int(number_of_videos[0].text) if len(number_of_videos) > 0 else None

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.PORN_STAR,
                                                  super_object=porn_star_data
                                                  )
            res.append(object_data)
        porn_star_data.add_sub_objects(res)
        return res

    # def _update_available_channels(self, channel_data):
    #     """
    #     Fetches all the available channels.
    #     :return: Object of all available shows (JSON).
    #     """
    #     return self._update_available_base_objects(channel_data,
    #                                                './/div[@class="items"]/div[@class="performer-item"]',
    #                                                PornCategories.CHANNEL)

    def _update_available_base_objects(self, base_object_data, sub_object_xpath, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(sub_object_xpath)
        res = []
        for category in categories:
            title = category.xpath('./h3/a')
            if len(title) == 0:
                # We have empty sequence, just skip it...
                continue

            image = category.xpath('./a/div[@class="thumbnail"]/img')
            assert len(image) == 1
            number_of_videos = category.xpath('./div[@class="buttons"]/a')
            assert len(number_of_videos) == 1
            number_of_videos = re.findall(r'(?:All )(\d+)(?: videos)', number_of_videos[0].text)
            number_of_videos = int(number_of_videos[0]) if len(number_of_videos) > 0 else None

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=title[0].attrib['href'],
                                                  url=urljoin(self.base_url, title[0].attrib['href']),
                                                  title=title[0].text,
                                                  image_link=image[0].attrib['src'],
                                                  number_of_videos=number_of_videos,
                                                  object_type=object_type,
                                                  super_object=base_object_data
                                                  )
            res.append(object_data)
        base_object_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """

        tmp_request = self.get_object_request(video_data)
        videos = self._get_video_links_from_video_data_method1(tmp_request)
        if len(videos) == 0:
            # We try another method
            videos = self._get_video_links_from_video_data_method2(tmp_request)

        return VideoNode(video_sources=videos)

    def _get_video_links_from_video_data_method1(self, page_request):
        """
        # Method 1 of fetching the videos.
        """
        tmp_tree = self.parser.parse(page_request.text)
        request_data = tmp_tree.xpath('.//form[@id="form1"]//option/@value')
        videos = []
        for new_url in request_data:
            if urlparse(new_url).hostname == 'streamcherry.com':
                videos.extend(self.external_fetchers.get_video_link_from_streamcherry(new_url))
            if urlparse(new_url).hostname == 'openload.co':
                videos.extend(self.external_fetchers.get_video_link_from_openload(new_url))
            else:
                warnings.warn('Unknown host {h}'.format(h=urlparse(new_url).hostname))

        videos = sorted((VideoSource(link=x[0], resolution=x[1]) for x in videos),
                        key=lambda x: x.resolution, reverse=True)
        return videos

    def _get_video_links_from_video_data_method2(self, page_request):
        """
        # Method 2 of fetching the videos.
        """
        tmp_tree = self.parser.parse(page_request.text)
        request_data = tmp_tree.xpath('.//video/source')
        res = sorted((VideoSource(link=x.attrib['src'],
                                  resolution=x.attrib['title'] if 'title' in x.attrib and x.attrib['title'].isdigit()
                                  else 720 if 'title' in x.attrib and 'HD' == x.attrib['title'] else 360)
                      for x in request_data),
                     key=lambda x: x.resolution, reverse=True)

        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        Finds the number of pages for the given parsed object.
        :param tree: Page tree.
        :return: number of pages (int).
        """
        pages = [int(re.findall(r'(\d+)(?:/*\?|/*$)', x.attrib['href'])[0])
                 for x in tree.xpath('.//*[@class="pagination"]/ul/li/a')
                 if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*\?|/*$)', x.attrib['href'])) > 0]
        return pages

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumbs"]/ul/li/a')
        res = []
        for video_tree_data in videos:
            image_data = video_tree_data.xpath('./img')
            image = image_data[0].attrib['data-original'] \
                if 'data-original' in image_data[0].attrib else image_data[0].attrib['data-src'] \
                if 'data-src' in image_data[0].attrib else image_data[0].attrib['src']
            title = image_data[0].attrib['alt'] if 'alt' in image_data[0].attrib else None

            rating = video_tree_data.xpath('./strong[@class="toolbar"]/em[@class="rate_thumb"]/em')
            assert len(rating) == 1
            rating = rating[0].text

            number_of_views = video_tree_data.xpath('./div[@class="post-views"]/div[@class="number"]/'
                                                    'div[@id="video_views"]')
            assert len(number_of_views) == 1
            number_of_views = int(self._clear_text(number_of_views[0].text))

            is_hd = video_tree_data.xpath('./strong[@class="toolbar"]/em[@class="time_thumb"]/i[@class="quality"]')
            is_hd = len(is_hd) == 1 and self._clear_text(is_hd[0].text) == 'HD'

            if title is None:
                title = video_tree_data.xpath('./span[@class="desc"]/span/em[@class="title"]')
                assert len(title) == 1
                title = title[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['href'],
                                                  url=urljoin(self.base_url, video_tree_data.attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  rating=rating,
                                                  is_hd=is_hd,
                                                  number_of_views=number_of_views,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')

        if page_number is not None and page_number != 1:
            if len(split_url[-1]) > 0:
                split_url.append('')
            split_url.insert(-1, 'page')
            split_url.insert(-1, str(page_number))
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
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id

        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            params['order'][0] += page_filter.period.value

        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?s={q}'.format(q=quote_plus(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(LetsJerk, self)._version_stack + [self.__version]
