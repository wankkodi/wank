import re
from .... import urljoin, parse_qs, quote

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .upornia import UPornia


class HDZog(UPornia):
    number_of_flip_images = 15

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://hdzog.com/categories/',
            PornCategories.CHANNEL_MAIN: 'https://hdzog.com/channels/',
            PornCategories.PORN_STAR_MAIN: 'https://hdzog.com/models/',
            PornCategories.LONGEST_VIDEO: 'https://hdzog.com/longest/',
            PornCategories.LATEST_VIDEO: 'https://hdzog.com/new/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://hdzog.com/popular/',
            PornCategories.SEARCH_MAIN: 'https://hdzog.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://hdzog.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        _, video_filters, search_filter, categories_filters, porn_stars_filters, channels_filters = \
            self._prepare_filters()

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=categories_filters,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filter,
                                         )

    def _prepare_filters(self):
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Latest', 'sortby=post_date'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'sortby=video_viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'sortby=rating'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'sortby=duration'),
                                        (PornFilterTypes.CommentsOrder, 'Most Commented', 'sortby=most_commented'),
                                        (PornFilterTypes.FavorOrder, 'Most Favorite', 'sortby=most_favourited'),
                                        ),
                         'period_filters': (((PornFilterTypes.AllDate, 'All time', None),
                                             (PornFilterTypes.TwoDate, 'Week', 'week'),
                                             (PornFilterTypes.OneDate, 'Month', 'month'),
                                             (PornFilterTypes.ThreeDate, 'Today', 'day'),
                                             ),
                                            (('sort_order', [PornFilterTypes.ViewsOrder,
                                                             PornFilterTypes.RatingOrder]),
                                             ),
                                            ),
                         'length_filters': ((PornFilterTypes.AllLength, 'Any duration', None),
                                            (PornFilterTypes.OneLength, '0-8 min', 'duration_from=&duration_to=480'),
                                            (PornFilterTypes.TwoLength, '10-40 min.',
                                             'duration_from=481&duration_to=1200'),
                                            (PornFilterTypes.ThreeLength, '40+ min.',
                                             'duration_from=1200&duration_to=1201'),
                                            ),
                         }
        categories_filters = \
            {'sort_order': ((PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sortby=title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Video Count', 'sortby=total_videos'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'sortby=avg_videos_rating'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'sortby=avg_videos_popularity'),
                            ),
             }
        porn_stars_filters = \
            {'sort_order': ((PornFilterTypes.RatingOrder, 'Model Rating', 'sortby=rating'),
                            (PornFilterTypes.ViewsOrder, 'Model Viewed', 'sortby=model_viewed'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Total Videos', 'sortby=total_videos'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sortby=title'),
                            (PornFilterTypes.DateOrder, 'Date Added', 'sortby=added_date'),
                            (PornFilterTypes.CommentsOrder, 'Most Comments', 'sortby=comments_count'),
                            (PornFilterTypes.SubscribersOrder, 'Most Subscribers', 'sortby=subscribers_count'),
                            ),
             }
        channels_filters = \
            {'sort_order': ((PornFilterTypes.VideosRatingOrder, 'Top Rated', 'sortby=avg_videos_rating'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Video Count', 'sortby=total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'sortby=avg_videos_popularity'),
                            (PornFilterTypes.ChannelViewsOrder, 'Recently Updated', 'sortby=cs_viewed'),
                            (PornFilterTypes.DateOrder, 'Recently Updated', 'sortby=last_content_date'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sortby=title'),
                            ),
             }
        return None, video_filters, video_filters, categories_filters, porn_stars_filters, channels_filters

    def __init__(self, source_name='HDZog', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HDZog, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                    session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, './/div[@class="thumbs-categories"]/ul/li/a',
                                                  PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channels.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(channel_data, './/div[@class="thumbs-channels"]/ul/li/a',
                                                  PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data, './/div[@class="thumbs-models"]/ul/li/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_base_object(self, object_data, xpath, object_type):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="thumb"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="thumb"]/span[@class="videos-count"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            country = category.xpath('./div[@class="thumb"]/span[@class="country"]/i')
            additional_info = {'country': re.findall(r'(?:flag-)(\w*$)',
                                                     country[0].attrib['class'])[0]} if len(country) == 1 else None

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               additional_data=additional_info,
                                               object_type=object_type,
                                               super_object=object_data,
                                               ))

        object_data.add_sub_objects(res)
        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        return max(pages) if len(pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(self._clear_text(x.text)) for x in tree.xpath('.//div[@class="pagination"]/ul/li/*')
                if x.text is not None and self._clear_text(x.text).isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        if (
                page_data.page_number is not None and page_data.page_number != 1 and
                page_data.super_object.object_type in (PornCategories.PORN_STAR, PornCategories.CHANNEL,)
        ):
            tree = self.parser.parse(tree.xpath('.//script[2]')[0].text)

        video_preview_url = dict(
            re.findall(r'(?:\[)(\d+)(?:\])(?:.*?)(https://cdn\d+.ahacdn.me/c\d+/videos)', page_request.text))
        videos = tree.xpath('.//div[@class="thumbs-videos"]/ul/li/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./div[@class="thumb thumb-paged"]/img')
            assert len(image_data) == 1
            video_id = image_data[0].attrib['data-video-id']
            image = image_data[0].attrib['src']
            flix_image = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                          for d in range(1, self.number_of_flip_images + 1)]
            video_source = image_data[0].attrib['data-sgid'].split(':')[-1]
            preview_link = (video_preview_url[video_source] +
                            '/{vid_prefix}/{vid}/{vid}_tr.mp4'
                            ''.format(vid_prefix=video_id[:-3]+'000', vid=video_id)) \
                if video_source in video_preview_url else None
            additional_info = {'video_id': video_id}

            video_length = video_tree_data.xpath('./div[@class="thumb thumb-paged"]/span[@class="time"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            rating = video_tree_data.xpath('./div[@class="thumb thumb-paged"]/span[@class="rating rating-gray"]')
            rating = rating[0].text if len(rating) == 1 else None

            added_before = video_tree_data.xpath('./div[@class="thumb-data"]/span[@class="added"]')
            assert len(added_before) == 1
            added_before = added_before[0].text

            title = video_tree_data.xpath('./div[@class="thumb-data"]/span[@class="title"]')
            assert len(title) == 1
            title = title[0].text if title[0].text is not None else ''

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  preview_video_link=preview_link,
                                                  additional_data=additional_info,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  added_before=added_before,
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
        if true_object.object_type == PornCategories.VIDEO:
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request

        if page_number is not None and page_number != 1:
            if true_object.object_type in (PornCategories.PORN_STAR, PornCategories.CHANNEL,):
                params['mode'] = 'async'
                params['mode2'] = 'najax'
                params['action'] = 'get_block'
                params['from'] = page_number
                if page_data.super_object.object_type == PornCategories.PORN_STAR:
                    params['block_id'] = 'list_videos_model_videos'
                elif page_data.super_object.object_type == PornCategories.CHANNEL:
                    params['block_id'] = 'list_videos_channel_videos'
                return self.session.get(fetch_base_url, headers=headers, params=params)

            else:
                if split_url[-2].isdigit():
                    split_url.pop(-2)
                split_url.insert(-1, str(page_number))

        conditions = self.get_proper_filter(page_data).conditions
        sort_filter_type = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id
        params.update(parse_qs(self.get_proper_filter(page_data).filters.sort_order[sort_filter_type].value))

        if page_filter.period.value is not None and sort_filter_type in conditions.period.sort_order:
            params['sortby'][0] += ('_' + page_filter.period.value)
        if page_filter.length.value is not None:
            params.update(parse_qs(page_filter.length.value))

        program_fetch_url = '/'.join(split_url)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote(query))
