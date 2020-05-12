import re
from .... import urljoin, parse_qsl

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogVideoPageNode
from .pervertsluts import PervertSluts


class MegaTubeXXX(PervertSluts):
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
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/porn-review'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/pornstars'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/new-videos'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/popular-videos'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-videos'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
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
        return 'https://www.megatube.xxx/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        channels_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Recently updated', 'last_content_date'),
                                          (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.ViewsOrder, 'Most viewed', 'avg_videos_popularity'),
                                          (PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          ],
                           }
        porn_stars_params = {'general_filters': [(PornFilterTypes.GirlType, 'Females', '0'),
                                                 (PornFilterTypes.GuyType, 'Males', '1'),
                                                 (PornFilterTypes.AllType, 'All', ''),
                                                 ],
                             'sort_order': [(PornFilterTypes.RatingOrder, 'Top Rated', 'avg_videos_rating'),
                                            (PornFilterTypes.ViewsOrder, 'Most Viewed', 'avg_videos_popularity'),
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
                        'length_filters': [(PornFilterTypes.AllLength, 'Any length', None),
                                           (PornFilterTypes.OneLength, '0-10', 'duration_to=600'),
                                           (PornFilterTypes.TwoLength, '10-40', 'duration_from=600&duration_to=2400'),
                                           (PornFilterTypes.ThreeLength, '40+', 'duration_from=2400'),
                                           ],
                        }
        search_params = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Most Relevant', ''),
                                        (PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'video_viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        ],
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_params,
                                         channels_args=channels_params,
                                         single_category_args=video_params,
                                         single_porn_star_args=video_params,
                                         single_channel_args=video_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='MegaTubeXXX', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(MegaTubeXXX, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                          session_id)

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        return self._get_video_links_from_video_data4(video_data)

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div/div[@class="item  "]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1

            image_data = link_data[0].xpath('./div[@class="img js-videoPreview"]')
            assert len(image_data) == 1
            image = image_data[0].xpath('./img')[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].xpath('./img')[0].attrib['data-original']
            flip_images = [x.attrib['data-src']
                           for x in image_data[0].xpath('./ul[@class="thumb-slider-screenshots"]/li')]
            video_preview = urljoin(self.base_url,
                                    image_data[0].xpath('./div[@class="thumb-video-info"]')[0].attrib['data-mediabook'])

            video_length = image_data[0].xpath('./div[@class="item__flags"]/span[@class="item__flag--duration"]')
            assert len(video_length) >= 1

            title = link_data[0].attrib['title']

            number_of_views = video_tree_data.xpath('./div[@class="wrap last-wrap"]/div[@class="views"]/i')
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].tail)

            added_before = video_tree_data.xpath('./div[@class="wrap last-wrap"]/div[@class="added"]')
            assert len(added_before) == 1
            added_before = self._clear_text(added_before[0].text)

            porn_stars = [{'name': x.text, 'url': x.attrib['href']}
                          for x in video_tree_data.xpath('./div[@class="wrap"]/div[@class="model-name"]/a')]
            channel = [{'name': x.text, 'url': x.attrib['href']}
                       for x in video_tree_data.xpath('./div[@class="wrap"]/div[@class="paysite-name"]/a')]
            channel = channel[0] if len(channel) > 0 else None
            additional_data = {'porn_stars': porn_stars, 'channel': channel}

            video_data = PornCatalogVideoPageNode(
                catalog_manager=self.catalog_manager,
                obj_id=re.findall(r'\d+', link_data[0].attrib['href'])[0],
                title=title,
                url=urljoin(self.base_url, link_data[0].attrib['href']),
                image_link=image,
                flip_images_link=flip_images,
                preview_video_link=video_preview,
                duration=self._format_duration(video_length[-1].text),
                additional_data=additional_data,
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
            conditions = self.get_proper_filter(page_data).conditions
            true_sort_filter_id = self._default_sort_by[true_object.object_type] \
                if true_object.object_type in self._default_sort_by \
                else page_filter.sort_order.filter_id

            if page_number is None:
                page_number = 1
            params.update({
                    'mode': 'async',
                    'function': 'get_block',
                })
            if page_filter.length.value is not None:
                params.update(parse_qsl(page_filter.length.value))

            params['block_id'] = 'list_videos_videos_list_search_result'
            params['q'] = self._search_query
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            return super(MegaTubeXXX, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                    page_filter, fetch_base_url)

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        res = super(MegaTubeXXX, self)._prepare_new_search_query(query.replace(' ', '-'))
        self._search_query = query
        return res

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(MegaTubeXXX, self)._version_stack + [self.__version]
