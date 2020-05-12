# -*- coding: UTF-8 -*-
# Internet tools
from .... import urljoin

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

from .hdtubeporn import HDTubePorn


class SexVid(HDTubePorn):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.sexvid.xxx/c/',
            PornCategories.PORN_STAR_MAIN: 'https://www.sexvid.xxx/pornstars/',
            PornCategories.CHANNEL_MAIN: 'https://www.sexvid.xxx/sponsor/',
            PornCategories.FAVORITE_VIDEO: 'https://www.sexvid.xxx/p/most-favourited/',
            PornCategories.LATEST_VIDEO: 'https://www.sexvid.xxx/p/date/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.sexvid.xxx/p/rating/',
            PornCategories.LONGEST_VIDEO: 'https://www.sexvid.xxx/p/duration/',
            PornCategories.MOST_DISCUSSED_VIDEO: 'https://www.sexvid.xxx/p/most-commented/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.sexvid.xxx/p/',
            PornCategories.SEARCH_MAIN: 'https://www.sexvid.xxx/s/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.sexvid.xxx/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        porn_stars_filters = {'general_filters': [(PornFilterTypes.GirlType, 'Females', '0'),
                                                  (PornFilterTypes.GuyType, 'Males', '1'),
                                                  (PornFilterTypes.AllType, 'All sexes', ''),
                                                  ],
                              'sort_order': [(PornFilterTypes.NumberOfVideosOrder, 'Total videos', None),
                                             (PornFilterTypes.AlphabeticOrder, 'Name', 'title'),
                                             (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                             (PornFilterTypes.PopularityOrder, 'Popularity', 'popularity'),
                                             ],
                              }
        channels_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most popular', None),
                                           (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sites_ab'),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Total videos', 'total-videos'),
                                           ],
                            }
        video_filters = {'sort_order': [(PornFilterTypes.ViewsOrder, 'Most viewed', None),
                                        (PornFilterTypes.FavorOrder, 'Most favourited', 'most-favourited'),
                                        (PornFilterTypes.DateOrder, 'Latest', 'date'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                        (PornFilterTypes.CommentsOrder, 'Most commented', 'most-commented'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                        ],
                         }
        search_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Relevance', None),
                                         (PornFilterTypes.FavorOrder, 'Most favourited', 'most-favourited'),
                                         (PornFilterTypes.DateOrder, 'Latest', 'date'),
                                         (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                         (PornFilterTypes.CommentsOrder, 'Most commented', 'most-commented'),
                                         (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                         ],
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_category_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='SexVid', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SexVid, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumbs"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            title_data = category.xpath('./span[@class="tools"]/span[@class="title_cat"]')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos_data = category.xpath('./span[@class="tools"]/span[@class="video_quantity"]/span')
            assert len(number_of_videos_data) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos_data[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
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
        categories = tree.xpath('.//div[@class="thumbs"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span[@class="images_wrapper"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            country = category.xpath('./span[@class="images_wrapper"]/i/img')
            assert len(country) == 1
            additional_data = {'country': country[0].attrib['alt']}

            title_data = category.xpath('./span[@class="tools"]/span[@class="title_thumb"]')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos_data = category.xpath('./span[@class="tools"]/span[@class="rating_holder"]/'
                                                   'span[@class="video_quantity"]/div/span')
            assert len(number_of_videos_data) > 0
            number_of_videos = int(re.findall(r'\d+', number_of_videos_data[0].text)[0])
            number_of_photos = int(re.findall(r'\d+', number_of_videos_data[1].text)[0]) \
                if len(number_of_videos_data) == 2 else None

            rating_data = category.xpath('./span[@class="tools"]/span[@class="rating_holder"]/'
                                         'span[@class="video_rating"]/span')
            assert len(rating_data) == 1
            rating = rating_data[0].text

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               number_of_photos=number_of_photos,
                                               additional_data=additional_data,
                                               rating=rating,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumbs"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            title_data = category.xpath('./span[@class="tools"]/span[@class="title_cat"]')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos_data = category.xpath('./span[@class="tools"]/span[@class="video_quantity"]/div/span')
            assert len(number_of_videos_data) > 0
            number_of_videos = int(re.findall(r'\d+', number_of_videos_data[0].text)[0])
            number_of_photos = int(re.findall(r'\d+', number_of_videos_data[1].text)[0]) \
                if len(number_of_videos_data) == 2 else None

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               number_of_photos=number_of_photos,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ))

        channel_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0])
                for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a')
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumbs"]/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']
            title = video_tree_data.attrib['title']

            image_data = video_tree_data.xpath('./span/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            max_images = len(video_tree_data.xpath('./span/ul[@class="screenshots-list"]/li'))
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, max_images+1)]

            added_before = video_tree_data.xpath('./span[@class="tools"]/span[@class="tools_holder"]/'
                                                 'span[@class="date"]')
            assert len(added_before) == 1
            added_before = self._clear_text(added_before[0].text)

            video_length = video_tree_data.xpath('./span[@class="tools"]/span[@class="tools_holder"]/'
                                                 'span[@class="info"]/span[@class="time"]/span')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0].text)

            number_of_views = video_tree_data.xpath('./span[@class="tools"]/span[@class="tools_holder"]/'
                                                    'span[@class="info"]/span[@class="eye"]/span')
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  duration=self._format_duration(video_length),
                                                  flip_images_link=flip_images,
                                                  added_before=added_before,
                                                  number_of_views=number_of_views,
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
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_filter.general.value is not None:
            self.session.cookies.set(domain=self.host_name, name='gender',
                                     value=page_filter.general.value)

        insert_value = None
        insert_index = -1
        if true_object.object_type not in self._default_sort_by:
            insert_value = page_filter.sort_order.value
            if true_object.object_type == PornCategories.SEARCH_MAIN:
                insert_index = -2
        if insert_value is not None:
            split_url.insert(insert_index, insert_value)
        if page_number is not None and page_number != 1:
            split_url.insert(-1, str(page_number))
        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(SexVid, self)._version_stack + [self.__version]
