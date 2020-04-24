# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin

# Generator id
from ..id_generator import IdGenerator

# Regex
import re

# KT fetcher
from ..tools.external_fetchers import KTMoviesFetcher

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


class OkXXX(PornFetcher):
    max_flip_images = 20

    @property
    def object_urls(self):
        return {
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, 'models/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, 'channels/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, 'tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, 'newest/'),
            PornCategories.TRENDING_VIDEO: urljoin(self.base_url, 'trending/'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, 'popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, 'search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TRENDING_VIDEO: PornFilterTypes.TrendingOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://ok.xxx/'

    @property
    def possible_empty_pages(self):
        """
        Defines whether it is possible to have empty pages in the site.
        :return:
        """
        return True

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'New', 'newest'),
                                        (PornFilterTypes.PopularityOrder, 'Popular', 'popular'),
                                        (PornFilterTypes.TrendingOrder, 'Trending', 'trending'),
                                        ),
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='OkXXX', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(OkXXX, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                    session_id)
        self.kt_fetcher = KTMoviesFetcher(self.session, self.user_agent, self.parser)

    def _update_available_porn_stars(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, './/div[@class="thumb thumb-ctr"]',
                                                  PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(channel_data, './/div[@class="thumb thumb-ctr"]',
                                                  PornCategories.CHANNEL)

    def _update_available_base_object(self, base_object_data, xpath, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])

            number_of_videos_data = category.xpath('./div[@class="thumb-total"]/i')
            assert len(number_of_videos_data) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos_data[0].tail)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(base_object_data.url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=object_type,
                                               super_object=base_object_data,
                                               ))
        base_object_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="top-list top-list-tags"]/div[@class="tags-holder"]/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], self._clear_text(x.xpath('./i')[0].tail), None)
                                                for x in raw_objects])
        return links, titles, number_of_videos

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        videos, resolutions = self.kt_fetcher.get_video_link(video_data.url)
        video_sources = [VideoSource(link=x, resolution=res) for x, res in zip(videos, resolutions)]
        if not all(x is None for x in resolutions):
            video_sources.sort(key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=video_sources)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        page_request = self._get_object_request_no_exception_check(category_data) if fetched_request is None \
            else fetched_request
        if not self._check_is_available_page(category_data, page_request):
            return 1
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//div[@class="pagination"]/div/ul/li/*') if x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumb-bl thumb-video  "]/div[@class="thumb"]/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']
            title = video_tree_data.attrib['title']

            image_data = video_tree_data.xpath('./img')
            image = (image_data[0].attrib['data-src'] if 'data-src' in image_data[0].attrib
                     else image_data[0].attrib['src']) \
                if len(image_data) == 1 else None
            if image is not None:
                if 'data:image' in image:
                    image = image_data[0].attrib['data-original']
                image = urljoin(self.base_url, image)
            flip_images = [re.sub(r'\d+.jpg$', '{p}.jpg'.format(p=p), image)
                           for p in range(1, self.max_flip_images + 1)]

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
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
        if len(split_url[-1]) > 0:
            split_url.append('')

        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            split_url.insert(-1, page_filter.sort_order.value)

        if page_number is not None and page_number != 1:
            split_url.insert(-1, str(page_number))

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


class PornHat(OkXXX):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornhat.com/'

    def __init__(self, source_name='PornHat', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornHat, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)


if __name__ == '__main__':
    # category_id = IdGenerator.make_id('/tag/mom')
    category_id = IdGenerator.make_id('/tag/wife')
    porn_star_id = IdGenerator.make_id('/pornstar/asa+akira')
    # module = OkXXX()
    module = PornHat()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['porn_stars']['obj'], (porn_star_id, ), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
