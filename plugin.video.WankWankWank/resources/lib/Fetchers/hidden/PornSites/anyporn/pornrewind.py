import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .pervertsluts import PervertSluts


class PornRewind(PervertSluts):
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
            PornCategories.CATEGORY_MAIN: 'https://www.pornrewind.com/categories/',
            PornCategories.TAG_MAIN: 'https://www.pornrewind.com/categories/',
            PornCategories.LATEST_VIDEO: 'https://www.pornrewind.com/videos/?sort_by=post_date',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.pornrewind.com/videos/?sort_by=video_viewed',
            PornCategories.TOP_RATED_VIDEO: 'https://www.pornrewind.com/videos/?sort_by=rating',
            PornCategories.SEARCH_MAIN: 'https://www.pornrewind.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornrewind.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        category_params = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          (PornFilterTypes.VideosPopularityOrder, 'Videos Popularity',
                                           'avg_videos_popularity'),
                                          (PornFilterTypes.VideosRatingOrder, 'Videos rating', 'avg_videos_rating'),
                                          ],
                           }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       ],
                        }
        search_params = video_params.copy()
        search_params['sort_order'] = [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                                       (PornFilterTypes.DateOrder, 'Recent videos', 'post_date'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.LengthOrder, 'By duration', 'duration'),
                                       ]

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_params,
                                         single_category_args=video_params,
                                         single_tag_args=video_params,
                                         video_args=video_params,
                                         search_args=search_params,
                                         )

    def __init__(self, source_name='PornRewind', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornRewind, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumbs-list"]/div[@class="th"]/a')
        res = []
        for category in categories:
            img = category.xpath('./span[@class="thumb-categories-img"]/img')
            assert len(img) == 1
            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=category.attrib['title'],
                                                  image_link=img[0].attrib['data-src'],
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="tags"]/ul[@class="tags-list"]/li/a')
        links = [x.attrib['href'] for x in raw_objects]
        titles = [x.text.title() for x in raw_objects]
        number_of_videos = [None] * len(titles)
        assert len(titles) == len(links)
        # assert len(titles) == len(number_of_videos)

        return links, titles, number_of_videos

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
        """
        return self._get_video_links_from_video_data4(video_data)

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
        if len(self._get_available_pages_from_tree(tree)) == 0:
            return 1
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//nav[@class="pagination"]/ul/li/*/text()') if x.isdigit()]

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
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumbs-list"]/div[@class="th "]/a[@class="thumb"]')
        res = []
        for video_tree_data in videos:
            image_data = video_tree_data.xpath('./span[@class="thumb-img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-src']
            flip_image = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                          for i in range(1, int(image_data[0].attrib['data-cnt']) + 1)]

            video_length = video_tree_data.xpath('./span[@class="thumb-desc"]/span[@class="thumb-info"]/'
                                                 'span[@class="thumb-label thumb-time"]/span/text()')
            assert len(video_length) == 1

            added_before = video_tree_data.xpath('./span[@class="thumb-desc"]/span[@class="thumb-info"]/'
                                                 'span[@class="thumb-label thumb-added"]/span/text()')
            assert len(added_before) == 1

            viewers = video_tree_data.xpath('./span[@class="thumb-desc"]/span[@class="thumb-info"]/'
                                            'span[@class="thumb-label thumb-viewed"]/span/text()')
            # assert len(viewers) == 1

            rating = video_tree_data.xpath('./span[@class="thumb-desc"]/span[@class="thumb-info"]/'
                                           'span[@class="thumb-label thumb-rating"]/text()')
            # assert len(rating) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['href'],
                                                  url=urljoin(self.base_url, video_tree_data.attrib['href']),
                                                  title=video_tree_data.attrib['title'],
                                                  image_link=image,
                                                  flip_images_link=flip_image,
                                                  duration=self._format_duration(video_length[0]),
                                                  added_before=added_before[0],
                                                  number_of_views=viewers[0] if len(viewers) > 0 else None,
                                                  rating=rating[0] if len(rating) > 0 else None,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        if true_object.object_type in (PornCategories.SEARCH_MAIN,):
            split_url = fetch_base_url.split('/')
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
            if len(split_url[-1]) != 0:
                split_url.append('')
            if page_number is not None and page_number != 1:
                if split_url[-2].isdigit():
                    split_url.pop(-2)
                split_url.insert(-1, str(page_number))
            params.update({
                'mode': 'async',
                'action': 'get_block',
                'block_id': 'list_videos_common_videos_list',
            })
            if len(page_filter.sort_order.value) > 0:
                params['sort_by'] = page_filter.sort_order.value

            fetch_base_url = '/'.join(split_url)
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            # fixme: problem with the categories sort... To return to it later on
            # if true_object.object_type == PornCategories.CATEGORY:
            #     if page_number is None:
            #         page_number = 1
            #     fetch_base_url += '{p}/'.format(p=page_number)
            return super(PornRewind, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                   page_filter, fetch_base_url)
