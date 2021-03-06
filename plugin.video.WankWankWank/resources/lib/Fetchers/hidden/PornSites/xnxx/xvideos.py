import json
import re
from .... import urljoin, quote_plus

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogPageNode, PornCatalogVideoPageNode

from .xnxx import Xnxx
from ....id_generator import IdGenerator


class XVideos(Xnxx):
    # Very similar to xvideos!
    max_flip_images = 30
    best_videos_url = 'https://www.xvideos.com/best'

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.xvideos.com/',
            PornCategories.TAG_MAIN: 'https://www.xvideos.com/tags',
            PornCategories.PORN_STAR_MAIN: 'https://www.xvideos.com/pornstars-index',
            PornCategories.CHANNEL_MAIN: 'https://www.xvideos.com/channels-index',
            PornCategories.TOP_RATED_VIDEO: self.best_videos_url,
            PornCategories.VERIFIED_VIDEO: 'https://www.xvideos.com/verified/videos',
            PornCategories.SEARCH_MAIN: 'https://www.xvideos.com/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.xvideos.com/'

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 5000

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filters = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', None),
                                               (PornFilterTypes.GayType, 'Gay', 'gay'),
                                               (PornFilterTypes.ShemaleType, 'Shemale', 'shemale'),
                                               ],
                           }
        channels_filters = \
            {'sort_order': ((PornFilterTypes.BeingWatchedOrder, 'Watched Recently', None),
                            (PornFilterTypes.RatingOrder, 'Top Rankings', 'top'),
                            (PornFilterTypes.DateOrder, 'New', 'new'),
                            ),
             }
        porn_stars_filters = \
            {'period_filters': ((PornFilterTypes.AllDate, 'All period', 'ever'),
                                (PornFilterTypes.OneDate, '1 Year', None),
                                (PornFilterTypes.TwoDate, '3 Month', '3months'),
                                (PornFilterTypes.ThreeDate, 'New', 'new'),
                                ),
             }
        search_filters = \
            {'sort_order': ((PornFilterTypes.RelevanceOrder, 'Relevance', 'relevance'),
                            (PornFilterTypes.DateOrder, 'Upload Date', 'uploaddate'),
                            (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                            (PornFilterTypes.LengthOrder, 'Length', 'length'),
                            (PornFilterTypes.ViewsOrder, 'Views', 'views'),
                            ),
             'period_filters': ((PornFilterTypes.AllDate, 'Any period', 'all'),
                                (PornFilterTypes.OneDate, 'Last 6 month', '6month'),
                                (PornFilterTypes.TwoDate, 'Last 3 month', '3month'),
                                (PornFilterTypes.ThreeDate, 'This Month', 'month'),
                                (PornFilterTypes.FourDate, 'This Week', 'week'),
                                (PornFilterTypes.FiveDate, 'Last 3 Days', 'today'),
                                ),
             'length_filters': ((PornFilterTypes.AllLength, 'Any duration', 'allduration'),
                                (PornFilterTypes.OneLength, '1-3 min', '1-3min'),
                                (PornFilterTypes.TwoLength, '3-10 min', '3-10min'),
                                (PornFilterTypes.ThreeLength, '10-20 min', '10-20min'),
                                (PornFilterTypes.FourLength, '20+ min', '20min_more'),
                                ),
             'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', 'all'),
                                 (PornFilterTypes.HDQuality, '720P+ quality', 'hd'),
                                 ),
             }
        single_tag_filters = \
            {'sort_order': search_filters['sort_order'],
             'period_filters': search_filters['period_filters'],
             'length_filters': search_filters['length_filters'],
             }
        single_category_filters = single_tag_filters
        # single_category_filters = \
        #     {'period_filters': ((PornFilterTypes.AllDate, 'All period', None),
        #                         (PornFilterTypes.OneDate, 'This Month', 'month'),
        #                         (PornFilterTypes.TwoDate, 'This Week', 'week'),
        #                         (PornFilterTypes.ThreeDate, 'Yesterday', 'yesterday'),
        #                         (PornFilterTypes.FiveDate, 'Today', 'day'),
        #                         ),
        #      }
        single_porn_star_filters = \
            {'sort_order': ((PornFilterTypes.BeingWatchedOrder, 'Watched Recently', 'best'),
                            (PornFilterTypes.DateOrder, 'New', 'new'),
                            (PornFilterTypes.ViewsOrder, 'Most Viewed', 'rating'),
                            (PornFilterTypes.CommentsOrder, 'Most Commented', 'comments'),
                            ),
             }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filters,
                                         channels_args=channels_filters,
                                         porn_stars_args=porn_stars_filters,
                                         single_category_args=single_category_filters,
                                         single_porn_star_args=single_porn_star_filters,
                                         single_channel_args=single_porn_star_filters,
                                         single_tag_args=single_tag_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='XVideos', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(XVideos, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available tags.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//li[@class="sub-list mobile-hide"]/ul/li/a')
        assert len(categories) >= 1
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x.attrib['href'],
                                       url=urljoin(category_data.url, x.attrib['href']),
                                       title=x.text,
                                       object_type=PornCategories.CATEGORY,
                                       super_object=category_data,
                                       ) for x in categories if x.attrib['href'].split('/')[1] == 'c']
        category_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        links = tree.xpath('.//ul[@class="tags-list"]/li/a/@href')
        titles = [x.replace('-', ' ').title()
                  for x in tree.xpath('.//ul[@class="tags-list"]/li/a/b/text()')]
        number_of_videos = [int(re.sub(',', '', x.text))
                            for x in tree.xpath('.//ul[@class="tags-list"]/li/a/span')]

        assert len(links) == len(titles)
        assert len(links) == len(number_of_videos)

        return links, titles, number_of_videos

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
        new_pages = [PornCatalogPageNode(catalog_manager=self.catalog_manager,
                                         obj_id=(IdGenerator.id_to_original_str(tag_data.id), chr(k)),
                                         title='{c} | Letter {p}'.format(c=tag_data.title, p=chr(k).title()),
                                         url=tag_data.url + '/' + (chr(k) if chr(k) != '#' else '09'),
                                         raw_data=tag_data.raw_data,
                                         additional_data={'letter': chr(k)},
                                         object_type=sub_object_type,
                                         super_object=tag_data,
                                         )
                     for k in ((ord('#'), ) + tuple(range(ord('a'), ord('z')+1)))]
        tag_data.add_sub_objects(new_pages)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = tree.xpath('.//div[@class="thumb-block thumb-block-profile "]')
        res = []
        for porn_star in porn_stars:
            link_data = porn_star.xpath('./div[@class="thumb-inside"]/div[@class="thumb"]/a')
            assert len(link_data) >= 1

            image_data = porn_star.xpath('./div[@class="thumb-inside"]/div[@class="thumb"]/a/script')
            assert len(image_data) == 1
            raw_image_data = re.findall(r'<.*?>', image_data[0].text)
            tmp_tree = self.parser.parse(raw_image_data[0])
            image_data = tmp_tree.xpath('.//img')
            image = image_data[0].attrib['src']
            additional_data = {'images': json.loads(image_data[0].attrib['data-videos'][2:-2])}

            is_verified = porn_star.xpath('./div[@class="thumb-inside"]/div[@class="thumb"]/'
                                          'a[@class="prof-verified-tick"]')
            additional_data['is_verified'] = len(is_verified) > 0

            country = porn_star.xpath('./div[@class="thumb-inside"]/span')
            additional_data['country'] = country[0].attrib['title'] if len(country) == 1 else None

            ranking = porn_star.xpath('./div[@class="thumb-under"]/p[@class="profile-name"]/strong/text()')
            ranking = ranking[0] if len(ranking) == 1 else None
            title = porn_star.xpath('./div[@class="thumb-under"]/p[@class="profile-name"]/a/text()')
            assert len(title) == 1
            additional_data['ranking'] = ranking

            count_data = porn_star.xpath('./div[@class="thumb-under"]/p[@class="profile-counts"]/span')
            assert len(count_data) == 1
            number_of_videos = re.findall(r'([\d,]+?)(?: *video)', count_data[0].text)[0]
            number_of_videos = re.sub(r',', '', number_of_videos)
            number_of_videos = int(number_of_videos)

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(porn_star_data.url, link_data[0].attrib['href']),
                                                  image_link=image,
                                                  title=title[0],
                                                  additional_data=additional_data,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.PORN_STAR,
                                                  super_object=porn_star_data,
                                                  )
            res.append(object_data)

        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        channels = tree.xpath('.//div[@class="thumb-block thumb-block-profile "]')
        res = []
        for channel in channels:
            link_data = channel.xpath('./div[@class="thumb-inside"]/div[@class="thumb"]/a')
            assert len(link_data) >= 1

            image_data = channel.xpath('./div[@class="thumb-inside"]/div[@class="thumb"]/a/script')
            assert len(image_data) == 1
            raw_image_data = re.findall(r'<.*?>', image_data[0].text)
            tmp_tree = self.parser.parse(raw_image_data[0])
            image_data = tmp_tree.xpath('.//img')
            image = image_data[0].attrib['src']
            additional_data = {'images': json.loads(image_data[0].attrib['data-videos'][2:-2])}

            is_verified = channel.xpath('./div[@class="thumb-inside"]/div[@class="thumb"]/'
                                        'a[@class="prof-verified-tick"]')
            additional_data['is_verified'] = len(is_verified) > 0

            title = channel.xpath('./div[@class="thumb-under"]/p[@class="profile-name"]/a/text()')

            count_data = channel.xpath('./div[@class="thumb-under"]/p[@class="profile-counts"]/'
                                       'span[@class="with-sub"]')
            assert len(count_data) == 1
            number_of_videos = re.findall(r'([\d,]+?)(?: *video)', count_data[0].text)[0]
            number_of_videos = re.sub(r',', '', number_of_videos)
            number_of_videos = int(number_of_videos)

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(channel_data.url, link_data[0].attrib['href']),
                                                  image_link=image,
                                                  title=title[0],
                                                  additional_data=additional_data,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.CHANNEL,
                                                  super_object=channel_data,
                                                  )
            res.append(object_data)

        channel_data.add_sub_objects(res)
        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.true_object.object_type in (PornCategories.TAG_MAIN, PornCategories.CATEGORY_MAIN):
            return 1
        # elif category_data.object_type in (PornCategories.CHANNEL, ):
        #     # We try to fetch all the possible activity pages
        #     activities = self.data_server.fetch_additional_data(category_data.url)
        #     if activities['status'] is False:
        #         activities = json.loads(activities['value'])
        #     else:
        #         activities = self._fetch_activity_pages(category_data)
        #     return len(activities) + 1, activities
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        our_page = category_data.page_number if category_data.page_number is not None else 1
        if len(pages) == 0:
            return 1
        if (max(pages) - our_page) < self._binary_search_page_threshold:
            return max(pages)
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _add_category_sub_pages(self, category_data, sub_object_type, page_request=None, clear_sub_elements=True):
        """
        Adds category sub pages.
        :param category_data: Category data object (PornCatalogCategoryNode).
        :param sub_object_type: Sub object type.
        :param page_request: Page request if such exist. In case it doesn't exist we fetch the object's url.
        :param clear_sub_elements: Flag that indicates whether we clear previous sub elements.
        :return:
        """
        # if category_data.object_type == PornCategories.CHANNEL:
        #     category_data.clear_sub_objects()
        #     if self._use_web_server is True:
        #         fetch_result = self.data_server.fetch_request(category_data.url)
        #
        #         if fetch_result['status'] is True:
        #             num_of_pages = fetch_result['value']['num_of_pages']
        #             activities = fetch_result['value']['activities']
        #         else:
        #             activities = self._fetch_activity_pages(category_data)
        #             num_of_pages = len(activities) + 1
        #             push_data = {'num_of_pages': num_of_pages, 'activities': activities}
        #             push_result = self.data_server.push_request(category_data.url, push_data)
        #             if push_result['status'] is False:
        #                 warnings.warn(push_result['err'])
        #     else:
        #         activities = self._fetch_activity_pages(category_data)
        #         num_of_pages = len(activities) + 1
        #
        #     new_pages = [PornCatalogPageNode(catalog_manager=self.catalog_manager,
        #                                      obj_id=(IdGenerator.id_to_original_str(category_data.id), i),
        #                                      title='{c} | Page {p}'.format(c=category_data.title, p=i),
        #                                      url=(category_data.url + '/activity' +
        #                                           ('/{p}'.format(p=activities[i-2] if i > 1 else ''))),
        #                                      page_number=i,
        #                                      raw_data=category_data.raw_data,
        #                                      additional_data=category_data.additional_data,
        #                                      object_type=sub_object_type,
        #                                      super_object=category_data,
        #                                      )
        #                  for i in range(1, num_of_pages + 1)]
        #     category_data.add_sub_objects(new_pages)
        #     return new_pages
        # elif category_data.object_type == PornCategories.TAG_MAIN:
        if category_data.object_type == PornCategories.TAG_MAIN:
            if clear_sub_elements is True:
                category_data.clear_sub_objects()
            return self._add_tag_sub_pages(category_data, sub_object_type)
        else:
            return super(Xnxx, self)._add_category_sub_pages(category_data, sub_object_type, page_request,
                                                             clear_sub_elements)

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 6

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = [x for x in tree.xpath('.//div') if 'data-id' in x.attrib]
        if len(videos) == 0:
            # todo: to implement fetch activity
            # We try to fetch the activity data from the server, or at worst case to push it there once again
            pass
        res = []
        for video_tree_data in videos:
            additional_data = {
                'id': video_tree_data.attrib['id']
                if 'id' in video_tree_data.attrib else 'video_{vid}'.format(vid=video_tree_data.attrib['data-id']),
                'data_id': video_tree_data.attrib['data-id'],
            }
            link_data = (video_tree_data.xpath('.//div[@class="thumb-inside"]/div[@class="thumb"]') +
                         video_tree_data.xpath('.//div[@class="thumb-inside"]/div[@class="thumb verified-pic"]'))
            assert len(link_data) == 1
            link = link_data[0].xpath('./a/@href')
            assert len(link) == 1

            # The logic was taken from xnxx
            image_data = link_data[0].xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'lightbox' in image:
                image = image_data[0].attrib['data-src']
            if 'THUMBNUM' in image:
                image = re.sub('THUMBNUM', '1', image)
            flip_images = [re.sub(r'\d+\.jpg', '{i}.jpg'.format(i=i), image)
                           for i in range(1, self.max_flip_images + 1)]
            video_preview_id_suffix = re.findall(r'(?:thumbs)(\d+)(?:.*ll)', image)
            video_preview_id = re.findall(r'(\w+)(?:\.\d+\.jpg)', image)
            video_preview = re.sub(r'thumbs\d+.*ll', 'videopreview', image)
            video_preview = re.sub(r'/{id}\.\d+\.jpg'.format(id=video_preview_id[0]),
                                   '_{i}.mp4'.format(i=video_preview_id_suffix[0]), video_preview)

            resolution = (video_tree_data.xpath('.//div[@class="thumb-inside"]//span[@class="video-sd-mark"]/text()') +
                          video_tree_data.xpath('.//div[@class="thumb-inside"]//span[@class="video-hd-mark"]/text()'))
            resolution = resolution[0] if len(resolution) > 0 else ''
            is_hd = resolution in ('720p', '1080p')

            title = video_tree_data.xpath('.//div[@class="thumb-under"]/p[@class="title"]/a')
            assert len(title) == 1
            title = title[0].attrib['title']

            video_length = video_tree_data.xpath('.//div[@class="thumb-under"]//p[@class="metadata"]/'
                                                 'span[@class="bg"]/span[@class="duration"]/text()')
            assert len(video_length) == 1

            video_category = video_tree_data.xpath('.//div[@class="thumb-under"]//p[@class="metadata"]/'
                                                   'span[@class="bg"]/a')
            if len(video_category) > 0:
                additional_data['uploader'] = {'name': (video_category[0].xpath('./span[@class="name"]/text()')[0]
                                                        if len(video_category[0].xpath('./span[@class="name"]/'
                                                                                       'text()')) > 0 else ''),
                                               'url': (video_category[0].attrib['href']
                                                       if 'href' in video_category[0].attrib else '')} \

            number_of_viewers = (video_tree_data.xpath('.//div[@class="thumb-under"]//p[@class="metadata"]/'
                                                       'span[@class="bg"]/span/span[@class="sprfluous"]') +
                                 video_tree_data.xpath('.//div[@class="thumb-under"]//p[@class="metadata"]/'
                                                       'span[@class="bg"]/span[@class="duration"]'))
            assert len(number_of_viewers) >= 1
            number_of_viewers = self._clear_text(number_of_viewers[0].tail) \
                if number_of_viewers[0].tail is not None else None

            res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                obj_id=additional_data['id'],
                                                url=urljoin(self.base_url, link[0]),
                                                title=title,
                                                image_link=image,
                                                flip_images_link=flip_images,
                                                preview_video_link=video_preview,
                                                is_hd=is_hd,
                                                resolution=resolution,
                                                duration=self._format_duration(video_length[0]),
                                                number_of_views=number_of_viewers,
                                                additional_data=additional_data,
                                                object_type=PornCategories.VIDEO,
                                                super_object=page_data,
                                                ))
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        split_url = fetch_base_url.split('/')
        if (
                split_url[-1].isdigit() and
                true_object.object_type not in (PornCategories.CHANNEL, PornCategories.TAG_MAIN, PornCategories.TAG)
        ):
            split_url.pop()
        elif true_object.object_type in (PornCategories.TAG, ) and split_url[-1].isdigit() and split_url[-2].isdigit():
            split_url.pop()
        if true_object.object_type in (PornCategories.PORN_STAR, PornCategories.CHANNEL):
            headers = {
                'Accept': 'text/html, */*; q=0.01',
                'Cache-Control': 'max-age=0',
                # 'Referer': self.base_url,
                # 'Host': self.host_name,
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
            method = 'post'
        else:
            headers = {
                'Accept': 'text/html, */*; q=0.01',
                'Cache-Control': 'max-age=0',
                # 'Referer': self.base_url,
                # 'Host': self.host_name,
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
            method = 'get'

        if true_object.object_type in (PornCategories.PORN_STAR, PornCategories.CHANNEL):
            if page_number is None:
                page_number = 1
            split_url.append('videos')
            split_url.append(page_filter.sort_order.value)
            split_url.append(str(page_number - 1))
        elif true_object.object_type in (PornCategories.PORN_STAR_MAIN, PornCategories.CHANNEL_MAIN,):
            if self.general_filter.current_filters.general.value is not None:
                if true_object.object_type == PornCategories.CHANNEL_MAIN:
                    split_url[3] = split_url[3].replace('index', self.general_filter.current_filters.general.value)
                elif true_object.object_type == PornCategories.PORN_STAR_MAIN:
                    split_url.append(self.general_filter.current_filters.general.value)
            if page_filter.sort_order.value is not None:
                split_url.append(page_filter.sort_order.value)
            if page_filter.period.value is not None:
                split_url.append(page_filter.period.value)
            if page_number is None:
                page_number = 1
            split_url.append(str(page_number - 1))
        elif true_object.object_type == PornCategories.CATEGORY_MAIN:
            if self.general_filter.current_filters.general.value is not None:
                split_url.append(self.general_filter.current_filters.general.value)
        # elif true_object.object_type == PornCategories.CATEGORY:
        #     if page_filter.period.value is not None:
        #         split_url.insert(-1, page_filter.period.value)
        #     if page_number is not None and page_number != 1:
        #         split_url.insert(-1, str(page_number - 1))
        elif true_object.object_type in (PornCategories.SEARCH_MAIN, ):
            if self.general_filter.current_filters.general.value is not None:
                params['typef'] = self.general_filter.current_filters.general.value
            if page_filter.sort_order.value is not None:
                params['sort'] = page_filter.sort_order.value
            if page_filter.period.value is not None:
                params['datef'] = page_filter.period.value
            if page_filter.length.value is not None:
                params['durf'] = page_filter.length.value
            if page_filter.quality.value is not None:
                params['quality'] = page_filter.quality.value
            if page_number is not None and page_number != 1:
                params['p'] = page_number
        elif true_object.object_type in (PornCategories.TAG, PornCategories.CATEGORY):
            if page_filter.sort_order.value is not None:
                split_url.insert(-1, 's:' + page_filter.sort_order.value)
            if page_filter.period.value is not None:
                split_url.insert(-1, 'm:' + page_filter.period.value)
            if page_filter.length.value is not None:
                split_url.insert(-1, 'd:' + page_filter.length.value)
            if page_number is not None and page_number != 1:
                split_url.append(str(page_number - 1))
        elif true_object.object_type == PornCategories.TOP_RATED_VIDEO:
            if len(split_url) == 4:
                tmp_request = self.session.get(fetch_base_url, headers=headers)
                tmp_tree = self.parser.parse(tmp_request.text)
                available_dates = tmp_tree.xpath('.//div[@id="date-links-pagination"]/ul/li/a')
                self.best_videos_url = urljoin(self.base_url, available_dates[0].attrib['href'])
                split_url = self.object_urls[PornCategories.TOP_RATED_VIDEO].split('/')
            if self.general_filter.current_filters.general.value is not None:
                split_url[-1] += '-of-{s}'.format(s=self.general_filter.current_filters.general.value)

            if page_number is not None and page_number != 1:
                split_url.append(str(page_number - 1))
        else:
            if page_number is not None and page_number != 1:
                split_url.append(str(page_number - 1))

        program_fetch_url = '/'.join(split_url)
        if method == 'get':
            page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        else:
            page_request = self.session.post(program_fetch_url, headers=headers)
        return page_request

    def _get_page_activity_request(self, page_data, event_id=None):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :param event_id: Activity event id.
        :return: Page request
        """
        headers = {
            'Accept': 'text/html, */*; q=0.01',
            'Cache-Control': 'max-age=0',
            # 'Referer': self.base_url,
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        program_fetch_url = page_data.url + '/activity'
        if event_id is not None:
            program_fetch_url += '/{a}'.format(a=event_id)
        page_request = self.session.get(program_fetch_url, headers=headers)
        return page_request

    def _fetch_activity_pages(self, channel_data):
        """
        Fetches page activities until we reach the end...
        """
        activities = []
        prev_res_activities = []
        last_activity = None
        while 1:
            page_request = self._get_page_activity_request(channel_data, last_activity)
            tree = self.parser.parse(page_request.text)
            # videos = [x for x in tree.xpath('.//div') if 'data-id' in x.attrib]
            current_activities = [re.findall(r'\d+', x)[0] for x in tree.xpath('.//div[@class="activity-event"]/@id')]
            if all(x in prev_res_activities for x in current_activities):
                # We have all the activities fetched
                return activities
            else:
                # Here we continue fetching activities
                last_activity = current_activities[-1]
                activities.append(last_activity)
                prev_res_activities = current_activities

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?k={q}'.format(q=quote_plus(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(XVideos, self)._version_stack + [self.__version]
