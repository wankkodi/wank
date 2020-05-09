# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote_plus, parse_qsl

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# JSON
from ....tools.text_json_manioulations import prepare_json_from_not_formatted_text


class PornDoe(PornFetcher):
    video_data_request_template = 'https://porndoe.com/service/index?device=desktop&page=video&id={vid}'
    max_flix_image = 29

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://porndoe.com/categories',
            PornCategories.TAG_MAIN: 'https://porndoe.com/tags',
            PornCategories.CHANNEL_MAIN: 'https://porndoe.com/channels?sort=ranking',
            PornCategories.PORN_STAR_MAIN: 'https://porndoe.com/pornstars',
            PornCategories.LATEST_VIDEO: 'https://porndoe.com/videos',
            PornCategories.MOST_VIEWED_VIDEO: 'https://porndoe.com/videos?sort=views-down',
            PornCategories.TOP_RATED_VIDEO: 'https://porndoe.com/videos?sort=likes-down',
            PornCategories.LONGEST_VIDEO: 'https://porndoe.com/videos?sort=duration-down',
            PornCategories.POPULAR_VIDEO: 'https://porndoe.com/videos?sort=popular-down',
            PornCategories.SEARCH_MAIN: 'https://porndoe.com/search',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://porndoe.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        category_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Most Popular', None),
                                           (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'sort=alpha'),
                                           (PornFilterTypes.NumberOfVideosOrder, 'Most Movies', 'sort=movies'),
                                           ),
                            }
        channels_filters = {'sort_order': ((PornFilterTypes.RatingOrder, 'Rating', 'sort=ranking'),
                                           (PornFilterTypes.ViewsOrder, 'Views', 'sort=views-down'),
                                           ),
                            }
        porn_stars_filters = {'general_filters': ((PornFilterTypes.GirlType, 'Female', None),
                                                  (PornFilterTypes.GuyType, 'Male', 'sex=0'),
                                                  (PornFilterTypes.ShemaleType, 'Shemale', 'sex=2'),
                                                  ),
                              'sort_order': ((PornFilterTypes.RatingOrder, 'Rating', None),
                                             (PornFilterTypes.AlphabeticOrder, 'Alphabetically',
                                              'sort=alphabetically'),
                                             # (PornFilterTypes.AlphabeticOrder2, 'Alphabetically Descending',
                                             #  'sort=alphabetically-down'),
                                             (PornFilterTypes.RatingOrder, 'Ranking', 'sort=ranking'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Movies', 'sort=movies-down'),
                                             (PornFilterTypes.PopularityOrder, 'Popular', 'sort=popular-down'),
                                             ),
                              }
        single_porn_star_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Date', None),
                                                   (PornFilterTypes.ViewsOrder, 'Views', 'sort=views-down'),
                                                   (PornFilterTypes.RatingOrder, 'Likes', 'sort=likes-down'),
                                                   (PornFilterTypes.LengthOrder, 'Duration', 'sort=duration-down'),
                                                   (PornFilterTypes.PopularityOrder, 'Popularity', 'sort=popular-down'),
                                                   ),
                                    }

        video_filters = single_porn_star_filters.copy()
        video_filters['length_filters'] = ((PornFilterTypes.AllLength, 'Any duration', None),
                                           (PornFilterTypes.OneLength, '-10 min', 'd1=0&d2=10'),
                                           (PornFilterTypes.TwoLength, '10-20 min', 'd1=10&d2=20'),
                                           (PornFilterTypes.ThreeLength, '20-30 min', 'd1=20&d2=30'),
                                           (PornFilterTypes.FourLength, '30+ min', 'd1=30&d2=40'),
                                           )

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_filters,
                                         channels_args=channels_filters,
                                         porn_stars_args=porn_stars_filters,
                                         single_channel_args=single_porn_star_filters,
                                         single_porn_star_args=single_porn_star_filters,
                                         single_category_args=single_porn_star_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='PornDoe', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornDoe, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _update_available_categories(self, object_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="categories-listing"]/div[@class="item"]/span')
        res = []
        for category in categories:
            link_data = category.xpath('./span[@class="thumb"]/a')
            assert len(link_data) == 1 and 'href' in link_data[0].attrib
            url = urljoin(self.base_url, link_data[0].attrib['href'])
            cat_id = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] \
                if 'src' in image_data[0].attrib and 'data:image' not in image_data[0].attrib['src'] \
                else (image_data[0].attrib['data-src'] if 'data-src' in image_data[0].attrib else None)
            if image is not None:
                image = urljoin(self.base_url, image)

            title = category.xpath('./span[@class="flex-row"]/span/h2/a/span[@class="txt"]/text()')
            assert len(title) > 0
            title = self._clear_text(title[0])

            num_of_viewers = category.xpath('./span[@class="flex-row"]/span/h2/a/span[@class="txt"]/'
                                            'span[@class="count"]/text()')
            assert len(num_of_viewers) == 1
            num_of_viewers = int(re.sub(r'[(),]', '', str(num_of_viewers[0])))

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=cat_id,
                                                      url=url,
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=num_of_viewers,
                                                      object_type=PornCategories.CATEGORY,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        object_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, object_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="pornstars-listing"]/div[@class="item"]/span')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) > 0 and 'href' in link_data[0].attrib
            url = urljoin(object_data.url, link_data[0].attrib['href'])
            cat_id = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./span[@class="thumb"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] \
                if 'src' in image_data[0].attrib and 'data:image' not in image_data[0].attrib['src'] \
                else (image_data[0].attrib['data-src'] if 'data-src' in image_data[0].attrib else None)
            if image is not None:
                image = urljoin(self.base_url, image)
            title = image_data[0].attrib['alt']

            num_of_viewers = category.xpath('./span[@class="footer"]/span[@class="item-text left"]/span[@class="txt"]/'
                                            'text()')
            num_of_viewers = int(re.findall(r'\d+', str(num_of_viewers[0]))[0]) if len(num_of_viewers) > 0 else 0

            rating = category.xpath('./span[@class="footer"]/span[@class="item-text right"]/span[@class="txt"]/text()')
            rating = re.findall(r'\d+', str(rating[0])) if len(rating) > 0 else []
            rating = int(rating[0]) if len(rating) > 0 else None

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=cat_id,
                                                      url=url,
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=num_of_viewers,
                                                      rating=rating,
                                                      object_type=PornCategories.PORN_STAR,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        object_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, object_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="channels-listing "]/div[@class="item"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1 and 'href' in link_data[0].attrib
            url = urljoin(object_data.url, link_data[0].attrib['href'])
            cat_id = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./span[@class="thumb"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src'] \
                if 'src' in image_data[0].attrib and 'data:image' not in image_data[0].attrib['src'] \
                else (image_data[0].attrib['data-src'] if 'data-src' in image_data[0].attrib else None)
            if image is not None:
                image = urljoin(self.base_url, image)
            title = self._clear_text(image_data[0].attrib['alt'])

            info = category.xpath('./div[@class="footer"]//div[@class="channel-footer-block"]/span[@class="rank"]/'
                                  'span[@class="number"]')
            assert len(info) == 2
            rating = int(re.findall(r'\d+', info[0].text)[0])

            additional_data = {'number_of_views': self._clear_text(info[1].xpath('./span[2]/text()')[0])}

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=cat_id,
                                                      url=url,
                                                      title=title,
                                                      image_link=image,
                                                      additional_data=additional_data,
                                                      rating=rating,
                                                      object_type=PornCategories.CHANNEL,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        object_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return NotImplemented

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//ul[@class="this-page-lists"]/li/a')
        links = [x.attrib['href'] for x in raw_objects]
        titles = [x.text for x in raw_objects]
        number_of_videos = [None] * len(titles)
        assert len(titles) == len(links)
        # assert len(titles) == len(number_of_videos)

        return links, titles, number_of_videos

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        raw_data = tmp_request.json()
        res = sorted((VideoSource(link=v['url'], resolution=int(k))
                      for k, v in raw_data['video']['player']['sources'].items()
                      if len(re.findall(r'\.mp4', v['url'])) > 0),
                     key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=res)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return ([int(x) for x in tree.xpath('.//ul[@class="paginator"]/li/span/text()') if x.isdigit()] +
                [int(re.findall(r'\d+', x)[0]) for x in tree.xpath('.//ul[@class="paginator"]/li/a/@href')
                 if len(re.findall(r'\d+', x))])

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = [x for x in tree.xpath('.//div') if 'class' in x.attrib and 'videos-listing' in x.attrib['class']]
        assert len(videos) >= 1
        videos = [x for y in videos for x in y.xpath('./div') if 'data-id' in x.attrib]
        res = []
        for video_tree_data in videos:

            link_data = video_tree_data.xpath('./div/a[@class="video-item-thumb"]')
            assert len(link_data) == 1
            additional_data = {'channel': video_tree_data.attrib['data-channel']}
            if 'data-ng-under' in link_data[0].attrib:
                additional_data['video_request_id'] = link_data[0].attrib['data-ng-under']
            url = urljoin(self.base_url, link_data[0].attrib['href'])

            image_data = link_data[0].xpath('./picture/source')
            assert len(image_data) == 2
            image = image_data[0].attrib['src'] if 'src' in image_data[1].attrib else None
            if image is None or 'data:image' in image:
                image = image_data[0].attrib['data-srcset']

            video_preview = link_data[0].attrib['ng-preview'] if 'ng-preview' in link_data[0].attrib else None
            if len(video_preview) == 0:
                video_preview = None
            flip_images = [re.sub(r'_\d+.jpg', '_{i}.jpg'.format(i=i), image)
                           for i in range(0, self.max_flix_image + 1)]

            video_length = link_data[0].xpath('./span/span[@class="txt"]')
            is_hd = link_data[0].xpath('./span/span[@class="-mm-icon mm_icon-hd"]')

            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0].text)

            user = video_tree_data.xpath('./div[@class="bottom_part"]/div[@class="bottom-item-bar item-stats"]/'
                                         'a[@class="site"]')
            additional_data['uploader_data'] = {'name': user[0].text,
                                                'url': urljoin(self.base_url, user[0].attrib['href']),
                                                } if len(user) > 0 else None

            viewers = video_tree_data.xpath('./div[@class="bottom_part"]/div[@class="bottom-item-bar item-stats"]/'
                                            'div[@class="right-stats"]/span/span[@class="txt"]')
            assert len(viewers) == 1
            viewers = self._clear_text(viewers[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['data-id'],
                                                  url=url,
                                                  title=video_tree_data.attrib['data-title'],
                                                  preview_video_link=video_preview,
                                                  flip_images_link=flip_images,
                                                  image_link=image,
                                                  duration=self._format_duration(video_length),
                                                  is_hd=len(is_hd) > 0,
                                                  number_of_views=viewers,
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
        if true_object.object_type == PornCategories.VIDEO:
            if 'video_request_id' in page_data.additional_data:
                video_id = page_data.additional_data['video_request_id']
            else:
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                              'q=0.8,application/signed-exchange;v=b3',
                    'Cache-Control': 'max-age=0',
                    'Host': self.host_name,
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': self.user_agent
                }
                tmp_request = self.session.get(fetch_base_url, headers=headers)
                raw_data = re.findall(r'(?:window.variables *= *)({.*}?)(?:;)', tmp_request.text, re.DOTALL)
                raw_data = prepare_json_from_not_formatted_text(raw_data[0])
                video_id = raw_data['banners']['id']
            new_url = self.video_data_request_template.format(vid=video_id)
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Cache-Control': 'max-age=0',
                'Referer': fetch_base_url,
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': self.user_agent
            }
            page_request = self.session.get(new_url, headers=headers)
        else:
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
            if page_number is not None and page_number > 1:
                params['page'] = page_data.page_number
            if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
                params.update(parse_qsl(page_filter.sort_order.value))
            if page_filter.length.value is not None:
                params.update(parse_qsl(page_filter.length.value))
            if page_filter.general.value is not None:
                params.update(parse_qsl(page_filter.general.value))

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)

        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?keywords={q}'.format(q=quote_plus(query))
