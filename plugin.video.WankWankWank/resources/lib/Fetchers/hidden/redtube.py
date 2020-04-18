# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError

# Internet tools
from .. import urljoin, quote_plus

# Regex
import re

# JSON
import json

# Generator id
from ..id_generator import IdGenerator

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


class RedTube(PornFetcher):
    # todo: add trending option according to a country...
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.redtube.com/categories',
            PornCategories.TAG_MAIN: 'https://www.redtube.com/tag',
            PornCategories.CHANNEL_MAIN: 'https://www.redtube.com/channel',
            PornCategories.PORN_STAR_MAIN: 'https://www.redtube.com/pornstar',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.redtube.com/mostviewed',
            PornCategories.TOP_RATED_VIDEO: 'https://www.redtube.com/top',
            PornCategories.LATEST_VIDEO: 'https://www.redtube.com/newest',
            PornCategories.LONGEST_VIDEO: 'https://www.redtube.com/longest',
            PornCategories.FAVORITE_VIDEO: 'https://www.redtube.com/mostfavored',
            PornCategories.TRENDING_VIDEO: 'https://www.redtube.com/hot',
            # PornCategories.RECOMMENDED_VIDEO: 'https://www.redtube.com/recommended',
            PornCategories.SEARCH_MAIN: 'https://www.redtube.com/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
            PornCategories.TRENDING_VIDEO: PornFilterTypes.TrendingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.redtube.com/'

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return False

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filters = {'general_filters': ((PornFilterTypes.StraightType, 'Straight', None),
                                               (PornFilterTypes.GayType, 'Gay', 'gay'),
                                               # (PornFilterTypes.ShemaleType, 'Shemale', 'redtube/transgender'),
                                               ),
                           }
        category_filters = {'sort_order': ((PornFilterTypes.AlphabeticOrder, 'Alphabetically', None),
                                           (PornFilterTypes.PopularityOrder, 'Popularity', 'popular'),
                                           ),
                            }
        # todo: add some other porn star filters...
        porn_stars_filters = {'general_filters': ((PornFilterTypes.GirlType, 'Female', None),
                                                  (PornFilterTypes.GuyType, 'Male', 'male'),
                                                  (PornFilterTypes.ShemaleType, 'Transgender', 'transgender'),
                                                  (PornFilterTypes.AllType, 'All', 'all'),
                                                  ),
                              'sort_order': ((PornFilterTypes.RatingOrder, 'Ranking', None),
                                             (PornFilterTypes.SubscribersOrder, 'Most Subscribers', 'subscribers'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Video Count', 'videocount'),
                                             (PornFilterTypes.AlphabeticOrder, 'Alphabetical', 'alphabetical'),
                                             (PornFilterTypes.FavorOrder, 'Trending', 'trending'),
                                             ),
                              }
        channels_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Recently Updated', 'recently-updated'),
                                           (PornFilterTypes.SubscribersOrder, 'Most Subscribers', 'most-subscribed'),
                                           (PornFilterTypes.FavorOrder, 'Trending', 'trending'),
                                           (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                           (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                           (PornFilterTypes.AlphabeticOrder, 'Alphabetical', 'alphabetical'),
                                           (PornFilterTypes.RecommendedOrder, 'Recommended', 'recommended'),
                                           ),
                            }
        single_category = {'sort_order': ((PornFilterTypes.FeaturedOrder, 'Recently Featured', 'featured'),
                                          (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                                          (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                                          (PornFilterTypes.FavorOrder, 'Most Favorite', 'mostfavored'),
                                          (PornFilterTypes.ViewsOrder, 'Most Viewed', 'mostviewed'),
                                          (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                          ),
                           'period_filters': ([(PornFilterTypes.AllDate, 'All time', 'alltime'),
                                               (PornFilterTypes.TwoDate, 'This Week', 'weekly'),
                                               (PornFilterTypes.OneDate, 'This Month', 'monthly'),
                                               ],
                                              [('sort_order', [PornFilterTypes.FavorOrder,
                                                               PornFilterTypes.ViewsOrder,
                                                               # PornFilterTypes.RatingOrder,
                                                               PornFilterTypes.LengthOrder,
                                                               ])]
                                              ),
                           }
        single_tag = {'sort_order': ((PornFilterTypes.RelevanceOrder, 'Most Relevant', 'rv'),
                                     (PornFilterTypes.DateOrder, 'Newest', 'cm'),
                                     (PornFilterTypes.RatingOrder, 'Top Rated', 'tr'),
                                     (PornFilterTypes.ViewsOrder, 'Most Viewed', 'mv'),
                                     (PornFilterTypes.LengthOrder, 'Longest', 'lg'),
                                     ),
                      'period_filters': ([(PornFilterTypes.AllDate, 'All time', 'a'),
                                          (PornFilterTypes.TwoDate, 'This Week', 'w'),
                                          (PornFilterTypes.OneDate, 'This Month', 'm'),
                                          ],
                                         [('sort_order', [PornFilterTypes.ViewsOrder,
                                                          PornFilterTypes.RatingOrder,
                                                          PornFilterTypes.LengthOrder,
                                                          ])]
                                         ),

                      }
        single_channel = {'sort_order': ((PornFilterTypes.DateOrder, 'Most Recent', None),
                                         (PornFilterTypes.RatingOrder, 'Top Rated', 'toprated'),
                                         (PornFilterTypes.ViewsOrder, 'Most Viewed', 'mostviewed'),
                                         (PornFilterTypes.FavorOrder, 'Most Favorite', 'mostfavored'),
                                         (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                         ),
                          }
        single_porn_star = {'sort_order': ((PornFilterTypes.DateOrder, 'Newest', None),
                                           (PornFilterTypes.RatingOrder, 'Top Rated', 'toprated'),
                                           (PornFilterTypes.ViewsOrder, 'Most Viewed', 'mostviewed'),
                                           (PornFilterTypes.FavorOrder, 'Most Favorite', 'mostfavored'),
                                           (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                           ),
                            }
        video_filters = {'sort_order': ((PornFilterTypes.TrendingOrder, 'Trending', 'hot'),
                                        (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'top'),
                                        (PornFilterTypes.FavorOrder, 'Most Favorite', 'mostfavored'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'mostviewed'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        ),
                         'period_filters': ([(PornFilterTypes.AllDate, 'All time', 'alltime'),
                                             (PornFilterTypes.TwoDate, 'This Week', 'weekly'),
                                             (PornFilterTypes.OneDate, 'This Month', 'monthly'),
                                             ],
                                            [('sort_order', [PornFilterTypes.FavorOrder,
                                                             PornFilterTypes.ViewsOrder,
                                                             PornFilterTypes.RatingOrder,
                                                             PornFilterTypes.LengthOrder,
                                                             ])]
                                            ),
                         }
        search_filters = {'sort_order': ((PornFilterTypes.RelevanceOrder, 'Most Relevant', None),
                                         (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                                         (PornFilterTypes.RatingOrder, 'Top Rated', 'top'),
                                         (PornFilterTypes.FavorOrder, 'Most Favorite', 'mostfavored'),
                                         (PornFilterTypes.ViewsOrder, 'Most Viewed', 'mostviewed'),
                                         (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                         ),
                          'period_filters': ([(PornFilterTypes.AllDate, 'All time', 'alltime'),
                                              (PornFilterTypes.TwoDate, 'This Week', 'weekly'),
                                              (PornFilterTypes.OneDate, 'This Month', 'monthly'),
                                              ],
                                             [('sort_order', [PornFilterTypes.FavorOrder,
                                                              PornFilterTypes.ViewsOrder,
                                                              PornFilterTypes.RatingOrder,
                                                              PornFilterTypes.LengthOrder,
                                                              ])]
                                             ),
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filters,
                                         categories_args=category_filters,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_tag_args=single_tag,
                                         single_category_args=single_category,
                                         single_channel_args=single_channel,
                                         single_porn_star_args=single_porn_star,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='RedTube', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(RedTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@id="categories_list_section"]//ul[@id="categories_list_block"]/li/'
                                'div[@class="category_item_wrapper tm_cat_wrapper"]')
        res = []
        for category in categories:
            link = category.xpath('./a')
            assert len(link) == 1

            image_data = category.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-src']

            title = category.xpath('./div[@class="category_item_info"]/a/strong/text()')
            assert len(title) == 1
            title = self._clear_text(title[0])

            number_of_videos = category.xpath('./div[@class="category_item_info"]/'
                                              'span[@class="category_count tm_cat_count"]/text()')
            assert len(number_of_videos) == 1
            number_of_videos = self._clear_text(number_of_videos[0])
            number_of_videos = re.sub(r',', '',  number_of_videos)
            number_of_videos = int(re.findall(r'\d+', number_of_videos)[0])

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  image_link=image,
                                                  title=title,
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
        categories = tree.xpath('.//div[@id="pornstars_list"]//ul[@id="recommended_pornstars_block"]/li/div')
        res = []
        for category in categories:
            link_data = category.xpath('./a[@class="pornstar_link js_mpop js-pop "]')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = category.xpath('./a[@class="pornstar_link js_mpop js-pop "]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-src']
            title = image_data[0].attrib['alt']

            # title = category.xpath('./div[@class="category_item_info"]/a/strong/text()')
            # assert len(title) == 1
            # title = self._clear_text(title[0])

            rank = category.xpath('./a[@class="pornstar_link js_mpop js-pop "]/div[@class="ps_info_rank"]/text()')
            assert len(rank) == 1
            additional_data = {'rank': self._clear_text(rank[0])}

            number_of_videos = category.xpath('./div[@class="ps_info_count"]/text()')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0])[0])

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(porn_star_data.url, link),
                                                  image_link=image,
                                                  title=title,
                                                  number_of_videos=number_of_videos,
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.PORN_STAR,
                                                  super_object=porn_star_data,
                                                  )
            res.append(object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channel.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//ul[@id="channels_main"]/li')
        res = []
        for category in categories:
            link_data = category.xpath('./a[@class="channels-list-img js-pop"]')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = category.xpath('./a[@class="channels-list-img js-pop"]/span[@class="channel-logo"]/img')
            if len(image_data) == 1:
                image = image_data[0].attrib['src']
                if 'data:image' in image:
                    image = image_data[0].attrib['data-src']
            else:
                image_data = category.xpath('./a[@class="channels-list-img js-pop"]/img')
                image = image_data[0].attrib['src']
                if 'data:image' in image:
                    image = image_data[0].attrib['data-src']

            title = image_data[0].attrib['alt']

            # title = category.xpath('./div[@class="category_item_info"]/a/strong/text()')
            # assert len(title) == 1
            # title = self._clear_text(title[0])

            subscribers = category.xpath('./div[@class="channels-list-info"]/span[@class="channel_suscribers"]/text()')
            assert len(subscribers) == 1
            additional_data = {'subscribers': self._clear_text(subscribers[0])}

            number_of_videos = category.xpath('./div[@class="channels-list-info"]/span[@class="channel_videos"]/'
                                              'text()')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0])[0])

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(channel_data.url, link),
                                                  image_link=image,
                                                  title=title,
                                                  number_of_videos=number_of_videos,
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.CHANNEL,
                                                  super_object=channel_data,
                                                  )
            res.append(object_data)
        channel_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available tag.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//script[@id="two_row_carousel_template"]')
        assert len(categories) == 1
        tree = self.parser.parse(categories[0].text)
        categories = tree.xpath('.//ul[@ref="original_elements"]/li[@class="original_item"]/a')
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=category.attrib['href'],
                                       url=urljoin(tag_data.url, category.attrib['href']),
                                       title=category.text,
                                       object_type=PornCategories.TAG,
                                       super_object=tag_data,
                                       ) for category in categories]
        tag_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        script = [x for x in tmp_tree.xpath('.//script/text()') if 'mediaDefinition' in x]
        raw_data = re.findall(r'(?:mediaDefinition: )(\[.*\])(?:,\n)', script[0])
        raw_data = json.loads(raw_data[0])
        video_links = sorted((VideoSource(link=x['videoUrl'], quality=int(re.findall(r'\d+', x['quality'])[0]))
                              for x in raw_data),
                             key=lambda x: x.quality, reverse=True)
        return VideoNode(video_sources=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN):
            return 1
        try:
            page_request = self.get_object_request(category_data, override_page_number=2, send_error=False)
        except PornFetchUrlError:
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
        return [int(re.findall(r'(?:page=)(\d+)', x)[0])
                for x in tree.xpath('.//ul[@id="w_pagination_list"]/li/a/@href')
                if len(re.findall(r'(?:page=)(\d+)', x)) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div/ul/li/div[@class="video_block_wrapper js_mediaBookBounds "]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./div[@class="video_title"]/a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            if link.split('/')[1] == 'premium':
                # todo: We have premium content, check if we could fetch it...
                continue

            images_data = video_tree_data.xpath('./span[@class="video_thumb_wrap"]/a/picture')
            if len(images_data) == 1:
                image_data = images_data[0].xpath('./img')
                assert len(image_data) == 1
                image = image_data[0].attrib['src']
                if 'data:image' in image:
                    image = image_data[0].attrib['data-src']
            else:
                images_data = video_tree_data.xpath('./span[@class="video_thumb_wrap"]/a/img')
                if len(images_data) == 0:
                    # We have private content
                    continue
                image = images_data[0].attrib['src']
                if 'data:image' in image:
                    image = images_data[0].attrib['data-src']

            flip_images = [images_data[0].attrib['data-path'].format(index=i)
                           for i in range(1, int(images_data[0].attrib['data-thumbs'])+1)]
            video_preview = images_data[0].attrib['data-mediabook'] if 'data-mediabook' in images_data[0].attrib \
                else None

            is_hd = video_tree_data.xpath('./span[@class="video_thumb_wrap"]/a/'
                                          'span[@class="hd-video-icon site_sprite"]')
            is_hd = len(is_hd) > 0
            duration_data = video_tree_data.xpath('./span[@class="video_thumb_wrap"]/a/span[@class="duration"]')
            assert len(duration_data) == 1
            if is_hd is True:
                is_vr = duration_data[0].xpath('./span[@class="vr-video"]')
                if len(is_vr) == 0:
                    is_vr = False
                    video_length = self._clear_text(duration_data[0].text)
                else:
                    duration_data = is_vr
                    is_vr = True
                    video_length = self._clear_text(duration_data[0].tail)
            else:
                video_length = self._clear_text(duration_data[0].text)
                is_vr = False

            title = video_tree_data.xpath('./div[@class="video_title"]/a')
            assert len(title) == 1
            title = title[0].text

            number_of_viewers = video_tree_data.xpath('./span[@class="video_count"]')
            assert len(number_of_viewers) == 1
            number_of_viewers = number_of_viewers[0].text

            rating = video_tree_data.xpath('./span[@class="video_percentage"]')
            assert len(rating) == 1
            rating = rating[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  is_hd=is_hd,
                                                  is_vr=is_vr,
                                                  duration=self._format_duration(video_length),
                                                  number_of_views=number_of_viewers,
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
            'Host': self.host_name,
            'Referer': fetch_base_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = page_filter.sort_order.filter_id

        if (
                self.general_filter.current_filters.general.value is not None and
                true_object.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN,
                                            PornCategories.CHANNEL_MAIN, PornCategories.CATEGORY,
                                            PornCategories.TAG, PornCategories.SEARCH_MAIN,)
        ):
            if len(split_url) <= 3 or split_url[3] != self.general_filter.current_filters.general.value:
                split_url.insert(3, self.general_filter.current_filters.general.value)
        if page_number is not None and page_number != 1:
            params['page'] = page_number
        if true_object.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN):
            if page_filter.sort_order.value is not None:
                split_url.append(page_filter.sort_order.value)
        elif true_object.object_type == PornCategories.PORN_STAR_MAIN:
            if page_filter.sort_order.value is not None:
                split_url.append(page_filter.sort_order.value)
            if page_filter.general.value is not None:
                split_url.append(page_filter.general.value)
        elif true_object.object_type == PornCategories.CHANNEL_MAIN:
            # We move the gender to the end of the url
            if len(split_url) > 3 and split_url[3] != self.general_filter.current_filters.general.value:
                split_url.append(split_url.pop(3))
            if page_filter.sort_order.value is not None:
                split_url.append(page_filter.sort_order.value)
        elif true_object.object_type == PornCategories.TAG:
            if page_filter.sort_order.value is not None:
                params['sort'] = page_filter.sort_order.value
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['period'] = page_filter.period.value
        elif true_object.object_type == PornCategories.CATEGORY:
            if page_filter.sort_order.value is not None:
                params['sorting'] = page_filter.sort_order.value
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['period'] = page_filter.period.value
        elif true_object.object_type == PornCategories.PORN_STAR:
            if page_filter.sort_order.value is not None:
                split_url.append(page_filter.sort_order.value)
        elif true_object.object_type == PornCategories.CHANNEL:
            if page_filter.sort_order.value is not None:
                split_url.append(page_filter.sort_order.value)
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            if page_filter.sort_order.value is not None:
                split_url.insert(3, page_filter.sort_order.value)
        # elif true_object.object_type in PornCategories.RECOMMENDED_VIDEO:
        #     if page_filter.sort_order.value is not None:
        #         split_url.insert(3, page_filter.sort_order.value)
        else:
            if true_object.object_type not in self._default_sort_by:
                if page_filter.sort_order.value is not None:
                    split_url.append(page_filter.sort_order.value)
            else:
                true_sort_filter_id = self._default_sort_by[true_object.object_type]
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['period'] = page_filter.period.value

        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?search={q}'.format(q=quote_plus(query))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('/redtube/amateur')
    porn_star_id = IdGenerator.make_id('/pornstar/mia+khalifa')
    tag_id = IdGenerator.make_id('https://www.redtube.com/redtube/arab')
    channel_id = IdGenerator.make_id('/channels/brazzers')
    module = RedTube()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['porn_stars']['obj'], (porn_star_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['channels']['obj'], (channel_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
