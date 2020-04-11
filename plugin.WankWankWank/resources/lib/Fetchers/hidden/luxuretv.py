# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# Generator id
from ..id_generator import IdGenerator


class LuxureTV(PornFetcher):
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
            PornCategories.CATEGORY_MAIN: 'https://en.luxuretv.com/channels/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://en.luxuretv.com/most-viewed/',
            PornCategories.TOP_RATED_VIDEO: 'https://en.luxuretv.com/top-rated/',
            PornCategories.LONGEST_VIDEO: 'https://en.luxuretv.com/longest/',
            PornCategories.MOST_DISCUSSED_VIDEO: 'https://en.luxuretv.com/most-discussed/',
            PornCategories.LATEST_VIDEO: 'https://en.luxuretv.com/',
            PornCategories.SEARCH_MAIN: 'https://en.luxuretv.com/search/videos/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://en.luxuretv.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        # todo: add support for premium content
        video_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Newest', None),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        (PornFilterTypes.CommentsOrder, 'Most Discussed', 'discussed'),
                                        (PornFilterTypes.FavorOrder, 'Most Favorite', 'favorited'),
                                        ],
                         }
        search_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Relevancy', None),
                                         (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                                         (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                                         (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                                         (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                         (PornFilterTypes.CommentsOrder, 'Most Discussed', 'discussed'),
                                         (PornFilterTypes.FavorOrder, 'Most Favorite', 'favorited'),
                                         ],
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='LuxureTV', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(LuxureTV, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="content content-channel"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1

            image = category.xpath('./a/img')
            assert len(image) == 1
            title = category.xpath('./div[@class="vtitle"]/a')
            assert len(title) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(self.base_url, link_data[0].attrib['href']),
                                                  title=(self._clear_text(title[0].text)
                                                         if link_data[0].text is not None else None),
                                                  image_link=urljoin(self.base_url, image[0].attrib['src']),
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
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
        tmp_tree = self.parser.parse(tmp_request.text)
        # new_video_data = json.loads([x for x in tmp_tree.xpath('.//script/text()') if 'gvideo' in x][0])
        # video_suffix = video_suffix = urlparse(tmp_data['contentUrl']).path

        videos = [VideoSource(link=x) for x in tmp_tree.xpath('.//source/@src')]
        assert len(videos) > 0
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type == PornCategories.CATEGORY_MAIN:
            return 1
        return self._binary_search_max_number_of_pages(category_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//div[@id="pagination"]/*/text()') if x.isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 10

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="contents"]/div[@class="content"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            flip_images = [re.sub(r'\d+.jpg$', '{i}.jpg'.format(i=i), image_data[0].attrib['src']) for i in range(11)]
            title = image_data[0].attrib['alt']

            rating = video_tree_data.xpath('./div[@class="rating"]/div[@class="star_off"]/div[@class="star_on"]/'
                                           '@style')
            assert len(rating) == 1

            video_length = video_tree_data.xpath('./div[@class="time"]/b')
            assert len(video_length) == 1

            number_of_views = video_tree_data.xpath('./div[@class="views"]/b')
            assert len(number_of_views) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(self.base_url, link_data[0].attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  rating=int(re.findall(r'\d+', rating[0])[0]) / 100,
                                                  duration=self._format_duration(video_length[0].text),
                                                  number_of_views=number_of_views[0].text,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')

        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            split_url.insert(-1, page_filter.sort_order.value)

        if page_number is not None and page_number != 1:
            page_suffix = 'page{p}.html'.format(p=page_number)
            if len(split_url[-1]) == 0 or len(re.findall(r'page\d+.html', split_url[-1])) > 0:
                split_url[-1] = page_suffix
            else:
                split_url.append('page{p}.html'.format(p=page_number))

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

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        true_query = re.sub(r'[^A-Za-z0-9 ]', '', query)
        true_query = re.sub(r'\s{2}\s*', ' ', true_query)
        true_query = re.sub(r'\s', '- ', true_query)
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=true_query)


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://en.luxuretv.com/channels/55/amateurs/')
    module = LuxureTV()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
