import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogVideoPageNode
from .pervertsluts import PervertSluts


class Fapster(PervertSluts):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://fapster.xxx/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://fapster.xxx/models/',
            PornCategories.CHANNEL_MAIN: 'https://fapster.xxx/sites/',
            PornCategories.LATEST_VIDEO: 'https://fapster.xxx/latest-updates/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://fapster.xxx/most-popular/',
            PornCategories.SEARCH_MAIN: 'https://fapster.xxx/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://fapster.xxx/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': [(PornFilterTypes.AllType, 'All genders', ''),
                                                     (PornFilterTypes.LesbianType, 'Girls', '0'),
                                                     (PornFilterTypes.GayType, 'Guys', '1'),
                                                     (PornFilterTypes.ShemaleType, 'Other', '2'),
                                                     ],
                                 }
        category_params = {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.ViewsOrder, 'Most viewed', 'avg_videos_popularity'),
                                          (PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          ],
                           }
        porn_stars_params = {'sort_order': [(PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                            (PornFilterTypes.ViewsOrder, 'Most viewed', 'avg_videos_popularity'),
                                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                            ],
                             }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                                       (PornFilterTypes.FavorOrder, 'Most Favourite', 'most_favourited'),
                                       ],
                        }
        search_params = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                                        (PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                        (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        (PornFilterTypes.CommentsOrder, 'Most Commented', 'most_commented'),
                                        (PornFilterTypes.FavorOrder, 'Most Favourite', 'most_favourited'),
                                        ],
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         categories_args=category_params,
                                         porn_stars_args=porn_stars_params,
                                         channels_args=porn_stars_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='Fapster', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Fapster, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div[@class="margin-fix"]/div[@class="item  "]/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./div[@class="img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            title = video_tree_data.attrib['title'] \
                if 'title' in video_tree_data.attrib else image_data[0].attrib['alt']

            is_hd = len(video_tree_data.xpath('./div[@class="img"]/span[@class="is-hd"]')) > 0

            video_length = video_tree_data.xpath('./div[@class="wrap"]/div[@class="duration"]')
            assert len(video_length) == 1

            rating = (video_tree_data.xpath('./div[@class="wrap"]/div[@class="rating positive"]') +
                      video_tree_data.xpath('./div[@class="wrap"]/div[@class="rating negative"]'))
            assert len(video_length) == 1
            rating = re.findall(r'\d+%', rating[0].text, re.DOTALL)

            added_before = video_tree_data.xpath('./div[@class="wrap"]/div[@class="added"]')
            assert len(added_before) == 1
            added_before = added_before[0].text

            number_of_views = video_tree_data.xpath('./div[@class="wrap"]/div[@class="views"]')
            number_of_views = number_of_views[0].text if len(number_of_views) == 1 else None

            video_data = PornCatalogVideoPageNode(
                catalog_manager=self.catalog_manager,
                obj_id=link,
                title=title,
                url=urljoin(page_data.url, link),
                image_link=image,
                is_hd=is_hd,
                duration=self._format_duration(video_length[0].text),
                rating=rating,
                added_before=added_before,
                number_of_views=number_of_views,
                object_type=PornCategories.VIDEO,
                super_object=page_data,
            )
            res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        if true_object.object_type == PornCategories.SEARCH_MAIN:
            headers = {
                'Accept': '*.*',
                'Cache-Control': 'max-age=0',
                'Referer': self.base_url,
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
            page_number = page_data.page_number if page_data.page_number is not None else 1
            params.update({
                'mode': 'async',
                'function': 'get_block',
            })
            page_filter = self.get_proper_filter(page_data).current_filters

            params['block_id'] = 'list_videos_videos_list_search_result'
            params['q'] = self._search_query
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            if page_filter.sort_order.filter_id in (PornFilterTypes.RatingOrder, PornFilterTypes.ViewsOrder):
                params['sort_by'] += page_filter.period.value
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            return super(PervertSluts, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                     page_filter, fetch_base_url)
