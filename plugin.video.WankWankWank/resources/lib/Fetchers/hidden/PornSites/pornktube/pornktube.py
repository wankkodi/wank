# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher
from ....tools.external_fetchers import ExternalFetcher

# Internet tools
from .... import urljoin, quote_plus

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


class PornKTube(PornFetcher):
    # Many similarities with rushporn module
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornktube.porn/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters, single_category_filters, _, _, _, _ = self._prepare_filters()
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=single_category_filters,
                                         video_args=video_filters,
                                         )

    @staticmethod
    def _prepare_filters():
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Recent', 'latest-updates'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                        (PornFilterTypes.PopularityOrder, 'Most Popular', 'most-popular'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        ),
                         'period_filters': ([(PornFilterTypes.AllDate, 'All time', None),
                                             (PornFilterTypes.TwoDate, 'Week', 'week'),
                                             (PornFilterTypes.OneDate, 'Month', 'month'),
                                             (PornFilterTypes.ThreeDate, 'Today', 'today'),
                                             ],
                                            [('sort_order', [PornFilterTypes.RatingOrder,
                                                             PornFilterTypes.PopularityOrder])]),
                         }
        single_category_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Recent', None),
                                                  (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                                  (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                                  (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                                  ),
                                   }
        single_porn_star_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Recent', None),
                                                   (PornFilterTypes.RatingOrder, 'Top Rated', 'voted'),
                                                   (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                                                   (PornFilterTypes.LengthOrder, 'Longest', 'long'),
                                                   ),
                                    }
        categories_filters = {'sort_order': ((PornFilterTypes.AlphabeticOrder, 'Alphabetically', None),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Videos', 'sort_by=total_videos'),
                                             (PornFilterTypes.VideosRatingOrder, 'Videos Rating',
                                              'sort_by=avg_videos_rating'),
                                             (PornFilterTypes.VideosPopularityOrder, 'Videos Popularity',
                                              'sort_by=avg_videos_popularity'),
                                             ),
                              }
        porn_stars_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Recent', None),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'count'),
                                             (PornFilterTypes.RatingOrder, 'Rated', 'rated'),
                                             (PornFilterTypes.ViewsOrder, 'Views', 'views'),
                                             ),
                              }
        channels_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Popular', None),
                                           (PornFilterTypes.RatingOrder, 'Rated', 'rated'),
                                           (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                                           (PornFilterTypes.DateOrder, 'New', 'recent'),
                                           ),
                            }
        return (video_filters, single_category_filters, single_porn_star_filters, categories_filters,
                porn_stars_filters, channels_filters)

    def __init__(self, source_name='PornKTube', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornKTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)
        # self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
        #                   'Chrome/76.0.3809.100 Safari/537.36'
        self.external_fetchers = ExternalFetcher(session=self.session, user_agent=self.user_agent,
                                                 parser=self.parser)

    def _update_available_base_category(self, base_data, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="cat"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            description = link_data[0].attrib['title'] if 'title' in link_data[0].attrib else None

            image_data = category.xpath('./a/img')
            assert len(image_data) == 1
            image = urljoin(base_data.url, image_data[0].attrib['src'])

            text_data = category.xpath('./h2/a')
            assert len(text_data) == 1
            title = re.findall(r'(\w+)(?: \(\d+\))', text_data[0].text)
            title = title[0] if len(title) > 0 else text_data[0].text
            number_of_videos = re.findall(r'(?:\w+ \()(\d+)(?:\))', text_data[0].text)
            number_of_videos = int(number_of_videos[0]) if len(number_of_videos) else None

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(base_data.url, link),
                                                  image_link=image,
                                                  title=title,
                                                  description=description,
                                                  number_of_videos=number_of_videos,
                                                  object_type=object_type,
                                                  super_object=base_data,
                                                  )
            res.append(object_data)
        base_data.add_sub_objects(res)
        return res

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_category(category_data, PornCategories.CATEGORY)

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """

        video_raw_data = self.external_fetchers.get_video_link_from_fapmedia(video_data.url)
        video_links = sorted((VideoSource(link=x[0], resolution=x[1]) for x in video_raw_data),
                             key=lambda x: x.resolution, reverse=True)
        headers = {
            'Accept-Encoding': 'identity;q=1, *;q=0',
            'Range': 'bytes=0-',
            'User-Agent': self.user_agent
        }
        return VideoNode(video_sources=video_links, headers=headers)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1
        page_request = self._get_object_request_no_exception_check(category_data) if fetched_request is None \
            else fetched_request
        if not self._check_is_available_page(category_data, page_request):
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
        return [int(x) for x in tree.xpath('.//div[@class="pagination"]/div[@class="block_content"]/*/text()')
                if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="pornkvideos"]/div[@class="wrap"]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./div[@class="vid_info"]/a')
            assert len(link) == 1

            image_data = video_tree_data.xpath('./div[@class="vid_info"]/a/img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])
            if 'onmouseover' in image_data[0].attrib:
                _, flip_url, flip_range = re.findall(r'(?:\()(.*)(?:\))',
                                                     image_data[0].attrib['onmouseover'])[0].split(', ')
                flip_image = ['{u}{i}.jpg'.format(u=flip_url[1:-1], i=i) for i in range(int(flip_range)+1)]
            else:
                flip_image = None

            video_length = video_tree_data.xpath('./div[@class="vid_info"]/div[@class="vlength"]')
            assert len(video_length) == 1

            pos_rating = video_tree_data.xpath('./div[@class="vid_info"]/div[@class="likes"]')
            assert len(pos_rating) == 1
            neg_rating = video_tree_data.xpath('./div[@class="vid_info"]/div[@class="dislikes"]')
            assert len(neg_rating) == 1
            try:
                rating = \
                    str(int(int(pos_rating[0].text)/(int(pos_rating[0].text) + int(neg_rating[0].text))*100)) + '%'
            except ZeroDivisionError:
                rating = 0

            title = video_tree_data.xpath('./h2/a')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=re.findall(r'\d+', link[0].attrib['href'])[0],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_image,
                                                  duration=self._format_duration(video_length[0].text),
                                                  rating=rating,
                                                  pos_rating=pos_rating,
                                                  neg_rating=neg_rating,
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
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        conditions = self.get_proper_filter(page_data).conditions
        fetch_base_url = self._prepare_request(page_number, true_object, page_filter, fetch_base_url, True, conditions)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        if not page_request.ok:
            # Sometimes we try another fetch
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_request(self, page_number, true_object, page_filter, fetch_base_url, use_last_slash, conditions):
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id
        split_url = fetch_base_url.split('/')
        if len(split_url[-1]) == 0:
            # We remove the last slash
            split_url.pop()
        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            split_url.append(page_filter.sort_order.value)
        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            split_url.append(page_filter.period.value)
        if page_number is not None and page_number != 1:
            split_url.append(str(page_number))

        if use_last_slash is True:
            split_url.append('')

        fetch_base_url = '/'.join(split_url)
        return fetch_base_url

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))
