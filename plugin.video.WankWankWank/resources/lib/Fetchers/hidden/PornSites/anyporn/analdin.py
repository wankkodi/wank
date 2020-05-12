import re

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .... import urljoin
from .pervertsluts import PervertSluts


class Analdin(PervertSluts):
    # Belongs to the AnyPorn network
    # todo: add playlists, webcams
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
            PornCategories.CATEGORY_MAIN: 'https://www.analdin.com/categories/',
            PornCategories.CHANNEL_MAIN: 'https://www.analdin.com/#popup-sponsors',
            PornCategories.PORN_STAR_MAIN: 'https://www.analdin.com/models/',
            PornCategories.LATEST_VIDEO: 'https://www.analdin.com/latest-updates/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.analdin.com/most-popular/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.analdin.com/top-rated/',
            PornCategories.SEARCH_MAIN: 'https://www.analdin.com/search/',
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
        return 'https://www.analdin.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': [(PornFilterTypes.AllType, 'All genders', ''),
                                                     (PornFilterTypes.GirlType, 'Girls', '0'),
                                                     (PornFilterTypes.GuyType, 'Guys', '1'),
                                                     (PornFilterTypes.OtherType, 'Other', '2'),
                                                     ],
                                 }
        category_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Recently updated', 'last_content_date'),
                                          (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'name'),
                                          (PornFilterTypes.ViewsOrder, 'Most viewed', 'avg_videos_popularity'),
                                          (PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          ],
                           }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       ],
                        'period_filters': ([(PornFilterTypes.AllDate, 'All time', ''),
                                            (PornFilterTypes.OneDate, 'This Month', '_month'),
                                            (PornFilterTypes.TwoDate, 'This week', '_week'),
                                            (PornFilterTypes.ThreeDate, 'Today', '_today'),
                                            ],
                                           [('sort_order', [PornFilterTypes.RatingOrder,
                                                            PornFilterTypes.ViewsOrder])]
                                           ),
                        'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', ''),
                                            (PornFilterTypes.HDQuality, 'HD quality', 'hd'),
                                            ],
                        }
        search_params = video_params.copy()
        search_params['sort_order'] = [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                                       (PornFilterTypes.DateOrder, 'Recent videos', 'most-recent'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                       (PornFilterTypes.LengthOrder, 'By duration', 'long-movies'),
                                       ]

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         categories_args=category_params,
                                         channels_args=category_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='Analdin', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Analdin, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _update_available_base_object(self, base_object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link = category.attrib['href']
            title = category.attrib['title']

            image = category.xpath('./div[@class="img"]/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            info_data = category.xpath('./*')[-1]
            number_of_videos = int(re.findall(r'(\d+)(?: video)', info_data.text)[0])
            rating = re.findall(r'(\d+%)', info_data.text)[0]

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(base_object_data.url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               rating=rating,
                                               object_type=object_type,
                                               super_object=base_object_data,
                                               ))
        if is_sort:
            res.sort(key=lambda x: x.title)
        base_object_data.add_sub_objects(res)
        return res

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        channels = tree.xpath('.//div[@class="wrap2"]/ul/li/a')
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x.attrib['href'],
                                       url=urljoin(channel_data.url, x.attrib['href']),
                                       title=x.attrib['title'],
                                       object_type=PornCategories.CHANNEL,
                                       super_object=channel_data,
                                       ) for x in channels]
        channel_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="wrap2"]/ul/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, None)
                                                for x in raw_objects])
        return links, titles, number_of_videos

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div[@class="margin-fix"]/div[@class="item  "]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1

            is_hd = 'class="hd"' in video_tree_data.xpath('./a/div[@class="img ithumb"]/*')[1].text

            video_length = video_tree_data.xpath('./a/div[@class="img ithumb"]/div[@class="duration"]')
            assert len(video_length) == 1

            title = video_tree_data.xpath('./a/strong')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            video_data = PornCatalogVideoPageNode(
                catalog_manager=self.catalog_manager,
                obj_id=re.findall(r'\d+', link[0].attrib['href'])[0],
                title=title,
                url=urljoin(self.base_url, link[0].attrib['href']),
                image_link=link[0].attrib['thumb'],
                preview_video_link=link[0].attrib['vthumb'] if 'vthumb' in link[0].attrib else None,
                is_hd=is_hd,
                duration=self._format_duration(video_length[0].text),
                object_type=PornCategories.VIDEO,
                super_object=page_data,
            )
            res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Analdin, self)._version_stack + [self.__version]
