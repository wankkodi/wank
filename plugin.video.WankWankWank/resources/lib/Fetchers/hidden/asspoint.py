# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote_plus

# Regex
import re

# JSON
from ..tools.text_json_manioulations import prepare_json_from_not_formatted_text

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, \
    VideoSource, VideoTypes
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# Heritages
from abc import ABCMeta, abstractmethod

# Generator id
from ..id_generator import IdGenerator


class Base1(PornFetcher):
    metaclass = ABCMeta

    general_filter_preference_mapping = {
        PornFilterTypes.StraightType: '1',
        PornFilterTypes.GayType: '5',
        PornFilterTypes.ShemaleType: '28',
        PornFilterTypes.MemberType: '89',
    }

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    @abstractmethod
    def base_url(self):
        """
        Base site url.
        :return:
        """
        raise NotImplementedError

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/pornstars/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/categories/#tab1'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/videos/straight/all-recent.html'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/videos/straight/all-view.html'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, '/videos/straight/all-popular.html'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/videos/straight/all-rate.html'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/videos/straight/all-length.html'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/tags/video/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', 'straight'),
                                                     (PornFilterTypes.GayType, 'Gay', 'gay'),
                                                     ],
                                 }
        video_params = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most Popular', 'popular'),
                                       (PornFilterTypes.DateOrder, 'Most Recent', 'recent'),
                                       (PornFilterTypes.ViewsOrder, 'Most Viewed', 'view'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rate'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'length'),
                                       ],
                        'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', 'min_width=0'),
                                            (PornFilterTypes.HDQuality, 'HD quality', 'min_width=1280'),
                                            ],
                        'length_filters': ((PornFilterTypes.AllLength, 'Any duration', 'min_duration=0'),
                                           (PornFilterTypes.OneLength, 'Short (0-8 min)', 'min_duration=1-480'),
                                           (PornFilterTypes.TwoLength, 'Med (8-20 min)', 'min_duration=480-1200'),
                                           (PornFilterTypes.ThreeLength, 'Long (20+ min)', 'min_duration=1200'),
                                           ),
                        }
        single_porn_star_params = video_params.copy()
        single_porn_star_params['sort_order'] = \
            [(PornFilterTypes.RelevanceOrder, 'Most Relevant', 'search_order=relevance'),
             (PornFilterTypes.BestOrder, 'Best', 'search_order=date-relevance'),
             (PornFilterTypes.PopularityOrder, 'Most Popular', 'search_order=popularity'),
             (PornFilterTypes.ViewsOrder, 'Most Viewed', 'search_order=views'),
             (PornFilterTypes.DateOrder, 'Most Recent', 'search_order=approval_date'),
             (PornFilterTypes.RatingOrder, 'Top Rated', 'search_order=rating'),
             (PornFilterTypes.LengthOrder, 'By duration', 'search_order=runtime'),
             ]
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         single_tag_args=single_porn_star_params,
                                         single_porn_star_args=single_porn_star_params,
                                         search_args=single_porn_star_params,
                                         video_args=video_params,
                                         )

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="cat-list ac"]/div[@class="item"]')
        res = []
        for category in categories:
            link_data = category.xpath('./div[@class="item-background"]/h2/a')
            if len(link_data) != 1:
                # We have dummy objects...
                continue
            link = self._clear_text(link_data[0].attrib['href'])
            title = self._clear_text(link_data[0].text)

            image = category.xpath('./div[@class="item-background"]/a/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            number_of_videos = category.xpath('./div[@class="item-panel ac"]/div[@class="item-date"]/a/span'
                                              '/span[@class="contentquantity"]/text()')
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0])[0]) if len(number_of_videos) == 1 else None

            number_of_photos = category.xpath('./div[@class="item-panel ac"]/div[@class="item-stats"]/a/span'
                                              '/span[@class="contentquantity"]/text()')
            number_of_photos = int(re.findall(r'\d+', number_of_photos[0])[0]) if len(number_of_photos) == 1 else None
            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               number_of_photos=number_of_photos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = tree.xpath('.//div[@class="cat-list ac"]/div[@class="item"]')
        res = []
        for porn_star in porn_stars:
            link_data = porn_star.xpath('./div[@class="item-background"]/h2/a')
            if len(link_data) != 1:
                # We have dummy objects...
                continue
            link = self._clear_text(link_data[0].attrib['href'])
            title = self._clear_text(link_data[0].text)

            image = porn_star.xpath('./div[@class="item-background"]/a/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
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
        link_data = tree.xpath('.//div[@class="tab-content"]/div[@id="tab1"]//div[@class="category-section"]/li/a')
        links = [self._clear_text(x.attrib['href']) for x in link_data]
        titles = tree.xpath('.//div[@class="tab-content"]//div[@class="category-section"]/li/a/span/text()')
        number_of_videos = [int(re.findall(r'\d+', x.tail)[0]) for x in link_data]
        return links, titles, number_of_videos

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        raw_data = re.findall(r'(?:playerInstance.setup\()(.*?)(?:\);)', tmp_request.text, re.DOTALL)
        raw_data = prepare_json_from_not_formatted_text(raw_data[0])
        res = [(x['label'], x['file']) for x in raw_data['sources']]
        res = [VideoSource(link=x[1], resolution=re.findall(r'(\d+)(?:p*)', x[0])[0],
                           video_type=VideoTypes.VIDEO_REGULAR)
               for x in res]
        res.sort(key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=res)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.PORN_STAR_MAIN,):
            return 1

        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) > 0 and max(pages) == 10:
            # We have potentially more pages...
            page_request = self.get_object_request(category_data, override_page_number=2)
            tree = self.parser.parse(page_request.text)
            pages = self._get_available_pages_from_tree(tree)

        return max(pages) if len(pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//div[@class="pagination"]/a')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumb-list ac"]/div[@class="item"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            if len(link_data) != 1:
                continue
            link = link_data[0].attrib['href']

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            video_preview = video_tree_data.xpath('./a/div[@class="trailer"]/video')
            video_preview = video_preview[0].attrib['src'] if len(video_preview) == 1 else None

            rating = video_tree_data.xpath('./div/span[1]/*')
            assert len(rating) == 1
            rating = rating[0].tail

            added_before = video_tree_data.xpath('./div/span[2]/*')
            assert len(added_before) == 1
            added_before = added_before[0].tail

            number_of_views = video_tree_data.xpath('./div/span[3]/*')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].tail

            video_length = video_tree_data.xpath('./div/span[4]/*')
            assert len(video_length) == 1
            video_length = video_length[0].tail

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  preview_video_link=video_preview,
                                                  duration=self._format_duration(video_length),
                                                  number_of_views=number_of_views,
                                                  rating=rating,
                                                  added_before=added_before,
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
        if true_object.object_type in (PornCategories.LATEST_VIDEO, PornCategories.MOST_VIEWED_VIDEO,
                                       PornCategories.TOP_RATED_VIDEO, PornCategories.POPULAR_VIDEO,
                                       PornCategories.LONGEST_VIDEO, PornCategories.SEARCH_MAIN,
                                       PornCategories.CATEGORY, PornCategories.PORN_STAR):
            split_fetch_url = fetch_base_url.split('/')
            if self.general_filter.current_filters.general.filter_id != PornFilterTypes.StraightType:
                split_fetch_url[4] = self.general_filter.current_filters.general.value
            if page_filter.length.filter_id != PornFilterTypes.AllLength:
                key, value = page_filter.length.value.split('=')
                params[key] = [value]
            if page_filter.quality.filter_id != PornFilterTypes.AllQuality:
                key, value = page_filter.quality.value.split('=')
                params[key] = [value]
            # Sort order
            if true_object.object_type in (PornCategories.CATEGORY,):
                last_prefix = re.findall(r'(.*?)(?:\.html)', split_fetch_url[-1])
                split_last_prefix = last_prefix[0].split('-')
                split_last_prefix[-1] = page_filter.sort_order.value
                split_fetch_url[-1] = '-'.join(split_last_prefix) + '.html'
            elif true_object.object_type in (PornCategories.PORN_STAR, PornCategories.SEARCH_PAGE,
                                             PornCategories.TAG):
                key, value = page_filter.sort_order.value.split('=')
                params[key] = [value]

            fetch_base_url = '/'.join(split_fetch_url)
        elif true_object.object_type in (PornCategories.CATEGORY_MAIN,):
            if self.general_filter.current_filters.general.filter_id in \
                    (PornFilterTypes.StraightType, PornFilterTypes.GayType, PornFilterTypes.ShemaleType,
                     PornFilterTypes.MemberType):
                params['preference'] = self.general_filter_preference_mapping[
                    self.general_filter.current_filters.general.filter_id]

        if page_number is not None and page_number != 1:
            if page_data.super_object.object_type in (PornCategories.TAG, PornCategories.PORN_STAR,
                                                      PornCategories.SEARCH_MAIN):
                fetch_base_url = re.sub(r'/*$', '', fetch_base_url)
                fetch_base_url += '/{d}/'.format(d=page_number)
            else:
                fetch_base_url = re.sub(r'\.html$', '-{d}.html'.format(d=page_number), fetch_base_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}'.format(q=quote_plus(query))


class AssPoint(Base1):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.asspoint.com/'

    def __init__(self, source_name='AssPoint', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(AssPoint, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)


class AsianPornVideos(Base1):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.asianpornmovies.com/'

    def __init__(self, source_name='AsianPornVideos', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(AsianPornVideos, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                              session_id)


class AnalPornVideos(Base1):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.analpornvideos.com/'

    def __init__(self, source_name='AnalPornVideos', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(AnalPornVideos, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                             session_id)


class GhettoTube(Base1):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.ghettotube.com/'

    def __init__(self, source_name='AnalPornVideos', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(GhettoTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)


class PornTV(Base1):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.porntv.com/'

    def __init__(self, source_name='PornTV', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornTV, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)


class YoungPornVideos(Base1):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.youngpornvideos.com/'

    def __init__(self, source_name='YoungPornVideos', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(YoungPornVideos, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                              session_id)


class CartoonPornVideos(Base1):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/characters/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/categories/#tab1'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/videos/straight/all-recent.html'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/videos/straight/all-view.html'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, '/videos/straight/all-popular.html'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/videos/straight/all-rate.html'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/videos/straight/all-length.html'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/tags/video/'),
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.cartoonpornvideos.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': [(PornFilterTypes.StraightType, 'Cartoon', 'straight'),
                                                     ],
                                 }
        video_params = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most Popular', 'popular'),
                                       (PornFilterTypes.DateOrder, 'Most Recent', 'recent'),
                                       (PornFilterTypes.ViewsOrder, 'Most Viewed', 'view'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rate'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'length'),
                                       ],
                        'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', 'min_width=0'),
                                            (PornFilterTypes.HDQuality, 'HD quality', 'min_width=1280'),
                                            ],
                        'length_filters': ((PornFilterTypes.AllLength, 'Any duration', 'min_duration=0'),
                                           (PornFilterTypes.OneLength, 'Short (0-8 min)', 'min_duration=1-480'),
                                           (PornFilterTypes.TwoLength, 'Med (8-20 min)', 'min_duration=480-1200'),
                                           (PornFilterTypes.ThreeLength, 'Long (20+ min)', 'min_duration=1200'),
                                           ),
                        }
        single_porn_star_params = video_params.copy()
        single_porn_star_params['sort_order'] = \
            [(PornFilterTypes.RelevanceOrder, 'Most Relevant', 'search_order=relevance'),
             (PornFilterTypes.BestOrder, 'Best', 'search_order=date-relevance'),
             (PornFilterTypes.PopularityOrder, 'Most Popular', 'search_order=popularity'),
             (PornFilterTypes.ViewsOrder, 'Most Viewed', 'search_order=views'),
             (PornFilterTypes.DateOrder, 'Most Recent', 'search_order=approval_date'),
             (PornFilterTypes.RatingOrder, 'Top Rated', 'search_order=rating'),
             (PornFilterTypes.LengthOrder, 'By duration', 'search_order=runtime'),
             ]
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         single_tag_args=single_porn_star_params,
                                         single_porn_star_args=single_porn_star_params,
                                         search_args=single_porn_star_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='CartoonPornVideos', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(CartoonPornVideos, self).__init__(source_name, source_id, store_dir, data_dir, source_type,
                                                use_web_server, session_id)

    def _update_available_character(self, character_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(character_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = tree.xpath('.//div[@class="cat-list ac"]/div[@class="item"]')
        res = []
        for porn_star in porn_stars:
            link_data = porn_star.xpath('./div[@class="item-background"]/h2/a')
            if len(link_data) != 1:
                # We have dummy objects...
                continue
            link = self._clear_text(link_data[0].attrib['href'])
            title = self._clear_text(link_data[0].text)

            image = porn_star.xpath('./div[@class="item-background"]/a/img')
            assert len(image) == 1
            image = re.sub(r'\n', '', image[0].attrib['src'])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=character_data,
                                               ))

        character_data.add_sub_objects(res)
        return res


class LesbianPornVideos(Base1):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.lesbianpornvideos.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': [(PornFilterTypes.LesbianType, 'Lesbian', 'lesbian'),
                                                     ],
                                 }
        video_params = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most Popular', 'popular'),
                                       (PornFilterTypes.DateOrder, 'Most Recent', 'recent'),
                                       (PornFilterTypes.ViewsOrder, 'Most Viewed', 'view'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rate'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'length'),
                                       ],
                        'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', 'min_width=0'),
                                            (PornFilterTypes.HDQuality, 'HD quality', 'min_width=1280'),
                                            ],
                        'length_filters': ((PornFilterTypes.AllLength, 'Any duration', 'min_duration=0'),
                                           (PornFilterTypes.OneLength, 'Short (0-8 min)', 'min_duration=1-480'),
                                           (PornFilterTypes.TwoLength, 'Med (8-20 min)', 'min_duration=480-1200'),
                                           (PornFilterTypes.ThreeLength, 'Long (20+ min)', 'min_duration=1200'),
                                           ),
                        }
        single_porn_star_params = video_params.copy()
        single_porn_star_params['sort_order'] = \
            [(PornFilterTypes.RelevanceOrder, 'Most Relevant', 'search_order=relevance'),
             (PornFilterTypes.BestOrder, 'Best', 'search_order=date-relevance'),
             (PornFilterTypes.PopularityOrder, 'Most Popular', 'search_order=popularity'),
             (PornFilterTypes.ViewsOrder, 'Most Viewed', 'search_order=views'),
             (PornFilterTypes.DateOrder, 'Most Recent', 'search_order=approval_date'),
             (PornFilterTypes.RatingOrder, 'Top Rated', 'search_order=rating'),
             (PornFilterTypes.LengthOrder, 'By duration', 'search_order=runtime'),
             ]
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         single_tag_args=single_porn_star_params,
                                         single_porn_star_args=single_porn_star_params,
                                         search_args=single_porn_star_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='LesbianPornVideos', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(LesbianPornVideos, self).__init__(source_name, source_id, store_dir, data_dir, source_type,
                                                use_web_server, session_id)


class SexOasis(Base1):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.sexoasis.com/'

    def __init__(self, source_name='SexOasis', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SexOasis, self).__init__(source_name, source_id, store_dir, data_dir, source_type,
                                       use_web_server, session_id)


class TeeniePorn(Base1):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.teenieporn.com/'

    def __init__(self, source_name='TeeniePorn', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(TeeniePorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type,
                                         use_web_server, session_id)


class Base2(Base1):
    metaclass = ABCMeta

    # Lot of similarities with asspoint
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, '/videos/all/all-popular.html'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/videos/all/all-view.html'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/videos/all/all-view.html'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/videos/all/all-length.html'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/videos/all/all-recent.html'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/video/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
        }

    @property
    @abstractmethod
    def base_url(self):
        """
        Base site url.
        :return:
        """
        raise NotImplementedError

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': [(PornFilterTypes.AllType, 'Any type', ''),
                                                     (PornFilterTypes.StraightType, 'Straight', 'straight'),
                                                     (PornFilterTypes.GayType, 'Gay', 'gay'),
                                                     (PornFilterTypes.ShemaleType, 'Shemale', 'shemale'),
                                                     (PornFilterTypes.MemberType, 'Members', 'members'),
                                                     ],
                                 }
        video_params = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most Popular', 'popular'),
                                       (PornFilterTypes.DateOrder, 'Most Recent', 'recent'),
                                       (PornFilterTypes.ViewsOrder, 'Most Viewed', 'view'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rate'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'length'),
                                       ],
                        'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', 'min_width=0'),
                                            (PornFilterTypes.HDQuality, 'HD quality', 'min_width=1280'),
                                            ],
                        'length_filters': ((PornFilterTypes.AllLength, 'Any duration', 'min_duration=0'),
                                           (PornFilterTypes.OneLength, 'Short (0-5 min)', 'min_duration=1-300'),
                                           (PornFilterTypes.TwoLength, 'Med (5-10 min)', 'min_duration=300-600'),
                                           (PornFilterTypes.ThreeLength, 'Long (10+ min)', 'min_duration=600'),
                                           ),
                        }
        single_porn_star_params = video_params.copy()
        single_porn_star_params['sort_order'] = \
            [(PornFilterTypes.RelevanceOrder, 'Most Relevant', 'search_order=relevance'),
             (PornFilterTypes.BestOrder, 'Best', 'search_order=date-relevance'),
             (PornFilterTypes.PopularityOrder, 'Most Popular', 'search_order=popularity'),
             (PornFilterTypes.ViewsOrder, 'Most Viewed', 'search_order=views'),
             (PornFilterTypes.DateOrder, 'Most Recent', 'search_order=approval_date'),
             (PornFilterTypes.RatingOrder, 'Top Rated', 'search_order=rating'),
             (PornFilterTypes.LengthOrder, 'By duration', 'search_order=runtime'),
             ]
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         single_tag_args=single_porn_star_params,
                                         single_porn_star_args=single_porn_star_params,
                                         search_args=single_porn_star_params,
                                         video_args=video_params,
                                         )

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="item"]/div[@class="itemIn"]')
        res = []
        for category in categories:
            link_data = category.xpath('./h2/a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            title = self._clear_text(link_data[0].text) if link_data[0].text is not None else 'Unknown category'

            image = category.xpath('./a/img')
            assert len(image) == 1
            image = image[0].attrib['src']

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
        return [int(x.text) for x in tree.xpath('.//div[@class="pagination"]/a/span')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="item"]/div[@class="itemIn"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            if len(link_data) != 1:
                continue
            link = link_data[0].attrib['href']

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['title']
            flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                           for d in range(1, int(re.findall(r'(?:\')(\d+)(?:\')',
                                                            image_data[0].attrib['onmouseover'])[0]))]

            rating = video_tree_data.xpath('./div/div[@class="star_static stars"]/ul/li')
            assert len(rating) == 1
            rating = re.findall(r'\d+%', rating[0].attrib['style'])[0]

            video_length = video_tree_data.xpath('./div/div[@class="infoBox"]/span[1]')
            assert len(video_length) == 1
            video_length = video_length[0].text
            number_of_views = video_tree_data.xpath('./div/div[@class="infoBox"]/span[2]')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            added_before = video_tree_data.xpath('./div/div[@class="infoBox"]/span[3]')
            assert len(added_before) == 1
            added_before = added_before[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  duration=self._format_duration(video_length),
                                                  number_of_views=number_of_views,
                                                  rating=rating,
                                                  added_before=added_before,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res


# class BigBoobsTube(Base2):
#
#     @property
#     def base_url(self):
#         """
#         Base site url.
#         :return:
#         """
#         return 'https://www.bigboobstube.com/'
#
#     def __init__(self, source_name='BigBoobsTube', source_id=0, store_dir='.', data_dir='../Data'):
#         """
#         C'tor
#         :param source_name: save directory
#         """
#         super().__init__(source_name, source_id, store_dir, data_dir)
#


class HoodTube(Base2):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.hoodtube.com/'

    def __init__(self, source_name='HoodTube', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HoodTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type,
                                       use_web_server, session_id)


class PornTitan(Base2):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.porntitan.com/'

    def __init__(self, source_name='PornTitan', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornTitan, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)


class YoungPorno(Base2):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.youngporno.com/'

    def __init__(self, source_name='YoungPorno', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(YoungPorno, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)


class SuzisPorn(Base2):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.suzisporn.com/'

    def __init__(self, source_name='SuzisPorn', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SuzisPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)


class MobilePornMovies(Base2):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.mobilepornmovies.com/'

    def __init__(self, source_name='MobilePornMovies', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(MobilePornMovies, self).__init__(source_name, source_id, store_dir, data_dir, source_type,
                                               use_web_server, session_id)


class MovieShark(Base2):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.movieshark.com/'

    def __init__(self, source_name='MovieShark', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(MovieShark, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)


class MovieTitan(Base2):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.movietitan.com/'

    def __init__(self, source_name='MovieTitan', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(MovieTitan, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)


class XJizz(Base2):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.xjizz.com/'

    def __init__(self, source_name='XJizz', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(XJizz, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                    session_id)


# class CartoonSexTubes(BigBoobsTube):
#     @property
#     def base_url(self):
#         """
#         Base site url.
#         :return:
#         """
#         return 'https://www.cartoonsextube.com/'
#
#     def _set_video_filter(self):
#         """
#         Sets the video filters and the default values of the current filters
#         :return:
#         """
#         self._video_filters = VideoFilter(data_dir=self.fetcher_data_dir,
#                                           general_filter=((StraightType, 'Straight', 'straight'),
#                                                           ),
#                                           length_filters=((AllLength, 'Any duration', 'min_duration=0'),
#                                                           (OneLength, 'Short (0-5 min)', 'min_duration=1-300'),
#                                                           (TwoLength, 'Med (5-10 min)', 'min_duration=300-600'),
#                                                           (ThreeLength, 'Long (10+ min)', 'min_duration=600'),
#                                                           ),
#                                           quality_filters=((AllQuality, 'All quality', 'min_width=0'),
#                                                            (HDQuality, 'HD quality', 'min_width=1280'),
#                                                            )
#                                           )
#
#     def __init__(self, source_name='CartoonSexTubes', source_id=0, store_dir='.', data_dir='../Data'):
#         """
#         C'tor
#         :param source_name: save directory
#         """
#         super().__init__(source_name, source_id, store_dir, data_dir)
#
#
# class XXXMilfs(BigBoobsTube):
#     @property
#     def base_url(self):
#         """
#         Base site url.
#         :return:
#         """
#         return 'https://www.xxxmilfs.com/'
#
#     def __init__(self, source_name='XXXMilfs', source_id=0, store_dir='.', data_dir='../Data'):
#         """
#         C'tor
#         :param source_name: save directory
#         """
#         super().__init__(source_name, source_id, store_dir, data_dir)
#
#     def _set_video_filter(self):
#         """
#         Sets the video filters and the default values of the current filters
#         :return:
#         """
#         self._video_filters = VideoFilter(data_dir=self.fetcher_data_dir,
#                                           general_filter=((StraightType, 'Straight', ''),
#                                                           ),
#                                           )
#
#     def _update_available_categories(self, category_data):
#         """
#         Fetches all the available categories.
#         :return: Object of all available shows (JSON).
#         """
#         page_request = self.get_object_request(category_data)
#         tree = self.parser.parse(page_request.text)
#         categories = tree.xpath('.//div[@style="width: 1000px"]/div[@style="width: 240px; float: left; text-align: '
#                                 'center; margin: 4px; padding: 0px; border: 1px solid #ECECD3"]')
#         res = []
#         for category in categories:
#             link_data = category.xpath('./a')
#             assert len(link_data) > 0
#             link = link_data[0].attrib['href']
#
#             title_data = category.xpath('./a/font/b')
#             assert len(title_data) > 0
#             title = self._clear_text(title_data[0].text) if title_data[0].text is not None else 'Unknown category'
#
#             image = category.xpath('./a/img')
#             assert len(image) == 1
#             image = image[0].attrib['src']
#
#             res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
#                                                obj_id=link,
#                                                url=urljoin(self.base_url, link),
#                                                image_link=image,
#                                                title=title,
#                                                object_type=Category,
#                                                super_object=category_data,
#                                                ))
#
#         category_data.add_sub_objects(res)
#         return res
#
#     def _get_available_pages_from_tree(self, tree):
#         """
#         In binary looks for the available pages from current page tree.
#         :param tree: Current page tree.
#         :return: List of available trees
#         """
#         return [int(x.text) for x in tree.xpath('.//div[@class="pages2"]/ul/li/a')
#                 if x.text is not None and x.text.isdigit()]
#
#     def get_videos_data(self, object_data):
#         """
#         Gets videos data for the given category.
#         :param object_data: Page data.
#         :return:
#         """
#         page_request = self.get_object_request(object_data)
#         tree = self.parser.parse(page_request.text)
#         videos = tree.xpath('.//div[@class="thumbs"]/div[@class="th"]/div[@class="thumb"]')
#         if len(videos) > 0:
#             method = 1
#         else:
#             # We try another method
#             videos = [x for x in tree.xpath('.//div[@class="left-6"]/div')
#                       if 'class' in x.attrib and 'group' in x.attrib['class']]
#             method = 2
#         res = []
#         if method == 1:
#             for video_tree_data in videos:
#                 link_data = video_tree_data.xpath('./a')
#                 if len(link_data) != 1:
#                     continue
#                 link = link_data[0].attrib['href']
#
#                 image_data = video_tree_data.xpath('./div[@class="t"]/a/img')
#                 assert len(image_data) == 1
#                 image = image_data[0].attrib['src']
#                 flip_images = [re.sub(r'main.jpg$', '{d}.jpg'.format(d=d), image)
#                                for d in range(1, int(re.findall(r'(?:\')(\d+)(?:\')',
#                                                                 image_data[0].attrib['onmouseover'])[0]))]
#                 title = image_data[0].attrib['alt']
#
#                 rating = video_tree_data.xpath('./div[@class="desc"]/div[@class="star_static"]/ul/li')
#                 assert len(rating) == 1
#                 rating = re.findall(r'\d+%', rating[0].attrib['style'])[0]
#
#                 video_length = video_tree_data.xpath('./div[@class="desc"]/p[@class="lenght"]')
#                 assert len(video_length) == 1
#                 video_length = video_length[0].text
#
#                 number_of_views = video_tree_data.xpath('./div[@class="desc"]/p[@class="views"]')
#                 assert len(number_of_views) == 1
#                 number_of_views = number_of_views[0].text + number_of_views[0].xpath('./span')[0].text
#
#                 added_before = video_tree_data.xpath('./div[@class="desc"]/p[@class="ago"]')
#                 assert len(added_before) == 1
#                 added_before = added_before[0].text
#
#                 video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
#                                                       obj_id=link,
#                                                       url=urljoin(self.base_url, link),
#                                                       title=title,
#                                                       image_link=image,
#                                                       flip_images_link=flip_images,
#                                                       duration=self._format_duration(video_length),
#                                                       number_of_views=number_of_views,
#                                                       rating=rating,
#                                                       added_before=added_before,
#                                                       object_type=Video,
#                                                       super_object=object_data,
#                                                       )
#                 res.append(video_data)
#         else:
#             for video_tree_data in videos:
#                 link_data = video_tree_data.xpath('./div[@class="gr-l"]/div[@class="grab-lx"]/a')
#                 if len(link_data) != 1:
#                     continue
#                 link = link_data[0].attrib['href']
#
#                 image_data = video_tree_data.xpath('./div[@class="gr-l"]/div[@class="grab-lx"]/a/img')
#                 assert len(image_data) == 1
#                 image = image_data[0].attrib['src']
#                 title = image_data[0].attrib['alt']
#                 flip_images = [re.sub(r'main.jpg$', '{d}.jpg'.format(d=d), image)
#                                for d in range(1, int(re.findall(r'(?:\')(\d+)(?:\')',
#                                                                 image_data[0].attrib['onmouseover'])[0]) + 1)]
#
#                 video_info = video_tree_data.xpath('./div[@class="gr-l"]/div[@class="grab-rx"]/'
#                                                    'p[@class="gr-st2"]//span')
#                 assert len(video_info) == 3
#                 video_length = video_info[0].text
#                 added_before = video_info[1].text
#                 number_of_views = video_info[2].text
#
#                 rating = video_tree_data.xpath('./div[@class="gr-l"]/div[@class="grab-rx"]/div[@class="star_static"]/'
#                                                'ul/li')
#                 assert len(rating) == 1
#                 rating = re.findall(r'\d%', rating[0].attrib['style'])[0]
#
#                 category_data = video_tree_data.xpath('./div[@class="gr-r"]/p//a')
#                 assert len(category_data) >= 2
#                 tag_data = video_tree_data.xpath('./div[@class="gr-r"]/div[@class="tags2"]/div/a')
#                 assert len(category_data) > 0
#                 additional_data = {'main_category': {'title': category_data[0].text,
#                                                      'link': category_data[0].attrib['href']},
#                                    'categories': [{'title': x.text,
#                                                    'link': x.attrib['href']} for x in category_data[1:]],
#                                    'tags': [{'title': x.xpath('./span')[0].text,
#                                              'link': x.attrib['href']} for x in tag_data]
#                                    }
#
#                 video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
#                                                       obj_id=link,
#                                                       url=urljoin(self.base_url, link),
#                                                       title=title,
#                                                       image_link=image,
#                                                       flip_images_link=flip_images,
#                                                       duration=self._format_duration(video_length),
#                                                       number_of_views=number_of_views,
#                                                       rating=rating,
#                                                       added_before=added_before,
#                                                       additional_data=additional_data,
#                                                       object_type=Video,
#                                                       super_object=object_data,
#                                                       )
#                 res.append(video_data)
#
#         object_data.add_sub_objects(res)
#         return res


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    # module = AssPoint()
    # module = AnalPornVideos()
    # module = AsianPornVideos()
    # module = GhettoTube()
    # module = PornTV()
    # module = YoungPornVideos()
    module = LesbianPornVideos()
    # module = SexOasis()
    # module = TeeniePorn()
    # module = CartoonPornVideos()
    # module = BigBoobsTube()
    # module = PornTitan()
    # module = YoungPorno()
    # module = SuzisPorn()
    # module = MobilePornMovies()
    # module = MovieShark()
    # module = MovieTitan()
    # module = XJizz()
    # module = CartoonSexTubes()
    # module = XXXMilfs()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=False)
