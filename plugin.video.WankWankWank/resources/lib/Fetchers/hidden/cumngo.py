# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornNoVideoError, PornValueError

# Internet tools
from .. import urljoin, quote_plus, parse_qsl

# External Fetchers
from ..tools.external_fetchers import ExternalFetcher

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, PornFilter, \
    VideoNode, VideoSource, VideoTypes
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes

# m3u8
import m3u8

# Regex
import re

# Generator id
from ..id_generator import IdGenerator


class CumNGo(PornFetcher):
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
            PornCategories.CATEGORY_MAIN: 'https://cumngo.co/tags?f=hot-tags',
            PornCategories.TAG_MAIN: 'https://cumngo.co/tags?f=all-tags',
            PornCategories.PORN_STAR_MAIN: 'https://cumngo.co/pornstar',
            PornCategories.LATEST_VIDEO: 'https://cumngo.co/videos?f=new-videos',
            PornCategories.TOP_RATED_VIDEO: 'https://cumngo.co/videos?f=top-rated',
            PornCategories.HOTTEST_VIDEO: 'https://cumngo.co/videos?f=hot-videos',
            PornCategories.MOST_VIEWED_VIDEO: 'https://cumngo.co/videos',
            PornCategories.SEARCH_MAIN: 'https://cumngo.co/search',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.HOTTEST_VIDEO: PornFilterTypes.HottestOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://cumngo.co/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        porn_stars_filter = {'sort_order': [(PornFilterTypes.TrendingOrder, 'Trending Porn stars', 'f=hot-people'),
                                            (PornFilterTypes.DateOrder, 'Newest Porn Stars', 'f=new-people'),
                                            (PornFilterTypes.RatingOrder, 'Top Rated Porn Stars', 'f=top-rated'),
                                            (PornFilterTypes.ViewsOrder, 'Most Viewed Porn Stars', ''),
                                            ],
                             'period_filters': ([(PornFilterTypes.AllDate, 'All time', 't=all'),
                                                 (PornFilterTypes.OneDate, 'Month', 't=month'),
                                                 (PornFilterTypes.TwoDate, 'Week', 't=week'),
                                                 ],
                                                [('sort_order', [PornFilterTypes.ViewsOrder])]
                                                ),
                             }
        video_filters = {'sort_order': [(PornFilterTypes.HottestOrder, 'Hot Videos', 'f=hot-videos'),
                                        (PornFilterTypes.DateOrder, 'New Videos', 'f=new-videos'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated Videos', 'f=top-rated'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed Videos', ''),
                                        ],
                         'period_filters': ([(PornFilterTypes.AllDate, 'All time', 't=all'),
                                             (PornFilterTypes.OneDate, 'Month', 't=month'),
                                             (PornFilterTypes.TwoDate, 'Week', 't=week'),
                                             ],
                                            [('sort_order', [PornFilterTypes.ViewsOrder])]
                                            ),
                         }
        single_porn_star_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'f=latest'),
                                                   (PornFilterTypes.ViewsOrder, 'Most Viewed', 'f=most-viewed'),
                                                   ],
                                    }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filter,
                                         single_porn_star_args=single_porn_star_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='CumNGo', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(CumNGo, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)
        self.external_fetchers = ExternalFetcher(session=self.session, user_agent=self.user_agent,
                                                 parser=self.parser)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        links, titles, numbers_of_videos = self._get_tag_properties(page_request)
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=link,
                                       url=urljoin(self.base_url, link),
                                       title=title,
                                       object_type=PornCategories.CATEGORY,
                                       super_object=category_data,
                                       ) for link, title, number_of_videos in zip(links, titles, numbers_of_videos)]
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//ul[@class="tags-grid-view clearfix"]/li/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            if link in self.object_urls.values():
                continue

            image_data = category.xpath('./div[@class="cover"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = (image_data[0].attrib['alt']
                     if 'alt' in image_data[0].attrib['alt'] else
                     category.xpath('./div[@class="overlay"]/div[@class="name"]/strong')[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))
        porn_star_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//ul[@class="tags-grid-view-big clearfix"]/li/a')
        res = []
        for x in raw_objects:
            link = x.attrib['href']
            title, number_of_videos = re.findall(r'(.*)(?:\()(\d+)(?:\))', x.text)[0]
            res.append((link, title, int(number_of_videos)))

        links, titles, number_of_videos = zip(*res)
        return links, titles, number_of_videos

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        ext_link = tmp_tree.xpath('.//section[@class="player float-left clearfix"]//iframe')
        if len(ext_link) == 0 or 'src' not in ext_link[0].attrib:
            error_module = self._prepare_porn_error_module_for_video_page(video_data, tmp_request.url)
            raise PornNoVideoError(error_module.message, error_module)
        new_link = ext_link[0].attrib['src']
        new_request = self.external_fetchers.get_video_link_from_videyo_tube(new_link)
        if not self._check_is_available_page(video_data, new_request):
            error_module = self._prepare_porn_error_module_for_video_page(video_data, new_request.url)
            raise PornNoVideoError(error_module.message, error_module)
        videos = []
        for source in new_request['sources']:
            if source['type'] == "application/x-mpegURL":
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;'
                              'q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Cache-Control': 'max-age=0',
                    'Referer': video_data.url,
                    'User-Agent': self.user_agent
                }
                segment_request = self.session.get(source['src'], headers=headers)
                if not self._check_is_available_page(video_data, segment_request):
                    error_module = self._prepare_porn_error_module_for_video_page(video_data, new_request.url)
                    raise PornNoVideoError(error_module.message, error_module)
                video_m3u8 = m3u8.loads(segment_request.text)
                video_playlists = video_m3u8.playlists

                videos.extend([VideoSource(link=urljoin(source['src'], x.uri),
                                           video_type=VideoTypes.VIDEO_SEGMENTS,
                                           quality=x.stream_info.bandwidth,
                                           resolution=x.stream_info.resolution[1],
                                           codec=x.stream_info.codecs)
                               for x in video_playlists])
            else:
                error_module = self._prepare_porn_error_module_for_video_page(
                    video_data, new_request.url, 'Unsupported type {t}'.format(t=source['type']))
                raise PornValueError(error_module.message, error_module)

        return VideoNode(video_sources=videos)

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
        if category_data.true_object.object_type in (PornCategories.CATEGORY, PornCategories.TAG):
            # We update the page, as we have redirection
            if len(page_request.history) > 0:
                category_data.url = page_request.url
        return max(pages) if len(pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return ([int(x.text) for x in tree.xpath('.//ul[@class="pagination"]/li/*')
                 if x.text is not None and x.text.isdigit()])

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = (tree.xpath('.//ul[@class="video-grid clearfix"]/li/a') +
                  tree.xpath('.//ul[@class="video-grid clearfix inner"]/li/a'))
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./div[@class="cover"]/img')
            info_data = video_tree_data.xpath('./div[@class="overlay"]')
            assert len(image_data) == 1
            assert len(info_data) == 1
            image = image_data[0].attrib['src']
            title = (image_data[0].attrib['alt']
                     if 'alt' in image_data[0].attrib['alt'] else
                     info_data[0].xpath('./div[@class="title"]/strong')[0].text)

            is_hd = info_data[0].xpath('./div[@class="quality"]')
            is_hd = len(is_hd) == 1 and is_hd[0].text == 'HD'

            number_of_views = info_data[0].xpath('./div[@class="meta-data"]/span[@class="views"]')
            assert len(number_of_views) == 1
            number_of_views = re.findall(r'\d+', number_of_views[0].text)

            added_before_data = info_data[0].xpath('./div[@class="meta-data"]/time')
            assert len(added_before_data) == 1
            additional_data = {'format_time_added_before': added_before_data[0].attrib['datetime']}
            added_before = added_before_data[0].text

            video_length = info_data[0].xpath('./div[@class="meta-data"]/span[@class="duration"]')
            assert len(video_length) == 1
            video_length = self._format_duration(video_length[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  is_hd=is_hd,
                                                  number_of_views=number_of_views,
                                                  additional_data=additional_data,
                                                  added_before=added_before,
                                                  duration=video_length,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
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
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        # sortable videos
        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            params.update(parse_qsl(page_filter.sort_order.value))
        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            params.update(parse_qsl(page_filter.period.value))

        if page_number is not None and page_number != 1:
            params['page'] = page_number
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    # module = HDTubePorn()
    # module = SexVid()
    # module = PornID()
    module = CumNGo()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=False)
