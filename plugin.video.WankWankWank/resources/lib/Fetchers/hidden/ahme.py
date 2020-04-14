# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote_plus

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, \
    VideoSource, VideoTypes
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# datetime
from datetime import datetime

# Generator id
from ..id_generator import IdGenerator


class AhMe(PornFetcher):
    # todo: add live cams...
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.ah-me.com/channels/',
            PornCategories.LATEST_VIDEO: 'https://www.ah-me.com/most-recent/page1.html',
            PornCategories.FAVORITE_VIDEO: 'https://www.ah-me.com/mostfavorites/page1.html',
            PornCategories.HD_VIDEO: 'https://www.ah-me.com/high-definition/page1.html',
            PornCategories.TOP_RATED_VIDEO: 'https://www.ah-me.com/top-rated/page1.html',
            # PornCategories.MOST_VIEWED_VIDEO: 'https://www.ah-me.com/most-viewed/page1.html',
            PornCategories.LONGEST_VIDEO: 'https://www.ah-me.com/long-movies/page1.html',
            PornCategories.SEARCH_MAIN: 'https://www.ah-me.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
            PornCategories.HD_VIDEO: PornFilterTypes.HDOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.ah-me.com/'

    def __init__(self, source_name='AhMe', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(AhMe, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server, session_id)

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': ((PornFilterTypes.StraightType, 'Straight', None),
                                                     (PornFilterTypes.GayType, 'Gay', 'gay'),
                                                     (PornFilterTypes.ShemaleType, 'Shemale', 'shemale'),
                                                     ),
                                 }
        video_params = {'sort_order': ((PornFilterTypes.DateOrder, 'Recent videos', 'most-recent'),
                                       (PornFilterTypes.LengthOrder, 'By duration', 'long-movies'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                       # (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                       (PornFilterTypes.QualityOrder, 'High definition', 'high-definition'),
                                       (PornFilterTypes.FavorOrder, 'Most favorite', 'mostfavorites'),
                                       ),
                        }
        search_params = {'sort_order': ((PornFilterTypes.RelevanceOrder, 'Most relevant', None),
                                        (PornFilterTypes.DateOrder, 'Most recent', 'most-recent'),
                                        (PornFilterTypes.LengthOrder, 'By duration', 'long-movies'),
                                        (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                        ),
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         video_args=video_params,
                                         search_args=search_params,
                                         )

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="moviec category"]/div[@class="thumb-wrap"]')
        res = []
        for category in categories:
            image = category.xpath('./a/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            title_data = category.xpath('./p[@class="title"]/a')
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].text)
            link = title_data[0].attrib['href']

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        assert tmp_request.ok
        tree = self.parser.parse(tmp_request.text)
        videos = tree.xpath('.//div[@class="video-container"]')
        assert len(videos) > 0
        res = [(x.attrib['data-size'], x.attrib['data-src']) for x in videos]
        res.sort(key=lambda x: int(''.join(re.findall(r'(\d+)(?:p*)', x[0]))), reverse=True)
        params = {'rnd': int(datetime.timestamp(datetime.now()) * 1000)}
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        self.session.cookies.update({re.findall(r'sk_\d+', res[0][1])[0]: re.findall(r'(?:key=)(.*?)(?:,)',
                                                                                     res[0][1])[0]})
        return VideoNode(video_sources=[VideoSource(link=x[1], size=x[0], video_type=VideoTypes.VIDEO_REGULAR)
                                        for x in res],
                         headers=headers, params=params, cookies=self.session.cookies)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN,):
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
        return [int(x.text) for x in tree.xpath('.//div[@class="pages-nav"]/ul/li/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumbs-container"]/div[@data-type="movie"]/div[@class="thumb-wrap"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']
            video_preview = link_data[0].attrib['data-preview'] if 'data-preview' in link_data[0].attrib else None

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            is_hd = video_tree_data.xpath('./img[@class="icon-hd"]')
            is_hd = len(is_hd) == 1

            video_length = video_tree_data.xpath('./p[@class="title"]/span')
            assert len(video_length) == 1
            video_length = video_length[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  preview_video_link=video_preview,
                                                  is_hd=is_hd,
                                                  duration=self._format_duration(video_length),
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
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

        # Take care about the filters
        split_fetch_url = fetch_base_url.split('/')
        general_filter = self.general_filter.current_filters.general
        if general_filter.filter_id != PornFilterTypes.StraightType:
            if general_filter.value is not None and split_fetch_url[3] != general_filter.value:
                split_fetch_url.insert(3, general_filter.value)

        # We remove page number from the suffix
        if page_number is not None and page_number != 1:
            if true_object.object_type in (PornCategories.PORN_STAR_MAIN, PornCategories.PORN_STAR):
                if split_fetch_url[-1].isdigit():
                    split_fetch_url.pop(-1)
            else:
                if len(re.findall(r'page\d+\.html$', split_fetch_url[-1])) > 0:
                    split_fetch_url[-1] = ''

        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            split_fetch_url.insert(-1, page_filter.sort_order.value)
        if page_filter.added_before.value is not None:
            split_fetch_url.insert(-1, page_filter.added_before.value)
        if page_filter.length.value is not None:
            split_fetch_url.insert(-1, page_filter.length.value)
        if page_filter.quality.value is not None:
            split_fetch_url.insert(-1, page_filter.quality.value)

        # if true_object.object_type == CATEGORY_MAIN:
        #     # We have a Porn star selection
        #     sort_order = page_filter.sort_order
        #     if len(sort_order.value) > 0:
        #         split_fetch_url.insert(-1, sort_order.value)
        # elif true_object.object_type == PORN_STAR_MAIN:
        #     # We have a porn star selection
        #     sort_order = page_filter.sort_order
        #     if len(sort_order.value) > 0:
        #         split_fetch_url.insert(-1, sort_order.value)
        # elif true_object.object_type == PORN_STAR:
        #     # We have a single porn star page
        #     sort_order = page_filter.sort_order
        #     if len(sort_order.value) > 0:
        #         split_fetch_url.insert(-1, sort_order.value)
        # elif true_object.object_type in (CATEGORY, SEARCH_MAIN, FAVORITE_VIDEO, HD_VIDEO, LATEST_VIDEO,
        #                                  TOP_RATED_VIDEO, LONGEST_VIDEO, MOST_VIEWED_VIDEO):
        #     # We have a single porn star page
        #     sort_order = page_filter.sort_order
        #     if (
        #             sort_order.value is not None and
        #             all(true_object.object_type not in (FAVORITE_VIDEO, HD_VIDEO, LATEST_VIDEO, TOP_RATED_VIDEO,
        #                                                 LONGEST_VIDEO, MOST_VIEWED_VIDEO))
        #     ):
        #         split_fetch_url.insert(-1, sort_order.value)
        #     added_before_filter = page_filter.added_before
        #     if added_before_filter.value is not None:
        #         split_fetch_url.insert(-1, added_before_filter.value)
        #     length_filter = page_filter.length
        #     if length_filter.value is not None:
        #         split_fetch_url.insert(-1, length_filter.value)
        #     quality_filter = page_filter.quality
        #     if quality_filter.value is not None:
        #         split_fetch_url.insert(-1, quality_filter.value)

        # Append page number
        if page_number is not None and page_number != 1:
            if true_object.object_type in (PornCategories.PORN_STAR_MAIN, PornCategories.PORN_STAR):
                split_fetch_url.insert(-1, str(page_number))
            else:
                split_fetch_url.insert(-1, 'page{d}.html'.format(d=page_number))
                if len(split_fetch_url[-1]) == 0:
                    split_fetch_url.pop(-1)

        fetch_base_url = '/'.join(split_fetch_url)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + quote_plus(query) + '/'


class SunPorno(AhMe):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.sunporno.com/channels/',
            PornCategories.PORN_STAR_MAIN: 'https://www.sunporno.com/pornstars/',
            PornCategories.LATEST_VIDEO: 'https://www.sunporno.com/most-recent/',
            PornCategories.FAVORITE_VIDEO: 'https://www.sunporno.com/mostfavorites/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.sunporno.com/top-rated/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.sunporno.com/most-viewed/',
            PornCategories.LONGEST_VIDEO: 'https://www.sunporno.com/long-movies/',
            PornCategories.SEARCH_MAIN: 'https://www.sunporno.com/search/',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.sunporno.com/'

    def __init__(self, source_name='SunPorno', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SunPorno, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': ((PornFilterTypes.StraightType, 'Straight', None),
                                                     (PornFilterTypes.GayType, 'Gay', 'gay'),
                                                     (PornFilterTypes.ShemaleType, 'Shemale', 'shemale'),
                                                     ),
                                 }
        category_params = {'sort_order': ((PornFilterTypes.ViewsOrder, 'Most viewed', None),
                                          (PornFilterTypes.AlphabeticOrder, 'A-Z listing', 'name'),
                                          (PornFilterTypes.DateOrder, 'Recently updated', 'most-recent'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'movie-count'),
                                          ),
                           }
        porn_stars_params = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Most popular', 'most-viewed'),
                                            (PornFilterTypes.AlphabeticOrder, 'A-Z listing', 'a-z/all'),
                                            (PornFilterTypes.DateOrder, 'Recent pornstars', 'most-recent'),
                                            ),
                             }
        porn_star_params = {'sort_order': ((PornFilterTypes.DateOrder, 'By date', None),
                                           (PornFilterTypes.LengthOrder, 'By duration', 'duration'),
                                           (PornFilterTypes.PopularityOrder, 'By popularity', 'popularity'),
                                           ),
                            }
        video_params = {'added_before_filters': ((PornFilterTypes.AllAddedBefore, 'All time', None),
                                                 (PornFilterTypes.OneAddedBefore, 'Last 2 days', 'date-last-days'),
                                                 (PornFilterTypes.TwoAddedBefore, 'Last week', 'date-last-week'),
                                                 (PornFilterTypes.ThreeAddedBefore, 'Last month', 'date-last-month'),
                                                 (PornFilterTypes.FourAddedBefore, 'Last year', 'date-last-year'),
                                                 ),
                        'length_filters': ((PornFilterTypes.AllLength, 'Any duration', None),
                                           (PornFilterTypes.OneLength, '0-10 min', 'length-0-10'),
                                           (PornFilterTypes.TwoLength, '10-30 min', 'length-10-30'),
                                           (PornFilterTypes.ThreeLength, '30+ min', 'length-30-50'),
                                           ),
                        'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', None),
                                            (PornFilterTypes.HDQuality, 'HD quality', 'hd'),
                                            ),
                        'sort_order': ((PornFilterTypes.DateOrder, 'Recent videos', 'most-recent'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                       (PornFilterTypes.LengthOrder, 'By duration', 'long-movies'),
                                       ),
                        }
        search_params = video_params.copy()
        search_params['sort_order'] = ((PornFilterTypes.RelevanceOrder, 'By relevance', None),
                                       (PornFilterTypes.DateOrder, 'Recent videos', 'most-recent'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                       (PornFilterTypes.LengthOrder, 'By duration', 'long-movies'),
                                       )

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         categories_args=category_params,
                                         porn_stars_args=porn_stars_params,
                                         single_porn_star_args=porn_star_params,
                                         single_category_args=video_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumb-container with-title moviec cat"]/div')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image = category.xpath('./a/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            title_data = category.xpath('./h3[@class="movie-title"]/a/span')
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="starec"]/div[@class="thumb-wrap"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = category.xpath('./div[@class="thumbscale"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="thumb-activity"]/p[@class="videos"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//ul[@id="pagination"]/li/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumbs-container"]/div[@data-type="movie"]/div')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']
            video_preview = urljoin(page_data.url, link_data[0].attrib['data-preview']) \
                if 'data-preview' in link_data[0].attrib else None

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            is_hd = video_tree_data.xpath('./a/span[@class="icon-hd"]')
            is_hd = len(is_hd) == 1

            video_length = video_tree_data.xpath('./p[@class="btime"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            number_of_views = video_tree_data.xpath('./span[@class="thumb-activity"]/span[@class="bviews"]')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            added_before = video_tree_data.xpath('./span[@class="thumb-activity"]/span[@class="ago"]')
            added_before = added_before[0].text if len(added_before) == 1 else None

            rating = (video_tree_data.xpath('./span[@class="thumb-activity"]/span[@class="brating r-green "]') +
                      video_tree_data.xpath('./span[@class="thumb-activity"]/span[@class="brating r-red "]')
                      )
            rating = rating[0].text if len(rating) == 1 else None

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  preview_video_link=video_preview,
                                                  is_hd=is_hd,
                                                  duration=self._format_duration(video_length),
                                                  number_of_views=number_of_views,
                                                  added_before=added_before,
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    # module = AhMe()
    module = SunPorno()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=False)
