# -*- coding: UTF-8 -*-
# Internet tools
from .... import urljoin

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# datetime
from .ahme import AhMe


class SunPorno(AhMe):
    video_preview_prefix = 'https://sunstatic.fuckandcdn.com/thumbs/previews/'

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
        videos = [x.xpath('./div')[0] for x in tree.xpath('.//div[@class="thumbs-container"]/div')
                  if 'class' in x.attrib and 'moviec' in x.attrib['class'] and
                  len(x.xpath('./div')) > 0]
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']
            video_preview = urljoin(self.video_preview_prefix, link_data[0].attrib['data-preview']) \
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

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(AhMe, self)._version_stack + [self.__version]


if __name__ == '__main__':
    module = SunPorno()
    module.download_category_input_from_user(use_web_server=False)
