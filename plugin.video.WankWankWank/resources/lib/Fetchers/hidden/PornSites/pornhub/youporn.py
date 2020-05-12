# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote_plus, parse_qs

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# JSON
import json


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
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(YouPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

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

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        script = [x for x in tmp_tree.xpath('.//script/text()') if 'mediaDefinition' in x]
        raw_data = re.findall(r'(?:mediaDefinition = )(\[.*\])(?:;\n)', script[0])
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
            image = image_data[0].attrib['src'] if 'data:image' not in image_data[0].attrib['src'] \
                else image_data[0].attrib['data-original']
            image = urljoin(self.base_url, image)

            flip_data = image_data[0].attrib['data-flipbook']
            number_of_flips = int(re.findall(r'(?:setLength: )(\d+)', flip_data)[0])
            first_i = int(re.findall(r'(?:firstThumbnail: )(\d+)', flip_data)[0])
            incrementer = int(re.findall(r'(?:incrementer: )(\d+)', flip_data)[0])
            flip_prefix = re.findall(r'(?:digitsPreffix: \')(.*?)(?:\',)', flip_data)[0]
            flip_suffix = re.findall(r'(?:digitsSuffix: \')(.*?)(?:\',)', flip_data)[0]
            flip_images = [flip_prefix + str(i) + flip_suffix
                           for i in range(first_i, number_of_flips+1, incrementer)]

            video_preview = urljoin(self.base_url, image_data[0].attrib['data-mediabook']) \
                if 'data-mediabook' in image_data[0].attrib else None

            title = video_tree_data.xpath('.//div[@class="video-box-title"]/text()')
            assert len(title) == 1
            title = re.sub(r'^[ \r\n]*|[ \r\n]*$', '', title[0])

            is_hd = video_tree_data.xpath('.//div[@class="video-duration-wrapper"]/div[@class="video-best-resolution"]')
            is_hd = len(is_hd) > 0 and is_hd[0] in ('720p', '1080p')

            video_length = video_tree_data.xpath('.//div[@class="video-duration-wrapper"]/div[@class="video-duration"]')
            assert len(video_length) == 1
            video_length = self._format_duration(video_length[0].text)

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
                                                image_link=image,
                                                flip_images_link=flip_images,
                                                preview_video_link=video_preview,
                                                is_hd=is_hd,
                                                duration=video_length,
                                                number_of_views=number_of_viewers,
                                                rating=rating,
                                                object_type=PornCategories.VIDEO,
                                                super_object=page_data,
                                                ))
        page_data.add_sub_objects(res)
        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
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

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(YouPorn, self)._version_stack + [self.__version]
