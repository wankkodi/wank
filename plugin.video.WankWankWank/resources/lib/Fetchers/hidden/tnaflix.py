# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError

# Internet tools
from .. import urljoin, parse_qs, quote, quote_plus

# Regex
import re

# Generator id
from ..id_generator import IdGenerator

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# Math
import math


class TnaFlix(PornFetcher):
    video_list_url_template = 'https://cdn-fck.tnaflix.com/tnaflix/{vkey}.fid'

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags.php'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/pornstars'),
            PornCategories.RECOMMENDED_VIDEO: urljoin(self.base_url, '/featured'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/new'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, '/popular'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/toprated'),
            PornCategories.USER_UPLOADED_VIDEO: urljoin(self.base_url, '/user-videos'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search.php'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.RECOMMENDED_VIDEO: PornFilterTypes.FeaturedOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.USER_UPLOADED_VIDEO: PornFilterTypes.UserVideosOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.tnaflix.com/'

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        # todo: find a better estimator
        return 50000

    @property
    def max_binary_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        # todo: find a better estimator
        return 50

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        tag_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Popular', None),
                                      (PornFilterTypes.AlphabeticOrder, 'Alphabetical',
                                       'search=&sort_alphabetically=1&order_desc=0'),
                                      ),
                       }
        channel_filters = {'sort_order': ((PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                          (PornFilterTypes.DateOrder, 'Most Recent', 'most-recent'),
                                          (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                          ),
                           }
        porn_star_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Popularity', '2'),
                                            (PornFilterTypes.AlphabeticOrder, 'Name', '0'),
                                            (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', '4'),
                                            ),
                             }
        single_category_filters = {'sort_order': ((PornFilterTypes.FeaturedOrder, 'Featured', 'featured'),
                                                  (PornFilterTypes.UserVideosOrder, 'User Videos', 'user-videos'),
                                                  (PornFilterTypes.DateOrder, 'Most Recent', 'most-recent'),
                                                  (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                                  (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                                  ),
                                   'length_filters': ((PornFilterTypes.AllLength, 'All durations', 'all'),
                                                      (PornFilterTypes.OneLength, 'Short (1-3 min)', 'short'),
                                                      (PornFilterTypes.TwoLength, 'Medium (3-10 min)', 'medium'),
                                                      (PornFilterTypes.ThreeLength, 'Long (10-30 min)', 'long'),
                                                      (PornFilterTypes.FourLength, 'Full length (+30 min)', 'full'),
                                                      ),
                                   'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', '0'),
                                                       (PornFilterTypes.HDQuality, 'HD quality', '1'),
                                                       ),
                                   }
        single_porn_star_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Most Recent', 'most-recent'),
                                                   (PornFilterTypes.PopularityOrder, 'Most Popular', 'most-viewed'),
                                                   (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                                   ),
                                    'length_filters': single_category_filters['length_filters'],
                                    'quality_filters': single_category_filters['quality_filters'],
                                    }
        single_channel_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Most Recent', 'most-recent'),
                                                 (PornFilterTypes.PopularityOrder, 'Most Popular', 'most-viewed'),
                                                 (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                                 ),
                                  'length_filters': single_category_filters['length_filters'],
                                  }
        video_filters = {'sort_order': ((PornFilterTypes.FeaturedOrder, 'Featured', 'featured'),
                                        (PornFilterTypes.UserVideosOrder, 'User Videos', 'user-videos'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'toprated'),
                                        (PornFilterTypes.DateOrder, 'Most Recent', 'new'),
                                        (PornFilterTypes.PopularityOrder, 'Most Popular', 'popular'),
                                        ),
                         'period_filters': ([(PornFilterTypes.AllDate, 'All time', 'all'),
                                             (PornFilterTypes.TwoDate, 'Week', 'week'),
                                             (PornFilterTypes.OneDate, 'Month', 'month'),
                                             (PornFilterTypes.ThreeDate, 'Day', 'day'),
                                             ],
                                            [('sort_order', [PornFilterTypes.PopularityOrder,
                                                             ])]
                                            ),
                         'length_filters': single_category_filters['length_filters'],
                         'quality_filters': single_category_filters['quality_filters'],
                         }
        search_filters = {'sort_order': ((PornFilterTypes.RelevanceOrder, 'Relevance', 'relevance'),
                                         (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                                         (PornFilterTypes.DateOrder, 'Most Recent', 'date'),
                                         ),
                          'period_filters': ((PornFilterTypes.AllDate, 'All time', 'all'),
                                             (PornFilterTypes.TwoDate, 'Week', 'week'),
                                             (PornFilterTypes.OneDate, 'Month', 'month'),
                                             (PornFilterTypes.ThreeDate, 'Day', 'today'),
                                             ),
                          'length_filters': single_category_filters['length_filters'],
                          'quality_filters': single_category_filters['quality_filters'],
                          }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         channels_args=channel_filters,
                                         tags_args=tag_filters,
                                         porn_stars_args=porn_star_filters,
                                         single_category_args=single_category_filters,
                                         single_porn_star_args=single_porn_star_filters,
                                         single_channel_args=single_channel_filters,
                                         single_tag_args=search_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='TnaFlix', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(TnaFlix, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, './/ul[@class="thumbsList catsList clear"]/li',
                                                  PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channels.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(channel_data, './/ul[@class="thumbsList channelsList channelsList1 '
                                                                'clear found-items"]/li',
                                                  PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data, './/ul[@class="thumbsList catsList clear"]/li',
                                                  PornCategories.PORN_STAR)

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        page_json = page_request.json()
        tree = self.parser.parse(page_json['content'])
        raw_objects = tree.xpath('.//div[@class="tagscolumn"]/div[@class="tagrow"]/a')
        raw_number_of_videos = tree.xpath('.//div[@class="tagscolumn"]/div[@class="tagrow"]/span')
        links = [x.attrib['href'] for x in raw_objects]
        titles = [x.text.title() for x in raw_objects]
        number_of_videos = [int(x.text) for x in raw_number_of_videos]
        assert len(titles) == len(links)
        assert len(titles) == len(number_of_videos)
        sub_tags = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                            obj_id=link,
                                            url=urljoin(tag_data.url, link),
                                            title=title,
                                            number_of_videos=number_of_videos,
                                            object_type=PornCategories.TAG,
                                            super_object=tag_data,
                                            )
                    for link, title, number_of_videos in zip(links, titles, number_of_videos)]
        tag_data.add_sub_objects(sub_tags)
        return sub_tags

    def _update_available_base_object(self, base_object_data, xpath, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object_data)
        page_json = page_request.json()
        tree = self.parser.parse(page_json['content'])
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link_data = [x for x in category.xpath('./a') if 'class' in x.attrib and 'thumb' in x.attrib['class']]
            assert len(link_data) == 1

            image = link_data[0].xpath('./img')
            assert len(image) == 1

            title = (category.xpath('./a[@class="categoryTitle"]/text()') +
                     category.xpath('./a[@class="categoryTitle channelTitle"]/text()'))
            assert len(title) > 0
            title = self._clear_text(title[0])

            number_of_videos = link_data[0].xpath('./div[@class="vidcountSp"]/text()')
            number_of_videos = int(re.sub(r'[(),]', '', str(number_of_videos[0]))) if len(number_of_videos) == 1 else 0

            num_of_subscribers = category.xpath('./div[@class="clear catsItemInfo"]/div[@class="inInBtnBlock clear"]/'
                                                'span[@id="subcatcount_6"]/text()')
            number_of_subscribers = (int(re.sub(r'[(),]', '', str(num_of_subscribers[0])))
                                     if len(num_of_subscribers) == 1 else None)

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(base_object_data.url, link_data[0].attrib['href']),
                                                  title=title,
                                                  image_link=image[0].attrib['src'],
                                                  number_of_videos=number_of_videos,
                                                  number_of_subscribers=number_of_subscribers,
                                                  object_type=object_type,
                                                  super_object=base_object_data,
                                                  )
            res.append(object_data)
        base_object_data.add_sub_objects(res)
        return res

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return False

    # def _get_tag_properties(self, page_request):
    #     """
    #     Fetches tag links and titles.
    #     :param page_request: Page request.
    #     :return:
    #     """
    #     page_json = page_request.json()
    #     tree = self.parser.parse(page_json['content'])
    #     raw_objects = tree.xpath('.//div[@class="tagscolumn"]/div[@class="tagrow"]/a')
    #     raw_number_of_videos = tree.xpath('.//div[@class="tagscolumn"]/div[@class="tagrow"]/span')
    #     links = [x.attrib['href'] for x in raw_objects]
    #     titles = [x.text.title() for x in raw_objects]
    #     number_of_videos = [int(x.text) for x in raw_number_of_videos]
    #     assert len(titles) == len(links)
    #     assert len(titles) == len(number_of_videos)
    #
    #     return links, titles, number_of_videos

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        request_data = tmp_tree.xpath('.//section[@class="sOutIn"]/input')
        request_data = {x.attrib['id']: x.attrib['value'] for x in request_data}
        assert len(request_data) > 0

        request_url = self.video_list_url_template.format(vkey=request_data['vkey'])
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
        params = {
            'key': request_data['nkey'],
            'VID': request_data['VID'],
            'nomp4': 1,
            'catID': 0,
            'rollover': 1,
            'startThumb': 13,
            'embed': 0,
            'utm_source': 0,
            'multiview': 0,
            'premium': 1,
            'country': '0user=0',
            'vip': 1,
            'cd': 0,
            'ref': 0,
            'alpha': '',
        }
        tmp_request = self.session.get(request_url, headers=headers, params=params)
        assert tmp_request.ok
        raw_text = re.sub(r'<!\[CDATA\[', '', re.sub(r']]>', '', tmp_request.text))
        tmp_tree = self.parser.parse(raw_text)
        # todo: could be videoLink instead of videoLinkDownload
        res = sorted((VideoSource(link=urljoin(self.base_url, x.xpath('./videolinkdownload')[0].text),
                                  resolution=int(re.findall(r'\d+', x.xpath('./res')[0].text)[0]),
                                  fps=int(re.findall(r'(\d+)(?:fps)', x.xpath('./res')[0].text)[0])
                                  if len(re.findall(r'(\d+)(?:fps)', x.xpath('./res')[0].text)) > 0 else 30)
                      for x in tmp_tree.xpath('.//quality/item')),
                     key=lambda x: (x.resolution, x.fps), reverse=True)
        return VideoNode(video_sources=res)

    def _binary_search_max_number_of_pages(self, category_data, last_available_number_of_pages):
        """
        Performs binary search in order to find the last available page.
        :param category_data: Category data.
        :param last_available_number_of_pages: Last available number of pages. Will be the pivot for our next search.
        By default is None, which mean the original pivot will be used...
        :return: Page request
        """
        try:
            page_request = self.get_object_request(category_data, override_page_number=1)
        except PornFetchUrlError as err:
            # page_request = self.get_object_request(category_data, override_page_number=1)
            raise err

        page_json = page_request.json()
        tree = self.parser.parse(page_json['content'])
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        if max(pages) - 1 < self._binary_search_page_threshold:
            return max(pages)

        left_page = 1
        right_page = self.max_binary_pages
        page = last_available_number_of_pages if last_available_number_of_pages is not None \
            else int(math.ceil((right_page + left_page) / 2))
        while 1:
            try:
                page_request = self.get_object_request(category_data, override_page_number=page, send_error=False)

                page_json = page_request.json()
                tree = self.parser.parse(page_json['content'])
                pages = self._get_available_pages_from_tree(tree)
                if len(pages) == 0:
                    return 1
                elif max(pages) < page:
                    # We also moved too far...
                    right_page = page - 1
                else:
                    max_page = max(pages)
                    if max_page - page < self._binary_search_page_threshold:
                        return max_page

                    left_page = max_page
            except PornFetchUrlError:
                # We moved too far...
                right_page = page - 1
            page = int(math.ceil((right_page + left_page) / 2))

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # At first we try to check whether we have max page from the initial page.
        # page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        # page_json = page_request.json()
        # tree = self.parser.parse(page_json['content'])
        # pages = self._get_available_pages_from_tree(tree)
        # if len(pages) == 0:
        #     return 1
        # if category_data.page_number is not None:
        #     max_page = max(pages)
        #     if max_page - category_data.page_number < self._binary_search_page_threshold:
        #         return max_page
        #
        # # We perform binary search
        # return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)
        # We perform binary search

        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1
        elif category_data.object_type in (PornCategories.TAG_MAIN, ):
            return 20
        elif category_data.object_type in (PornCategories.CHANNEL, PornCategories.PORN_STAR):
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)
        else:
            start_page = self.max_pages
            while 1:
                try:
                    self.get_object_request(category_data, start_page, send_error=False)
                    # We propagate the start page
                    start_page += self.max_pages
                except PornFetchUrlError as err:
                    # We have been redirected to the last available page.
                    if category_data.object_type in (PornCategories.PORN_STAR_MAIN, PornCategories.PORN_STAR,
                                                     PornCategories.SEARCH_MAIN, PornCategories.TAG):
                        return int(re.findall(r'(?:page=)(\d+)', err.request.url)[0])
                    else:
                        return int(re.findall(r'(?:/)(\d+)(?:\?|/|$)', err.request.url)[0])

    def _check_is_available_page(self, page_request):
        """
        In binary search performs test whether the current page is available.
        :param page_request: Page request.
        :return:
        """
        return len(page_request.history) == 0

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//div[@class="navigation clear"]/a/text()') if x.isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 4

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        try:
            page_request = self.get_object_request(page_data)
        except PornFetchUrlError:
            # page_request = self.get_object_request(page_data)
            return None
        videos = page_request.json()
        tree = self.parser.parse(videos['content'])
        videos = tree.xpath('.//ul[@class="thumbsList nThumbsList  clear found-items"]/li')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a[@class="thumb no_ajax"]')
            assert len(link) == 1

            image_data = video_tree_data.xpath('./a[@class="thumb no_ajax"]/img[@class="lazy"]')
            assert len(link) == 1
            image = image_data[0].attrib['data-original']
            flip_images = [re.sub(r'/\d+_', '/{i}_'.format(i=x), image) for x in range(1, 30, 2)]

            video_length = video_tree_data.xpath('./a[@class="thumb no_ajax"]/div[@class="videoDuration"]')
            assert len(video_length) == 1

            is_hd = video_tree_data.xpath('./a[@class="thumb no_ajax"]/div[@class="hdIcon"]')

            user = video_tree_data.xpath('./div[@class="curatorUser"]/div')
            assert len(user) == 1
            additional_data = \
                {'uploader_data': {'id': (user[0].attrib['data-uid'] if 'data-uid' in user[0].attrib else
                                          (user[0].attrib['data-chid'] if 'data-chid' in user[0].attrib else None)),
                                   'url': urljoin(self.base_url, user[0].xpath('./a/@href')[0])},
                 }

            viewers = video_tree_data.xpath('./div[@class="thumbHidenBlock"]/div[@class="thumbAdditionalInfo"]/'
                                            'div[@class="tai clear"]/div[@class="floatRight"]/i')
            assert len(viewers) == 1

            added_before = video_tree_data.xpath('./div[@class="thumbHidenBlock"]/div[@class="thumbAdditionalInfo"]/'
                                                 'div[@class="tai clear"]/div[@class="floatLeft"]')
            assert len(added_before) == 1

            categories = video_tree_data.xpath('./div[@class="thumbHidenBlock"]/div[@class="thumbAdditionalInfo"]/'
                                               'div[@class="ntlTagsCats"]/span/@data-href')
            additional_data['categories'] = categories if len(categories) > 0 else None

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['data-vid'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=video_tree_data.attrib['data-name'],
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  is_hd=len(is_hd) > 0,
                                                  resolution=is_hd[0].text if len(is_hd) > 0 else '480',
                                                  duration=self._format_duration(video_length[0].text),
                                                  added_before=added_before[0].text,
                                                  number_of_views=viewers[0].tail,
                                                  additional_data=additional_data,
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
            'Accept': '*/*',
            'Cache-Control': 'no-cache',
            'Referer': page_data.url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if true_object.object_type == PornCategories.VIDEO:
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request

        params.update({
            'isAJAX': 1,
            'hd_only': 0,
            # 'browsefilter-hd': 0,
            # 'browsefilter-duration': 'all',
        })
        if page_number is None:
            page_number = 1

        conditions = self.get_proper_filter(page_data).conditions

        # Valid for all object_types
        # if page_filter.sort_order.value is not None:
        #     params['browsefilter-sort'] = page_filter.sort_order.value[1]

        if true_object.object_type in (PornCategories.SEARCH_MAIN, PornCategories.TAG):
            params['page'] = page_number
            params['tab'] = 'videos'
            if page_filter.period.value is not None:
                params['su'] = page_filter.period.value
            if page_filter.sort_order.value:
                params['sb'] = page_filter.sort_order.value
            if page_filter.quality.value is not None:
                # params['browsefilter-hd'] = page_filter.quality.value
                params['hd'] = page_filter.quality.value
            if page_filter.length.value is not None:
                params['sd'] = page_filter.length.value

        elif true_object.object_type in (PornCategories.PORN_STAR, ):
            params['section'] = 'videos'
            params['page'] = page_number
            if page_filter.sort_order.value is not None:
                params['sort'] = page_filter.sort_order.value
            if page_filter.quality.value is not None:
                # params['browsefilter-hd'] = page_filter.quality.value
                params['hd'] = page_filter.quality.value
            if page_filter.length.value is not None:
                params['d'] = page_filter.length.value
                # params['browsefilter-duration'] = page_filter.length.value

        elif true_object.object_type in (PornCategories.PORN_STAR_MAIN, ):
            params['section'] = 'videos'
            params['page'] = page_number
            if page_filter.sort_order.value is not None:
                params['filters[sorting]'] = page_filter.sort_order.value
                params['filter_set'] = True

        elif true_object.object_type in (PornCategories.CATEGORY_MAIN, ):
            # Do nothing
            pass

        elif true_object.object_type in (PornCategories.CATEGORY, ):
            if page_filter.sort_order.value is not None:
                split_url.append(page_filter.sort_order.value)
            if page_filter.quality.value is not None:
                # params['browsefilter-hd'] = page_filter.quality.value
                params['hd'] = page_filter.quality.value
            if page_filter.length.value is not None:
                params['d'] = page_filter.length.value
                # params['browsefilter-duration'] = page_filter.length.value
            split_url.append(str(page_number))

        elif true_object.object_type in (PornCategories.TAG_MAIN, ):
            params['page'] = page_number
            if page_filter.sort_order.value is not None:
                params.update(parse_qs(page_filter.sort_order.value))

        elif true_object.object_type in (PornCategories.CHANNEL_MAIN, PornCategories.CHANNEL):
            if page_filter.sort_order.value is not None:
                if true_object.object_type == PornCategories.CHANNEL:
                    split_url.append('videos')
                else:
                    split_url.append('all')
                split_url.append(page_filter.sort_order.value)
                split_url.append(str(page_number))
            if page_filter.length.value is not None:
                split_url.append(page_filter.length.value)
                # params['browsefilter-duration'] = page_filter.length.value

        else:
            # Videos
            true_sort_filter_id = self._default_sort_by[true_object.object_type] \
                if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id
            if split_url[-1].isdigit():
                split_url.pop()

            if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
                split_url[-1] = page_filter.sort_order.value
            split_url.append(str(page_number))
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['period'] = page_filter.period.value
            if page_filter.quality.value is not None:
                # params['browsefilter-hd'] = page_filter.quality.value
                params['hd'] = page_filter.quality.value
            if page_filter.length.value is not None:
                params['d'] = page_filter.length.value
                # params['browsefilter-duration'] = page_filter.length.value

        program_fetch_url = '/'.join(split_url)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        if not self._check_is_available_page(page_request):
            # We check whether we have redirection for porn star
            if true_object.object_type in (PornCategories.PORN_STAR, ):
                new_fetch_base_url = page_request.url.split('?')[0]
                if new_fetch_base_url != page_data.url:
                    page_data.url = new_fetch_base_url
                    return self.get_object_request(page_data, page_number, params)

        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?what={q}&tab='.format(q=quote(query))


class EmpFlix(TnaFlix):

    # Has the same structure as tnaflix
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        res = super(EmpFlix, self).object_urls
        res.pop(PornCategories.TAG_MAIN)
        res.pop(PornCategories.CHANNEL_MAIN)
        return res

    # @property
    # def object_urls(self):
    #     return {
    #         PornCategories.CATEGORY_MAIN: 'https://www.empflix.com/categories',
    #         # PornCategories.CHANNEL_MAIN: 'https://www.empflix.com/channels',
    #         PornCategories.PORN_STAR_MAIN: 'https://www.empflix.com/pornstars',
    #         PornCategories.TOP_RATED_VIDEO: 'https://www.empflix.com/toprated/',
    #         PornCategories.POPULAR_VIDEO: 'https://www.empflix.com/popular/',
    #         PornCategories.LATEST_VIDEO: 'https://www.empflix.com/new/',
    #         PornCategories.RECOMMENDED_VIDEO: 'https://www.empflix.com/featured/',
    #     }
    #     # return {
    #     #     CategoryMain: 'https://www.empflix.com/categories',
    #     #     # CHANNEL_MAIN: 'https://www.empflix.com/channels',
    #     #     PornStarMain: 'https://www.empflix.com/pornstars',
    #     #     TopRatedVideo: 'https://www.empflix.com/toprated/?d=all&period=all',
    #     #     PopularVideo: 'https://www.empflix.com/popular/?d=all&period=all',
    #     #     LatestVideo: 'https://www.empflix.com/new/?d=all&period=all',
    #     #     RecommendedVideo: 'https://www.empflix.com/featured/?d=all&period=all',
    #     # }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.empflix.com/'

    def __init__(self, source_name='EmpFlix', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(EmpFlix, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)


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

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        request_data = tmp_tree.xpath('.//form[@id="vid_info"]/input')
        request_data = {x.attrib['id']: x.attrib['value'] for x in request_data}
        assert len(request_data) > 0

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
        assert tmp_request.ok
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


if __name__ == '__main__':
    category_id = IdGenerator.make_id('/amateur-porn')
    # module = TnaFlix()
    # module = EmpFlix()
    module = MovieFap()
    # module.get_available_categories()
    # module.download_object(None, category_id, verbose=1)
    module.download_category_input_from_user(use_web_server=True)
