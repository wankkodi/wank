from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes
from .pornfd import PornFd


class ZeroDaysPorn(PornFd):
    max_flip_images = 30
    videos_per_video_page = 31

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://0dayporn.com/'

    @property
    def max_pages(self):
        return 2000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    def _prepare_filters(self):
        """
        Prepares the filters
        :return:
        """
        video_sort_order = [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                            (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                            (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                            (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                            (PornFilterTypes.FavorOrder, 'Most Favorite', 'most_favourited'),
                            ]
        search_sort_order = [(PornFilterTypes.RelevanceOrder, 'Most Relevant', '')] + video_sort_order
        video_period = ([(PornFilterTypes.AllDate, 'All time', ''),
                         (PornFilterTypes.OneDate, 'This Month', '_month'),
                         (PornFilterTypes.TwoDate, 'This week', '_week'),
                         (PornFilterTypes.ThreeDate, 'Today', '_today'),
                         ],
                        [('sort_order', [PornFilterTypes.RatingOrder,
                                         PornFilterTypes.ViewsOrder])]
                        )
        category_params = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            ],
             }
        porn_stars_params = \
            {'sort_order': [(PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            ],
             }
        actress_params = None
        channel_params = porn_stars_params
        tag_params = None
        video_params = {'sort_order': video_sort_order,
                        'period_filters': video_period,
                        }
        search_params = {'sort_order': search_sort_order,
                         'period_filters': video_period,
                         }

        return (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
                search_params)

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
        pages = self._get_available_pages_from_tree(tree)
        return max(pages) if len(pages) != 0 else 1

    def __init__(self, source_name='ZeroDaysPorn', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(ZeroDaysPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                           session_id)
