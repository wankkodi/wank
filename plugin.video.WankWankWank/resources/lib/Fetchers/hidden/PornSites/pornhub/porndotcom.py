# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, urlparse, quote, parse_qs
from requests import exceptions

# Regex
import re

# Math
import math

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# JSON
import json


class PornDotCom(PornFetcher):
    # todo: add live video
    embed_video_json_url = 'https://www.paidperview.com/video/embed-conf.json'

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.porn.com',
            PornCategories.TAG_MAIN: 'https://www.porn.com/categories',
            PornCategories.CHANNEL_MAIN: 'https://www.porn.com/channels',
            PornCategories.PORN_STAR_MAIN: 'https://www.porn.com/pornstars',
            PornCategories.ALL_VIDEO: 'https://www.porn.com/search?so=PORN.COM',
            PornCategories.SEARCH_MAIN: 'https://www.porn.com/search?so=PORN.COM',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.ALL_VIDEO: PornFilterTypes.PopularityOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', None),
                                                     (PornFilterTypes.GayType, 'Gay', 'gay'),
                                                     (PornFilterTypes.ShemaleType, 'Transgender', 'trans'),
                                                     ],
                                 }
        video_filters = {'added_before_filters': ((PornFilterTypes.AllAddedBefore, 'All time', None),
                                                  (PornFilterTypes.OneAddedBefore, 'Today', 'ad=1'),
                                                  (PornFilterTypes.TwoAddedBefore, 'This Week', 'ad=7'),
                                                  (PornFilterTypes.ThreeAddedBefore, 'This Month', 'ad=30'),
                                                  (PornFilterTypes.FourAddedBefore, '3 Months', 'ad=90'),
                                                  (PornFilterTypes.FiveAddedBefore, 'This Year', 'ad=365'),
                                                  ),
                         'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', None),
                                             (PornFilterTypes.HDQuality, 'HD quality', 'qu=hd'),
                                             ),
                         'length_filters': ((PornFilterTypes.AllLength, 'Any duration', None),
                                            (PornFilterTypes.OneLength, '0-10 min', 'lh=10'),
                                            (PornFilterTypes.TwoLength, '10-30 min', 'll=10&lh=30'),
                                            (PornFilterTypes.ThreeLength, '30+ min', 'll=30'),
                                            ),

                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         single_category_args=video_filters,
                                         single_tag_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         video_args=video_filters,
                                         search_args=video_filters,
                                         )

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 20000

    @property
    def possible_empty_pages(self):
        """
        Defines whether it is possible to have empty pages in the site.
        :return:
        """
        return True

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.porn.com/'

    def __init__(self, source_name='PornDotCom', source_id=0, store_dir='.',  data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornDotCom, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="list-global__item"]/a/'
                                'div[@class="list-global__thumb"]/..')
        res = []
        for category in categories:
            link = category.attrib['href']
            title = category.attrib['title'] if 'title' in category.attrib else None

            image_data = category.xpath('./div/picture/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            if title is None:
                title_data = category.xpath('./div[@class="list-global__meta flex"]/p')
                assert len(title_data) == 1
                title = self._clear_text(title_data[0].text)

            number_of_videos_data = category.xpath('./div[@class="list-global__meta flex"]/div/span')
            assert len(number_of_videos_data) == 1
            number_of_videos_data = re.findall(r'([\d.]+)(\w*)', number_of_videos_data[0].text)
            number_of_videos = float(number_of_videos_data[0][0])
            if len(number_of_videos_data[0]) > 1:
                if number_of_videos_data[0][1] == 'M':
                    number_of_videos *= 1e6
                elif number_of_videos_data[0][1] == 'K':
                    number_of_videos *= 1e3
            number_of_videos = int(number_of_videos)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(category_data.url, link),
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
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@class="list-global__item"]',
                                                  PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """

        return self._update_available_base_object(channel_data,
                                                  './/div[@class="list-global__item"]',
                                                  PornCategories.CHANNEL)

    def _update_available_base_object(self, object_data, xpath, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link_data = category.xpath('./div/a/picture/..')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = category.attrib['title'] if 'title' in category.attrib else None

            image_data = link_data[0].xpath('./picture/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            if title is None:
                title_data = category.xpath('./div[@class="list-global__meta flex"]/p/a')
                assert len(title_data) == 1
                title = self._clear_text(title_data[0].text)

            number_of_videos_data = category.xpath('./div[@class="list-global__meta flex"]/div/span')
            assert len(number_of_videos_data) == 1
            number_of_videos_data = re.findall(r'([\d.]+)(\w*)', number_of_videos_data[0].text)
            number_of_videos = float(number_of_videos_data[0][0])
            if len(number_of_videos_data[0]) > 1:
                if number_of_videos_data[0][1] == 'M':
                    number_of_videos *= 1e6
                elif number_of_videos_data[0][1] == 'K':
                    number_of_videos *= 1e3
            number_of_videos = int(number_of_videos)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(object_data.url, link),
                                               title=title,
                                               image_link=image,
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
        raw_data = tree.xpath('.//div[@class="category-list__group"]/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, None)
                                                for x in raw_data])
        return links, titles, number_of_videos

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        if urlparse(tmp_request.url).hostname == urlparse(self.embed_video_json_url).hostname:
            # We need to request the videos
            video_id = tmp_request.url.split('?')[0].split('/')[-1]
            params = {'scene_id': video_id, 'hls': 'no'}
            headers = {
                'Accept': '*/*',
                'Cache-Control': 'no-cache',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Host': urlparse(self.embed_video_json_url).hostname,
                'Origin': self.base_url[:-1],
                'Referer': video_data.super_object.url,
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'User-Agent': self.user_agent
            }
            tmp_request = self.session.post(self.embed_video_json_url, headers=headers, data=params)
            raw_data = tmp_request.json()
            videos = sorted((VideoSource(link=x['url'], resolution=int(re.findall(r'\d+', x['id'])[0]))
                             for x in raw_data['player']['streams']),
                            key=lambda x: x.resolution, reverse=True)

        else:
            videos = tmp_tree.xpath('.//video/source')
            assert len(videos) > 0
            if len(videos) > 1:
                videos = sorted((VideoSource(link=x.attrib['src'],
                                             resolution=int(re.findall(r'\d+', x.attrib['title'])[0]))
                                 for x in videos),
                                key=lambda x: x.resolution, reverse=True)
            else:
                videos = [VideoSource(link=videos[0].attrib['src'])]
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type == PornCategories.CATEGORY_MAIN:
            return 1

        if fetched_request is None:
            fetched_request = self.get_object_request(category_data)

        tree = self.parser.parse(fetched_request.text)
        total_number_of_items = tree.xpath('.//div[@class="pagination__label"]')
        number_of_items_per_page = (tree.xpath('.//div[@class="list-global__item"]') +
                                    tree.xpath('.//div[@class="list-global__item has-player"]'))
        if len(total_number_of_items) > 0 and len(number_of_items_per_page) > 0:
            total_number_of_items = int(''.join(re.findall(r'\d+', total_number_of_items[0].text)))
            return math.ceil(total_number_of_items / len(number_of_items_per_page))
        else:
            return 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//nav[@class="pager flex align-center justify-center"]/a/text()')
                if x.isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 1

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = (tree.xpath('.//div[@class="list-global list-global--small list-videos"]/'
                             'div[@class="list-global__item"]') +
                  tree.xpath('.//div[@class="list-global list-global--small list-videos"]/'
                             'div[@class="list-global__item has-player"]')
                  )
        res = []
        for video_tree_data in videos:
            raw_data = json.loads(video_tree_data.attrib['data-sobj'])
            link = raw_data['embed']
            title_data = video_tree_data.xpath('./div[@class="list-global__thumb"]/a')
            assert len(title_data) == 2
            title = title_data[0].attrib['title']

            video_length = video_tree_data.xpath('./div[@class="list-global__thumb"]/span')
            assert len(video_length) == 1
            video_length = video_length[0].text

            image_data = title_data[0].xpath('./picture/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'image:data' in image:
                image = image_data[0].attrib['data-src']

            # todo: Manually made.
            preview_video = re.sub('promo.*$', 'roll.webm', image)

            is_hd = video_tree_data.xpath('./div[@class="list-global__thumb"]/a/span[@class="hd"]/span')

            uploader = video_tree_data.xpath('./div[@class="list-global__meta"]/div[@class="list-global__details"]/'
                                             'span/a')
            additional_data = {'uploader': {'url': uploader[0].attrib['href'], 'name': uploader[0].text}} \
                if len(uploader) == 1 else None

            rating = video_tree_data.xpath('./div[@class="list-global__meta"]/div[@class="list-global__details"]/'
                                           'span/i[@class="ico-thumb_up"]')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].tail)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  preview_video_link=preview_video,
                                                  is_hd=len(is_hd) > 0,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  additional_data=additional_data,
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
        minutes = re.findall(r'\d+', raw_duration)
        assert len(minutes) == 1
        return int(minutes[0]) * 60

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        if self.general_filter.current_filters.general.filter_id != PornFilterTypes.StraightType:
            split_url = fetch_base_url.split('/')
            if len(split_url) > 3:
                if split_url[3] != self.general_filter.current_filters.general.value:
                    if split_url[3] not in (x.value for x in self.general_filter.filters.general):
                        split_url.insert(3, self.general_filter.current_filters.general.value)
                    else:
                        split_url[3] = self.general_filter.current_filters.general.value
            else:
                split_url[3] = self.general_filter.current_filters.general.value
            fetch_base_url = '/'.join(split_url)

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
        if true_object.object_type not in (PornCategories.CATEGORY_MAIN, PornCategories.PORN_STAR_MAIN,
                                           PornCategories.CHANNEL_MAIN, PornCategories.TAG_MAIN):
            params['so'] = 'PORN.COM'
        if page_number is not None and page_number > 1:
            params['pg'] = page_data.page_number
        if page_filter.added_before.value is not None:
            params.update(parse_qs(page_filter.added_before.value))
        if page_filter.length.value is not None:
            params.update(parse_qs(page_filter.length.value))
        if page_filter.quality.value is not None:
            params.update(parse_qs(page_filter.quality.value))
        try:
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        except exceptions.RetryError:
            page_request = self.session.head(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '&sq={q}'.format(q=quote(query))
