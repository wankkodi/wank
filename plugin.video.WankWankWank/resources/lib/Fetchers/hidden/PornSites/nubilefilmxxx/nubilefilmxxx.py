# -*- coding: UTF-8 -*-
# Internet tools
from .... import urljoin, quote_plus

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode
from ....catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# abstract
from .base import BaseObject


class NubileFilmXXX(BaseObject):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '?filter=latest'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '?filter=most-viewed'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '?filter=longest'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, '?filter=popular'),
            PornCategories.RANDOM_VIDEO: urljoin(self.base_url, '?filter=random'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.RANDOM_VIDEO: PornFilterTypes.RandomOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.nubilefilm.xxx/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Latest Videos', 'latest'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed Videos', 'most-viewed'),
                                        (PornFilterTypes.LengthOrder, 'Longest Videos', 'longest'),
                                        (PornFilterTypes.PopularityOrder, 'Popular Videos', 'popular'),
                                        (PornFilterTypes.RandomOrder, 'Random Videos', 'random'),
                                        ),
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         video_args=video_filters,
                                         search_args=video_filters,
                                         )

    def __init__(self, source_name='NubileFilmXXX', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(NubileFilmXXX, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                            session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, './/section[@id="tag_cloud-7"]/div/a',
                                                  PornCategories.CATEGORY)

    def _update_available_porn_stars(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, './/section[@id="tag_cloud-6"]/div/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(channel_data, './/section[@id="extended-tags-3"]/p/a',
                                                  PornCategories.CHANNEL)

    def _update_available_base_object(self, base_object_data, xpath, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=category.attrib['href'],
                                       url=urljoin(base_object_data.url, category.attrib['href']),
                                       title=category.text
                                       if category.text is not None else category.xpath('./span')[0].text,
                                       number_of_videos=int(re.findall(r'\d+', category.attrib['title'])[0]),
                                       object_type=object_type,
                                       super_object=base_object_data,
                                       ) for category in categories]
        base_object_data.add_sub_objects(res)
        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.PORN_STAR_MAIN,
                                         PornCategories.CHANNEL_MAIN):
            return 1
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
        return ([int(x.text) for x in tree.xpath('.//div[@class="pagination"]/ul/li/a') if x.text.isdigit()] +
                [int(re.findall(r'(?:page/)(\d+)', x.attrib['href'])[0])
                 for x in tree.xpath('.//div[@class="pagination"]/ul/li/a')
                 if 'href' in x.attrib and len(re.findall(r'(?:page/)(\d+)', x.attrib['href'])) > 0])

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        # videos = tree.xpath('.//div[@class="videos-list"]/article/a')
        videos = tree.xpath('.//div/article/a')
        res = []
        for video_tree_data in videos:
            title = video_tree_data.attrib['title'] \
                if 'title' in video_tree_data.attrib else video_tree_data.attrib['data-title']

            image = video_tree_data.xpath('./div[@class="post-thumbnail "]/img')
            image = (image[0].attrib['data-src'] if 'data-src' in image[0].attrib else image[0].attrib['src']) \
                if len(image) == 1 else None

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['href'],
                                                  url=urljoin(self.base_url, video_tree_data.attrib['href']),
                                                  title=title,
                                                  image_link=image,
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
        if page_number is not None and page_number != 1:
            if len(split_url[-1]) > 0:
                split_url.append('')
            split_url.insert(-1, 'page')
            split_url.insert(-1, str(page_number))

        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            params['filter'] = [page_filter.sort_order.value]

        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?s={q}'.format(q=quote_plus(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(NubileFilmXXX, self)._version_stack + [self.__version]
