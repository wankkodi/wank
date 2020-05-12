# -*- coding: UTF-8 -*-
# Internet tools
from .... import urljoin

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

from .hdtubeporn import HDTubePorn


class PornID(HDTubePorn):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.pornid.xxx/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://www.pornid.xxx/pornstars/',
            PornCategories.CHANNEL_MAIN: 'https://www.pornid.xxx/channels/',
            PornCategories.LATEST_VIDEO: 'https://www.pornid.xxx/latest/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.pornid.xxx/top-rated/',
            PornCategories.LONGEST_VIDEO: 'https://www.pornid.xxx/longest/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.pornid.xxx/most-viewed/',
            PornCategories.SEARCH_MAIN: 'https://www.pornid.xxx/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornid.xxx/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        porn_stars_filters = {'general_filters': [(PornFilterTypes.GirlType, 'Females', '0'),
                                                  (PornFilterTypes.AllType, 'All sexes', ''),
                                                  (PornFilterTypes.GuyType, 'Males', '1'),
                                                  ],
                              'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Name', None),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Videos', 'videos'),
                                             (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                             (PornFilterTypes.PopularityOrder, 'Popularity', 'popularity'),
                                             ],
                              }
        channels_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most popular', None),
                                           (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sites_ab'),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Total videos', 'total-videos'),
                                           ],
                            }
        video_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', None),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                        ],
                         }
        search_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Relevance', None),
                                         (PornFilterTypes.DateOrder, 'Latest', 'latest'),
                                         (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                         (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                         (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
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

    def __init__(self, source_name='PornID', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornID, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumb"]/div/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] if 'src' in image_data[0].attrib else image_data[0].attrib['data-src']
            if 'data:image' in image and 'data-original' in image_data[0].attrib:
                image = image_data[0].attrib['data-original']

            title_data = category.xpath('./span[@class="thumb-info"]/span[@class="info-ctgs"]/span[@class="name-ctg"]')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos_data = category.xpath('./span[@class="thumb-info"]/span[@class="info-ctgs"]/'
                                                   'span[@class="amount-vids"]/span')
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
        categories = tree.xpath('.//div[@class="thumb"]/div/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span[@class="preview"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] if 'src' in image_data[0].attrib else image_data[0].attrib['data-src']
            if 'data:image' in image and 'data-original' in image_data[0].attrib:
                image = image_data[0].attrib['data-original']

            title_data = category.xpath('./span[@class="thumb-info"]/span[@class="info-models"]/'
                                        'span[@class="name-model"]')
            assert len(title_data) == 1
            title = title_data[0].text

            rating_data = category.xpath('./span[@class="thumb-info"]/span[@class="info-models"]/'
                                         'span[@class="rating"]/span')
            assert len(rating_data) == 1
            rating = re.findall(r'\d+%', rating_data[0].attrib['style'])[0]

            number_of_videos_data = category.xpath('./span[@class="preview"]/span[@class="duration"]/span')
            assert len(number_of_videos_data) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos_data[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
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
        categories = tree.xpath('.//div[@class="thumb"]/div/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span[@class="preview"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] if 'src' in image_data[0].attrib else image_data[0].attrib['data-src']
            if 'data:image' in image and 'data-original' in image_data[0].attrib:
                image = image_data[0].attrib['data-original']

            title_data = category.xpath('./span[@class="thumb-info"]/span[@class="info-channel"]/'
                                        'div[@class="channel-name"]')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos_data = category.xpath('./span[@class="thumb-info"]/span[@class="info-channel"]/'
                                                   'div[@class="channel-count"]/span')
            assert len(number_of_videos_data) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos_data[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
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
                for x in tree.xpath('.//div[@class="pagination"]/div/a')
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumb"]/div/div')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title']

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] if 'src' in image_data[0].attrib else image_data[0].attrib['data-src']
            max_images = len(video_tree_data.xpath('./a/ul[@class="screenshots-list"]/li'))
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, max_images+1)]

            video_length = video_tree_data.xpath('./a/span[@class="duration"]')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0].text)

            added_before = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="info-bottom"]/'
                                                 'span[@class="added"]')
            assert len(added_before) == 1
            added_before = self._clear_text(added_before[0].text)

            number_of_views = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="info-bottom"]/'
                                                    'span[@class="views"]/span')
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

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(PornID, self)._version_stack + [self.__version]
