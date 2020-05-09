# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote_plus

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter


class HomeMoviesTube(PornFetcher):
    max_flip_images = 10

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.homemoviestube.com/channels/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.homemoviestube.com/top-rated/',
            PornCategories.FAVORITE_VIDEO: 'https://www.homemoviestube.com/most-favored/',
            PornCategories.LONGEST_VIDEO: 'https://www.homemoviestube.com/longest/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.homemoviestube.com/most-viewed/',
            PornCategories.LATEST_VIDEO: 'https://www.homemoviestube.com/most-recent/',
            PornCategories.SEARCH_MAIN: 'https://www.homemoviestube.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.homemoviestube.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'newest'),
                                        (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                        (PornFilterTypes.ViewsOrder, 'Views', 'views'),
                                        (PornFilterTypes.LengthOrder, 'Length', 'longest'),
                                        (PornFilterTypes.FavorOrder, 'Favored', 'most-favored'),
                                        ],
                         }
        search_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Relevance', None),
                                         (PornFilterTypes.DateOrder, 'Latest', 'newest'),
                                         (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                         (PornFilterTypes.ViewsOrder, 'Views', 'views'),
                                         (PornFilterTypes.LengthOrder, 'Length', 'length'),
                                         ],
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='HomeMoviesTube', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HomeMoviesTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                             session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="films-row row"]/div/div[@class="category-item-inner"]')
        res = []
        for category in categories:
            link_data = category.xpath('./div[@class="category-th-wrapper"]/a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title']

            image_data = link_data[0].xpath('./span[@class="category-thumb"]/img')
            assert len(image_data) == 1
            image = urljoin(category_data.url, image_data[0].attrib['src'])

            number_of_videos = category.xpath('./div[@class="category-mini-desc"]/div[@class="category-title"]/'
                                              'span[@class="category-counter"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(category_data.url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        sources = tmp_tree.xpath('.//video/source')
        videos = [VideoSource(link=urljoin(video_data.url, x.attrib['src'])) for x in sources]
        assert len(videos) > 0
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN, PornCategories.CATEGORY_MAIN):
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
        return [int(x.text) for x in tree.xpath('.//div[@class="col-xs-20 pagination-items"]/ul/li/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="films-row row"]//div[@class="film-item-inner"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./div[@class="film-th-wrapper"]/a')
            assert len(link_data)
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title']

            image_data = link_data[0].xpath('./span[@class="film-thumb"]/img')
            assert len(image_data) == 1
            image = urljoin(page_data.url, image_data[0].attrib['src'])
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image)
                           for d in range(1, self.max_flip_images + 1)]

            video_length_data = link_data[0].xpath('./span[@class="film-time"]')
            assert len(video_length_data) == 1
            video_length = video_length_data[0].text

            info_data = video_tree_data.xpath('./div[@class="film-mini-desc"]/div[@class="film-stats"]/span')
            assert len(info_data) > 0
            added_before = info_data[0].text
            number_of_views = info_data[1].text
            rating = info_data[2].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
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

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Referer': page_data.url,
            # 'Host': urlparse(object_data.url).hostname,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if true_object.object_type not in self._default_sort_by and page_filter.sort_order.value is not None:
            if true_object.object_type in (PornCategories.SEARCH_MAIN,):
                params['sortby'] = page_filter.sort_order.value
            else:
                split_url.insert(-1, page_filter.sort_order.value)

        if true_object.object_type not in (PornCategories.CATEGORY_MAIN,):
            if page_number is not None:
                new_page = 'page{p}.html'.format(p=page_number)
                if len(re.findall(r'page\d*.html', split_url[-1])) > 0 or len(split_url[-1]) == 0:
                    split_url[-1] = new_page
                else:
                    split_url.append(new_page)

        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query.replace(' ', '-')))
