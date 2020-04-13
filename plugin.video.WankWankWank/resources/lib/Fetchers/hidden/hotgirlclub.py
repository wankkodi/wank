# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin

# datetime
from datetime import timedelta

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# Generator id
from ..id_generator import IdGenerator


class HotGirlClub(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'http://www.hotgirlclub.com/categories/',
            PornCategories.TAG_MAIN: 'http://www.hotgirlclub.com/tags/',
            PornCategories.PORN_STAR_MAIN: 'http://www.hotgirlclub.com/pornstars/',
            PornCategories.LATEST_VIDEO: 'http://www.hotgirlclub.com/videos/newest/',
            PornCategories.MOST_VIEWED_VIDEO: 'http://www.hotgirlclub.com/videos/most-viewed/',
            PornCategories.TOP_RATED_VIDEO: 'http://www.hotgirlclub.com/videos/top-rated/',
            PornCategories.LONGEST_VIDEO: 'http://www.hotgirlclub.com/videos/longest/',
            PornCategories.POPULAR_VIDEO: 'http://www.hotgirlclub.com/videos/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.hotgirlclub.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        porn_stars_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Popular', None),
                                             (PornFilterTypes.AlphabeticOrder, 'Name', 'name'),
                                             (PornFilterTypes.DateOrder, 'Recently Updated', 'recently'),
                                             (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Total videos', 'total-videos'),
                                             ],
                              }
        video_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Popular', None),
                                        (PornFilterTypes.DateOrder, 'Latest', 'newest'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        ],
                         'period_filters': ([(PornFilterTypes.OneDate, 'Today', 'today'),
                                             (PornFilterTypes.TwoDate, 'Yesterday', 'yesterday'),
                                             (PornFilterTypes.ThreeDate, 'Daily', 'daily'),
                                             (PornFilterTypes.AllDate, 'All time', 'all-time'),
                                             ],
                                            [('sort_order', [PornFilterTypes.ViewsOrder,
                                                             PornFilterTypes.RatingOrder])]
                                            ),
                         }
        search_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Relevance', None),
                                         (PornFilterTypes.DateOrder, 'Latest', 'newest'),
                                         (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                         (PornFilterTypes.ViewsOrder, 'Views', 'views'),
                                         (PornFilterTypes.LengthOrder, 'Length', 'length'),
                                         ],
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filters,
                                         single_category_args=video_filters,
                                         single_tag_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='HotGirlClub', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HotGirlClub, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/section//ul[@class="thumbs-items"]/'
                                                  'li[@class="thumb thumb-category"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/section//ul[@class="thumbs-items"]/'
                                                  'li[@class="thumb thumb-pornstar"]/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_base_object(self, object_data, xpath, object_type):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        res = []
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        for category in categories:
            image = category.xpath('./span[@class="thumb-image"]/img')
            assert len(image) == 1

            number_of_videos = category.xpath('./span[@class="thumb-info"]/span[@class="info"]/span[@class="views"]/i')
            assert len(number_of_videos) == 1

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=category.attrib['href'],
                                                      url=urljoin(object_data.url, category.attrib['href']),
                                                      title=category.attrib['title'],
                                                      image_link=image[0].attrib['src'],
                                                      number_of_videos=int(re.findall(r'\d+',
                                                                                      number_of_videos[0].tail)[0]),
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        object_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles. The fetched objects MUST be sorted wrt title.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        links, titles, numbers_of_videos = \
            zip(*[(x.attrib['href'], x.attrib['title'], None)
                  for x in tree.xpath('.//div[@id="tags_list"]//div[@class="info-col"]/a')])
        return links, titles, numbers_of_videos

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
        tmp_tree = self.parser.parse(tmp_request.text)

        videos = tmp_tree.xpath('.//video/source')
        videos = [VideoSource(link=x.attrib['src']) for x in videos]
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN,):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        Finds the number of pages for the given parsed object.
        :param tree: Page tree.
        :return: number of pages (int).
        """
        pages = tree.xpath('.//ul[@class="pagination-list"]/li/*')
        pages = [int(x.text) for x in pages if x.text.isdigit()]
        return pages

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//ul[@class="thumbs-items"]/li[@class="thumb thumb-video"]/a')
        res = []
        for video_tree_data in videos:
            image_data = video_tree_data.xpath('./span[@class="thumb-image"]/img')
            assert len(image_data) == 1
            if 'src' in image_data[0].attrib:
                image = image_data[0].attrib['src']
                number_of_flip_images = int(re.findall(r'(\d+)(?:\))', image_data[0].attrib['onmouseover'])[0])
            else:
                image = image_data[0].attrib['data-src']
                number_of_flip_images = int(image_data[0].attrib['data-img-amount'])
            flip_images = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                           for i in range(1, number_of_flip_images + 1)]

            rating = video_tree_data.xpath('./span[@class="thumb-image"]/span[@class="percent"]')
            assert len(rating) == 1

            video_length = video_tree_data.xpath('./span[@class="thumb-image"]/span[@class="duration"]')
            assert len(video_length) == 1

            added_before = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="info"]/'
                                                 'span[@class="added"]')
            assert len(added_before) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['href'],
                                                  url=urljoin(self.base_url, video_tree_data.attrib['href']),
                                                  title=video_tree_data.attrib['title'],
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  rating=rating[0].text,
                                                  number_of_views=video_length[0].text,
                                                  added_before=added_before[0].text,
                                                  duration=self._format_duration(video_length[0].text),
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _convert_raw_duration_to_true_duration(self, raw_number):
        """
        Converts the raw number into integer.
        :param raw_number: Raw number, i.e. '4.87K'.
        :return:
        """
        raw_number_of_videos = self._clear_text(raw_number)
        hours = int(re.findall(r'(\d+)(?:h)', raw_number)[0]) if 'h' in raw_number_of_videos else 0
        minutes = int(re.findall(r'(\d+)(?: min)', raw_number)[0]) if 'min' in raw_number_of_videos else 0
        return timedelta(hours=hours, minutes=minutes)

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            split_url.insert(-1, page_filter.sort_order.value)
        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            split_url.insert(-1, page_filter.period.value)

        if page_number is not None and page_number != 1:
            split_url.insert(-1, str(page_number))
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
        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request


if __name__ == '__main__':
    # category_id = IdGenerator.make_id)'/search/biggest-tits/')
    category_id = IdGenerator.make_id('http://www.hotgirlclub.com/categories/milf/')
    tag_id = IdGenerator.make_id('/tags/tattoo/')
    module = HotGirlClub()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user()
