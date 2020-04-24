# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote_plus

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, PornCatalogPageNode, VideoNode, \
    VideoSource
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# Generator id
from ..id_generator import IdGenerator

# Heritages
from abc import ABCMeta, abstractmethod


# todo: to make more precise test...
class BaseClass(PornFetcher):
    metaclass = ABCMeta

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    @abstractmethod
    def base_url(self):
        """
        Base site url.
        :return:
        """
        raise NotImplementedError

    @property
    def possible_empty_pages(self):
        """
        Defines whether it is possible to have empty pages in the site.
        :return:
        """
        return True

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, 'porn-categories/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, 'paysites/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, 'models/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, 'tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, 'videos/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, 'most-viewed/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, 'top-rated/'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, 'longest/'),
            PornCategories.MOST_DISCUSSED_VIDEO: urljoin(self.base_url, 'most-discussed/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, 'search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        self._video_filters = PornFilter(**self._prepare_filters())

    def _prepare_filters(self):
        length_filters = [(PornFilterTypes.AllLength, 'All', None),
                          (PornFilterTypes.OneLength, '0-5 min.', 'durationTo=300'),
                          (PornFilterTypes.TwoLength, '5-15 min.', 'durationFrom=300&durationTo=900'),
                          (PornFilterTypes.ThreeLength, '15-30 min.', 'durationFrom=900&durationTo=1800'),
                          (PornFilterTypes.FourLength, '30+ min.', 'durationFrom=1800'),
                          ]
        video_sort_order = [(PornFilterTypes.DateOrder, 'Newest', None),
                            (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                            (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                            (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                            ]
        video_sort_order2 = [(PornFilterTypes.RelevanceOrder, 'Most Relevant', None),
                             (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                             (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                             (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                             (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                             ]
        video_sort_order3 = [(PornFilterTypes.DateOrder, 'Most recent', 'videos'),
                             (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                             (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                             (PornFilterTypes.CommentsOrder, 'Most discussed', 'most-discussed'),
                             (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                             ]
        period_filter = [(PornFilterTypes.AllDate, 'All time', None),
                         (PornFilterTypes.OneDate, 'Today', 'day'),
                         (PornFilterTypes.TwoDate, 'Last 7 days', 'week'),
                         (PornFilterTypes.ThreeDate, 'Last 30 days', 'month'),
                         ]

        porn_starts_filters = {'sort_order': [(PornFilterTypes.RatingOrder, 'Ranking', 'rating'),
                                              (PornFilterTypes.AlphabeticOrder, 'Alphabetic', None),
                                              ],
                               }
        single_category_filters = {'sort_order': video_sort_order,
                                   'length_filters': length_filters,
                                   }
        video_filters = {'sort_order': video_sort_order3,
                         'length_filters': length_filters,
                         'period_filters': (period_filter, [('sort_order', [x[0] for x in video_sort_order3]), ]),
                         }
        search_filters = {'sort_order': video_sort_order2,
                          'length_filters': length_filters,
                          }
        return {'data_dir': self.fetcher_data_dir,
                'general_args': None,
                'categories_args': None,
                'tags_args': None,
                'porn_stars_args': porn_starts_filters,
                'channels_args': None,
                'single_category_args': single_category_filters,
                'single_tag_args': search_filters,
                'single_porn_star_args': None,
                'single_channel_args': single_category_filters,
                'video_args': video_filters,
                'search_args': search_filters,
                }

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_objects(category_data, './/div[@class="inner-box-container"]'
                                                                  '/div[@class="row"]'
                                                                  '//div[@class="item-inner-col inner-col"]/a',
                                                   PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channel.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_objects(channel_data, './/div[@class="inner-box-container"]'
                                                                 '/div[@class="row"]'
                                                                 '//div[@class="item-inner-col inner-col"]/a',
                                                   PornCategories.CHANNEL)

    def _update_available_porn_stars(self, pornstar_data):
        """
        Fetches all the available channel.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_objects(pornstar_data, './/div[@class="inner-box-container"]'
                                                                  '/div[@class="row"]'
                                                                  '//div[@class="item-inner-col inner-col"]/a',
                                                   PornCategories.PORN_STAR)

    def _update_available_base_objects(self, base_object_data, sub_object_xpath, object_type):
        page_request = self.get_object_request(base_object_data)

        tree = self.parser.parse(page_request.text)
        sub_objects = tree.xpath(sub_object_xpath)
        res = []
        used_ids = set()
        for sub_object in sub_objects:
            image_data = sub_object.xpath('./span[@class="image"]/img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])
            title = image_data[0].attrib['alt']

            rating = sub_object.xpath('./span[@class="item-info"]/span[@class="item-stats"]/'
                                      'span[@class="s-elem s-e-rate"]/span[@class="sub-desc"]/text()')
            rating = rating[0] if len(rating) > 0 else None

            number_of_videos = sub_object.xpath('./span[@class="item-info"]/span[@class="item-stats"]/'
                                                'span[@class="s-elem s-e-views"]/span[@class="sub-desc"]/text()')
            number_of_videos = number_of_videos[0] if len(number_of_videos) > 0 else None

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=sub_object.attrib['href'],
                                                  url=urljoin(self.base_url, sub_object.attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  rating=rating,
                                                  number_of_videos=number_of_videos,
                                                  object_type=object_type,
                                                  super_object=base_object_data,
                                                  )
            if object_data.id in used_ids:
                continue
            res.append(object_data)
            used_ids.add(object_data.id)
        base_object_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        links, titles, numbers_of_videos = self._get_tag_properties(page_request)
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=link,
                                       url=urljoin(self.base_url, link),
                                       title=title,
                                       number_of_videos=number_of_videos,
                                       object_type=PornCategories.TAG,
                                       super_object=tag_data,
                                       ) for link, title, number_of_videos in zip(links, titles, numbers_of_videos)]
        tag_data.add_sub_objects(res)
        return res

    def _add_tag_sub_pages(self, tag_data, sub_object_type):
        """
        Adds sub pages to the tags according to the first letter of the title. Stores all the tags to the proper pages.
        Notice that the current method contradicts with the _get_tag_properties method, thus you must use either of
        them, according to the way you want to implement the parsing (Use the _make_tag_pages_by_letter property to
        indicate which of the methods you are about to use...)
        :param tag_data: Tag data.
        :param sub_object_type: Object types of the sub pages (either Page or VideoPage).
        :return:
        """
        page_request = self.get_object_request(tag_data)
        tree = self.parser.parse(page_request.text)
        pages = tree.xpath('.//div[@class="alphabet-col col col-full"]/div[@class="alphabet-inner-col inner-col"]/a')
        new_pages = [PornCatalogPageNode(catalog_manager=self.catalog_manager,
                                         obj_id=(IdGenerator.id_to_original_str(tag_data.id), p.text),
                                         title='{c} | Letter {p}'.format(c=tag_data.title, p=p.text),
                                         url=urljoin(tag_data.url, p.attrib['href']),
                                         raw_data=tag_data.raw_data,
                                         additional_data={'letter': p.text},
                                         object_type=sub_object_type,
                                         super_object=tag_data,
                                         ) for p in pages[1:]]
        tag_data.add_sub_objects(new_pages)

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="textpage-inner-col inner-col"]/'
                                 'div[@style="width: 25%; min-width: 250px; float: left;"]/a')
        raw_numbers = tree.xpath('.//div[@class="textpage-inner-col inner-col"]/'
                                 'div[@style="width: 25%; min-width: 250px; float: left;"]/span')
        assert len(raw_objects) == len(raw_numbers)
        links, titles, number_of_videos = \
            zip(*[(x.attrib['href'], x.text, int(re.findall(r'\d+', y.text)[0]))
                  for x, y in zip(raw_objects, raw_numbers)])
        return links, titles, number_of_videos

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)

        if video_data.is_vr is True:
            # The site uses special engine for vr.
            request_data = tmp_tree.xpath('.//dl8-video/source')
            new_video_data = [dict(x.attrib) for x in request_data]
            res = sorted((VideoSource(link=x['src'], resolution=re.findall(r'\d+', x['quality'])[0])
                          for x in new_video_data if 'quality' in x and 'src' in x),
                         key=lambda x: int(), reverse=True)
        else:
            request_data = tmp_tree.xpath('.//video/source')
            if len(request_data) > 0:
                res = [VideoSource(link=x.attrib['src']) for x in request_data]
            else:
                # We try another method
                request_data = tmp_tree.xpath('.//li/a[@data-mb="download"]')
                res = [VideoSource(link=x.attrib['href']) for x in request_data]

        return VideoNode(video_sources=res, verify=False)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        start_page = category_data.page_number if category_data.page_number is not None else 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        max_page = max(pages)
        if (max_page - start_page) < self._binary_search_page_threshold:
            return max_page
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        pages = [int(x) for x in tree.xpath('.//div[@class="pagination-inner-col inner-col"]/*/text()')
                 if x.isdigit()]
        return pages

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 10

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        if page_data.super_object.object_type == PornCategories.PORN_STAR:
            videos = tree.xpath('.//div[@class="recent-uploads"]/div[@class="row"]/div/'
                                'div[@class="item-inner-col inner-col"]')
        else:
            videos = tree.xpath('.//div[@class="inner-box-container"]/div[@class="row"]/div/'
                                'div[@class="item-inner-col inner-col"]')
        res = []
        for video_tree_data in videos:
            video_preview = video_tree_data.attrib['data-video'] if 'data-video' in video_tree_data.attrib else None

            sub_node = video_tree_data.xpath('./a')
            assert len(sub_node) >= 1
            sub_node = sub_node[0]
            link = sub_node.attrib['href']
            title = sub_node.attrib['title'] if 'title' in sub_node.attrib else None

            data_node = (sub_node.xpath('./span[@class="image image-ar"]') +
                         sub_node.xpath('./span[@class="image"]') +
                         sub_node.xpath('./span[@class="image fadex"]')
                         )
            assert len(data_node) == 1
            data_node = data_node[0]

            image_data = (data_node.xpath('./div[@class="image-wrapp"]/img') +
                          data_node.xpath('./img'))
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])
            if title is None:
                title = image_data[0].attrib['alt'] if 'alt' in image_data[0].attrib else None
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image)
                           for d in range(1, int(image_data[0].attrib['data-opt-limit']) + 1)] \
                if 'data-opt-limit' in image_data[0].attrib else None

            video_length = data_node.xpath('./span[@class="time"]')
            if len(video_length) != 1:
                # We have a foreign object
                continue
            video_length = video_length[0].text
            if 'Photo' in video_length:
                # We have a gallery, skip that item...
                continue

            is_hd_data = data_node.xpath('./span[@class="quality"]/span')
            is_hd = len(is_hd_data) == 1 and is_hd_data[0].text == 'HD'
            is_vr = len(is_hd_data) == 1 and is_hd_data[0].text == 'VR'

            if title is None:
                title = sub_node.xpath('./span[@class="item-info"]/span[@class="title"]')
                assert len(title) == 1
                title = self._clear_text(title[0].text)

            viewers_xpath = './span[@class="item-info"]/span[@class="item-stats"]/' \
                            'span[@class="s-elem s-e-views"]/span[@class="sub-desc"]'
            viewers_data = sub_node.xpath(viewers_xpath) + video_tree_data.xpath(viewers_xpath)
            assert len(viewers_data) >= 1
            viewers = viewers_data[0].text
            is_vr = is_vr or (len(viewers_data) == 2 and 'VR' in viewers_data[1].text)

            rating_xpath = './span[@class="item-info"]/span[@class="item-stats"]/' \
                           'span[@class="s-elem s-e-rate"]/span[@class="sub-desc"]'
            rating = sub_node.xpath(rating_xpath) + video_tree_data.xpath(rating_xpath)
            assert len(rating) == 1
            rating = rating[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  is_hd=is_hd,
                                                  is_vr=is_vr,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  number_of_views=viewers,
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
            if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id

        # We remove page number from the suffix
        if page_number is not None and page_number != 1:
            if len(re.findall(r'page\d+\.html$', split_url[-1])) > 0:
                split_url.pop(-1)

        # Quality
        if (
                self.general_filter.current_filters.quality.value is not None and
                all(x is not None for x in self.general_filter.current_filters.quality.value)
        ):
            category_quality_filter, other_quality_filter = \
                self.video_filters.general_filters.current_filters.quality.value
            if true_object.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.CATEGORY):
                if category_quality_filter is not None:
                    split_url[3] = category_quality_filter
            elif true_object.object_type in (PornCategories.PORN_STAR_MAIN, PornCategories.PORN_STAR):
                pass
            else:
                if other_quality_filter is not None:
                    split_url.insert(3, other_quality_filter)

        # Sort order
        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            split_url.insert(-1, page_filter.sort_order.value)
        # Length filter
        if page_filter.length is not None and page_filter.length.value is not None:
            params.update(dict((x.split('=') for x in page_filter.length.value.split('&'))))
        # Period filter
        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            split_url.insert(-1, page_filter.period.value)

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Referer': page_data.url,
            # 'Host': urlparse(object_data.url).hostname,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_number is not None and page_number != 1:
            split_url.insert(-1, 'page{d}.html'.format(d=page_number))
            if len(split_url[-1]) == 0:
                split_url.pop(-1)

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


class BaseClass2(BaseClass):
    metaclass = ABCMeta

    @property
    def object_urls(self):
        res = super(BaseClass2, self).object_urls
        res.pop(PornCategories.TAG_MAIN)
        res[PornCategories.SEARCH_MAIN] = self.base_url
        return res

    @property
    @abstractmethod
    def base_url(self):
        """
        Base site url.
        :return:
        """
        raise NotImplementedError

    def _prepare_filters(self):
        quality_filters = [(PornFilterTypes.AllQuality, 'All', (None, None)),
                           (PornFilterTypes.VRQuality, 'VR', ('vr-porn-categories', 'vr')),
                           (PornFilterTypes.HDQuality, 'HD', ('categories', 'hd')),
                           ]
        length_filters = [(PornFilterTypes.AllLength, 'All', None),
                          (PornFilterTypes.OneLength, '0-5 min.', 'durationTo=300'),
                          (PornFilterTypes.TwoLength, '5-15 min.', 'durationFrom=300&durationTo=900'),
                          (PornFilterTypes.ThreeLength, '15-30 min.', 'durationFrom=900&durationTo=1800'),
                          (PornFilterTypes.FourLength, '30+ min.', 'durationFrom=1800'),
                          ]
        video_sort_order = [(PornFilterTypes.DateOrder, 'Newest', None),
                            (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                            (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                            (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                            ]
        video_sort_order2 = [(PornFilterTypes.RelevanceOrder, 'Most Relevant', None),
                             (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                             (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                             (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                             (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                             ]
        period_filter = [(PornFilterTypes.AllDate, 'All time', None),
                         (PornFilterTypes.OneDate, 'Today', 'day'),
                         (PornFilterTypes.TwoDate, 'Last 7 days', 'week'),
                         (PornFilterTypes.ThreeDate, 'Last 30 days', 'month'),
                         ]

        single_category_filters = {'sort_order': video_sort_order,
                                   'length_filters': length_filters,
                                   }
        single_porn_star_filters = {'length_filters': length_filters,
                                    }
        video_filters = {'sort_order': video_sort_order,
                         'length_filters': length_filters,
                         'period_filters': period_filter,
                         }
        search_filters = {'sort_order': video_sort_order2,
                          'length_filters': length_filters,
                          }
        return {'data_dir': self.fetcher_data_dir,
                'general_args': {'quality_filters': quality_filters},
                'categories_args': None,
                'tags_args': None,
                'channels_args': None,
                'single_category_args': single_category_filters,
                'single_tag_args': None,
                'single_porn_star_args': single_porn_star_filters,
                'single_channel_args': single_category_filters,
                'video_args': video_filters,
                'search_args': search_filters,
                }

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        return max(pages) if len(pages) > 0 else 1

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="inner-box-container"]/div[@class="row"]/div/'
                            'div[@class="item-inner-col inner-col"]')
        res = []
        for video_tree_data in videos:
            video_preview = video_tree_data.attrib['data-video'] if 'data-video' in video_tree_data.attrib else None

            sub_node = video_tree_data.xpath('./a')
            assert len(sub_node) >= 1
            sub_node = sub_node[0]
            link = sub_node.attrib['href']
            title = sub_node.attrib['title'] if 'title' in sub_node.attrib else None

            data_node = (sub_node.xpath('./span[@class="image image-ar"]') +
                         sub_node.xpath('./span[@class="image"]'))
            assert len(data_node) == 1
            data_node = data_node[0]

            image_data = (data_node.xpath('./div[@class="image-wrapp"]/img') +
                          data_node.xpath('./img'))
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if title is None:
                title = image_data[0].attrib['alt'] if 'alt' in image_data[0].attrib else None
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image)
                           for d in range(1, int(image_data[0].attrib['data-opt-limit']) + 1)] \
                if 'data-opt-limit' in image_data[0].attrib else None

            is_hd = data_node.xpath('./span[@class="quality"]/span')

            if title is None:
                title = sub_node.xpath('./span[@class="item-info"]/span[@class="title"]')
                assert len(title) == 1
                title = self._clear_text(title[0].text)

            video_length = sub_node.xpath('./span[@class="item-stats"]/'
                                          'span[@class="s-elem s-e-views"]/span[@class="sub-desc"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            rating = sub_node.xpath('./span[@class="item-stats"]/'
                                    'span[@class="s-elem s-e-rate"]/span[@class="sub-desc"]')
            assert len(rating) == 1
            rating = rating[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  is_hd=len(is_hd) == 1 and is_hd[0].text == 'HD',
                                                  is_vr=len(is_hd) == 1 and is_hd[0].text == 'VR',
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res


class BaseClass3(BaseClass):
    metaclass = ABCMeta
    _max_flip_images = 9

    @property
    def object_urls(self):
        res = super(BaseClass3, self).object_urls
        # res.pop(PornCategories.CHANNEL_MAIN)
        # res.pop(PornCategories.TAG_MAIN)
        res[PornCategories.CATEGORY_MAIN] = urljoin(self.base_url, '/cat/')
        return res

    @property
    @abstractmethod
    def base_url(self):
        """
        Base site url.
        :return:
        """
        raise NotImplementedError

    def _prepare_filters(self):
        length_filters = [(PornFilterTypes.AllLength, 'All', None),
                          (PornFilterTypes.OneLength, '0-5 min.', 'durationTo=300'),
                          (PornFilterTypes.TwoLength, '5-15 min.', 'durationFrom=300&durationTo=900'),
                          (PornFilterTypes.ThreeLength, '15-30 min.', 'durationFrom=900&durationTo=1800'),
                          (PornFilterTypes.FourLength, '30+ min.', 'durationFrom=1800'),
                          ]
        # video_sort_order = [(PornFilterTypes.DateOrder, 'Newest', None),
        #                     (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
        #                     (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
        #                     (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
        #                     ]
        video_sort_order2 = [(PornFilterTypes.RelevanceOrder, 'Most Relevant', None),
                             (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                             (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                             (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                             (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                             ]
        video_sort_order3 = [(PornFilterTypes.DateOrder, 'Most recent', 'videos'),
                             (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                             (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                             (PornFilterTypes.CommentsOrder, 'Most discussed', 'most-discussed'),
                             (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                             ]
        period_filter = [(PornFilterTypes.AllDate, 'All time', None),
                         (PornFilterTypes.OneDate, 'Today', 'day'),
                         (PornFilterTypes.TwoDate, 'Last 7 days', 'week'),
                         (PornFilterTypes.ThreeDate, 'Last 30 days', 'month'),
                         ]

        porn_starts_filters = {'sort_order': [(PornFilterTypes.RatingOrder, 'Ranking', 'rating'),
                                              (PornFilterTypes.AlphabeticOrder, 'Alphabetic', None),
                                              ],
                               }
        single_category_filters = {'length_filters': length_filters,
                                   }
        video_filters = {'sort_order': video_sort_order3,
                         'length_filters': length_filters,
                         'period_filters': (period_filter, [('sort_order', [x[0] for x in video_sort_order3]), ]),
                         }
        search_filters = {'sort_order': video_sort_order2,
                          # 'length_filters': length_filters,
                          }
        return {'data_dir': self.fetcher_data_dir,
                'general_args': None,
                'categories_args': None,
                'tags_args': None,
                'porn_stars_args': porn_starts_filters,
                'channels_args': None,
                'single_category_args': single_category_filters,
                'single_tag_args': search_filters,
                'single_porn_star_args': None,
                'single_channel_args': single_category_filters,
                'video_args': video_filters,
                'search_args': search_filters,
                }

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_objects(category_data, './/div[@class="box__bd-inner"]//'
                                                                  'a[@class="citem__link"]',
                                                   PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channel.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_objects(channel_data, './/div[@class="box__bd-inner"]//'
                                                                 'a[@class="citem__link"]',
                                                   PornCategories.CHANNEL)

    def _update_available_porn_stars(self, pornstar_data):
        """
        Fetches all the available channel.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_objects(pornstar_data, './/div[@class="box__bd-inner"]//'
                                                                  'a[@class="mitem__link"]',
                                                   PornCategories.PORN_STAR)

    def _update_available_base_objects(self, base_object_data, sub_object_xpath, object_type):
        page_request = self.get_object_request(base_object_data)

        object_prefix = re.findall(r'(?:")(\w+)(?:__link")', sub_object_xpath)[0]
        tree = self.parser.parse(page_request.text)
        sub_objects = tree.xpath(sub_object_xpath)
        res = []
        used_ids = set()
        for sub_object in sub_objects:
            img = sub_object.xpath('./span/img')
            assert len(img) == 1

            # title = sub_object.xpath('./span[@class="{op}__ct"]/span[@class="{op}__bd"]/span[@class="{op}__title"]'
            #                          ''.format(op=object_prefix))

            rating = sub_object.xpath('./span[@class="{op}__ft"]/span[@class="{op}__stat"]/'
                                      'span[@class="{op}__stat-label"]'.format(op=object_prefix))
            rating = rating[0] if len(rating) > 0 else None

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=sub_object.attrib['href'],
                                                  url=urljoin(self.base_url, sub_object.attrib['href']),
                                                  title=img[0].attrib['alt'],
                                                  image_link=img[0].attrib['src'],
                                                  rating=rating,
                                                  object_type=object_type,
                                                  super_object=base_object_data,
                                                  )
            if object_data.id in used_ids:
                continue
            res.append(object_data)
            used_ids.add(object_data.id)
        base_object_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        pages = [int(x) for x in tree.xpath('.//li[@class="pagination-list__li"]/*/text()')
                 if x.isdigit()]
        return pages

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = (tree.xpath('.//div[@class="box__bd-inner"]/div[@class="row -cols-narrow"]/div/'
                             'div[@class="item__inner"]') +
                  tree.xpath('.//div[@class="box__bd-inner"]/div[@class="row"]/div/'
                             'div[@class="item__inner"]'))
        res = []
        for video_tree_data in videos:
            sub_node = video_tree_data.xpath('./a[@class="item__link"]')
            assert len(sub_node) >= 1
            sub_node = sub_node[0]
            link = sub_node.attrib['href']
            title = sub_node.attrib['title'] if 'title' in sub_node.attrib else None

            image_node = sub_node.xpath('./span[@class="item__bd"]')
            image_node = image_node[0] if len(image_node) == 1 else None

            if image_node is not None:
                image_data = (image_node.xpath('./span[@class="item__thumb"]/img') +
                              image_node.xpath('./img'))
                assert len(image_data) == 1
                image = image_data[0].attrib['src']
                if title is None:
                    title = image_data[0].attrib['alt'] if 'alt' in image_data[0].attrib else None
                flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image)
                               for d in range(1, self._max_flip_images + 1)]
            else:
                image = None
                flip_images = None

            if title is None:
                title = image_node.xpath('span[@class="item__title"]/span[@class="item__title-label"]')
                assert len(title) == 1
                title = title[0].text

            data_node = sub_node.xpath('./span[@class="item__hd"]/span[@class="item__stats-bar"]')
            assert len(data_node) == 1
            data_node = data_node[0]

            video_length = data_node.xpath('./span[@class="item__stat -duration"]/span[@class="item__stat-label"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            rating = data_node.xpath('./span[@class="item__stat -bg-t1 -rating"]/span[@class="item__stat-label"]')
            assert len(rating) == 1
            rating = rating[0].text

            number_of_views = data_node.xpath('./span[@class="item__stat -views"]/span[@class="item__stat-label"]')
            assert len(number_of_views) == 1
            number_of_views = int(number_of_views[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  number_of_views=number_of_views,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res


# class PornPine(LaidHub):
#     @property
#     def max_pages(self):
#         """
#         Most viewed videos page url.
#         :return:
#         """
#         return 20000
#
#     @property
#     def object_urls(self):
#         return {
#             # CategoryMain: 'https://www.pornpine.com/channels/',
#             TagMain: 'https://www.pornpine.com/tags/',
#             VideoCategories.CHANNEL_MAIN: 'https://www.pornpine.com/channels/',
#             PornStarMain: 'https://www.pornpine.com/models/',
#             TopRatedVideo: 'https://www.pornpine.com/top-rated/',
#         }
#
#     @property
#     def base_url(self):
#         """
#         Base site url.
#         :return:
#         """
#         return 'https://www.pornpine.com/'
#
#     def __init__(self, source_name='StileProject', source_id=0, store_dir='.', data_dir='../Data'):
#         """
#         C'tor
#         :param source_name: save directory
#         """
#         super().__init__(source_name, source_id, store_dir, data_dir)
#
#     def _get_tag_properties(self, page_request):
#         """
#         Fetches tag links and titles.
#         :param page_request: Page request.
#         :return:
#         """
#         tree = self.parser.parse(page_request.text)
#         links = tree.xpath('.//ul[@class="item list-tags"]/li[@class="box"]/a/@href')
#         titles = tree.xpath('.//ul[@class="item list-tags"]/li[@class="box"]/a/span/b/text()')
#         number_of_videos = [None] * len(titles)
#         return links, titles, number_of_videos
#
#     def _add_tag_sub_pages(self, tag_data, sub_object_type):
#         return super(LaidHub, self)._add_tag_sub_pages(tag_data, sub_object_type)
#
#     def _update_available_channels(self, channel_data):
#         """
#         Fetches all the available channel.
#         :return: Object of all available shows (JSON).
#         """
#         return self._update_available_base_objects(channel_data,
#                                                    './/div[@class="list-sponsors"]/div[@class="cards-list"]'
#                                                    '/div[@class="card"]/a',
#                                                    Channel)
#
#     def _update_available_porn_stars(self, pornstar_data):
#         """
#         Fetches all the available channel.
#         :return: Object of all available shows (JSON).
#         """
#         return self._update_available_base_objects(pornstar_data,
#                                                    './/div[@class="list-models"]/div[@class="cards-list"]'
#                                                    '/div[@class="card"]/a',
#                                                    PornStar)
#
#     def _update_available_base_objects(self, base_object_data, sub_object_xpath, object_type):
#         page_request = self.get_object_request(base_object_data)
#
#         tree = self.parser.parse(page_request.text)
#         sub_objects = tree.xpath(sub_object_xpath)
#         res = []
#         used_ids = set()
#         for sub_object in sub_objects:
#             img = sub_object.xpath('./div[@class="card-img"]/img')
#             assert len(img) == 1
#
#             object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
#                                                   obj_id=sub_object.attrib['href'],
#                                                   url=urljoin(base_object_data.url, sub_object.attrib['href']),
#                                                   title=sub_object.attrib['title'],
#                                                   image_link=img[0].attrib['src'],
#                                                   object_type=object_type,
#                                                   super_object=base_object_data,
#                                                   )
#             if object_data.id in used_ids:
#                 continue
#             res.append(object_data)
#             used_ids.add(object_data.id)
#         base_object_data.add_sub_objects(res)
#         return res
#
#     def _get_available_pages_from_tree(self, tree):
#         """
#         In binary looks for the available pages from current page tree.
#         :param tree: Current page tree.
#         :return: List of available trees
#         """
#         pages = [int(x) for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a/text()')
#                  if x.isdigit()]
#         return pages
#
#     def _check_is_available_page(self, page_request):
#         """
#         In binary search performs test whether the current page is available.
#         :param page_request: Page request.
#         :return:
#         """
#         return page_request.ok
#
#     @property
#     def _binary_search_page_threshold(self):
#         """
#         Available pages threshold. 1 by default.
#         """
#         return 4
#
#     def get_videos_data(self, object_data):
#         """
#         Gets videos data for the given category.
#         :param object_data: Page data.
#         :return:
#         """
#         page_request = self.get_object_request(object_data)
#         tree = self.parser.parse(page_request.text)
#         videos = tree.xpath('.//div[@class="cards-list"]/div[@class="item card card-video  "]')
#         res = []
#         for video_tree_data in videos:
#             sub_node = video_tree_data.xpath('./a')
#             assert len(sub_node) >= 1
#             sub_node = sub_node[0]
#             link = sub_node.attrib['href']
#             if 'title' in sub_node.attrib:
#                 title = sub_node.attrib['title']
#             else:
#                 title = video_tree_data.xpath('./div[@class="card-footer noupp"]/strong[@class="card-name"]')
#                 assert len(title) == 1
#                 title = self._clear_text(title[0].text)
#
#             additional_categories = video_tree_data.xpath('./div[@class="card-footer noupp"]/'
#                                                           'div[@class="cols-tools"]/div/ul/li/a')
#             additional_data = {'categories': [{'name': x.text, 'link': x.attrib['href']}
#                                               for x in additional_categories]}
#             video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
#                                                   obj_id=link,
#                                                   url=urljoin(self.base_url, link),
#                                                   title=title,
#                                                   additional_data=additional_data,
#                                                   object_type=Video,
#                                                   super_object=object_data,
#                                                   )
#             res.append(video_data)
#         object_data.add_sub_objects(res)
#         return res
#
#     def get_object_request(self, object_data, override_page_number=None):
#         """
#         Fetches the page number with respect to base url.
#         :param object_data: Page data.
#         :param override_page_number: Override page number.
#         :return: Page request
#         """
#         program_fetch_url = object_data.url.split('?')[0]
#         if len(object_data.url.split('?')) > 1:
#             params = object_data.url.split('?')[1]
#             params = parse_qs(params)
#         else:
#             params = {}
#
#         headers = {
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
#                       'q=0.8,application/signed-exchange;v=b3',
#             'Cache-Control': 'max-age=0',
#             'Referer': object_data.url,
#             # 'Host': urlparse(object_data.url).hostname,
#             'Sec-Fetch-Mode': 'navigate',
#             'Sec-Fetch-Site': 'same-origin',
#             'Sec-Fetch-User': '?1',
#             'Upgrade-Insecure-Requests': '1',
#             'User-Agent': self.user_agent
#         }
#         page_number = object_data.page_number if override_page_number is None else override_page_number
#         if page_number is not None and page_number != 1:
#             program_fetch_url = re.sub(r'/(page\d+.html)*$', '', program_fetch_url)
#             program_fetch_url += '/{d}/'.format(d=page_number)
#
#         page_request = self.session.get(program_fetch_url, headers=headers, params=params)
#         return page_request
#

class LaidHub(BaseClass):
    # todo: add types (a bit tricky)

    @property
    def object_urls(self):
        res = super(LaidHub, self).object_urls
        res.pop(PornCategories.TAG_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.laidhub.com/'

    def _prepare_filters(self):
        res = super(LaidHub, self)._prepare_filters()
        res['single_tag_args'] = None
        quality_filters = [(PornFilterTypes.AllQuality, 'All', (None, None)),
                           (PornFilterTypes.VRQuality, 'VR', ('vr-porn-categories', 'vr')),
                           (PornFilterTypes.HDQuality, 'HD', ('categories', 'hd')),
                           ]
        res['general_args'] = {'quality_filters': quality_filters}
        return res

    def __init__(self, source_name='LaidHub', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(LaidHub, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)


class Nudez(BaseClass):
    # todo: add types (a bit tricky)

    @property
    def object_urls(self):
        res = super(Nudez, self).object_urls
        res.pop(PornCategories.CHANNEL_MAIN)
        res.pop(PornCategories.TAG_MAIN)
        res[PornCategories.CATEGORY_MAIN] = urljoin(self.base_url, 'channels/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://nudez.com/'

    def _prepare_filters(self):
        res = super(Nudez, self)._prepare_filters()
        res['single_tag_args'] = None
        res['single_channel_args'] = None
        return res

    def __init__(self, source_name='Nudez', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Nudez, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                    session_id)


class HypnoTube(BaseClass):
    @property
    def object_urls(self):
        res = super(HypnoTube, self).object_urls
        res.pop(PornCategories.CHANNEL_MAIN)
        res.pop(PornCategories.PORN_STAR_MAIN)
        res.pop(PornCategories.TAG_MAIN)
        res[PornCategories.CATEGORY_MAIN] = urljoin(self.base_url, 'channels/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://hypnotube.com/'

    def _prepare_filters(self):
        res = super(HypnoTube, self)._prepare_filters()
        res['porn_stars_args'] = None
        res['single_tag_args'] = None
        res['single_channel_args'] = None
        return res

    def __init__(self, source_name='HypnoTube', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HypnoTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)


class HandJobHub(BaseClass):
    @property
    def object_urls(self):
        res = super(HandJobHub, self).object_urls
        res.pop(PornCategories.PORN_STAR_MAIN)
        res[PornCategories.CATEGORY_MAIN] = urljoin(self.base_url, 'category/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://handjobhub.com/'

    def _prepare_filters(self):
        res = super(HandJobHub, self)._prepare_filters()
        res['porn_stars_args'] = None
        return res

    def __init__(self, source_name='HandJobHub', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HandJobHub, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)


class WetSins(BaseClass):
    @property
    def object_urls(self):
        res = super(WetSins, self).object_urls
        res.pop(PornCategories.CHANNEL_MAIN)
        res[PornCategories.CATEGORY_MAIN] = urljoin(self.base_url, 'channels/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.wetsins.com/'

    def _prepare_filters(self):
        res = super(WetSins, self)._prepare_filters()
        res['single_channel_args'] = None
        return res

    def __init__(self, source_name='WetSins', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(WetSins, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="textpage-inner-col inner-col"]/'
                                 'div[@style="width: 25%; min-width: 250px; float: left;"]/span/a')
        raw_numbers = tree.xpath('.//div[@class="textpage-inner-col inner-col"]/'
                                 'div[@style="width: 25%; min-width: 250px; float: left;"]/span/span')
        assert len(raw_objects) == len(raw_numbers)
        links, titles, number_of_videos = \
            zip(*[(x.attrib['href'], x.text, int(re.findall(r'\d+', y.text)[0]))
                  for x, y in zip(raw_objects, raw_numbers)])
        return links, titles, number_of_videos


class XnxxHamster(BaseClass):
    @property
    def object_urls(self):
        res = super(XnxxHamster, self).object_urls
        res.pop(PornCategories.CHANNEL_MAIN)
        res[PornCategories.CATEGORY_MAIN] = urljoin(self.base_url, 'channels/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://xnxxhamster.net/'

    def _prepare_filters(self):
        res = super(XnxxHamster, self)._prepare_filters()
        res['single_channel_args'] = None
        return res

    def __init__(self, source_name='XnxxHamster', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(XnxxHamster, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                          session_id)


class DrPornTube(BaseClass):
    @property
    def object_urls(self):
        res = super(DrPornTube, self).object_urls
        res.pop(PornCategories.CHANNEL_MAIN)
        res[PornCategories.CATEGORY_MAIN] = urljoin(self.base_url, 'channels/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.drporntube.com/'

    def _prepare_filters(self):
        res = super(DrPornTube, self)._prepare_filters()
        res['single_channel_args'] = None
        return res

    def __init__(self, source_name='DrPornTube', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(DrPornTube, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)


class SinClips(BaseClass):
    @property
    def object_urls(self):
        res = super(SinClips, self).object_urls
        res.pop(PornCategories.CHANNEL_MAIN)
        res.pop(PornCategories.CATEGORY_MAIN)
        res.pop(PornCategories.PORN_STAR_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://sinclips.com/'

    def _prepare_filters(self):
        res = super(SinClips, self)._prepare_filters()
        res['single_channel_args'] = None
        res['single_category_args'] = None
        res['porn_stars_args'] = None
        return res

    def __init__(self, source_name='SinClips', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SinClips, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)


class PornXio(BaseClass):
    @property
    def object_urls(self):
        res = super(PornXio, self).object_urls
        res[PornCategories.CATEGORY_MAIN] = urljoin(self.base_url, 'category/')
        res[PornCategories.CHANNEL_MAIN] = urljoin(self.base_url, 'studios/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://pornxio.com/'

    def __init__(self, source_name='PornXio', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornXio, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)


class PornRabbit(BaseClass2):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornrabbit.com/'

    def __init__(self, source_name='PornRabbit', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornRabbit, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)


class PornWatchers(BaseClass2):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornwatchers.com/'

    def __init__(self, source_name='PornWatchers', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornWatchers, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                           session_id)


class StileProject(BaseClass2):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.stileproject.com/'

    def __init__(self, source_name='StileProject', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(StileProject, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                           session_id)


class Eroxia(BaseClass3):
    @property
    def object_urls(self):
        res = super(Eroxia, self).object_urls
        # res.pop(PornCategories.CHANNEL_MAIN)
        res.pop(PornCategories.TAG_MAIN)
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.eroxia.com/'

    def __init__(self, source_name='Eroxia', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Eroxia, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)


if __name__ == '__main__':
    # category_id = IdGenerator.make_id('https://www.laidhub.com/porn-categories/60-fps/')
    category_id = IdGenerator.make_id('https://www.laidhub.com/porn-categories/big-tits/')
    channel_id = IdGenerator.make_id('https://www.laidhub.com/paysites/431/18-videoz/')
    pornstar_id = IdGenerator.make_id('https://www.laidhub.com/models/aimi-nakatani-2871.html')
    # module = LaidHub()
    # module = Nudez()
    # module = HypnoTube()
    # module = HandJobHub()
    # module = PornRabbit()
    # module = PornWatchers()
    # module = StileProject()
    module = PornXio()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['channels']['obj'], (channel_id, ), verbose=1)
    # module.download_object(module.objects['porn_stars']['obj'], (pornstar_id, ), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
