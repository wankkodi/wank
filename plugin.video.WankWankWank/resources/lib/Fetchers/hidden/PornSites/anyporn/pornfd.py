import re
import time
from .... import urljoin, parse_qsl

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .anyporn import AnyPorn
from .pervertsluts import PervertSluts


class PornFd(PervertSluts):
    # Some of the models we took from AnyPorn module (has thee same structure)
    flip_number = 15

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.pornfd.com/'

    def _prepare_filters(self):
        """
        Prepares the filters
        :return:
        """
        video_sort_order = [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                            (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                            (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                            (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                            (PornFilterTypes.FavorOrder, 'Most Favorite', 'most_favourited'),
                            ]
        search_sort_order = [(PornFilterTypes.RelevanceOrder, 'Most Relevant', '')] + video_sort_order
        video_period = ([(PornFilterTypes.AllDate, 'All time', ''),
                         (PornFilterTypes.OneDate, 'This Month', '_month'),
                         (PornFilterTypes.TwoDate, 'This week', '_week'),
                         (PornFilterTypes.ThreeDate, 'Today', '_today'),
                         ],
                        [('sort_order', [PornFilterTypes.RatingOrder,
                                         PornFilterTypes.ViewsOrder])]
                        )
        category_params = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            ],
             }
        porn_stars_params = \
            {'sort_order': [(PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            ],
             }
        actress_params = None
        channel_params = porn_stars_params
        tag_params = None
        video_params = {'sort_order': video_sort_order,
                        'period_filters': video_period,
                        }
        search_params = {'sort_order': search_sort_order,
                         'period_filters': video_period,
                         }

        return (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
                search_params)

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
         search_params) = self._prepare_filters()
        self._video_filters = \
            PornFilter(data_dir=self.fetcher_data_dir,
                       categories_args=category_params if PornCategories.CATEGORY_MAIN in self.object_urls else None,
                       channels_args=channel_params if PornCategories.CHANNEL_MAIN in self.object_urls else None,
                       porn_stars_args=porn_stars_params
                       if PornCategories.PORN_STAR_MAIN in self.object_urls else None,
                       actresses_args=actress_params if PornCategories.ACTRESS_MAIN in self.object_urls else None,
                       single_category_args=video_params if PornCategories.CATEGORY_MAIN in self.object_urls else None,
                       single_channel_args=video_params if PornCategories.CHANNEL_MAIN in self.object_urls else None,
                       single_porn_star_args=video_params
                       if PornCategories.PORN_STAR_MAIN in self.object_urls else None,
                       single_tag_args=video_params if PornCategories.TAG_MAIN in self.object_urls else None,
                       video_args=video_params,
                       search_args=search_params,
                       )

    def __init__(self, source_name='PornFd', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornFd, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="list-categories"]/div[@class="margin-fix"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="list-channels"]/div[@class="margin-fix"]/div/a',
                                                  PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@class="list-models"]/div[@class="margin-fix"]/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_actresses(self, actress_data):
        return self._update_available_base_object(actress_data,
                                                  './/div[@class="list-models"]/div[@class="margin-fix"]/a',
                                                  PornCategories.ACTRESS)

    def _update_available_base_object(self, object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('div[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None
            title = category.attrib['title'].title() \
                if 'title' in category.attrib else image_data[0].attrib['alt'].title()

            number_of_videos = category.xpath('./div[@class="wrap"]/div[@class="videos"]')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].text)[0]) if len(number_of_videos) > 0 else None

            rating = (category.xpath('./div[@class="wrap"]/div[@class="rating positive"]') +
                      category.xpath('./div[@class="wrap"]/div[@class="rating negative"]'))
            assert len(rating) == 1
            rating = self._clear_text(rating[0].text)

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      rating=rating,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        if is_sort:
            res.sort(key=lambda x: x.title)
        object_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//div[@class="list-tags"]/div[@class="margin-fix"]/ul/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, None)
                                                for x in raw_data])
        return links, titles, number_of_videos

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        return self._get_video_links_from_video_data2(video_data)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        elif max(pages) - 1 < self._binary_search_page_threshold:
            return max(pages)
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

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
        # Took from AnyPorn module with somme modifications...
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = (tree.xpath('.//div[@class="list-videos"]/div[@class="margin-fix"]/div[@class="item  "]') +
                  tree.xpath('.//div[@class="list-videos"]/div[@class="margin-fix"]/div[@class="item private "]')
                  )
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title'] if 'title' in link_data[0].attrib else None

            image_data = link_data[0].xpath('./div[@class="img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, self.flip_number + 1)]
            if title is None:
                title = image_data[0].attrib['alt']
            preview = image_data[0].attrib['data-preview'] if 'data-preview' in image_data[0].attrib else None

            is_hd = link_data[0].xpath('./div[@class="img"]/span[@class="is-hd"]')
            is_hd = len(is_hd) > 0 and is_hd[0] == 'HD'

            if title is None:
                title = self._clear_text(link_data[0].xpath('./span[@class="title"]')[0].text)

            data_info = link_data[0].xpath('./div[@class="wrap"]')
            assert len(data_info) == 2

            video_length = data_info[0].xpath('./div[@class="duration"]')
            assert len(video_length) == 1
            video_length = self._format_duration(self._clear_text(video_length[0].text))

            rating = (data_info[0].xpath('./div[@class="rating positive"]') +
                      data_info[0].xpath('./div[@class="rating negative"]') +
                      data_info[0].xpath('./div[@class="rating positive}"]') +
                      data_info[0].xpath('./div[@class="rating negative}"]')
                      )
            assert len(rating) == 1
            rating = self._clear_text(rating[0].text)

            added_before = data_info[1].xpath('./div[@class="added"]/*')[0].text
            number_of_views = int(''.join(re.findall(r'\d+', data_info[1].xpath('./div[@class="views"]')[0].text)))

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=preview,
                                                  is_hd=is_hd,
                                                  duration=video_length,
                                                  rating=rating,
                                                  number_of_views=number_of_views,
                                                  added_before=added_before,
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
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        if page_number is None:
            page_number = 1
        params.update({
            'mode': 'async',
            'function': 'get_block',
        })
        if page_filter.length.value is not None:
            params.update(parse_qsl(page_filter.length.value))
        if page_number > 1:
            params['from'] = str(page_number).zfill(2)

        if true_object.object_type == PornCategories.SEARCH_MAIN:
            params['block_id'] = 'list_videos_videos_list_search_result'
            params['q'] = self._search_query
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            if 'from' in params:
                params.pop('from')
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

        elif true_object.object_type == PornCategories.CHANNEL_MAIN:
            params['block_id'] = 'list_dvds_channels_list'
            params['sort_by'] = page_filter.sort_order.value
        else:
            return super(PornFd, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                               page_filter, fetch_base_url)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        max_number_of_retries = 5
        number_of_retries = 0
        while number_of_retries < max_number_of_retries:
            if len(page_request.text) == 0:
                # We have some sort of empty page
                time.sleep(1)
                page_request = self.session.get(fetch_base_url, headers=headers, params=params)
                number_of_retries += 1
            else:
                break
        if len(page_request.text) == 0:
            raise ValueError('Got empty page for url {u}'.format(u=page_request.url))
        return page_request

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw number, i.e. '7m:58s'.
        :return:
        """
        return super(AnyPorn, self)._format_duration(raw_duration)

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return super(PervertSluts, self)._prepare_new_search_query(query)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(PornFd, self)._version_stack + [self.__version]
