# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher, PornFetchUrlError, PornValueError

# Internet tools
from .... import urljoin, quote_plus, parse_qs

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode, VideoTypes
from ....catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# JSON
import json

# Math
import math


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
    def possible_empty_pages(self):
        """
        Defines whether it is possible to have empty pages in the site.
        :return:
        """
        return True

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

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
        channels_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Most Popular', 'o=rk'),
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
        single_channel_filters = {'sort_order': ((PornFilterTypes.FeaturedOrder, 'Most Recent', 'o=da'),
                                                 (PornFilterTypes.ViewsOrder, 'Most Viewed', 'o=vi'),
                                                 (PornFilterTypes.RatingOrder, 'Top Rated', 'o=ra'),
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
        search_filters = {'sort_order': (((PornFilterTypes.RelevanceOrder, 'Most Relevant', None),) +
                                         video_filters['sort_order']),
                          'quality_filters': video_filters['quality_filters'],
                          'length_filters': video_filters['length_filters'],
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         categories_args=categories_filters,
                                         channels_args=channels_filters,
                                         porn_stars_args=porn_stars_filters,
                                         single_category_args=video_filters,
                                         single_tag_args=video_filters,
                                         single_porn_star_args=single_porn_star_filters,
                                         single_channel_args=single_channel_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='Pornhub', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornHub, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

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

            is_verified = len(category.xpath('.//span/i[@class="verifiedIcon"]')) > 0

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

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
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
        i = 0
        while 1:
            # if 'flashvars' in k or 'qualityItems' in k:
            #     continue
            k = 'media_{i}'.format(i=i)
            if k in urls:
                v = urls[k]
                correct_v = re.sub(r'/\*.*?\*/', '', v)
                split_v = correct_v.split(' + ')
                new_v = ''.join([tmp_dict[x] for x in split_v])
                new_v = re.sub(r'[" +]', '', new_v)
                new_urls.append(re.sub(r'[" +]', '', new_v))
                i += 1
            else:
                break

        # todo: add support for dash
        assert len(raw_data['mediaDefinitions']) == len(new_urls)
        res = sorted((VideoSource(quality=x['quality'] if type(x['quality']) != list else max(x['quality']),
                                  link=y,
                                  video_type=VideoTypes.VIDEO_REGULAR if type(x['quality']) != list
                                  else VideoTypes.VIDEO_DASH)
                      for x, y in zip(raw_data['mediaDefinitions'], new_urls)
                      if len(y) > 0),
                     key=lambda x: x.quality, reverse=True)
        return VideoNode(video_sources=res)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type == PornCategories.CATEGORY_MAIN:
            return 1
        elif category_data.object_type == PornCategories.CHANNEL_MAIN:
            # todo: Hard coded, need to update from time to time
            return 79
        elif category_data.object_type == PornCategories.PORN_STAR_MAIN:
            # todo: Hard coded, need to update from time to time
            return 1754

        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        if category_data.object_type == PornCategories.CHANNEL:
            # Private treatment
            videos = tree.xpath('.//div[@class="info floatRight"]')
            videos = int(re.sub(r'[ ,]', '', videos[-1].text))
            videos_per_page = len(tree.xpath('.//div[@class="widgetContainer"]/ul/li'))
            return int(math.ceil((videos / videos_per_page)))
        if category_data.object_type == PornCategories.PORN_STAR:
            # Private treatment
            videos = tree.xpath('.//div[@class="showingInfo"]')
            if len(videos) > 0:
                raw_res = re.findall(r'\d+', videos[-1].text)
                # All pages has 40 videos
                return int(math.ceil((int(raw_res[2]) / 40)))
            else:
                videos = tree.xpath('.//div[@class="showingCounter pornstarVideosCounter"]')
                raw_res = re.findall(r'\d+', videos[0].text)
                # All pages has 36 videos
                return int(math.ceil((int(raw_res[2]) / 36)))
        if category_data.object_type == PornCategories.SEARCH_MAIN:
            # Private treatment
            videos = tree.xpath('.//div[@class="showingCounter"]')
            if len(videos) > 0:
                raw_res = re.findall(r'\d+', videos[-1].text)
                # All pages has 20 videos
                return int(math.ceil((int(raw_res[2]) / 20)))
            else:
                return 0
        else:
            videos = tree.xpath('.//div[@class="showingCounter"]')
            if len(videos) > 0:
                # New - try to fetch from general number of videos
                raw_res = re.findall(r'\d+', videos[0].text)
                # All pages has 44 videos except the first, which has 32
                return int(math.ceil(((int(raw_res[2]) - 32) / 44) + 1 if int(raw_res[2]) > 32 else 1))
            else:
                # Old
                available_pages = self._get_available_pages_from_tree(tree)
                if len(available_pages) == 0:
                    return 1
                return self._binary_search_max_number_of_pages_with_broken_pages(category_data,
                                                                                 last_available_number_of_pages)

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 1

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
        preview_videos = 4
        videos = [x for x in tree.xpath('.//ul/li') if 'data-video-id' in x.attrib][preview_videos:]
        res = []
        for video_tree_data in videos:
            additional_data = {'_vkey': video_tree_data.attrib['data-video-id']}

            link_data = [x for x in video_tree_data.xpath('.//a')
                         if 'class' in x.attrib and 'linkVideoThumb' in x.attrib['class']]
            assert len(link_data) == 1
            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] if 'src' in image_data[0].attrib else None
            if image is None or 'data:image' in image:
                # We try alternative path
                image = image_data[0].attrib['data-thumb_url']

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
            if len(viewers) == 0:
                # We have a premium video with no viewers
                continue

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
            # 'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_number is not None and page_number != 1:
            params['page'] = [page_number]
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

    @property
    def __version(self):
        return 3

    @property
    def _version_stack(self):
        return super(PornHub, self)._version_stack + [self.__version]
