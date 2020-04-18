# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, urlparse, quote

# Regex
import re

# JSON
from ..tools.text_json_manioulations import prepare_json_from_not_formatted_text

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# # Generator id
# from ..id_generator import IdGenerator


class ClipHunter(PornFetcher):
    flip_number = 11

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.cliphunter.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://www.cliphunter.com/pornstars/',
            PornCategories.CHANNEL_MAIN: 'https://www.cliphunter.com/channels/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.cliphunter.com/categories/All/1/date/50/super',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.cliphunter.com/categories/All/1/views',
            PornCategories.LATEST_VIDEO: 'https://www.cliphunter.com/categories/All/1/date/50/all/all/all',
            PornCategories.POPULAR_VIDEO: 'https://www.cliphunter.com/popular/ratings/month',
            PornCategories.SEARCH_MAIN: 'https://www.cliphunter.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.cliphunter.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Date', 'date'),
                                       (PornFilterTypes.RelevanceOrder, 'Relevance', 'rel'),
                                       (PornFilterTypes.ViewsOrder, 'Views', 'views'),
                                       (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                       ],
                        'added_before_filters': [(PornFilterTypes.AllAddedBefore, 'All time', 'all'),
                                                 (PornFilterTypes.OneAddedBefore, 'Today', 'today'),
                                                 (PornFilterTypes.TwoAddedBefore, 'Yesterday', 'yesterday'),
                                                 (PornFilterTypes.ThreeAddedBefore, 'This week', 'week'),
                                                 (PornFilterTypes.FourAddedBefore, 'This month', 'month'),
                                                 (PornFilterTypes.FiveAddedBefore, '3 months', '3months'),
                                                 (PornFilterTypes.SixAddedBefore, 'This Year', 'year'),
                                                 ],
                        'length_filters': [(PornFilterTypes.AllLength, 'All durations', '0'),
                                           (PornFilterTypes.OneLength, 'Short duration', '300'),
                                           (PornFilterTypes.TwoLength, 'Medium duration', '900'),
                                           (PornFilterTypes.ThreeLength, 'Long duration', '1800'),
                                           ],
                        'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', '0'),
                                            (PornFilterTypes.HDQuality, 'HD quality', '1'),
                                            ],
                        'rating_filters': [(PornFilterTypes.AllRating, 'All rating', 'all'),
                                           (PornFilterTypes.OneRating, 'Medium rating', 'medium'),
                                           (PornFilterTypes.TwoRating, 'High rating', 'high'),
                                           (PornFilterTypes.ThreeRating, 'Super high rating', 'super'),
                                           ],

                        }
        porn_stars_filter = {'sort_order': [(PornFilterTypes.RatingOrder, 'Rating', 'top'),
                                            (PornFilterTypes.PopularityOrder, 'Followers', 'mostfollowed'),
                                            # (FilterTypes.RelevanceOrder, 'Relevance', 'rel'),
                                            # (FilterTypes.ViewsOrder, 'Views', 'views'),
                                            ],
                             }
        channels_filter = {'sort_order': [(PornFilterTypes.DateOrder, 'Recently Updated', 'recently-updated'),
                                          (PornFilterTypes.PopularityOrder, 'Most Popular', 'most-popular'),
                                          (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                          (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                          (PornFilterTypes.LengthOrder, 'Video Duration', 'video-duration'),
                                          (PornFilterTypes.AlphabeticOrder, 'A-Z', 'alphabetical'),
                                          ],
                           }
        single_porn_stars_filter = video_params.copy()
        single_porn_stars_filter['sort_order'] = [(PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                                  (PornFilterTypes.DateOrder, 'Date', ''),
                                                  (PornFilterTypes.RelevanceOrder, 'Relevance', 'rel'),
                                                  (PornFilterTypes.ViewsOrder, 'Views', 'views'),
                                                  ]
        single_channel_filter = {'sort_order': [(PornFilterTypes.RatingOrder, 'Best', 'rating'),
                                                (PornFilterTypes.DateOrder, 'Newest', 'date'),
                                                (PornFilterTypes.ViewsOrder, 'Most Views', 'views'),
                                                ],
                                 'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', '0'),
                                                     (PornFilterTypes.HDQuality, 'HD quality', '1'),
                                                     ],
                                 }

        search_filter = video_params.copy()
        search_filter['sort_order'] = [(PornFilterTypes.RelevanceOrder, 'Relevance', 'rel'),
                                       (PornFilterTypes.DateOrder, 'Date', ''),
                                       (PornFilterTypes.ViewsOrder, 'Views', 'views'),
                                       (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                       ]

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filter,
                                         channels_args=channels_filter,
                                         single_category_args=video_params,
                                         single_porn_star_args=single_porn_stars_filter,
                                         single_channel_args=single_channel_filter,
                                         search_args=search_filter,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='ClipHunter', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(ClipHunter, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, PornCategories.CATEGORY, '')

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data, PornCategories.PORN_STAR, '/movies')

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="paper paperSpacings xs-fullscreen"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = category.xpath('./ul/li/a[@class="t pop-execute"]/img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])

            channel_data = category.xpath('./ul/li/a/b')
            assert len(channel_data) == 3
            number_of_videos = int(re.findall(r'\d+', channel_data[0])[0])
            number_of_views = channel_data[1]

            title = category.xpath('./ul/li/a[@class="chtl pop-execute"]')
            assert len(title) == 1
            title = title[0].text

            sub_object_data = \
                PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                        obj_id=link,
                                        title=title,
                                        url=urljoin(self.base_url, link + '/1/rating'),
                                        image_link=image,
                                        number_of_videos=number_of_videos,
                                        number_of_views=number_of_views,
                                        object_type=PornCategories.CHANNEL,
                                        super_object=channel_data,
                                        )
            res.append(sub_object_data)
        channel_data.add_sub_objects(res)
        return res

    def _update_available_base_object(self, object_data, object_type, video_suffix):
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="paper paperSpacings xs-fullscreen photoGrid"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])

            if 'title' in category.attrib:
                title = category.attrib['title']
            else:
                title = category.xpath('./div[@class="caption"]/span')
                assert len(title) == 1
                title = title[0].text

            sub_object_data = \
                PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                        obj_id=link,
                                        title=title,
                                        url=urljoin(self.base_url, link) + video_suffix,
                                        image_link=image,
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
        tmp_request = self.get_object_request(video_data)
        tmp_data = re.findall(r'(?:var gexoFiles *= *)({.*})(?:;)', tmp_request.text)
        tmp_data = prepare_json_from_not_formatted_text(tmp_data[0])

        videos = sorted((VideoSource(link=x['url'].replace('\\/', '/'), resolution=x['h']) for x in tmp_data.values()),
                        key=lambda y: y.resolution, reverse=True)
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Get number of pages from category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if fetched_request is None:
            page_request = self.get_object_request(category_data)
        else:
            page_request = fetched_request
        tree = self.parser.parse(page_request.text)
        max_page = tree.xpath('.//ul[@class="fibonacci_pagination"]')
        max_page = int(max_page[0].attrib['maxpages']) if len(max_page) == 1 else 1
        return max_page

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = (tree.xpath('.//ul[@class="moviethumbs bigthumbs clear"]/li') +
                  tree.xpath('.//ul[@class="moviethumbs clear two-cols"]/li'))
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a[1]')
            assert len(link) == 1

            image = video_tree_data.xpath('./a[1]/img')
            assert len(image) == 1
            number_of_flip_images = image[0].attrib['tc']
            image = image[0].attrib['src']

            is_hd = video_tree_data.xpath('./a[1]/div[@class="sharpCorner"]/div[@class="tl adjusted"]')

            title = video_tree_data.xpath('./a[2]')
            assert len(title) == 1

            number_of_viewers = (video_tree_data.xpath('./div[@class="info long"]') +
                                 video_tree_data.xpath('./div[@class="info"]'))
            assert len(number_of_viewers) == 1

            video_data = PornCatalogVideoPageNode(
                catalog_manager=self.catalog_manager,
                obj_id=link[0].attrib['href'],
                url=urljoin(self.base_url, link[0].attrib['href']),
                title=title[0].text,
                image_link=image,
                flip_images_link=[re.sub(r'(?:_)(\d+)(?:.jpg)', '_{x}.jpg'.format(x=x), image)
                                  for x in range(1, int(number_of_flip_images) + 1)],
                is_hd=len(is_hd) == 1 and is_hd[0].text == 'HD',
                number_of_views=int(''.join(re.findall(r'\d+', number_of_viewers[0].text, re.DOTALL))),
                object_type=PornCategories.VIDEO,
                super_object=page_data,
            )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        """
        Example of request page: https://www.cliphunter.com/categories/All/1/date/50/super/3months/1800/1
        -> https://www.cliphunter.com/{object_type}/{object}/{page_number}/{sort}/50/{rating_filter}
                                                                    /{period_filter}/{length-filter}/{quality_filter}
        """
        parsed_url = urlparse(page_data.url)
        split_url_path = parsed_url.path.split('/')
        fetch_base_url = urljoin(page_data.url, '/'.join(split_url_path[:3]))
        if page_number is None:
            page_number = 1
        if true_object.object_type == PornCategories.PORN_STAR_MAIN:
            suffix = '/{sort}/overview/{p}'.format(sort=page_filter.sort_order.value, p=page_number)
        elif true_object.object_type == PornCategories.CHANNEL_MAIN:
            suffix = '/{sort}/{p}'.format(sort=page_filter.sort_order.value, p=page_number)
        elif true_object.object_type == PornCategories.CHANNEL:
            suffix = '/{p}/{sort}/{q}' \
                     ''.format(p=page_number,
                               sort=page_filter.sort_order.value,
                               q=page_filter.quality.value,
                               )
        elif true_object.object_type == PornCategories.PORN_STAR:
            suffix = '/movies/{p}/{sort}/50/{r}/{d}/{l}/{q}' \
                     ''.format(p=page_number,
                               sort=page_filter.sort_order.value,
                               r=page_filter.rating.value,
                               d=page_filter.added_before.value,
                               l=page_filter.length.value,
                               q=page_filter.quality.value,
                               )
        elif true_object.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.VIDEO):
            suffix = ''
        elif true_object.object_type == PornCategories.POPULAR_VIDEO:
            suffix = '/{d}/{p}'.format(d=page_filter.added_before.value,
                                       p=page_number)
        elif true_object.object_type == PornCategories.TOP_RATED_VIDEO:
            suffix = '/{p}/rating/50/{r}/{d}/{l}/{q}' \
                     ''.format(p=page_number,
                               r=page_filter.rating.value,
                               d=page_filter.added_before.value,
                               l=page_filter.length.value,
                               q=page_filter.quality.value,
                               )
        elif true_object.object_type == PornCategories.LATEST_VIDEO:
            suffix = '/{p}/date/50/{r}/{d}/{l}/{q}' \
                     ''.format(p=page_number,
                               r=page_filter.rating.value,
                               d=page_filter.added_before.value,
                               l=page_filter.length.value,
                               q=page_filter.quality.value,
                               )
        elif true_object.object_type == PornCategories.MOST_VIEWED_VIDEO:
            suffix = '/{p}/views/50/{r}/{d}/{l}/{q}' \
                     ''.format(p=page_number,
                               r=page_filter.rating.value,
                               d=page_filter.added_before.value,
                               l=page_filter.length.value,
                               q=page_filter.quality.value,
                               )
        # elif true_object_type == VideoCategories.CATEGORY:
        #     suffix = '/{p}/{sort}/50/{r}/{d}/{l}/{q}' \
        #              ''.format(p=page_number,
        #                        sort=page_filter.sort_order.value,
        #                        r=page_filter.rating.value,
        #                        d=page_filter.added_before.value,
        #                        l=page_filter.length.value,
        #                        q=page_filter.quality.value,
        #                        )
        else:
            suffix = '/{p}/{sort}/50/{r}/{d}/{l}/{q}' \
                     ''.format(p=page_number,
                               sort=page_filter.sort_order.value,
                               r=page_filter.rating.value,
                               d=page_filter.added_before.value,
                               l=page_filter.length.value,
                               q=page_filter.quality.value,
                               )

        fetch_base_url += suffix
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
        page_request = self.session.get(fetch_base_url, headers=headers)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}'.format(q=quote(query))


if __name__ == '__main__':
    # category_id = IdGenerator.make_id('/categories/Asian')  # 'Japanese'
    module = ClipHunter()
    # module.get_available_categories()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user()
