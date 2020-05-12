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
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(TubeEight, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

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

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
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

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        script = [x for x in tmp_tree.xpath('.//script/text()') if 'var flashvars' in x]
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
        videos = (tree.xpath('.//div[@id="category_video_list"]/div[@class="gridList"]/figure') +
                  tree.xpath('.//div[@id="search_results_page_wrapper"]/div[@class="gridList"]/figure') +
                  tree.xpath('.//div[@class="pornstar-layout clearfix"]/div[@class="content"]/div[@class="gridList"]/'
                             'figure') +
                  tree.xpath('.//div[@class="channel_content_wrapper"]//div[@class="gridList channel_video_list"]/'
                             'figure') +
                  tree.xpath('.//div[@id="result_container_wrapper"]//div[@class="gridList"]/figure'))
        videos = [x for x in videos if 'data-videoid' in x.attrib]
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
            is_hd = len(is_hd) > 0 and is_hd[0] == 'HD'

            video_length = video_tree_data.xpath('./div[@class="thumb_box"]/span[@class="video-attribute-duration"]/'
                                                 'span[@class="video-duration"]/text()')
            video_length = video_length[0] if len(video_length) == 1 else None

            title = video_tree_data.xpath('./figcaption/p[@class="video-title"]/a/text()')
            assert len(title) == 1
            title = self._clear_text(title[0])

            number_of_viewers = video_tree_data.xpath('./figcaption/p[@class="video-attributes"]/'
                                                      'span[@class="video-views"]/span[2]/text()')
            assert len(number_of_viewers) == 1
            number_of_viewers = self._clear_text(number_of_viewers[0])

            rating = video_tree_data.xpath('./figcaption/p[@class="video-attributes"]/'
                                           'span[@class="video-likes"]/span[@class="icon-video-likes"]')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].tail)

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
                                                  is_hd=is_hd,
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

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(TubeEight, self)._version_stack + [self.__version]
