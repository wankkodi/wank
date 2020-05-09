# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote_plus, urlparse

# Regex
import re

# Math
import math

# JSON
from ....tools.text_json_manioulations import prepare_json_from_not_formatted_text

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter


class HQPorner(PornFetcher):
    video_request_base_url = {"mydaddy.cc": 'https://mydaddy.cc/',
                              "www.flyflv.com": 'https://www.flyflv.com/',
                              }

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://hqporner.com/categories',
            PornCategories.PORN_STAR_MAIN: 'https://hqporner.com/girls',
            PornCategories.TOP_RATED_VIDEO: 'https://hqporner.com/top',
            PornCategories.SEARCH_MAIN: 'https://hqporner.com/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://hqporner.com/'

    @property
    def number_of_videos_per_page(self):
        return 46

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'period_filters': [(PornFilterTypes.AllDate, 'All time', None),
                                            (PornFilterTypes.OneDate, 'This Week', 'week'),
                                            (PornFilterTypes.TwoDate, 'This Month', 'month'),
                                            ],
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='HQPorner', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HQPorner, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data, PornCategories.PORN_STAR)

    def _update_available_base_object(self, object_data, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="box page-content"]//section[@class="box feature"]')
        res = []
        for category in categories:
            link = category.xpath('./a')
            assert len(link) == 1
            link = link[0].attrib['href']

            image = category.xpath('./a/img')
            assert len(image) == 1
            image = urljoin(self.base_url, image[0].attrib['src'])

            title = category.xpath('./h3/a')
            assert len(title) == 1
            title = title[0].text

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        object_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        new_video_url = tmp_tree.xpath('.//div[@class="videoWrapper"]/iframe')
        new_video_url = urljoin(self.base_url, new_video_url[0].attrib['src'])
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(new_video_url, headers=headers)
        if urlparse(new_video_url).hostname == 'hqwo.cc':
            tree = self.parser.parse(tmp_request.text)
            new_video_url = [x.attrib['src'] for x in tree.xpath('.//body/script/[@src]')]
            tmp_request = self.session.get(new_video_url[0], headers=headers)
            raw_data = prepare_json_from_not_formatted_text(re.findall(r'(?:play\()(\[.*\])(?:[,)])',
                                                                       tmp_request.text, re.DOTALL)[0])
            video_links = sorted((VideoSource(link=x['file'],
                                              resolution=int(x['q'] if 'q' in x
                                                             else re.findall(r'(\d+)(?:p)', x['label'])[0]),
                                              )
                                  for x in raw_data),
                                 key=lambda x: x.resolution, reverse=True)

        # elif urlparse(new_video_url).hostname == 'mydaddy.cc':
        #     new_video_data = re.findall(r'(?:srca = )(\[.*\])(?:;if)', tmp_request.text)
        #     found_video_links = re.findall(r'(?:file: *")(.*?)(?:")', new_video_data[0])
        #     found_video_resolution = re.findall(r'(?:label: *")(.*?)(?:")', new_video_data[0])
        #     assert len(found_video_links) == len(found_video_resolution)
        #
        #     video_links = sorted(
        #         (VideoSource(link=urljoin(self.video_request_base_url[urlparse(new_video_url).hostname], x),
        #                      resolution=int(re.findall(r'\d+', v)[0])
        #                      )
        #          for x, v in zip(found_video_links, found_video_resolution)
        #          if len(re.findall(r'\d+', v)) > 0),
        #         key=lambda x: x.resolution, reverse=True)
        elif urlparse(new_video_url).hostname == 'www.flyflv.com':
            tree = self.parser.parse(tmp_request.text)
            videos = tree.xpath('.//video/source')
            video_links = sorted(
                (VideoSource(link=urljoin(self.video_request_base_url[urlparse(new_video_url).hostname],
                                          x.attrib['src']),
                             resolution=int(re.findall(r'\d+', x.attrib['label'])[0]))
                 for x in videos),
                key=lambda x: x.resolution, reverse=True)
        else:
            possible_sections = [x for x in re.findall(r'(?:\.html\(")(.*?)(?:"\);)', tmp_request.text, re.DOTALL)
                                 if 'video' in x]
            tree = self.parser.parse(possible_sections[-1])
            videos = tree.xpath('.//video/source')

            video_links = sorted((VideoSource(link=urljoin(self.base_url,
                                                           re.findall(r'(?:\\")(.*?)(?:\\")', x.attrib['src'])[0]),
                                              resolution=int(re.findall(r'\d+', x.attrib['title'])[0]),
                                              fps=int(re.findall(r'(?:p)(\d+)', x.attrib['title'])[0])
                                              if len(re.findall(r'(?:p)(\d+)', x.attrib['title'])) > 0 else None)
                                  for x in videos),
                                 key=lambda x: (x.resolution, x.fps), reverse=True)
        return VideoNode(video_sources=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        start_page = category_data.page_number if category_data.page_number is not None else 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        num_of_videos = tree.xpath('.//p/i[@class="icon fa-film"]')
        if len(num_of_videos) == 1:
            num_of_videos = re.findall(r'\d+', num_of_videos[0].tail)
            return math.ceil(int(num_of_videos[0]) / self.number_of_videos_per_page)
        else:
            # At first we try to check whether we have max page from the initial page.
            pages = self._get_available_pages_from_tree(tree)
            if len(pages) == 0:
                # We have no pages at all!
                return 1
            else:
                max_page = max(pages)
                if max_page - start_page < self._binary_search_page_threshold:
                    return max_page
                else:
                    # We perform binary search
                    return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//ul[@class="actions pagination"]/li/*/text()') if x.isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 3

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//section[@class="box features"]//div[@class="6u"]//section[@class="box feature"]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1

            img = video_tree_data.xpath('./a/div/@onmouseleave')
            assert len(img) == 1
            image = urljoin(self.base_url, re.findall(r'(?:")(.*)(?:")', img[0])[0])
            flip_images = video_tree_data.xpath('./a/div/div/@onmouseover')
            assert len(flip_images) >= 1
            flip_images = [urljoin(self.base_url, re.findall(r'(?:")(.*?)(?:")', x)[0]) for x in flip_images]

            title = video_tree_data.xpath('./div[@id="span-case"]/h3/a/text()')
            assert len(title) == 1

            video_length = video_tree_data.xpath('./div[@id="span-case"]/span[@class="icon fa-clock-o meta-data"]')
            assert len(video_length) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=title[0],
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  duration=self._format_duration(video_length[0].text),
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw duration.
        :return:
        """
        raw_duration = ':'.join([x.zfill(2) for x in re.findall(r'\d+', raw_duration)])
        super(HQPorner, self)._format_duration(raw_duration)

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')
        if true_object.object_type in self._default_sort_by:
            if page_filter.period.value is not None:
                split_url.append(page_filter.period.value)

        if page_number is not None and page_number != 1:
            if true_object.object_type == PornCategories.SEARCH_MAIN:
                params['p'] = page_number
            else:
                split_url.append(str(page_number))
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Referer': page_data.url,
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
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))
