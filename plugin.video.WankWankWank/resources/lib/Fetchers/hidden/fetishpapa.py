# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote_plus

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# JSON
from ..tools.text_json_manioulations import prepare_json_from_not_formatted_text

# Generator id
from ..id_generator import IdGenerator

# Abstract
from abc import ABCMeta, abstractmethod


class BaseFetcher(PornFetcher):
    metaclass = ABCMeta

    @property
    def object_urls(self):
        return {
            PornCategories.TAG_MAIN: urljoin(self.base_url, 'tags/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, 'models/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, 'videos/top-rated/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, 'videos/newest/'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, 'videos/most-popular/'),
            PornCategories.TRENDING_VIDEO: urljoin(self.base_url, ''),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, 'videos/longest/'),
            PornCategories.MOST_DISCUSSED_VIDEO: urljoin(self.base_url, 'videos/comment/'),
            PornCategories.RANDOM_VIDEO: urljoin(self.base_url, 'videos/random/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, 'search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.TRENDING_VIDEO: PornFilterTypes.TrendingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
            PornCategories.RANDOM_VIDEO: PornFilterTypes.RandomOrder,
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
        porn_stars_filters = {'sort_order': [(PornFilterTypes.FavorOrder, 'User Favorite', 'ms_favorites'),
                                             (PornFilterTypes.AlphabeticOrder, 'Alphabet', 'm_name'),
                                             (PornFilterTypes.RatingOrder, 'Top rated', 'm_rating_for_sort'),
                                             (PornFilterTypes.DateOrder, 'Date Added', 'm_created'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'ms_videos'),
                                             (PornFilterTypes.NumberOfGalleriesOrder, 'Most Galleries', 'ms_galleries'),
                                             (PornFilterTypes.CommentsOrder, 'Most Comments', 'ms_comments'),
                                             ],
                              }
        video_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most Popular', 'most-popular'),
                                        (PornFilterTypes.TrendingOrder, 'Trending', 'best-recent'),
                                        (PornFilterTypes.DateOrder, 'Date Added', 'newest'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                        (PornFilterTypes.CommentsOrder, 'Comments', 'comment'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        (PornFilterTypes.RandomOrder, 'Random', 'random'),
                                        ],
                         'period_filters': ([(PornFilterTypes.OneDate, 'Today', 'today'),
                                             (PornFilterTypes.TwoDate, 'Yesterday', 'yesterday'),
                                             (PornFilterTypes.ThreeDate, 'Daily', 'daily'),
                                             (PornFilterTypes.AllDate, 'All time', 'all-time'),
                                             ],
                                            [('sort_order', [PornFilterTypes.PopularityOrder])]
                                            ),
                         'comments_filters': ([(PornFilterTypes.OneComments, 'Last comments first', 'last'),
                                               (PornFilterTypes.TwoComments, 'Trending comments first', 'trending'),
                                               (PornFilterTypes.ThreeComments, 'Most commented first', 'most'),
                                               ],
                                              [('sort_order', [PornFilterTypes.CommentsOrder, ])]
                                              ),

                         'quality_filters': [(PornFilterTypes.AllQuality, 'All', None),
                                             (PornFilterTypes.HDQuality, 'HD', 'hd'),
                                             ],
                         'length_filters': [(PornFilterTypes.AllLength, 'All durations', 'all'),
                                            (PornFilterTypes.OneLength, 'Short', 'short'),
                                            (PornFilterTypes.TwoLength, 'Normal', 'normal'),
                                            (PornFilterTypes.ThreeLength, 'Long', 'long'),
                                            ]
                         }
        search_filters = video_filters.copy()
        search_filters['sort_order'] = [(PornFilterTypes.RelevanceOrder, 'Relevancy', 're'),
                                        (PornFilterTypes.PopularityOrder, 'Most Popular', 'mw'),
                                        (PornFilterTypes.TrendingOrder, 'Trending', 'br'),
                                        (PornFilterTypes.DateOrder, 'Date Added', 'mr'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'tr'),
                                        (PornFilterTypes.CommentsOrder, 'Comments', 'col'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'lg'),
                                        (PornFilterTypes.RandomOrder, 'Random', 'rd'),
                                        ]
        search_filters.pop('comments_filters')
        search_filters['period_filters'] = ([(PornFilterTypes.OneDate, 'Today', ''),
                                             (PornFilterTypes.TwoDate, 'Yesterday', 'y'),
                                             (PornFilterTypes.ThreeDate, 'Daily', 'd'),
                                             (PornFilterTypes.AllDate, 'All time', 'a'),
                                             ],
                                            [('sort_order', [PornFilterTypes.PopularityOrder])]
                                            )
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filters,
                                         single_tag_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="models-list"]//li[@class="modelspot modelItem"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="wrapper"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos_data = category.xpath('./div[@class="info "]/span[@class="fa fa-fw fa-video-camera"]')
            assert len(number_of_videos_data) == 1
            raw_number_of_videos = self._clear_text(number_of_videos_data[0].tail)
            raw_number_of_videos = re.sub(r'\.\dk', lambda x: x[0][1] + '00', raw_number_of_videos)
            number_of_videos = int(raw_number_of_videos)

            number_of_galleries_data = category.xpath('./div[@class="info "]/span[@class="fa fa-fw fa-camera"]')
            assert len(number_of_galleries_data) == 1
            raw_number_of_galleries = self._clear_text(number_of_galleries_data[0].tail)
            raw_number_of_galleries = re.sub(r'\.\dk', lambda x: x[0][1] + '00', raw_number_of_galleries)
            number_of_galleries = int(raw_number_of_galleries)

            number_of_subscribers_data = category.xpath('./div[@class="info "]/span[@class="fa fa-user fa-fw"]')
            assert len(number_of_subscribers_data) == 1
            raw_number_of_subscribers = self._clear_text(number_of_subscribers_data[0].tail)
            raw_number_of_subscribers = re.sub(r'\.\dk', lambda x: x[0][1] + '00', raw_number_of_subscribers)
            number_of_subscribers = int(raw_number_of_subscribers)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               number_of_photos=number_of_galleries,
                                               number_of_subscribers=number_of_subscribers,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    # # Obsolete
    # def _update_available_general_tags(self, tag_data, object_type):
    #     """
    #     Fetches all the available categories.
    #     :return: Object of all available shows (JSON).
    #     """
    #     page_request = self.get_object_request(tag_data)
    #     tree = self.parser.parse(page_request.text)
    #     categories = tree.xpath('.//div[@class="default-padding"]/div[@class="pull-left text-left"]/a')
    #     res = []
    #     for category in categories:
    #         link = category.attrib['href']
    #         title = self._clear_text(category.text)
    #
    #         number_of_videos = category.xpath('./span[@class="tag-badge"]')
    #         assert len(number_of_videos) == 1
    #         number_of_videos = int(re.sub('[\r\n\t ,]*', '', self._clear_text(number_of_videos[0].text)))
    #
    #         res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
    #                                            obj_id=link,
    #                                            url=urljoin(self.base_url, link),
    #                                            title=title,
    #                                            number_of_videos=number_of_videos,
    #                                            object_type=object_type,
    #                                            super_object=tag_data,
    #                                            ))
    #
    #     tag_data.add_sub_objects(res)
    #     return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles. The fetched objects MUST be sorted wrt title.
        :param page_request: Page request.
        :return:
        """
        res = [(urljoin(self.base_url, x['link']), x['name'], int(x['videos'].replace(',', '')))
               for x in page_request.json()]
        links, titles, number_of_videos = zip(*res)
        return links, titles, number_of_videos

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        request_data = re.findall(r'(?:sources: )({.*?})(?:,\n)', tmp_request.text, re.DOTALL)
        request_data = prepare_json_from_not_formatted_text(request_data[0])
        videos = sorted((VideoSource(link=x['src'].replace('\\/', '/'), resolution=re.findall(r'\d+', x['desc'])[0])
                         for x in request_data['mp4']),
                        key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN,):
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
        return [int(re.findall(r'(\d+)(?:/$|/\?.*$)', x.attrib['href'])[0])
                for x in tree.xpath('.//div[@class="pagination"]/a')
                if 'href' in x.attrib is not None and len(re.findall(r'(\d+)(?:/$|/\?.*$)', x.attrib['href'])) > 0] + \
               [int(re.findall(r'(?:page=)(\d+)', x.attrib['href'])[0])
                for x in tree.xpath('.//div[@class="pagination no-popup"]/a')
                if 'href' in x.attrib is not None and len(re.findall(r'(?:page=)(\d+)', x.attrib['href'])) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//ul[@class="block ul-no-dots"]/li/div[@class="thumb vidItem"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data)
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title']

            image_data = video_tree_data.xpath('./span[@class="thumb-inner-wrapper"]/a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            resolution = video_tree_data.xpath('./div[@class="fs11 viddata flr time-label-wrapper"]/'
                                               'span[@class="text-active bold"]')
            if len(resolution) == 1:
                resolution = resolution[0].text
                is_hd = True
            else:
                resolution = '360p'
                is_hd = False

            video_length = video_tree_data.xpath('./div[@class="fs11 viddata flr time-label-wrapper"]/span')
            assert len(video_length) >= 1
            video_length = self._clear_text(video_length[-1].text)

            rating = video_tree_data.xpath('./div[@class="videoRating"]/div')
            assert len(rating) == 1
            rating = rating[0].attrib['title']

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  resolution=resolution,
                                                  is_hd=is_hd,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
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
        if true_object.object_type in (PornCategories.PORN_STAR_MAIN,):
            params['sorterMode'] = [1]
            params['sorterColumn'] = [page_filter.sort_order.value]
            params['page'] = [page_number if page_number is not None else 1]

        elif true_object.object_type in (PornCategories.TAG_MAIN,):
            headers = {
                'Accept': '*/*',
                'Cache-Control': 'max-age=0',
                'Referer': page_data.url,
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
            fetch_base_url = urljoin(page_data.url, 'json/')
        else:
            split_url = fetch_base_url.split('/')
            if true_object.object_type in (PornCategories.TAG_MAIN, PornCategories.VIDEO, PornCategories.PORN_STAR,
                                           PornCategories.VIDEO):
                pass
            else:
                if page_filter.quality.value is not None:
                    split_url[3] = page_filter.quality.value
                    if len(split_url) == 4:
                        # We want to have '/' at the end of the url
                        split_url.append('')

                if true_object.object_type in (PornCategories.TAG,):
                    split_url = split_url[:5] + ['']
                    split_url.insert(-1, page_filter.sort_order.value)
                    if page_filter.sort_order.filter_id in (PornFilterTypes.PopularityOrder,):
                        split_url.insert(-1, page_filter.period.value)
                    elif page_filter.sort_order.filter_id in (PornFilterTypes.CommentsOrder,):
                        split_url.insert(-1, page_filter.comments.value)
                elif true_object.object_type == PornCategories.SEARCH_MAIN:
                    params['sort'] = [page_filter.sort_order.value]
                    params['quality'] = [page_filter.quality.value] if page_filter.quality.value is not None else ''
                    if page_filter.sort_order.filter_id == PornFilterTypes.PopularityOrder:
                        params['so'] = [page_filter.period.value]
                else:
                    conditions = self.get_proper_filter(page_data).conditions
                    true_sort_filter_id = self._default_sort_by[true_object.object_type] \
                        if true_object.object_type in self._default_sort_by \
                        else page_filter.sort_order.filter_id

                    split_url = split_url[:5]
                    if len(split_url[-1]) > 0:
                        # We want to have '/' at the end of the url
                        split_url.append('')
                    if (
                            page_filter.period.value is not None and
                            conditions.period.sort_order is not None and
                            true_sort_filter_id in conditions.period.sort_order
                    ):
                        split_url.insert(-1, page_filter.period.value)
                    if (
                            conditions.comments.sort_order is not None and
                            page_filter.sort_order.filter_id in conditions.comments.sort_order and
                            page_filter.comments.value is not None
                    ):
                        split_url.insert(-1, page_filter.period.value)

                params['s'] = ['']
                params['vl'] = [page_filter.length.value]

            if page_number is not None and page_number != 1:
                split_url.insert(-1, str(page_number))

            fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query.replace(' ', '_')))


class FetishPapa(BaseFetcher):
    @property
    def object_urls(self):
        res = super(FetishPapa, self).object_urls
        res.pop(PornCategories.PORN_STAR_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.fetishpapa.com/'

    def __init__(self, source_name='FetishPapa', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(FetishPapa, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)


class Pornoxo(BaseFetcher):
    @property
    def object_urls(self):
        res = super(Pornoxo, self).object_urls
        res.pop(PornCategories.PORN_STAR_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornoxo.com/'

    def __init__(self, source_name='Pornoxo', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Pornoxo, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)


class BoyfriendTV(BaseFetcher):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.boyfriendtv.com/'

    def __init__(self, source_name='BoyfriendTV', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(BoyfriendTV, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                          session_id)


class AShemaleTube(BaseFetcher):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.ashemaletube.com/'

    def __init__(self, source_name='AShemaleTube', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(AShemaleTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                           session_id)


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    # module = FetishPapa()
    # module = Pornoxo()
    # module = BoyfriendTV()
    module = AShemaleTube()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=False)
