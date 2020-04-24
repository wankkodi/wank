# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote_plus

# Regex
import re

# Math
import math

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# Generator id
from ..id_generator import IdGenerator


class GoForPorn(PornFetcher):
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
            PornCategories.CATEGORY_MAIN: 'https://goforporn.com/',
            PornCategories.TAG_MAIN: 'https://goforporn.com/',
            PornCategories.CHANNEL_MAIN: 'https://goforporn.com/paysites/',
            PornCategories.PORN_STAR_MAIN: 'https://goforporn.com/pornstars/',
            PornCategories.LATEST_VIDEO: 'https://goforporn.com/sort/new/',
            PornCategories.TOP_RATED_VIDEO: 'https://goforporn.com/sort/top/',
            PornCategories.LONGEST_VIDEO: 'https://goforporn.com/sort/longest/',
            PornCategories.SEARCH_MAIN: 'https://goforporn.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://goforporn.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': [(PornFilterTypes.RatingOrder, 'Top', None),
                                        (PornFilterTypes.DateOrder, 'Recent', 'new'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        ],
                         }
        search_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Relevance', None),
                                         (PornFilterTypes.RatingOrder, 'Top', 'top'),
                                         (PornFilterTypes.DateOrder, 'Recent', 'new'),
                                         (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                         ],
                          }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=video_filters,
                                         single_channel_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         single_tag_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='GoForPorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(GoForPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="camp cow"]/div[@class="tightly"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="camp cow"]/div[@class="tightly"]/a',
                                                  PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@class="camp cow"]/div[@class="tightly"]/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_base_object(self, object_data, xpath, object_type):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link = category.attrib['href']
            title = category.attrib['title']

            image = category.xpath('./div[@class="age"]/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            number_of_videos = category.xpath('./div[@class="coach cow"]/span[@class="destruction"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(object_data.url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=object_type,
                                               super_object=object_data,
                                               ))

        object_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//ul[@class="bedroom"]/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.attrib['title'], int(x.xpath('./span')[0].text))
                                                for x in raw_data])
        return links, titles, number_of_videos

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        new_url_suffix = re.findall(r'(?:sourceUrl: \')(.*?)(?:\')', tmp_request.text)
        new_url = urljoin(video_data.url, new_url_suffix[0])
        headers = {
            'Accept': '*/*',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(new_url, headers=headers)
        raw_data = tmp_request.json()
        videos = sorted((VideoSource(link=x['url'],
                                     resolution=int(re.findall(r'\d+', x['name'])[0])
                                     if len(re.findall(r'\d+', x['name'])) > 0 else
                                     (1 if len(re.findall(r'high', x['name'])) > 0 else 0))
                         for x in raw_data['content']['urls']),
                        key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=videos)

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
        if len(pages) == 0:
            return 1
        elif (max(pages) - 1) < self._binary_search_page_threshold:
            return max(pages)
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)
        # max_videos = tree.xpath('.//div[@class="beast"]/span[@class="artifact"]')
        # assert len(max_videos) == 1
        # max_videos = re.findall(r'([\d.]*)(K* *$)', max_videos[0].text)
        # max_videos = int(float(max_videos[0][0]) * (1000 if 'K' in max_videos[0][1] else 1))
        # videos_per_page = len(tree.xpath('.//div[@class="camp cow"]/div[@class="tightly"]'))
        # return math.ceil(max_videos / videos_per_page)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//ul[@class="hidden seal"]/li/*')
                if x.text is not None and x.text.isdigit()]

    @property
    def _binary_search_page_threshold(self):
        return 5

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="camp cow"]/div[@class="tightly"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./div[@class="age"]/a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            video_length = link_data[0].xpath('./span')
            assert len(video_length) == 1
            video_length = video_length[0].text
            additional_data = {}
            additional_info = video_tree_data.xpath('./div[@class="appreciation"]/div[@class="annual"]/div')
            for info in additional_info:
                items = info.xpath('./div/a') + info.xpath('./div/a')
                title = info.xpath('./div/span') + info.xpath('./span')
                if len(items) == 0 and len(title) == 0:
                    continue
                title = title[0].text
                if title == 'Cats: ':
                    additional_data['categories'] = [{'name': x.text, 'link': x.attrib['href']} for x in items]
                elif title == 'Models ':
                    additional_data['porn_stars'] = [{'name': x.text, 'link': x.attrib['href']} for x in items]
                elif title == 'Niches ':
                    additional_data['tags'] = [{'name': x.text, 'link': x.attrib['href']} for x in items]
                elif title == 'Sponsor: ':
                    additional_data['channels'] = [{'name': x.text, 'link': x.attrib['href']} for x in items]
                elif title == 'Sponsor: ':
                    raise RuntimeError('Unknown category {c}'.format(c=title))

            title = link.split('/')[-3].replace('-', ' ').title()
            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  duration=self._format_duration(video_length),
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
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
        split_url = fetch_base_url.split('/')
        if true_object.object_type not in self._default_sort_by:
            if page_filter.sort_order.value is not None:
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
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query.replace(' ', '-')))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    module = GoForPorn()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=False)
