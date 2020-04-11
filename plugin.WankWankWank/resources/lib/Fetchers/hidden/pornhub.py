# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError, PornValueError

# Internet tools
from .. import urljoin, urlparse, quote, quote_plus, parse_qs

# Regex
import re

# Math
import math

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# JSON
import json

# Generator id
from ..id_generator import IdGenerator


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
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.porn.com/'

    def __init__(self, source_name='PornDotCom', source_id=0, store_dir='.',  data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornDotCom, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="list-global list-global--small"]/'
                                                  'div[@class="list-global__item"]/'
                                                  'div[@class="list-global__thumb"]/..',
                                                  PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@class="list-global list-global--small"]/'
                                                  'div[@class="list-global__item"]/'
                                                  'div[@class="list-global__thumb"]/..',
                                                  PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="list-global"]/'
                                                  'div[@class="list-global__item"]/'
                                                  'div[@class="list-global__thumb list-global__thumb--channel"]/..',
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
            link_data = category.xpath('./div[1]/a')
            assert len(link_data) == 2
            link = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./picture/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            title_data = category.xpath('./div[@class="list-global__meta flex"]/p/a')
            assert len(title_data) == 1
            title = title_data[0].text

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
        raw_data = tree.xpath('.//ul[@class="category-list__group"]/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, None)
                                                for x in raw_data])
        return links, titles, number_of_videos

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        if urlparse(tmp_request.url).hostname == urlparse(self.embed_video_json_url).hostname:
            # We need to request the videos
            video_id = tmp_request.url.split('/')[-1]
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
            assert tmp_request.ok
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

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type == PornCategories.CATEGORY_MAINa:
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
        return 4

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
            link_data = video_tree_data.xpath('./div[@class="list-global__thumb"]/a')
            assert len(link_data) == 2
            link = link_data[0].attrib['href']
            title = link_data[0].attrib['title']

            video_length = video_tree_data.xpath('./div[@class="list-global__thumb"]/span')
            assert len(video_length) == 1
            video_length = video_length[0].text

            image_data = video_tree_data.xpath('./div[@class="list-global__thumb"]/a/picture/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

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

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '&sq={q}'.format(q=quote(query))


class PornHub(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.pornhub.com/categories/',
            PornCategories.CHANNEL_MAIN: 'https://www.pornhub.com/channels',
            PornCategories.PORN_STAR_MAIN: 'https://www.pornhub.com/pornstars',
            PornCategories.LATEST_VIDEO: 'https://www.pornhub.com/video?o=cm',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.pornhub.com/video?o=mv',
            PornCategories.TOP_RATED_VIDEO: 'https://www.pornhub.com/video?o=tr',
            PornCategories.RECOMMENDED_VIDEO: 'https://www.pornhub.com/recommended',
            PornCategories.HOTTEST_VIDEO: 'https://www.pornhub.com/video?o=ht',
            # TopRatedAmateurVideo: 'https://www.pornhub.com/video?p=homemade&o=tr',
            PornCategories.RANDOM_VIDEO: 'https://www.pornhub.com/video/random',
            PornCategories.SEARCH_MAIN: 'https://www.pornhub.com/video/search',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.RECOMMENDED_VIDEO: PornFilterTypes.RecommendedOrder,
            PornCategories.HOTTEST_VIDEO: PornFilterTypes.HottestOrder,
            PornCategories.RANDOM_VIDEO: PornFilterTypes.RandomOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornhub.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', None),
                                                     (PornFilterTypes.GayType, 'Gay', 'gay'),
                                                     ],
                                 }
        categories_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Popular', None),
                                             (PornFilterTypes.AlphabeticOrder, 'Alphabetic', 'o=al'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'o=mv'),
                                             ),
                              }
        porn_stars_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Most Popular', None),
                                             (PornFilterTypes.TrendingOrder, 'Trending', 'o=t'),
                                             (PornFilterTypes.ViewsOrder, 'Most Viewed', 'o=mv'),
                                             (PornFilterTypes.SubscribersOrder, 'Most Subscribers', 'o=ms'),
                                             (PornFilterTypes.AlphabeticOrder, 'Alphabetical', 'o=a'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'o=nv'),
                                             ),
                              }
        channels_filters = {'sort_order': ((PornFilterTypes.FeaturedOrder, 'All Channels', None),
                                           (PornFilterTypes.PopularityOrder, 'Most Popular', 'o=rk'),
                                           (PornFilterTypes.TrendingOrder, 'Trending', 'o=t'),
                                           (PornFilterTypes.FeaturedOrder, 'Featured Recently', 'o=mr'),
                                           (PornFilterTypes.AlphabeticOrder, 'Alphabetical', 'o=al'),
                                           ),
                            }
        single_porn_star_filters = {'sort_order': ((PornFilterTypes.FeaturedOrder, 'Most Recent', 'o=mr'),
                                                   (PornFilterTypes.ViewsOrder, 'Most Viewed', 'o=mv'),
                                                   (PornFilterTypes.RatingOrder, 'Top Rated', 'o=tr'),
                                                   (PornFilterTypes.HottestOrder, 'Hottest', 'o=ht'),
                                                   (PornFilterTypes.LengthOrder, 'Longest', 'o=lg'),
                                                   (PornFilterTypes.DateOrder, 'Newest', 'o=cm'),
                                                   ),
                                    }
        video_filters = {'sort_order': ((PornFilterTypes.FeaturedOrder, 'Most Recent', 'o=mr'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'o=mv'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'o=tr'),
                                        (PornFilterTypes.HottestOrder, 'Hottest', 'o=ht'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'o=lg'),
                                        (PornFilterTypes.DateOrder, 'Newest', 'o=cm'),
                                        ),
                         'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', None),
                                             (PornFilterTypes.HDQuality, 'HD quality', 'hd=1'),
                                             ),
                         'length_filters': ((PornFilterTypes.AllLength, 'Any duration', None),
                                            (PornFilterTypes.OneLength, '0-10 min', 'max_duration=10'),
                                            (PornFilterTypes.TwoLength, '10-30 min', 'min_duration=10&max_duration=30'),
                                            (PornFilterTypes.ThreeLength, '30+ min', 'min_duration=30'),
                                            ),

                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         categories_args=categories_filters,
                                         channels_args=channels_filters,
                                         porn_stars_args=porn_stars_filters,
                                         single_category_args=video_filters,
                                         single_tag_args=video_filters,
                                         single_porn_star_args=single_porn_star_filters,
                                         single_channel_args=video_filters,
                                         video_args=video_filters,
                                         search_args=video_filters,
                                         )

    def __init__(self, source_name='Pornhub', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornHub, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//ul[@id="categoriesListSection"]/li')
        res = []
        for category in categories:
            id_data = category.xpath('./@data-category')
            assert len(id_data) == 1
            cat_id = id_data[0]

            sub_node = (category.xpath('./div[@class="category-wrapper "]') +
                        category.xpath('./div[@class="category-wrapper thumbInteractive"]'))
            assert len(sub_node) == 1
            sub_node = sub_node[0]

            link_data = sub_node.xpath('./a')
            assert len(link_data) == 1 and 'href' in link_data[0].attrib

            image_data = sub_node.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] if 'src' in image_data else image_data[0].attrib['data-thumb_url']
            if 'data:image' in image:
                image = image_data[0].attrib['data-thumb_url']

            assert len(image) == 1

            title = sub_node.xpath('./h5/a/strong/text()')
            assert len(title) == 1

            num_of_videos = sub_node.xpath('./h5/a/span/var/text()')
            assert len(num_of_videos) == 1
            num_of_videos = int(re.sub(r'[(),]', '', str(num_of_videos[0])))

            additional_data = {'category_id': cat_id}

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=cat_id,
                                                  url=urljoin(self.base_url, link_data[0].attrib['href']),
                                                  title=title[0],
                                                  image_link=image,
                                                  number_of_videos=num_of_videos,
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//ul[@id="filterChannelsSection"]/li/div[@class="channelsWrapper clearfix"]')
        res = []
        for category in categories:
            link_data = category.xpath('./div[@class="imgWrapper"]/a')
            assert len(link_data) == 1 and 'href' in link_data[0].attrib
            link = link_data[0].attrib['href']

            rank_data = category.xpath('./div[@class="imgWrapper"]/a/div[@class="rank"]/span/br')
            assert len(rank_data) == 1
            rank = self._clear_text(rank_data[0].tail)

            image_data = category.xpath('./div[@class="description"]/div[@class="avatar"]/a/img')
            assert len(image_data) == 1
            image = (image_data[0].attrib['src']
                     if 'src' in image_data[0].attrib and 'data:image' not in image_data[0].attrib['src']
                     else image_data[0].attrib['data-thumb_url'])
            title = image_data[0].attrib['alt']

            info_data = category.xpath('./div[@class="description"]/div[@class="descriptionContainer"]/ul/li')
            assert len(info_data) == 4
            num_of_videos = int(re.sub(r'[,]', '', info_data[2].xpath('./span/text()')[0])[0])
            additional_data = {'rank': rank,
                               'subscribers': int(re.sub(r'[,]', '', info_data[1].xpath('./span/text()')[0])[0]),
                               'number_of_views': int(re.sub(r'[,]', '', info_data[3].xpath('./span/text()')[0])[0]),
                               }

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=(urljoin(self.base_url, link_data[0].attrib['href']) +
                                                       '/videos?o=da'),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=num_of_videos,
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.CHANNEL,
                                                  super_object=channel_data,
                                                  )
            res.append(object_data)
        channel_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//ul[@id="popularPornstars"]/li/div[@class="wrap"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1 and 'href' in link_data[0].attrib
            link = link_data[0].attrib['href']

            is_verified = len(link_data[0].xpath('./span/i[@class="verifiedIcon"]')) > 0

            rank_data = category.xpath('./a/span[@class="pornstar_label"]/span[@class="title-album"]/'
                                       'span[@class="rank_number"]/text()')
            assert len(rank_data) == 1
            rank = self._clear_text(rank_data[0])

            image_data = category.xpath('./a/img')
            assert len(image_data) == 1
            image = (image_data[0].attrib['src']
                     if 'src' in image_data[0].attrib and 'data:image' not in image_data[0].attrib['src']
                     else image_data[0].attrib['data-thumb_url'])
            title = image_data[0].attrib['alt']

            info_data = category.xpath('./div[@class="thumbnail-info-wrapper"]/span[@class="videosNumber"]/text()')
            assert len(info_data) == 1
            num_of_videos = int(re.findall(r'(\d+)(?: Videos)', info_data[0])[0])
            additional_data = {'rank': rank,
                               'number_of_views': re.findall(r'(\d+\w*)(?: views)', info_data[0])[0],
                               'is_verified': is_verified
                               }

            full_url = urljoin(self.base_url, link_data[0].attrib['href'])
            if is_verified:
                full_url += '/videos?o=mr'

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=full_url,
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=num_of_videos,
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.PORN_STAR,
                                                  super_object=porn_star_data,
                                                  )
            res.append(object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        # new_video_data = json.loads([x for x in tmp_tree.xpath('.//script/text()') if 'gvideo' in x][0])
        # video_suffix = video_suffix = urlparse(tmp_data['contentUrl']).path

        raw_script = [x for x in tmp_tree.xpath('.//script/text()') if 'flashvars' in x][0]
        request_data = re.findall(r'({.*})(?:;)', raw_script)
        raw_data = json.loads(request_data[0])

        request_data2 = re.findall(r'(?:var )(\w+)(?: *= *)(.+?)(?:;)', raw_script)
        tmp_dict = {x[0]: x[1][1:-1] for x in request_data2 if x[1][0] == '"' and x[1][-1] == '"'}
        urls = {x[0]: x[1] for x in request_data2 if x[1][0] != '"' and x[1][-1] != '"'}
        new_urls = []
        for k, v in urls.items():
            # if 'flashvars' in k or 'qualityItems' in k:
            #     continue
            if 'media' in k:
                correct_v = re.sub(r'/\*.*?\*/', '', v)
                split_v = correct_v.split(' + ')
                new_v = ''.join([tmp_dict[x] for x in split_v])
                new_v = re.sub(r'[" +]', '', new_v)
                new_urls.append(re.sub(r'[" +]', '', new_v))

        # todo: add support for dash
        assert len(raw_data['mediaDefinitions']) == len(new_urls)
        res = sorted((VideoSource(quality=x['quality'], link=y) for x, y in zip(raw_data['mediaDefinitions'], new_urls)
                      if len(y) > 0 and type(x['quality']) != list),
                     key=lambda x: x.quality, reverse=True)
        return VideoNode(video_sources=res)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type == PornCategories.CATEGORY_MAIN:
            return 1
        try:
            page_request = self.get_object_request(category_data, override_page_number=2)
        except PornFetchUrlError:
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
        return [int(x.text)
                for x in tree.xpath('.//div[@class="pagination3"]/ul/li/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        try:
            page_request = self.get_object_request(page_data)
        except (PornValueError, PornFetchUrlError):
            return []
        tree = self.parser.parse(page_request.text)
        videos = ([x for x in tree.xpath('.//ul[@id="videoCategory"]/li') if '_vkey' in x.attrib] +
                  [x for x in tree.xpath('.//ul[@id="showAllChanelVideos"]/li') if '_vkey' in x.attrib] +
                  [x for x in tree.xpath('.//ul[@id="pornstarsVideoSection"]/li') if '_vkey' in x.attrib] +
                  [x for x in tree.xpath('.//ul[@id="mostRecentVideosSection"]/li') if '_vkey' in x.attrib] +
                  [x for x in tree.xpath('.//ul[@class="related-video-thumbs videos user-playlist"]/li')
                   if '_vkey' in x.attrib] +
                  [x for x in tree.xpath('.//ul[@class="videos recommendedContainerLoseOne"]/li')
                   if '_vkey' in x.attrib] +
                  [x for x in tree.xpath('.//ul[@class="videos search-video-thumbs freeView"]/li')
                   if '_vkey' in x.attrib] +
                  [x for x in tree.xpath('.//ul[@class="videos search-video-thumbs"]/li')
                   if '_vkey' in x.attrib])
        res = []
        for video_tree_data in videos:
            additional_data = {'_vkey': video_tree_data.attrib['_vkey']}

            image_data = (video_tree_data.xpath('.//a[@class="linkVideoThumb js-linkVideoThumb img "]/img') +
                          video_tree_data.xpath('.//a[@class="linkVideoThumb js-linkVideoThumb img js-viewTrack "]/'
                                                'img'))
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] if 'src' in image_data[0].attrib else None
            if image is None or 'data:image' in image:
                # We try alternative path
                image = image_data[0].attrib['data-thumb_url']

            link_data = (video_tree_data.xpath('.//a[@class="linkVideoThumb js-linkVideoThumb img "]') +
                         video_tree_data.xpath('.//a[@class="linkVideoThumb js-linkVideoThumb img js-viewTrack "]'))
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            url = urljoin(self.base_url, link)
            additional_data['data_related_url'] = urljoin(self.base_url, link_data[0].attrib['data-related-url'])
            title = link_data[0].attrib['title']

            user = video_tree_data.xpath('.//div[@class="usernameWrap"]/a')
            additional_data['uploader_data'] = {'name': user[0].attrib['title'] if 'title' in user[0].attrib else '',
                                                'url': urljoin(self.base_url, user[0].attrib['href']),
                                                } if len(user) > 0 else None

            is_hd = video_tree_data.xpath('.//div[@class="marker-overlays js-noFade"]/span[@class="hd-thumbnail"]/'
                                          'text()')
            is_hd = len(is_hd) > 0 and is_hd[0] == 'HD'
            video_length = video_tree_data.xpath('.//div[@class="marker-overlays js-noFade"]/'
                                                 'var[@class="duration"]/text()')
            assert len(video_length) == 1

            viewers = video_tree_data.xpath('.//div[@class="videoDetailsBlock"]/span[@class="views"]/var/text()')
            assert len(viewers) == 1

            rating = video_tree_data.xpath('.//div[@class="videoDetailsBlock"]/'
                                           'div[@class="rating-container neutral"]/div[@class="value"]/text()')
            assert len(rating) == 1

            added_before = video_tree_data.xpath('.//div[@class="videoDetailsBlock"]/var[@class="added"]/text()')
            assert len(added_before) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['id'],
                                                  url=url,
                                                  title=title,
                                                  image_link=image,
                                                  duration=self._format_duration(video_length[0]),
                                                  is_hd=is_hd,
                                                  number_of_views=viewers[0],
                                                  rating=rating[0],
                                                  added_before=added_before[0],
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        if (
                self.general_filter.current_filters.general.filter_id != PornFilterTypes.StraightType and
                true_object.object_type != PornCategories.PORN_STAR
        ):
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
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_number is not None and page_number != 1:
            params['page'] = page_number
        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            params.update(parse_qs(page_filter.sort_order.value))
        if page_filter.length.value is not None:
            params.update(parse_qs(page_filter.length.value))
        if page_filter.quality.value is not None:
            params.update(parse_qs(page_filter.quality.value))

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?search={q}'.format(q=quote_plus(query))


class YouPorn(PornFetcher):
    # todo: to add search api option
    # Example: Request URL: https://www.youporn.com/searchapi/popular/?page=2&combinedCategory[]=63&_=1576890456508
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.youporn.com/categories/',
            PornCategories.CHANNEL_MAIN: 'https://www.youporn.com/channels/',
            PornCategories.PORN_STAR_MAIN: 'https://www.youporn.com/pornstars/',
            PornCategories.RECOMMENDED_VIDEO: 'https://www.youporn.com/recommended/',
            PornCategories.LATEST_VIDEO: 'https://www.youporn.com/browse/time/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.youporn.com/top_rated/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.youporn.com/most_viewed/',
            PornCategories.FAVORITE_VIDEO: 'https://www.youporn.com/most_favorited/',
            PornCategories.MOST_DISCUSSED_VIDEO: 'https://www.youporn.com/most_discussed/',
            PornCategories.SEARCH_MAIN: 'https://www.youporn.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.RECOMMENDED_VIDEO: PornFilterTypes.RecommendedOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.youporn.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        porn_stars_params = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most Popular', None),
                                            (PornFilterTypes.SubscribersOrder, 'Most Subscribers', 'subscribers'),
                                            (PornFilterTypes.ViewsOrder, 'Most Views', 'views'),
                                            (PornFilterTypes.AlphabeticOrder, 'Alphabetical', 'alphabetical'),
                                            ],
                             }
        video_filters = {'added_before_filters': ((PornFilterTypes.AllAddedBefore, 'All time', None),
                                                  (PornFilterTypes.OneAddedBefore, 'Today', 'days_ago=1'),
                                                  (PornFilterTypes.TwoAddedBefore, 'Past 2 Days', 'days_ago=2'),
                                                  (PornFilterTypes.ThreeAddedBefore, 'This Week', 'days_ago=7'),
                                                  (PornFilterTypes.FourAddedBefore, 'This Month', 'days_ago=30'),
                                                  (PornFilterTypes.FiveAddedBefore, 'This Year', 'days_ago=365'),
                                                  ),
                         'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', None),
                                             (PornFilterTypes.HDQuality, 'HD quality', 'res=HD'),
                                             (PornFilterTypes.VRQuality, 'VR quality', 'res=VR'),
                                             ),
                         'length_filters': ((PornFilterTypes.AllLength, 'Any duration', None),
                                            (PornFilterTypes.OneLength, '0-10 min', 'max_minutes=10'),
                                            (PornFilterTypes.TwoLength, '10-30 min', 'min_minutes=10&max_minutes=30'),
                                            (PornFilterTypes.ThreeLength, '30+ min', 'min_minutes=30'),
                                            ),

                         }
        single_category = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Popular', None),
                                          (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                                          (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                                          (PornFilterTypes.DateOrder, 'Date', 'time'),
                                          (PornFilterTypes.LengthOrder, 'Duration', 'duration'),
                                          ),
                           'added_before_filters': video_filters['added_before_filters'],
                           'quality_filters': video_filters['quality_filters'],
                           'length_filters': video_filters['length_filters'],
                           }
        single_porn_star = {'sort_order': ((PornFilterTypes.DateOrder, 'Date', None),
                                           (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                                           (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                                           (PornFilterTypes.LengthOrder, 'Duration', 'duration'),
                                           ),
                            'added_before_filters': video_filters['added_before_filters'],
                            'quality_filters': video_filters['quality_filters'],
                            'length_filters': video_filters['length_filters'],
                            }
        search_filters = {'sort_order': ((PornFilterTypes.RelevanceOrder, 'Relevance', None),
                                         (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                                         (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                                         (PornFilterTypes.DateOrder, 'Date', 'time'),
                                         (PornFilterTypes.LengthOrder, 'Duration', 'duration'),
                                         ),
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_params,
                                         single_category_args=single_category,
                                         single_porn_star_args=single_porn_star,
                                         single_channel_args=single_porn_star,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='YouPorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(YouPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="categories-row"]/a')
        # categories = [x.xpath('./div[@class="row"]/a') for x in tree.xpath('.//div[@class="row grouped"]/div')
        #               if 'class' in x.attrib and 'categories_list' in x.attrib['class']]
        res = []
        for category in categories:
            category_tree = category.xpath('./div[@class="link-container"]')[0]
            image_data = category_tree.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']

            title = category_tree.xpath('./div[@class="categoryTitle"]/p/text()')
            assert len(title) == 1 or (len(title) == 2 and title[1] == '\n')
            title = self._clear_text(title[0])

            number_of_videos = category_tree.xpath('./div[@class="categoryTitle"]/p/span/text()')
            assert len(number_of_videos) == 1
            number_of_videos = self._clear_text(number_of_videos[0])
            number_of_videos = int(re.findall(r'\d+', number_of_videos)[0])

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)

        res.sort(key=lambda x: x.title)
        category_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        channels = tree.xpath('.//div[@data-espnode="most_popular_channels"]//div[@data-espnode="channel_box"]')
        res = []
        for channel in channels:
            link = channel.xpath('./a')
            assert len(link)

            image_data = channel.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            title = image_data[0].attrib['alt']

            number_of_videos = channel.xpath('./div[@class="channel-box-title"]/div[@class="videoCount"]/text()')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0])[0])

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.CHANNEL,
                                                  super_object=channel_data,
                                                  )
            res.append(object_data)

        channel_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        if porn_star_data.page_number in (1, None):
            # We need to skip local favorites
            porn_stars = tree.xpath('.//div[@class="container pornstars-list"]/div[5]//div[@data-espnode="pornstar"]')
        else:
            porn_stars = tree.xpath('.//div[@class="container pornstars-list"]//div[@data-espnode="pornstar"]')
        res = []
        for porn_star in porn_stars:
            link = porn_star.xpath('./a')
            assert len(link)

            image_data = porn_star.xpath('./a/div[@class="image-wrapper"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            title = image_data[0].attrib['alt']

            rank = porn_star.xpath('./div[@class="porn-star-info-box"]/div[@class="porn-star-rank"]/span/text()')
            assert len(rank) == 1
            additional_data = {'rank': int(re.findall(r'\d+', rank[0])[0])}

            number_of_videos = porn_star.xpath('./div[@class="porn-star-info-box"]/'
                                               'div[@class="porn-star-videos-count"]/'
                                               'span[@class="video-count"]/text()')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0])[0])

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.PORN_STAR,
                                                  super_object=porn_star_data,
                                                  )
            res.append(object_data)

        porn_star_data.add_sub_objects(res)
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
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_url, headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)
        script = [x for x in tmp_tree.xpath('.//script/text()') if 'mediaDefinition' in x]
        assert len(script) == 1
        raw_data = re.findall(r'(?:mediaDefinition = )(\[.*\])(?:;\n)', script[0])
        assert len(raw_data) == 1
        raw_data = json.loads(raw_data[0])

        video_links = sorted((VideoSource(link=x['videoUrl'], quality=int(re.findall(r'\d+', x['quality'])[0]))
                              for x in raw_data if 'videoUrl' in x),
                             key=lambda x: x.quality, reverse=True)
        return VideoNode(video_sources=video_links)

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="video-box four-column video_block_wrapper"]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1

            image_data = video_tree_data.xpath('./a//img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']

            flip_data = image_data[0].attrib['data-flipbook']
            number_of_flips = int(re.findall(r'(?:setLength: )(\d+)', flip_data)[0])
            first_i = int(re.findall(r'(?:firstThumbnail: )(\d+)', flip_data)[0])
            incrementer = int(re.findall(r'(?:incrementer: )(\d+)', flip_data)[0])
            flip_prefix = re.findall(r'(?:digitsPreffix: )(\'.*\')(?:,)', flip_data)[0]
            flip_suffix = re.findall(r'(?:digitsSuffix: )(\'.*\')(?:,)', flip_data)[0]
            flip_images = [flip_prefix + str(i) + flip_suffix
                           for i in range(first_i, number_of_flips+1, incrementer)]

            video_preview = image_data[0].attrib['data-mediabook'] if 'data-mediabook' in image_data[0].attrib else None

            title = video_tree_data.xpath('.//div[@class="video-box-title"]/text()')
            assert len(title) == 1
            title = re.sub(r'^[ \r\n]*|[ \r\n]*$', '', title[0])

            is_hd = video_tree_data.xpath('.//div[@class="video-duration-wrapper"]/div[@class="video-best-resolution"]')
            is_hd = len(is_hd) > 0 and is_hd[0] in ('720p', '1080p')

            video_length = video_tree_data.xpath('.//div[@class="video-duration-wrapper"]/div[@class="video-duration"]')
            assert len(video_length) == 1

            number_of_viewers = video_tree_data.xpath('.//div[@class="video-box-infos"]/'
                                                      'div[@class="video-box-rating"]/span[@class="video-box-views"]')
            number_of_viewers = number_of_viewers[0].text if len(number_of_viewers) > 0 else None

            rating = (video_tree_data.xpath('.//div[@class="video-box-infos"]/'
                                            'div[@class="video-box-rating"]/'
                                            'span[@class="video-box-percentage up"]') +
                      video_tree_data.xpath('.//div[@class="video-box-infos"]/'
                                            'div[@class="video-box-rating"]/'
                                            'span[@class="video-box-percentage down"]'))
            rating = rating[0].text if len(rating) == 1 else '0%'

            res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                obj_id=video_tree_data.attrib['data-video-id'],
                                                url=urljoin(self.base_url, link[0].attrib['href']),
                                                title=title,
                                                image_link=image[0],
                                                flip_images_link=flip_images,
                                                preview_video_link=video_preview,
                                                is_hd=is_hd,
                                                duration=self._format_duration(video_length[0].text),
                                                number_of_views=number_of_viewers,
                                                rating=rating,
                                                object_type=PornCategories.VIDEO,
                                                super_object=page_data,
                                                ))
        page_data.add_sub_objects(res)
        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1
        else:
            page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
            tree = self.parser.parse(page_request.text)
            tmp_pages = tree.xpath('.//div[@id="pages"]/ul/li/*')
            if len(tmp_pages) == 0:
                return 1
            tmp_max_pages = max(int(x.text) for x in tree.xpath('.//div[@id="pages"]/ul/li/*')
                                if x.text is not None and x.text.isdigit())
            page_request = self.get_object_request(category_data, override_page_number=tmp_max_pages)
            tree = self.parser.parse(page_request.text)
            pages = self._get_available_pages_from_tree(tree)
            return max(pages) if len(pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//div[@id="pages"]/ul/@data-max')]

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            fetch_base_url += '{s}/'.format(s=page_filter.sort_order.value)

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            # 'Referer': self.category_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_number is not None and page_number != 1:
            params['page'] = page_number
        if page_filter.added_before.value is not None:
            params.update(parse_qs(page_filter.added_before.value))
        if page_filter.length.value is not None:
            params.update(parse_qs(page_filter.length.value))
        if page_filter.quality.value is not None:
            params.update(parse_qs(page_filter.quality.value))

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?search-btn=&query={q}'.format(q=quote_plus(query))


class TubeEight(PornFetcher):
    video_request_format = 'https://token.4tube.com/{id}/desktop/1080+720+480+360+240'
    number_of_flip_images = 16

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.tube8.com/categories.html',
            PornCategories.TAG_MAIN: 'https://www.tube8.com/tags.html',
            PornCategories.CHANNEL_MAIN: 'https://www.tube8.com/top-channels/',
            PornCategories.PORN_STAR_MAIN: 'https://www.tube8.com/pornstars/',
            PornCategories.RECOMMENDED_VIDEO: 'https://www.tube8.com/latest',
            PornCategories.LATEST_VIDEO: 'https://www.tube8.com/newest',
            PornCategories.HOTTEST_VIDEO: 'https://www.tube8.com/hottest',
            PornCategories.TOP_RATED_VIDEO: 'https://www.tube8.com/top',
            PornCategories.LONGEST_VIDEO: 'https://www.tube8.com/longest',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.tube8.com/most-viewed/',
            PornCategories.FAVORITE_VIDEO: 'https://www.tube8.com/most-favorited',
            PornCategories.SEARCH_MAIN: 'https://www.tube8.com/searches.html',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.RECOMMENDED_VIDEO: PornFilterTypes.RecommendedOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.HOTTEST_VIDEO: PornFilterTypes.HottestOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.tube8.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        # todo: update the filters AND ITS IMPLEMENTATION
        general_filter_params = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', None),
                                                     (PornFilterTypes.GayType, 'Gay', 'gay'),
                                                     (PornFilterTypes.ShemaleType, 'Shemale', 'shemale'),
                                                     ],
                                 }
        porn_stars_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Recently Active', None),
                                             (PornFilterTypes.TrendingOrder, 'Trending', 'sort=rw'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'sort=mmm'),
                                             (PornFilterTypes.PopularityOrder, 'Most Popular', 'o=rl'),
                                             ),
                              }
        channels_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Popular', None),
                                           (PornFilterTypes.TrendingOrder, 'Trending', 'orderBy=t'),
                                           (PornFilterTypes.DateOrder, 'Latest', 'orderBy=mr'),
                                           (PornFilterTypes.AlphabeticOrder, 'Alphabetic', 'orderBy=al'),
                                           ),
                            }
        single_porn_star_filter = {'sort_order': ((PornFilterTypes.DateOrder, 'Most Recent', None),
                                                  (PornFilterTypes.RatingOrder, 'Top Rated', 'sort=tr'),
                                                  (PornFilterTypes.ViewsOrder, 'Viewed', 'sort=mv'),
                                                  (PornFilterTypes.LengthOrder, 'Longest', 'sort=ln'),
                                                  ),
                                   }
        single_channel_filter = {'sort_order': ((PornFilterTypes.DateOrder, 'Most Recent', 'orderBy=mr'),
                                                (PornFilterTypes.RatingOrder, 'Top Rated', 'orderBy=tr'),
                                                (PornFilterTypes.ViewsOrder, 'Most Viewed', 'orderBy=mv'),
                                                ),
                                 }
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Newest', 'orderby=nt'),
                                        (PornFilterTypes.FavorOrder, 'Favorites', 'orderby=mf'),
                                        (PornFilterTypes.FeaturedOrder, 'Featured', 'orderby=lt'),
                                        (PornFilterTypes.HottestOrder, 'Hottest', 'orderby=rl'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'orderby=ln'),
                                        (PornFilterTypes.RatingOrder, 'Rating', 'orderby=tr'),
                                        (PornFilterTypes.ViewsOrder, 'Views', 'orderby=mv'),
                                        (PornFilterTypes.VotesOrder, 'Votes', 'orderby=mt'),
                                        ),
                         'length_filters': ((PornFilterTypes.AllLength, 'Any duration', None),
                                            (PornFilterTypes.OneLength, 'Short (0-5 min)', 'filter_duration=short'),
                                            (PornFilterTypes.TwoLength, 'Medium (5-20 min)', 'filter_duration=medium'),
                                            (PornFilterTypes.ThreeLength, 'Long (20+ min)', 'filter_duration=long'),
                                            ),
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         channels_args=channels_filters,
                                         porn_stars_args=porn_stars_filters,
                                         single_category_args=video_filters,
                                         single_tag_args=video_filters,
                                         single_porn_star_args=single_porn_star_filter,
                                         single_channel_args=single_channel_filter,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='Tube8', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(TubeEight, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//ul[@id="porn-categories-box"]/li/a')
        res = []
        for category in categories:
            assert 'href' in category.attrib

            image_data = category.xpath('./div[@class="flexRatio"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-thumb']

            title = category.xpath('./h5/text()')
            assert len(title) == 1
            title = self._clear_text(title[0])

            number_of_videos = category.xpath('./h5/span/text()')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.sub(r'[(),]', '', number_of_videos[0]))

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(category_data.url, category.attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)

        category_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channel_data.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        channels = tree.xpath('.//div[@class="channel-box"]/div[@class="channelbox-inner"]')
        res = []
        for channel in channels:
            rank = channel.xpath('./div[@class="rank-badge-wrapper"]/div/span[@class="rank-number"]')
            assert len(rank) == 1
            additional_data = {'rank': int(rank[0].text)}

            link_data = channel.xpath('./div[@class="channel"]/a')
            assert len(link_data) == 1

            image_data = channel.xpath('./div[@class="channel"]/a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-thumb']

            title = channel.xpath('./div[@class="channel"]/ul[@class="channel-infos"]/li[@class="channel-title"]/a')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            number_of_videos = channel.xpath('./div[@class="channel"]/ul[@class="channel-infos"]/li[2]/span')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            number_of_views = channel.xpath('./div[@class="channel"]/ul[@class="channel-infos"]/li[3]/span')
            assert len(number_of_views) == 1
            additional_data['number_of_views'] = number_of_views[0].text

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(channel_data.url, link_data[0].attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.CHANNEL,
                                                  super_object=channel_data,
                                                  )
            res.append(object_data)

        channel_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available pornstar.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        channels = tree.xpath('.//div[@class="pornstar-box content-wrapper"]/div[@class="pornstar-box-inner"]')
        res = []
        for channel in channels:
            rank = channel.xpath('./div[@class="rank-box"]/span[@class="rank-number"]')
            assert len(rank) == 1
            additional_data = {'rank': int(rank[0].text)}

            link_data = channel.xpath('./div[@class="pornstar"]/a')
            assert len(link_data) == 1

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-thumb']

            title = link_data[0].xpath('./ul[@class="pornstar-infos"]/li[@class="pornstar-name"]')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            number_of_videos = link_data[0].xpath('./ul[@class="pornstar-infos"]/'
                                                  'li[@class="pornstar-videos"]/span')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(porn_star_data.url, link_data[0].attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.PORN_STAR,
                                                  super_object=porn_star_data,
                                                  )
            res.append(object_data)

        porn_star_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        links = re.findall(r'(?:<a class="tag" href=")(.*?)(?:")', page_request.text, re.DOTALL)
        titles = re.findall(r'(?:<div class="tag-w grd-tags grd">)(.*?)(?:</div>)', page_request.text, re.DOTALL)
        number_of_videos = re.findall(r'(?:<div class="tag-c grd-tags grd tag-count">\()(.*?)(?:\)</div>)',
                                      page_request.text, re.DOTALL)
        number_of_videos = [int(re.findall(r'\d+', x)[0]) for x in number_of_videos]
        assert len(titles) == len(links)
        assert len(titles) == len(number_of_videos)

        return links, titles, number_of_videos

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # At first we try to check whether we have max page from the initial page.
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        return max(pages) if len(pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//ul[@id="pagination"]/li/strong//text()') if x.isdigit()]

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
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_url, headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)
        script = [x for x in tmp_tree.xpath('.//script/text()') if 'var flashvars' in x]
        assert len(script) == 1
        raw_data = re.findall(r'(?:var flashvars = )({.*})(?:;\n)', script[0])
        raw_data = json.loads(raw_data[0])

        video_links = sorted((VideoSource(quality=x['quality'], link=x['videoUrl'])
                              for x in raw_data['mediaDefinition']),
                             key=lambda x: x.quality, reverse=True)

        return VideoNode(video_sources=video_links)

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = (tree.xpath('.//div[@id="category_video_list"]/div[@class="gridList"]/'
                             'figure[@class="video_box"]') +
                  tree.xpath('.//div[@id="search_results_page_wrapper"]/div[@class="gridList"]/'
                             'figure[@class="video_box"]') +
                  tree.xpath('.//div[@class="pornstar-layout clearfix"]/div[@class="content"]/div[@class="gridList"]/'
                             'figure[@class="video_box"]') +
                  tree.xpath('.//div[@class="channel_content_wrapper"]//div[@class="gridList channel_video_list"]/'
                             'figure[@class="video_box"]') +
                  tree.xpath('.//div[@id="result_container_wrapper"]//div[@class="gridList"]/'
                             'figure[@class="video_box"]'))
        res = []
        for video_tree_data in videos:
            # We skip vip title
            if 'data-esp-node' in video_tree_data.attrib and video_tree_data.attrib['data-esp-node'] == 'vip_video_box':
                continue

            link_data = video_tree_data.xpath('./div[@class="thumb_box"]/a/@href')
            assert len(link_data) == 1

            image_data = video_tree_data.xpath('./div[@class="thumb_box"]/a/div[@class="videoThumbsWrapper"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-thumb']
            flip_image = [re.sub(r'(?:original/)(\d+)', 'original/{i}'.format(i=i), image)
                          for i in range(self.number_of_flip_images + 1)]

            is_hd = video_tree_data.xpath('./div[@class="thumb_box"]/span[@class="video-attributes-features"]/'
                                          'span[@class="hdIcon"]/text()')

            video_length = video_tree_data.xpath('./div[@class="thumb_box"]/span[@class="video-attribute-duration"]/'
                                                 'span[@class="video-duration"]/text()')
            video_length = video_length[0] if len(video_length) == 1 else None

            title = video_tree_data.xpath('./figcaption/p[@class="video-title"]/a/text()')
            assert len(title) == 1
            title = re.sub(r'^[ \r\n]*|[ \r\n]*$', '', title[0])

            number_of_viewers = video_tree_data.xpath('./figcaption/p[@class="video-attributes"]/'
                                                      'span[@class="video-views"]/span[2]/text()')
            assert len(number_of_viewers) == 1
            number_of_viewers = re.sub(r'^[ \r\n]*|[ \r\n]*$', '', number_of_viewers[0])

            rating = video_tree_data.xpath('./figcaption/p[@class="video-attributes"]/'
                                           'span[@class="video-likes"]/span[@class="icon-video-likes"]')
            assert len(rating) == 1
            rating = re.sub(r'^[ \r\n]*|[ \r\n]*$', '', rating[0].tail)

            channel = video_tree_data.xpath('./figcaption/p[@class="video-attributes"]/'
                                            'span[@class="content-partner"]/a')
            additional_data = {'channel': {'name': channel[0].attrib['title'], 'url': channel[0].attrib['href']}} \
                if len(channel) == 1 else None

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['data-videoid'],
                                                  url=urljoin(self.base_url, link_data[0]),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_image,
                                                  is_hd=len(is_hd) > 0 and is_hd[0] == 'HD',
                                                  duration=self._format_duration(video_length)
                                                  if video_length is not None else None,
                                                  number_of_views=number_of_viewers,
                                                  rating=rating,
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        split_url = fetch_base_url.split('/')
        if self.general_filter.current_filters.general.filter_id != PornFilterTypes.StraightType:
            if len(split_url) > 3:
                if split_url[3] != self.general_filter.current_filters.general.value:
                    if split_url[3] not in (x.value for x in self.general_filter.filters.general):
                        split_url.insert(3, self.general_filter.current_filters.general.value)
                    else:
                        split_url[3] = self.general_filter.current_filters.general.value
            else:
                split_url[3] = self.general_filter.current_filters.general.value
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            # 'Referer': self.base_url,
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_number is not None and page_number != 1:
            if true_object.object_type in (PornCategories.TAG, PornCategories.SEARCH_MAIN):
                params['page'] = page_number
            elif true_object.object_type in (PornCategories.CHANNEL_MAIN, PornCategories.CHANNEL):
                if len(split_url) == 6:
                    split_url.pop(-2)
                split_url.insert(-1, str(page_number))
            else:
                if len(re.findall(r'\.html', split_url[-1])):
                    split_url.pop(-2)
                elif len(split_url[-1]) != 0:
                    split_url.append('')
                split_url.insert(-1, 'page')
                split_url.insert(-1, str(page_number))
                # program_fetch_url = re.sub(r'/*$|\.html$', '', program_fetch_url)
                # program_fetch_url += '/page/{p}/'.format(p=page_data.page_number)
        fetch_base_url = '/'.join(split_url)
        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            params.update(parse_qs(page_filter.sort_order.value))
        if page_filter.length.value is not None:
            params.update(parse_qs(page_filter.length.value))
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('111')
    channel_id = IdGenerator.make_id('/channels/porn-fidelity')
    # channel_id = IdGenerator.make_id('/channels/pure-taboo')
    # porn_star_id = IdGenerator.make_id('/pornstar/mia-khalifa')
    porn_star_id = IdGenerator.make_id('/pornstar/natasha-nice')
    module = PornHub()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['channels']['obj'], (channel_id, ), verbose=1)
    # module.download_object(module.objects['porn_stars']['obj'], (porn_star_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
