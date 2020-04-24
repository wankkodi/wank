# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote, quote_plus, unquote_plus, parse_qsl

# Regex
import re

# JSON
import json

# m3u8
import m3u8

# Datetime
from datetime import datetime

# Generator id
from ..id_generator import IdGenerator

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode, VideoTypes
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes, PornCatalogPageNode


class XHamster(PornFetcher):
    _default_single_page_sort_value = 'best'
    _default_video_page_sort_value = 'newest'

    video_format_order = {'mp4': 3, 'avc1.42e00a,mp4a.40.2': 2, 'h265': 1, 'vp9': 0}
    request_api = 'https://xhamster.com/x-api'

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://xhamster.com/',
            PornCategories.CHANNEL_MAIN: 'https://xhamster.com/channels',
            PornCategories.PORN_STAR_MAIN: 'https://xhamster.com/pornstars',
            PornCategories.TAG_MAIN: 'https://xhamster.com/categories',
            PornCategories.TOP_RATED_VIDEO: 'https://xhamster.com/best',
            PornCategories.MOST_VIEWED_VIDEO: 'https://xhamster.com/most-viewed',
            PornCategories.MOST_DISCUSSED_VIDEO: 'https://xhamster.com/most-commented',
            PornCategories.LATEST_VIDEO: 'https://xhamster.com/',
            PornCategories.SEARCH_MAIN: 'https://xhamster.com/search',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://xhamster.com/'

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
        curr_year = datetime.now().year
        prev_year = curr_year - 1
        general_filters = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', None),
                                               (PornFilterTypes.GayType, 'Gay', 'gay'),
                                               (PornFilterTypes.ShemaleType, 'Shemale', 'shemale'),
                                               ],
                           }
        video_filters = \
            {'sort_order': ((PornFilterTypes.DateOrder, 'Latest', None),
                            (PornFilterTypes.RatingOrder, 'Best', 'best'),
                            (PornFilterTypes.ViewsOrder, 'Views', 'most-viewed'),
                            (PornFilterTypes.CommentsOrder, 'Most Commented', 'most-commented'),
                            ),
             'period_filters': ((PornFilterTypes.AllDate, 'Any period', None),
                                (PornFilterTypes.OneDate, 'Year {y}'.format(y=curr_year),
                                 'year-{y}'.format(y=curr_year)),
                                (PornFilterTypes.TwoDate, 'Year {y}'.format(y=prev_year),
                                 'year-{y}'.format(y=prev_year)),
                                (PornFilterTypes.ThreeDate, 'Last Month', 'monthly'),
                                (PornFilterTypes.FourDate, 'Last Week', 'weekly'),
                                (PornFilterTypes.FiveDate, 'Today', 'daily'),
                                ),
             'length_filters': ((PornFilterTypes.AllLength, 'Any duration', None),
                                (PornFilterTypes.OneLength, '0-10 min', 'max-duration=10'),
                                (PornFilterTypes.TwoLength, '10-40 min', 'min-duration=10&max-duration=40'),
                                (PornFilterTypes.FourLength, '40+ min', 'min-duration=50'),
                                ),
             'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', None),
                                 (PornFilterTypes.HDQuality, 'HD quality', 'hd'),
                                 (PornFilterTypes.UHDQuality, '4K quality', '4k'),
                                 (PornFilterTypes.VRQuality, 'VR quality', 'vr'),
                                 ),
             }
        search_filters = \
            {'sort_order': ((PornFilterTypes.RelevanceOrder, 'Relevance', None),
                            (PornFilterTypes.DateOrder, 'Newest', 'sort=date'),
                            (PornFilterTypes.ViewsOrder, 'Views', 'sort=views'),
                            (PornFilterTypes.RatingOrder, 'Rating', 'sort=rating'),
                            (PornFilterTypes.LengthOrder, 'Duration', 'sort=duration'),
                            ),
             'period_filters': ((PornFilterTypes.AllDate, 'Any period', None),
                                (PornFilterTypes.OneDate, 'Last Year', 'date=year'),
                                (PornFilterTypes.TwoDate, 'Last Month', 'date=month'),
                                (PornFilterTypes.ThreeDate, 'Last Week', 'date=week'),
                                (PornFilterTypes.FourDate, 'Today', 'date=today'),
                                ),
             'length_filters': ((PornFilterTypes.AllLength, 'Any duration', None),
                                (PornFilterTypes.OneLength, '0-10 min', 'max-duration=10'),
                                (PornFilterTypes.TwoLength, '10-40 min', 'min-duration=10&max-duration=40'),
                                (PornFilterTypes.FourLength, '40+ min', 'min-duration=50'),
                                ),
             'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', None),
                                 (PornFilterTypes.HDQuality, 'HD quality', 'quality=hd'),
                                 (PornFilterTypes.UHDQuality, '4K quality', 'quality=4k'),
                                 (PornFilterTypes.VRQuality, 'VR quality', 'quality=vr'),
                                 ),
             }
        # todo: Add support for professional/amateur studios
        channels_filters = \
            {'sort_order': ((PornFilterTypes.PopularityOrder, 'Most Popular', None),
                            (PornFilterTypes.DateOrder, 'Recent Updates', 'updates'),
                            ),
             'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', None),
                                 (PornFilterTypes.VRQuality, 'VR quality', 'vr'),
                                 ),
             }
        porn_stars_filters = \
            {'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', None),
                                 (PornFilterTypes.UHDQuality, '4K quality', '4k'),
                                 (PornFilterTypes.VRQuality, 'VR quality', 'vr'),
                                 ),
             }
        single_porn_star_filters = \
            {'sort_order': ((PornFilterTypes.RatingOrder, 'Best', None),
                            (PornFilterTypes.DateOrder, 'Latest', 'newest'),
                            (PornFilterTypes.ViewsOrder, 'Views', 'most-viewed'),
                            (PornFilterTypes.CommentsOrder, 'Most Commented', 'most-commented'),
                            ),
             'period_filters': video_filters['period_filters'],
             'quality_filters': video_filters['quality_filters'],
             'length_filters': video_filters['length_filters'],
             }
        single_tag_filters = single_porn_star_filters
        single_channel_filters = single_porn_star_filters
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filters,
                                         channels_args=channels_filters,
                                         porn_stars_args=porn_stars_filters,
                                         single_category_args=search_filters,
                                         single_channel_args=single_channel_filters,
                                         single_porn_star_args=single_porn_star_filters,
                                         single_tag_args=single_tag_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='Xhamster', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(XHamster, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="all-categories"]/ul/li')
        res = []
        for category in categories:
            if 'class' in category.attrib and category.attrib['class'] == 'show-all-link':
                # We reached the end of our list
                break
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            title = self._clear_text(link_data[0].text) if link_data[0].text is not None else None
            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(category_data.url, link_data[0].attrib['href']),
                                                  title=title,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)

        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = tree.xpath('.//div[@class="pornstar-thumb-container"]')
        res = []
        for porn_star in porn_stars:
            link_data = porn_star.xpath('./a[@class="pornstar-thumb-container__image"]')
            image_data = link_data[0].xpath('./img')
            image = image_data[0].attrib['src'] if len(image_data) > 0 and 'src' in image_data[0].attrib else None

            ranking = porn_star.xpath('./a[2]/text()')
            assert len(ranking) == 1
            videos_raw_info = porn_star.xpath('./div[@class="pornstar-thumb-container__info"]/'
                                              'div[@class="pornstar-thumb-container__info-videos"]/i')
            assert len(videos_raw_info) == 2

            is_verified = porn_star.xpath('./a/i[@class="xh-icon verified-beta exclude-tablet"]')

            additional_data = {'ranking': self._clear_text(ranking[0]),
                               'number_of_views': self._clear_text(videos_raw_info[0].tail),
                               'is_verified': len(is_verified) == 1}
            number_of_videos = self._clear_text(videos_raw_info[1].tail)

            title = porn_star.xpath('./div[@class="pornstar-thumb-container__info"]/'
                                    'div[@class="pornstar-thumb-container__info-title"]/a')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(porn_star_data.url, link_data[0].attrib['href']),
                                                  image_link=image,
                                                  title=title,
                                                  additional_data=additional_data,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.PORN_STAR,
                                                  super_object=porn_star_data,
                                                  )
            res.append(object_data)

        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = tree.xpath('.//div[@class="channel-thumb-container"]')
        res = []
        for channel in porn_stars:
            link_data = channel.xpath('./div[@class="channel-thumb-container__image-container"]/a')
            assert len(link_data) >= 1
            image_data = link_data[0].xpath('./img')
            assert len(image_data) > 0
            image = image_data[0].attrib['src']
            logo_image_data = link_data[1].xpath('.//div[@class="logo-container"]')
            logo_image = re.findall(r'(?:url\()(.*?)(?:\))', logo_image_data[0].attrib['style'])[0] \
                if len(logo_image_data) == 1 else None

            ranking = channel.xpath('./div[@class="channel-thumb-container__image-container"]/a[3]/text()')
            assert len(ranking) == 1
            ranking = self._clear_text(ranking[0])

            subscribers = channel.xpath('./div[@class="channel-thumb-container__info"]/button')
            assert len(subscribers) == 1

            number_of_videos = channel.xpath('./div[@class="channel-thumb-container__info"]/'
                                             'div[@class="channel-thumb-container__info-videos"]')
            assert len(number_of_videos) == 1
            number_of_videos = self._clear_text(number_of_videos[0].text)
            if 'K' in number_of_videos:
                number_of_videos = int(float(re.findall(r'([\d.]*)(?:K)', number_of_videos)[0]) * 1000) + 99
            else:
                number_of_videos = int(re.findall(r'([\d.]*)(?: video)', number_of_videos)[0])

            additional_data = {'subscribers': int(subscribers[0].attrib['data-subscribers']),
                               'ranking': ranking,
                               'logo': logo_image,
                               }

            title = channel.xpath('./div[@class="channel-thumb-container__info"]/'
                                  'a[@class="channel-thumb-container__info-title"]')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(channel_data.url, link_data[0].attrib['href']),
                                                  image_link=image,
                                                  title=title,
                                                  additional_data=additional_data,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.CHANNEL,
                                                  super_object=channel_data,
                                                  )
            res.append(object_data)

        channel_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available tags.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        tree = self.parser.parse(page_request.text)
        tags = tree.xpath('.//div[@class="items"]/div[@class="item"]/a')
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x.attrib['href'],
                                       url=urljoin(tag_data.url, x.attrib['href']),
                                       title=self._clear_text(x.text),
                                       object_type=PornCategories.TAG
                                       if x.attrib['href'].split('/')[-2] == 'tags' else PornCategories.CATEGORY,
                                       super_object=tag_data,
                                       ) for x in tags]
        tag_data.add_sub_objects(res)
        return res

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return False

    def _add_category_sub_pages(self, category_data, sub_object_type, page_request=None, clear_sub_elements=True):
        """
        Adds category sub pages.
        :param category_data: Category data object (PornCatalogCategoryNode).
        :param sub_object_type: Sub object type.
        :param page_request: Page request if such exist. In case it doesn't exist we fetch the object's url.
        :param clear_sub_elements: Flag that indicates whether we clear previous sub elements.
        :return:
        """
        if category_data.object_type == PornCategories.TAG_MAIN:
            if clear_sub_elements is True:
                category_data.clear_sub_objects()
            return self._add_tag_sub_pages(category_data, sub_object_type)
        else:
            return super(XHamster, self)._add_category_sub_pages(category_data, sub_object_type, page_request,
                                                                 clear_sub_elements)

    def _add_tag_sub_pages(self, tag_data, sub_object_type):
        page_request = self.get_object_request(tag_data)
        tree = self.parser.parse(page_request.text)
        tags = tree.xpath('.//div[@class="alphabet"]/div/a')
        new_pages = [PornCatalogPageNode(catalog_manager=self.catalog_manager,
                                         obj_id=(IdGenerator.id_to_original_str(tag_data.id), i),
                                         title='{c} | Letter {p}'.format(c=tag_data.title, p=x.text),
                                         url=urljoin(tag_data.url, x.attrib['href']),
                                         raw_data=tag_data.raw_data,
                                         additional_data=tag_data.additional_data,
                                         object_type=PornCategories.PAGE,
                                         super_object=tag_data,
                                         ) for i, x in enumerate(tags[1:])]
        tag_data.add_sub_objects(new_pages)

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)

        request_data = re.findall(r'(?:window.initials = )({.*})(?:;)',
                                  [x for x in tmp_tree.xpath('.//script/text()') if 'window.initials' in x][0])
        # MP4
        new_video_data = json.loads(request_data[0])
        video_links = []
        for k, v in new_video_data['xplayerSettings']['sources']['standard'].items():
            for x in v:
                url = urljoin(video_data.url, x['url'])
                if re.findall(r'(?:\.)(\w+$)', url.split('?')[0])[0] == 'mp4':
                    video_links.append(VideoSource(link=url, resolution=x['quality'][:-1], codec=k,
                                                   video_type=VideoTypes.VIDEO_REGULAR))
        # HLS
        url = urljoin(video_data.url, new_video_data['xplayerSettings']['sources']['hls']['url'])
        segment_request = self.session.get(url)
        video_m3u8 = m3u8.loads(segment_request.text)
        video_playlists = video_m3u8.playlists
        video_links.extend([VideoSource(link=urljoin(url, x.uri),
                                        video_type=VideoTypes.VIDEO_SEGMENTS,
                                        quality=x.stream_info.bandwidth,
                                        resolution=x.stream_info.resolution[1],
                                        codec=x.stream_info.codecs)
                            for x in video_playlists])

        video_links.sort(key=lambda x: (x.resolution, self.video_format_order[x.codec]), reverse=True)
        return VideoNode(video_sources=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type == PornCategories.CATEGORY_MAIN:
            return 1
        else:
            page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
            if category_data.true_object.object_type in (PornCategories.SEARCH_MAIN, PornCategories.CATEGORY):
                raw_data = page_request.json()
                return raw_data[0]['extras']['entity']['paging']['maxPages']
            else:
                tree = self.parser.parse(page_request.text)
                pages = self._get_available_pages_from_tree(tree)
                return max(pages) if len(pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        pages = tree.xpath('.//div[@class="pager-container"]//li/a[@class="xh-paginator-button "]/text()')
        if len(pages) == 0:
            return pages
        return [int(re.sub(',', '', x)) for x in pages]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        if page_data.true_object.object_type in (PornCategories.SEARCH_MAIN, PornCategories.CATEGORY):
            raw_data = page_request.json()
            res = [PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                            obj_id=x['pageURL'],
                                            url=x['pageURL'],
                                            title=x['title'],
                                            image_link=x['thumbURL'],
                                            preview_video_link=x['trailerURL'],
                                            is_hd=x['isHD'],
                                            is_vr=x['isVR'],
                                            duration=x['duration'],
                                            number_of_views=x['views'],
                                            rating=x['rating']['value'],
                                            object_type=PornCategories.VIDEO,
                                            super_object=page_data,
                                            ) for x in raw_data[0]['responseData']]
        else:
            tree = self.parser.parse(page_request.text)
            if page_data.true_object.object_type == PornCategories.LATEST_VIDEO:
                videos = [x for x in tree.xpath('.//div')
                          if 'class' in x.attrib and
                          'thumb-list__item video-thumb' in x.attrib['class']]
            else:
                videos = tree.xpath('.//div[@class="thumb-list__item video-thumb"]')
            res = []
            for video_tree_data in videos:

                link_data = video_tree_data.xpath('./a')
                assert len(link_data) == 1
                link = link_data[0].attrib['href']

                is_hd = video_tree_data.xpath('./a/i')
                is_vr = False
                assert len(is_hd) == 1
                if 'thumb-image-container__icon' == is_hd[0].attrib['class']:
                    resolution = 'SD'
                elif 'thumb-image-container__icon thumb-image-container__icon--hd' == is_hd[0].attrib['class']:
                    resolution = 'HD'
                elif ('thumb-image-container__icon thumb-image-container__icon--hd thumb-image-container__icon--uhd' ==
                      is_hd[0].attrib['class']):
                    resolution = 'UHD'
                elif 'thumb-image-container__icon thumb-image-container__icon--vr' == is_hd[0].attrib['class']:
                    resolution = 'HD'
                    is_vr = True
                else:
                    raise RuntimeError('Wrong class of HD indicator!')
                is_hd = resolution != 'SD'

                image = video_tree_data.xpath('./a/img')
                assert len(image) == 1
                image = image[0].attrib['src']
                preview_video_link = link_data[0].attrib['data-previewvideo'] \
                    if 'data-previewvideo' in link_data[0].attrib else None

                video_length = video_tree_data.xpath('./a/div[@class="thumb-image-container__duration"]')
                assert len(video_length) == 1
                video_length = self._format_duration(video_length[0].text)

                title = video_tree_data.xpath('.//div[@class="video-thumb-info"]/a')
                assert len(title) == 1
                title = title[0].text

                viewers = video_tree_data.xpath('.//div[@class="video-thumb-info"]//'
                                                'div[@class="video-thumb-info__metric-container views"]/span')
                assert len(viewers) == 1
                viewers = viewers[0].text

                rating = (video_tree_data.xpath('.//div[@class="video-thumb-info"]//'
                                                'div[@class="video-thumb-info__metric-container rating colored-green"]/'
                                                'span') +
                          video_tree_data.xpath('.//div[@class="video-thumb-info"]//'
                                                'div[@class="video-thumb-info__metric-container rating colored-red"]/'
                                                'span'))
                assert len(rating) == 1
                rating = rating[0].text

                res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                    obj_id=link,
                                                    url=urljoin(self.base_url, link),
                                                    title=title,
                                                    image_link=image,
                                                    preview_video_link=preview_video_link,
                                                    is_hd=is_hd,
                                                    is_vr=is_vr,
                                                    duration=video_length,
                                                    number_of_views=viewers,
                                                    rating=rating,
                                                    object_type=PornCategories.VIDEO,
                                                    super_object=page_data,
                                                    ))

        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        split_url = fetch_base_url.split('/')
        if len(split_url[-1]) == 0:
            split_url.pop()
        # todo add special support for not straight categories (implemented in old style).
        # if (
        #         true_object.object_type == PornCategories.SEARCH_MAIN or
        #         (true_object.object_type == PornCategories.CATEGORY and
        #          self.general_filter.current_filters.general.filter_id == PornFilterTypes.StraightType)
        # ):
        # todo: add special treatment to the 4k/HD/VR categories (also implemented in old style).
        if true_object.object_type in (PornCategories.SEARCH_MAIN, PornCategories.CATEGORY):
            headers = {
                'Accept': '*/*',
                'Content-Type': 'text/plain',
                'Referer': fetch_base_url,
                # 'Host': self.host_name,
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }

            params['name'] = 'searchResultsCollectionFetch'
            params['requestData'] = {'q': unquote_plus(split_url[-1]),
                                     'page': page_number if page_number is not None else 1,
                                     }
            if page_filter.sort_order.value is not None:
                params['requestData'].update(parse_qsl(page_filter.sort_order.value, keep_blank_values=True))
            if page_filter.period.value is not None:
                params['requestData'].update(parse_qsl(page_filter.period.value, keep_blank_values=True))
            if page_filter.length.value is not None:
                params['requestData'].update(parse_qsl(page_filter.length.value, keep_blank_values=True))
            if page_filter.quality.value is not None:
                params['requestData'].update(parse_qsl(page_filter.quality.value, keep_blank_values=True))
            if self.general_filter.current_filters.general.filter_id == PornFilterTypes.StraightType:
                categories = {'straight': True, 'gay': False, 'shemale': False}
            elif self.general_filter.current_filters.general.filter_id == PornFilterTypes.GayType:
                categories = {'straight': False, 'gay': True, 'shemale': False}
            elif self.general_filter.current_filters.general.filter_id == PornFilterTypes.ShemaleType:
                categories = {'straight': False, 'gay': False, 'shemale': True}
            else:
                raise ValueError('Unsupported general filter type {ft}'
                                 ''.format(ft=self.general_filter.current_filters.general.filter_id))
            params['requestData']['categories'] = categories
            params = {'r': quote(json.dumps([params]))}
            page_request = self.session.get(self.request_api, headers=headers, params=params)

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
            if self.general_filter.current_filters.general.filter_id != PornFilterTypes.StraightType:
                if len(split_url) <= 3 or split_url[3] not in (x.value for x in self.general_filter.filters.general):
                    split_url.insert(3, self.general_filter.current_filters.general.value)
            if true_object.object_type in (PornCategories.TAG_MAIN, PornCategories.VIDEO):
                page_request = self.session.get(fetch_base_url, headers=headers)
                return page_request
            elif true_object.object_type in (PornCategories.CHANNEL_MAIN, PornCategories.PORN_STAR_MAIN):
                added_all = False
                if page_filter.sort_order.value is not None:
                    if added_all is False:
                        split_url.append('all')
                        added_all = True
                    split_url.append(page_filter.sort_order.value)
                if page_filter.quality.value is not None:
                    if added_all is False:
                        split_url.append('all')
                        # added_all = True
                    split_url.append(page_filter.quality.value)
                if page_number is not None and page_number != 1:
                    split_url.append(str(page_number))
            # elif true_object.object_type in (PornCategories.PORN_STAR, PornCategories.TAG, PornCategories.CHANNEL):
            else:
                added_sort_order = False
                if page_filter.quality.value is not None:
                    split_url.append(page_filter.quality.value)
                if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
                    split_url.append(page_filter.sort_order.value)
                    added_sort_order = True
                if page_filter.period.value is not None:
                    if added_sort_order is False:
                        # Add the default value
                        split_url.append(self._default_single_page_sort_value)
                        # added_sort_order = True
                    split_url.append(page_filter.period.value)
                if page_filter.length.value is not None:
                    params.update(parse_qsl(page_filter.length.value, keep_blank_values=True))
                if page_number is not None and page_number != 1:
                    split_url.append(str(page_number))

            # else:
            #     if page_filter.quality.value is not None:
            #         split_url.insert(-1, page_filter.quality.value)
            #     if page_filter.period.value is not None:
            #         split_url.append(page_filter.period.value)
            #     if page_filter.length.value is not None:
            #         params.update(parse_qsl(page_filter.length.value, keep_blank_values=True))
            #     if page_number is not None and page_number != 1:
            #         split_url.append(str(page_number))
            program_fetch_url = '/'.join(split_url)
            page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '/{q}'.format(q=quote_plus(query))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://xhamster.com/categories/18-year-old')
    module = XHamster()
    # module.get_available_categories()
    # module.download_object(None, category_id, verbose=1)
    module.download_category_input_from_user(use_web_server=False)
