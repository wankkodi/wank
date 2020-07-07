import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode
from . import Base3


class CartoonPornVideos(Base3):
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

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(CartoonPornVideos, self)._version_stack + [self.__version]
