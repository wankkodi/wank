# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote_plus

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# Generator id
from ..id_generator import IdGenerator


class CollectionOfBestPorn(PornFetcher):
    flip_number = 11

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 5000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://collectionofbestporn.com/channels/',
            PornCategories.TAG_MAIN: 'https://collectionofbestporn.com/tags',
            PornCategories.PORN_STAR_MAIN: 'https://collectionofbestporn.com/pornstars/',
            PornCategories.LATEST_VIDEO: 'https://collectionofbestporn.com/most-recent',
            PornCategories.MOST_VIEWED_VIDEO: 'https://collectionofbestporn.com/most-viewed',
            PornCategories.LONGEST_VIDEO: 'https://collectionofbestporn.com/longest',
            PornCategories.TOP_RATED_VIDEO: 'https://collectionofbestporn.com/top-rated',
            PornCategories.SEARCH_MAIN: 'https://collectionofbestporn.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://collectionofbestporn.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        base_common_params = {
            'length_filters': [(PornFilterTypes.AllLength, 'Any durations', None),
                               (PornFilterTypes.OneLength, 'Short (0-5 min.)', 'short'),
                               (PornFilterTypes.TwoLength, 'Medium (5-20 min.)', 'medium'),
                               (PornFilterTypes.ThreeLength, 'Long (20+ min.)', 'long')
                               ],
            'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', None),
                                (PornFilterTypes.HDQuality, 'HD quality', '1'),
                                ],
        }
        video_params = base_common_params.copy()
        video_params.update({'period_filters': [(PornFilterTypes.AllDate, 'All date', None),
                                                (PornFilterTypes.OneDate, 'Last 24 hours', 'day'),
                                                (PornFilterTypes.TwoDate, 'Last week', 'week'),
                                                (PornFilterTypes.ThreeDate, 'Last month', 'month'),
                                                ],

                             })
        porn_stars_filter = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', None),
                                            (PornFilterTypes.PopularityOrder, 'Likes', '1'),
                                            ],
                             }
        single_porn_stars_filter = base_common_params.copy()
        single_porn_stars_filter.update({'sort_order': [(PornFilterTypes.DateOrder, 'Date', None),
                                                        (PornFilterTypes.PopularityOrder, 'Popularity', 'popularity'),
                                                        (PornFilterTypes.LengthOrder, 'Duration', 'duration'),
                                                        (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                                        (PornFilterTypes.ViewsOrder, 'Views', 'views'),
                                                        ],
                                         'added_before_filters':
                                             [(PornFilterTypes.AllAddedBefore, 'All time', 'all'),
                                              (PornFilterTypes.OneAddedBefore, 'Past 24 hours', 'past24'),
                                              (PornFilterTypes.TwoAddedBefore, 'Past week', 'week'),
                                              (PornFilterTypes.ThreeAddedBefore, 'Past month', 'month'),
                                              (PornFilterTypes.FourAddedBefore, 'Past year', 'year'),
                                              ],
                                         })
        single_channel_filter = base_common_params.copy()
        single_channel_filter.update({'sort_order': [(PornFilterTypes.DateOrder, 'Date', 'newest'),
                                                     (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                                                     (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                                                     (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                                     ],
                                      })
        single_tag_filter = base_common_params.copy()
        single_tag_filter.update({'sort_order': [(PornFilterTypes.RelevanceOrder, 'Relevance', None),
                                                 (PornFilterTypes.DateOrder, 'Most recent', 'newest'),
                                                 (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                                                 (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                                                 (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                                 ],
                                  })
        search_filter = single_tag_filter.copy()

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filter,
                                         single_category_args=video_params,
                                         single_tag_args=single_tag_filter,
                                         single_porn_star_args=single_porn_stars_filter,
                                         search_args=search_filter,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='CollectionOfBestPorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(CollectionOfBestPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type,
                                                   use_web_server, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data, PornCategories.PORN_STAR)

    def _update_available_base_object(self, object_data, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        res = []
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="row content-row video-list"]//div[@class="inner-wrapper"]')
        for category in categories:
            title = category.xpath('./div[@class="video-desc"]/div[@class="title"]/a/span')
            assert len(title) == 1
            title = title[0].text

            sub_object = category.xpath('./div[@class="video-thumb"]/a')
            assert len(sub_object) == 1
            sub_object = sub_object[0]

            image = sub_object.xpath('./div[@class="image image-ar"]/img')
            assert len(image) == 1

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=sub_object.attrib['href'],
                                                      title=title,
                                                      url=urljoin(object_data.url, sub_object.attrib['href']),
                                                      image_link=image[0].attrib['src'],
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        object_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//div[@class="tag-group"]/div[@class="columns-wrap"]/div[@class="column"]/a')
        links = [x.attrib['href'] for x in raw_data]
        titles = [re.findall(r'(.*?)(?: *\($)', x.text)[0] for x in raw_data]
        number_of_videos = [int(x.text) for x in tree.xpath('.//div[@class="tag-group"]/div[@class="columns-wrap"]/'
                                                            'div[@class="column"]/a/small')]
        return links, titles, number_of_videos

    # def _update_available_tags(self, tag_data):
    #     """
    #     Fetches all the available shows.
    #     :return: Object of all available shows (JSON).
    #     """
    #     headers = {
    #         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
    #                   'q=0.8,application/signed-exchange;v=b3',
    #         'Cache-Control': 'max-age=0',
    #         'Host': self.host_name,
    #         'Referer': self.base_url,
    #         'Sec-Fetch-Mode': 'navigate',
    #         'Sec-Fetch-Site': 'same-origin',
    #         'Sec-Fetch-User': '?1',
    #         'Upgrade-Insecure-Requests': '1',
    #         'User-Agent': self.user_agent
    #     }
    #     res = []
    #     page_request = self.session.get(tag_data.url, headers=headers)
    #     tree = self.parser.parse(page_request.text)
    #     categories = tree.xpath('.//div[@class="tag-group"]/div[@class="columns-wrap"]/'
    #                             'div[@class="column"]/a')
    #     for category in categories:
    #         number_of_videos = category.xpath('./small/text()')
    #         assert len(number_of_videos) == 1
    #
    #         object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
    #                                               obj_id=category.attrib['href'],
    #                                               title=re.findall(r'(.*?)(?: *\($)', category.text)[0],
    #                                               url=urljoin(tag_data.url, category.attrib['href']),
    #                                               number_of_videos=int(number_of_videos[0]),
    #                                               object_type='Tag',
    #                                               super_object=tag_data,
    #                                               )
    #         res.append(object_data)
    #
    #     return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)

        videos = tmp_tree.xpath('.//video/source')
        videos = sorted((VideoSource(link=x.attrib['src'], resolution=x.attrib['res']) for x in videos),
                        key=lambda y: y.resolution, reverse=True)
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        if len(available_pages) == 0:
            return 1
        elif (category_data.page_number is not None and
              max(available_pages) - category_data.page_number < self._binary_search_page_threshold):
            return max(available_pages)
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//ul[@class="pagination p-ignore"]/li/*/text()')
                if x.isdigit()] + \
               [int(x) for x in tree.xpath('.//ul[@class="pagination"]/li/*/text()')
                if x.isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 9

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)

        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="row content-row video-list"]//div[@class="inner-wrapper"]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./div[@class="video-thumb"]/a')
            assert len(link) == 1

            image = video_tree_data.xpath('./div[@class="video-thumb"]/a/div[@class="image image-ar"]/img')
            assert len(image) == 1
            title = image[0].attrib['title']
            image = image[0].attrib['src']
            flip_image = [re.sub(r'(?:mp4-)(\d+)(?:.jpg)', 'mp4-{x}.jpg'.format(x=x), image)
                          for x in range(1, self.flip_number + 1)]

            rating = video_tree_data.xpath('./div[@class="video-thumb"]/a/div[@class="video-time"]/'
                                           'div[@class="ratings"]/div[@class="starOff"]/div[@class="starOn"]')
            assert len(rating) == 1
            rating = re.findall(r'\d+%', rating[0].attrib['style'])

            is_hd = video_tree_data.xpath('./div[@class="video-thumb"]/a/div[@class="video-time"]/'
                                          'span[@class="quality"]')

            video_length = video_tree_data.xpath('./div[@class="video-thumb"]/a/div[@class="video-time"]/'
                                                 'span[@class="time"]')
            assert len(video_length) == 1

            number_of_viewers = video_tree_data.xpath('./div[@class="video-desc"]/div[@class="stats"]/'
                                                      'span[@class="views-stats"]')
            assert len(number_of_viewers) == 1

            added_before = video_tree_data.xpath('./div[@class="video-desc"]/div[@class="stats"]/'
                                                 'span[@class="added-stats"]/i')

            video_data = \
                PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                         obj_id=link[0].attrib['href'],
                                         url=urljoin(self.base_url, link[0].attrib['href']),
                                         title=title,
                                         image_link=image,
                                         flip_images_link=flip_image,
                                         rating=rating[0] if len(rating) > 0 else None,
                                         is_hd=len(is_hd) == 1,
                                         duration=self._format_duration(video_length[0].text),
                                         number_of_views=int(re.findall(r'\d+', number_of_viewers[0].text)[0]),
                                         added_before=added_before[0].tail if len(added_before) == 1 else None,
                                         object_type=PornCategories.VIDEO,
                                         super_object=page_data,
                                         )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        conditions = self.get_proper_filter(page_data).conditions
        if true_object.object_type == PornCategories.PORN_STAR_MAIN:
            if page_filter.sort_order.value is not None:
                params['plikes'] = [page_filter.sort_order.value]
            if page_number is not None:
                fetch_base_url += '/page/{p}'.format(p=page_number)
        elif true_object.object_type == PornCategories.PORN_STAR:
            if page_filter.sort_order.value is not None:
                params['psort'] = [page_filter.sort_order.value]
            if page_filter.quality.value is not None:
                params['pquality'] = [page_filter.quality.value]
            if page_filter.length.value is not None:
                params['pduration'] = [page_filter.length.value]
            if page_filter.added_before.value is not None:
                params['padded'] = [page_filter.added_before.value]
            if page_number is not None:
                params['page'] = page_number
        elif true_object.object_type in (PornCategories.TAG, PornCategories.CATEGORY, PornCategories.SEARCH_PAGE):
            if page_filter.sort_order.value is not None:
                fetch_base_url += '/{so}'.format(so=page_filter.sort_order.value)
            if page_filter.quality.value is not None:
                params['hd'] = [page_filter.quality.value]
            if page_filter.length.value is not None:
                params['duration'] = [page_filter.length.value]
            if page_number is not None:
                fetch_base_url += '/page/{p}'.format(p=page_number)
        elif true_object.object_type in self._default_sort_by:
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or
                     page_filter.sort_order.filter_id in conditions.period.sort_order)
            ):
                fetch_base_url += '/{so}'.format(so=page_filter.period.value)
            if page_filter.quality.value is not None:
                params['hd'] = [page_filter.quality.value]
            if page_filter.length.value is not None:
                params['duration'] = [page_filter.length.value]
            if page_number is not None:
                fetch_base_url += '/page/{p}'.format(p=page_number)

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
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    @staticmethod
    def _convert_raw_number_to_true_number(raw_number):
        """
        Converts the raw number into integer.
        :param raw_number: Raw number, i.e. '7m:58s'.
        :return:
        """
        res = ''
        hours = re.findall(r'(\d+)(?:h)', raw_number)
        if len(hours) > 0:
            res += '{s}:'.format(s=hours[0].zfill(2))
        minutes = re.findall(r'(\d+)(?:m)', raw_number)
        if len(minutes) > 0:
            res += '{s}:'.format(s=minutes[0].zfill(2))
        seconds = re.findall(r'(\d+)(?:s)', raw_number)
        if len(seconds) > 0:
            res += '{s}'.format(s=seconds[0].zfill(2))
        return res

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}'.format(q=quote_plus(query.replace(' ', '-')))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://collectionofbestporn.com/category/big-tits')
    tag_id = IdGenerator.make_id('https://collectionofbestporn.com/tag/21naturals')
    module = CollectionOfBestPorn()
    # module.get_available_categories()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user()
