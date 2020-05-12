import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .sex3 import Sex3


class AnySex(Sex3):
    max_flip_image = 72

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://anysex.com/'

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://anysex.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://anysex.com/models/',
            PornCategories.LATEST_VIDEO: 'https://anysex.com/new-movies/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://anysex.com/most-popular/',
            PornCategories.TOP_RATED_VIDEO: 'https://anysex.com/top-rated/',
            PornCategories.SEARCH_MAIN: 'https://anysex.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        category_params = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'total_videos'),
                                          (PornFilterTypes.VideosPopularityOrder, 'Videos Popularity',
                                           'avg_videos_popularity'),
                                          (PornFilterTypes.VideosRatingOrder, 'Videos rating', 'avg_videos_rating'),
                                          ],
                           }
        single_category_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Recent first', 'latest'),
                                                 (PornFilterTypes.VideosRatingOrder, 'Top Rated first', 'top-rated'),
                                                 (PornFilterTypes.ViewsOrder, 'Most Viewed first', 'most-viewed'),
                                                 (PornFilterTypes.LengthOrder, 'Longest first', 'longest'),
                                                 ],
                                  }
        model_params = {'sort_order': [(PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                       (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                       (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'total_videos'),
                                       (PornFilterTypes.VideosPopularityOrder, 'Videos Popularity',
                                        'avg_videos_popularity'),
                                       (PornFilterTypes.VideosRatingOrder, 'Videos rating', 'avg_videos_rating'),
                                       ],
                        }
        video_params = {'period_filters': [[(PornFilterTypes.ThreeDate, 'Today', 'today'),
                                            (PornFilterTypes.TwoDate, 'This week', 'week'),
                                            (PornFilterTypes.OneDate, 'This Month', 'month'),
                                            (PornFilterTypes.AllDate, 'All time', None),
                                            ],
                                           [('sort_order', [PornFilterTypes.ViewsOrder,
                                                            PornFilterTypes.RatingOrder])]
                                           ]
                        }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_params,
                                         single_category_args=single_category_params,
                                         single_tag_args=single_category_params,
                                         porn_stars_args=model_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='AnySex', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(AnySex, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_general_category(category_data,
                                                       './/div[@class="list_categories"]//ul[@class="box"]/li',
                                                       PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_general_category(porn_star_data,
                                                       './/div[@class="modelleft"]//ul[@class="box"]/li',
                                                       PornCategories.PORN_STAR)

    def _update_available_general_category(self, category_data, xpath, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        for category in categories:
            link = category.xpath('./div[@class="img"]/a')
            assert len(link) == 1

            image = category.xpath('./div[@class="img"]/a/img/@src')
            assert len(image) == 1

            title = category.xpath('./div[@class="img"]/a/span/text()')
            assert len(title) == 1

            number_of_videos = category.xpath('./div[@class="desc"]/span[@class="views"]/text()')
            assert len(title) == 1
            number_of_videos = re.findall(r'\d+', number_of_videos[0])
            number_of_videos = number_of_videos[0] if len(number_of_videos) > 0 else None

            sub_category_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                        obj_id=link[0].attrib['href'],
                                                        url=urljoin(category_data.url, link[0].attrib['href']),
                                                        title=title[0],
                                                        image_link=image[0],
                                                        number_of_videos=number_of_videos,
                                                        object_type=object_type,
                                                        super_object=category_data,
                                                        )
            res.append(sub_category_data)
        category_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        return self._get_video_links_from_video_data3(video_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//div[@class="pagination"]/div[@class="block_content"]/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//ul[@class="box"]/li[@class="item "]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            image = video_tree_data.xpath('./a/div/img')
            assert len(image) == 1
            image = urljoin(self.base_url, image[0].attrib['src'])

            video_length = video_tree_data.xpath('./span[@class="time"]')
            assert len(video_length) == 1

            video_data = PornCatalogVideoPageNode(
                catalog_manager=self.catalog_manager,
                obj_id=re.findall(r'\d+', link_data[0].attrib['href'])[0],
                title=link_data[0].attrib['title'],
                url=urljoin(self.base_url, link_data[0].attrib['href']),
                image_link=image,
                flip_images_link=[re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                                  for i in range(self.max_flip_image + 1)],
                duration=self._format_duration(self._clear_text(video_length[0].text)),
                object_type=PornCategories.VIDEO,
                super_object=page_data,
            )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(AnySex, self)._version_stack + [self.__version]
