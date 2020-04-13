# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote_plus

# Regex
import re

# JSON
import json

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# Generator id
from ..id_generator import IdGenerator


class DrTuber(PornFetcher):
    max_flip_image = 20
    video_request_json_url = 'https://www.drtuber.com/player_config_json'
    _default_rating_all_date_filter = 'like_sum'

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.drtuber.com/categories',
            PornCategories.TAG_MAIN: 'https://www.drtuber.com/categories',
            PornCategories.CHANNEL_MAIN: 'https://www.drtuber.com/channels',
            PornCategories.PORN_STAR_MAIN: 'https://www.drtuber.com/pornstars',
            PornCategories.LATEST_VIDEO: 'https://www.drtuber.com/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.drtuber.com/',
            PornCategories.LONGEST_VIDEO: 'https://www.drtuber.com/',
            PornCategories.MOST_DISCUSSED_VIDEO: 'https://www.drtuber.com/',
            PornCategories.SEARCH_MAIN: 'https://www.drtuber.com/search/videos/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', ''),
                                              (PornFilterTypes.GayType, 'Gay', 'gay'),
                                              (PornFilterTypes.ShemaleType, 'Transsexual', 'trans'),
                                              ],
                          }
        channels_filter = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Top channels', 'top'),
                                          (PornFilterTypes.DateOrder, 'New channels', 'new'),
                                          (PornFilterTypes.AlphabeticOrder, 'A-Z', 'az'),
                                          ],

                           }
        video_filters = {'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', ''),
                                             (PornFilterTypes.HDQuality, 'HD quality', 'hd'),
                                             ],
                         'sort_order': [(PornFilterTypes.DateOrder, 'Date added', 'addtime'),
                                        (PornFilterTypes.LengthOrder, 'Duration', 'longest'),
                                        (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                        (PornFilterTypes.CommentsOrder, 'Comments', 'comments'),
                                        ],
                         'period_filters': ([(PornFilterTypes.TwoDate, 'Week', 'week'),
                                             (PornFilterTypes.OneDate, 'Month', 'month'),
                                             (PornFilterTypes.ThreeDate, 'Day', 'day'),
                                             (PornFilterTypes.AllDate, 'All time', 'all'),
                                             ],
                                            [('sort_order', [PornFilterTypes.RatingOrder,
                                                             PornFilterTypes.CommentsOrder])]
                                            ),
                         }
        search_filters = {'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', ''),
                                              (PornFilterTypes.HDQuality, 'HD quality', 'hd'),
                                              ],
                          'sort_order': [(PornFilterTypes.RelevanceOrder, 'Most relevant', 'rv'),
                                         (PornFilterTypes.DateOrder, 'Most recent', 'mr'),
                                         (PornFilterTypes.RatingOrder, 'Top rated', 'rt'),
                                         ],
                          'rating_filters': [(PornFilterTypes.AllRating, 'All rating', ''),
                                             (PornFilterTypes.OneRating, '95%', '0.95'),
                                             (PornFilterTypes.TwoRating, '80%', '0.8'),
                                             (PornFilterTypes.ThreeRating, '60%', '0.6'),
                                             ],
                          'length_filters': [(PornFilterTypes.AllLength, 'Any length', ''),
                                             (PornFilterTypes.OneLength, '0-10', '0-10'),
                                             (PornFilterTypes.TwoLength, '10-40', '10-40'),
                                             (PornFilterTypes.ThreeLength, '40+', '40-'),
                                             ],
                          'added_before_filters': [(PornFilterTypes.AllAddedBefore, 'Anytime', ''),
                                                   (PornFilterTypes.OneAddedBefore, 'Last Day', '1'),
                                                   (PornFilterTypes.TwoAddedBefore, 'Last Week', '7'),
                                                   (PornFilterTypes.ThreeAddedBefore, 'Last Month', '30'),
                                                   (PornFilterTypes.FourAddedBefore, 'Last Year', '365'),
                                                   ],
                          }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter,
                                         channels_args=channels_filter,
                                         single_category_args=video_filters,
                                         single_tag_args=video_filters,
                                         search_args=search_filters,
                                         video_args=video_filters,
                                         )

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.drtuber.com/'

    def __init__(self, source_name='DrTuber', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(DrTuber, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)
        self._category_mapping = None

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="drop_inner show"]')
        categories = categories[0].xpath('./div[@class="cols"]/span/a')
        res = []
        for category in categories:
            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(category_data.url, category.attrib['href']),
                                                  title=category.text,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        links = [x.attrib['href'] for x in tree.xpath('.//div[@class="ID-list-category"]/div[@class="row_ct"]//'
                                                      'div[@class="holder_ct"]/ul/li[@class="item"]/a')]
        titles = [x.text for x in tree.xpath('.//div[@class="ID-list-category"]/div[@class="row_ct"]//'
                                             'div[@class="holder_ct"]/ul/li[@class="item"]/a/span')]
        number_of_videos = [int(re.findall(r'\d+', x.text)[0])
                            for x in tree.xpath('.//div[@class="ID-list-category"]/div[@class="row_ct"]//'
                                                'div[@class="holder_ct"]/ul/li[@class="item"]/a/b')]
        assert len(titles) == len(links)
        assert len(titles) == len(number_of_videos)

        return links, titles, number_of_videos

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@class="thumbs"]/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="thumbs thumbs_channels"]/a',
                                                  PornCategories.CHANNEL)

    def _update_available_base_object(self, object_data, xpath, object_category):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            image = category.xpath('./img/@src')
            assert len(image) == 1

            title = category.xpath('./img/@alt')
            assert len(title) == 1

            number_of_videos = category.xpath('./em[@class="video_thumb"]/em[@title="video"]/text()')
            assert len(number_of_videos) == 1

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=category.attrib['href'],
                                                      url=urljoin(self.base_url, category.attrib['href']),
                                                      title=title[0],
                                                      image_link=image[0],
                                                      number_of_videos=int(number_of_videos[0]),
                                                      object_type=object_category,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        object_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """

        video_url = video_data.url
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_url, headers=headers)
        config_data = re.findall(r'(?:configData: *)({.*?})', tmp_request.text, re.DOTALL)
        assert len(config_data) > 0
        config_data = re.sub(r'\w+', lambda x: '"' + x[0] + '"', config_data[0])
        params = json.loads(config_data)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        tmp_request = self.session.get(self.video_request_json_url, headers=headers, params=params)
        raw_data = tmp_request.json()

        videos = []
        if raw_data['files']['hq'] is not None:
            videos.append(VideoSource(link=raw_data['files']['hq'], resolution=720))
        if raw_data['files']['lq'] is not None:
            videos.append(VideoSource(link=raw_data['files']['lq'], resolution=480))
        videos.sort(key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//ul[@class="pagination"]/li/*/text()') if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumbs"]/a')
        if len(videos) == 0:
            # We try another method before giving up
            videos = tree.xpath('.//div[@class="box_part"]//div[@class="thumbs"]/div[@class="wrap_inner"]/a')
        if len(videos) == 0:
            raise RuntimeError('Could not fetch the videos from page {u}'.format(u=page_data.url))
        res = []
        for video_tree_data in videos:
            image = video_tree_data.xpath('./img')
            assert len(image) == 1
            video_preview = \
                urljoin(self.base_url, image[0].attrib['data-webm']) if 'data-webm' in image[0].attrib else None
            image = urljoin(self.base_url, image[0].attrib['src'])
            flip_images = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image) for i in range(self.max_flip_image + 1)]

            rating = video_tree_data.xpath('./strong[@class="toolbar"]/em[@class="rate_thumb"]/em')
            assert len(rating) == 1

            video_length = video_tree_data.xpath('./strong[@class="toolbar"]/em[@class="time_thumb"]/em')
            assert len(video_length) == 1

            is_hd = video_tree_data.xpath('./strong[@class="toolbar"]/em[@class="time_thumb"]/i[@class="quality"]')

            title_data = video_tree_data.xpath('./span/em') + video_tree_data.xpath('./span/em/i')
            assert len(title_data) >= 1
            title = ''.join([x.text for x in title_data if x.text is not None])
            if title_data[-1].tail is not None:
                title += title_data[-1].tail

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=re.findall(r'\d+', video_tree_data.attrib['href'])[0],
                                                  url=urljoin(self.base_url, video_tree_data.attrib['href']),
                                                  preview_video_link=video_preview,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  rating=rating[0].text,
                                                  duration=self._format_duration(video_length[0].text),
                                                  title=title,
                                                  is_hd=len(is_hd) > 0,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        # todo: to make more generic (move some of the mappings outside)
        split_program_fetch_url = fetch_base_url.split('/')
        # Type filter
        self.session.cookies.set(name='cattype',
                                 value=self.general_filter.current_filters.general.value,
                                 domain='.drtuber.com')
        if true_object.object_type in (PornCategories.CATEGORY, PornCategories.TAG, PornCategories.LATEST_VIDEO,
                                       PornCategories.TOP_RATED_VIDEO, PornCategories.LONGEST_VIDEO,
                                       PornCategories.MOST_DISCUSSED_VIDEO):
            if self.general_filter.current_filters.general.filter_id != PornFilterTypes.StraightType:
                url_suffix = 'gay' \
                    if self.general_filter.current_filters.general.filter_id == PornFilterTypes.GayType else 'shemale'
                split_program_fetch_url.insert(3, url_suffix)

            # Quality filter
            if page_filter.quality.filter_id == PornFilterTypes.HDQuality:
                split_program_fetch_url.insert(-1, page_filter.quality.value)

            conditions = self.get_proper_filter(page_data).conditions
            if true_object.object_type in self._default_sort_by:
                true_filter_id = self._default_sort_by[true_object.object_type]
                value = self.get_proper_filter(page_data).filters.sort_order[true_filter_id].value
                if true_filter_id in conditions.period.sort_order:
                    if (
                            true_filter_id == PornFilterTypes.RatingOrder and
                            page_filter.period.filter_id == PornFilterTypes.AllDate
                    ):
                        value = self._default_rating_all_date_filter
                    else:
                        value += '_' + page_filter.period.value

            # if true_object.object_type == PornCategories.LATEST_VIDEO:
            #     value = 'addtime'
            # elif true_object.object_type == PornCategories.LONGEST_VIDEO:
            #     value = 'longest'
            # elif true_object.object_type == PornCategories.TOP_RATED_VIDEO:
            #     value = 'rating'
            #     if page_filter.period.filter_id == PornFilterTypes.AllDate:
            #         value = self._default_rating_all_date_filter
            #     else:
            #         value += '_' + page_filter.period.value
            # elif true_object.object_type == PornCategories.MOST_DISCUSSED_VIDEO:
            #     value = 'comments'
            #     if page_filter.sort_order.filter_id == PornFilterTypes.CommentsOrder:
            #         value += '_' + page_filter.period.value
            else:
                value = page_filter.sort_order.value
                if page_filter.sort_order.filter_id == PornFilterTypes.RatingOrder:
                    if page_filter.period.filter_id == PornFilterTypes.AllDate:
                        value = self._default_rating_all_date_filter
                    else:
                        value += '_' + page_filter.period.value
                elif page_filter.sort_order.filter_id == PornFilterTypes.CommentsOrder:
                    value += '_' + page_filter.period.value
            self.session.cookies.set(name='index_filter_sort',
                                     value=value,
                                     domain='.drtuber.com')
        elif true_object.object_type == PornCategories.CHANNEL_MAIN:
            self.session.cookies.set(name='channels_filter_sort',
                                     value=page_filter.sort_order.value,
                                     domain='.drtuber.com')
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            if self._category_mapping is None:
                self._update_available_channel_mapping()
            raw_cookie = {
                'ch': '.'.join(self._category_mapping[self.general_filter.current_filters.general.filter_id]) + '.',
                'rate': page_filter.rating.value,
                'dur': page_filter.length.value,
                'added': page_filter.added_before.value,
                'hq': '1' if page_filter.quality.filter_id == PornFilterTypes.HDQuality else '0',
                'sort': page_filter.sort_order.value,
            }
            cookie = quote_plus('&'.join(('='.join((k, v)) for k, v in raw_cookie.items())))
            self.session.cookies.set(name='search_filter_new',
                                     value=cookie,
                                     domain='.drtuber.com')

        program_fetch_url = '/'.join(split_program_fetch_url)

        if page_number is not None and page_number > 1:
            program_fetch_url = program_fetch_url + '/{p}'.format(p=page_number)
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
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}'.format(q=quote_plus(query))

    def _update_available_channel_mapping(self, page_request=None):
        """
        Updates the available category mapping
        :param page_request: Page request (Optional).
        :return: None
        """
        if page_request is None:
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
            page_request = self.session.get(self.object_urls[PornCategories.SEARCH_MAIN], headers=headers)
        tree = self.parser.parse(page_request.text)
        elements = tree.xpath('.//div/ul/li/label')
        self._category_mapping = \
            {PornFilterTypes.StraightType: [x.attrib['for'].split('_')[-1]
                                            for x in elements
                                            if 'for' in x.attrib and x.attrib['for'].split('_')[-4] == 'straight'],
             PornFilterTypes.GayType: [x.attrib['for'].split('_')[-1]
                                       for x in elements
                                       if 'for' in x.attrib and x.attrib['for'].split('_')[-4] == 'gay'],
             PornFilterTypes.ShemaleType: [x.attrib['for'].split('_')[-1]
                                           for x in elements
                                           if 'for' in x.attrib and x.attrib['for'].split('_')[-4] == 'trans'],
             }


if __name__ == '__main__':
    category_id = IdGenerator.make_id('/tags/adorable')
    channel_id = IdGenerator.make_id('/channel/lovehomeporn-com-the-biggest-home-porn-collection')
    module = DrTuber()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['channels']['obj'], (channel_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
