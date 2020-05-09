# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher
from ....tools.external_fetchers import ExternalFetcher

# Internet tools
from .... import urlparse, urljoin, quote_plus

# Regex
import re

# Warnings and exceptions
import warnings

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


class Porn00(PornFetcher):
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 2000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'http://www.porn00.org/categories/',
            PornCategories.MOST_VIEWED_VIDEO: 'http://www.porn00.org/most-viewed/',
            PornCategories.SEARCH_MAIN: 'http://www.porn00.org/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.porn00.org/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Top', None),
                                        ),
                         'period_filters': ([(PornFilterTypes.OneDate, 'Today', None),
                                             (PornFilterTypes.TwoDate, 'This Week', 'week'),
                                             (PornFilterTypes.ThreeDate, 'This Month', 'month'),
                                             (PornFilterTypes.AllDate, 'Ever', 'ever'),
                                             ],
                                            [('sort_order', [PornFilterTypes.PopularityOrder])]),
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='Porn00', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Porn00, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)
        self.external_fetchers = ExternalFetcher(session=self.session, user_agent=self.user_agent,
                                                 parser=self.parser)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = [x for x in tree.xpath('.//div[@class]') if 'post-con categories' in x.attrib['class']]
        res = []
        for category in categories:
            link = category.xpath('./div[@class="image"]/a')
            assert len(link) == 1

            image = category.xpath('./div[@class="image"]/a/img')
            assert len(image) == 1

            title = category.xpath('./div[@class="title-con tk"]/span/a')
            assert len(title) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=title[0].text.title(),
                                                  image_link=image[0].attrib['src'],
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        org_request = self.get_object_request(video_data)
        org_tree = self.parser.parse(org_request.text)
        tmp_url = org_tree.xpath('.//div[@class="video-con"]/iframe')
        original_tmp_url = tmp_url[0].attrib['src']
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(original_tmp_url, headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)

        videos = [VideoSource(link=x.attrib['src'], resolution=int(re.findall(r'\d+', x.attrib['title'])[0]))
                  for x in tmp_tree.xpath('.//source')]

        alternatives = [x for x in org_tree.xpath('.//div[@id="alternatives"]/p/a') if 'Alternative' in x.text]
        for alternative in alternatives:
            tmp_url = alternative.attrib['href']
            tmp_request = self.session.get(tmp_url, headers=headers)
            tmp_tree = self.parser.parse(tmp_request.text)
            new_source = tmp_tree.xpath('.//div[@class="video-con"]/iframe/@src')
            if urlparse(new_source[0]).hostname == 'verystream.com':
                # Not available anymore...
                # videos.extend([VideoSource(link=x[0], resolution=x[1])
                #                for x in self.external_fetchers.get_video_link_from_verystream(new_source[0])])
                continue
            else:
                warnings.warn('Unknown source {h}...'.format(h=urlparse(new_source[0]).hostname))

        assert len(videos) > 0
        videos.sort(key=lambda x: x.resolution, reverse=True)

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Referer': original_tmp_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        return VideoNode(video_sources=videos, headers=headers)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.MOST_VIEWED_VIDEO):
            return 1
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return ([int(x) for x in tree.xpath('.//div[@class="donw pagination col-md-12"]/ul/li/a/text()')
                if x.isdigit()] +
                [int(x) for x in tree.xpath('.//div[@class="donw pagination col-md-12"]/ul/li/text()')
                 if x.isdigit()])

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 2

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="post-con"]')
        res = []
        for video_tree_data in videos:
            if 'style' in video_tree_data.attrib:
                continue

            link = video_tree_data.xpath('./div[@class="image"]/a')
            assert len(link) == 1

            image = video_tree_data.xpath('./div[@class="image"]/a/img/@src')
            assert len(image) == 1

            title = video_tree_data.xpath('./div[@class="title-con"]/span[@class="heading"]/a/text()')
            assert len(title) == 1

            categories = video_tree_data.xpath('./div[@class="title-con"]/span[@class="title k5"]/span[@class="p5"]/a')
            assert len(categories) > 0
            additional_data = {'categories': [(x.text.title(), x.attrib['href']) for x in categories]}

            date_added = video_tree_data.xpath('./div[@class="title-con"]/span[@class="title k5"]/h4[@class="dunk"]/'
                                               'text()')
            assert len(date_added) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=title[0],
                                                  image_link=image[0],
                                                  additional_data=additional_data,
                                                  added_before=date_added[0],
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            split_url[-2] += '-' + page_filter.period.value

        if page_number is not None and page_number != 1:
            if len(split_url[-1]) > 0:
                split_url.append('')
            split_url.insert(-1, 'page')
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

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?s={q}'.format(q=quote_plus(query))
