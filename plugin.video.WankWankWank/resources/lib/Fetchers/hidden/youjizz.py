# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote, parse_qsl

# Regex
import re

# JSON
import json

# M3U8
import m3u8

# Datetime
from datetime import datetime, timedelta

# Generator id
from ..id_generator import IdGenerator

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, PornCatalogPageNode, \
    VideoSource, VideoNode, VideoTypes
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter


class YouJizz(PornFetcher):
    video_format_order = {'mp4': 1, 'avc1.42e00a,mp4a.40.2': 0}
    max_flip_images = 8
    _time_format = '%Y-%m-%d'

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.youjizz.com/',  # Dummy suffix 'categories'
            PornCategories.TAG_MAIN: 'https://www.youjizz.com/tags',
            PornCategories.PORN_STAR_MAIN: 'https://www.youjizz.com/pornstars',
            PornCategories.POPULAR_VIDEO: 'https://www.youjizz.com/most-popular/1.html',
            PornCategories.LATEST_VIDEO: 'https://www.youjizz.com/newest-clips/1.html',
            PornCategories.RANDOM_VIDEO: 'https://www.youjizz.com/random',
            PornCategories.TOP_RATED_VIDEO: 'https://www.youjizz.com/top-rated/1.html',
            PornCategories.TRENDING_VIDEO: 'https://www.youjizz.com/trending/1.html',
            PornCategories.SEARCH_MAIN: 'https://www.youjizz.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.RANDOM_VIDEO: PornFilterTypes.RandomOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.TRENDING_VIDEO: PornFilterTypes.TrendingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.youjizz.com/'

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 5000

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': [(PornFilterTypes.PopularityOrder, 'Most Popular', 'most-popular'),
                                        (PornFilterTypes.DateOrder, 'Latest', 'newest-clips'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                        (PornFilterTypes.TrendingOrder, 'Trending', 'trending'),
                                        ],
                         'period_filters': ([(PornFilterTypes.AllDate, 'All time', None),
                                             (PornFilterTypes.OneDate, 'This Week', 'week'),
                                             (PornFilterTypes.TwoDate, 'This Month', 'month'),
                                             ],
                                            [('sort_order', [PornFilterTypes.RatingOrder])]),
                         }
        now_time = datetime.now()
        search_filters = \
            {'sort_order': ((PornFilterTypes.RelevanceOrder, 'Relevance', None),
                            (PornFilterTypes.DateOrder, 'Newest', 'recent'),
                            (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                            (PornFilterTypes.RatingOrder, 'Top Rated', 'rating'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'length'),
                            ),
             'added_before_filters': ((PornFilterTypes.AllAddedBefore, 'All time', None),
                                      (PornFilterTypes.OneAddedBefore, 'This Week',
                                       'date_added_min={md}&date_added_max={Md}'
                                       ''.format(md=(now_time-timedelta(days=7)).strftime(self._time_format),
                                                 Md=now_time.strftime(self._time_format))),
                                      (PornFilterTypes.TwoAddedBefore, 'This Month',
                                       'date_added_min={md}&date_added_max={Md}'
                                       ''.format(md=(now_time-timedelta(days=30)).strftime(self._time_format),
                                                 Md=now_time.strftime(self._time_format))),
                                      (PornFilterTypes.ThreeAddedBefore, 'Last 3 months',
                                       'date_added_min={md}&date_added_max={Md}'
                                       ''.format(md=(now_time-timedelta(days=30*3)).strftime(self._time_format),
                                                 Md=now_time.strftime(self._time_format))),
                                      (PornFilterTypes.FourAddedBefore, 'Last 6 months',
                                       'date_added_min={md}&date_added_max={Md}'
                                       ''.format(md=(now_time-timedelta(days=30*6)).strftime(self._time_format),
                                                 Md=now_time.strftime(self._time_format))),
                                      (PornFilterTypes.FiveAddedBefore, 'Last 9 months',
                                       'date_added_min={md}&date_added_max={Md}'
                                       ''.format(md=(now_time-timedelta(days=30*9)).strftime(self._time_format),
                                                 Md=now_time.strftime(self._time_format))),
                                      ),
             'length_filters': ((PornFilterTypes.AllLength, 'All durations', None),
                                (PornFilterTypes.OneLength, 'Short (1-3 min)', 'duration_max=180'),
                                (PornFilterTypes.TwoLength, 'Medium (3-10 min)', 'duration_min=180&duration_max=600'),
                                (PornFilterTypes.ThreeLength, 'Long (10-20 min)', 'duration_min=600&duration_max=1200'),
                                (PornFilterTypes.FourLength, 'Extra Long (+20 min)', 'duration_min=1200'),
                                ),
             'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', None),
                                 (PornFilterTypes.HDQuality, 'HD quality', 'hd=1'),
                                 ),
             }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='YouJizz', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(YouJizz, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/76.0.3809.100 Safari/537.36'

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x.attrib['href'],
                                       url=urljoin(self.base_url, x.attrib['href']),
                                       title=x.text.title(),
                                       object_type=PornCategories.CATEGORY,
                                       super_object=category_data,
                                       ) for x in tree.xpath('.//ul[@class="footer-menu-links"]/li/a')]

        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = tree.xpath('.//div[@class="tags-wrapper text-left"]/ul/li')
        res = []
        for porn_star in porn_stars:
            number_of_videos = porn_star.xpath('./span/text()')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0])[0])
            sub_object = porn_star.xpath('./a')
            assert len(sub_object) == 1
            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=sub_object[0].attrib['href'],
                                               url=urljoin(porn_star_data.url, sub_object[0].attrib['href']),
                                               title=sub_object[0].text.title(),
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        links = tree.xpath('.//div[@class="tags-wrapper text-left"]/ul/li/a/@href')
        titles = tree.xpath('.//div[@class="tags-wrapper text-left"]/ul/li/a/text()')
        number_of_videos = [int(re.findall(r'\d+', x)[0])
                            for x in tree.xpath('.//div[@class="tags-wrapper text-left"]/ul/li/span/text()')]
        assert len(titles) == len(links)
        assert len(titles) == len(number_of_videos)
        return links, titles, number_of_videos

    def _add_category_sub_pages(self, category_data, sub_object_type, page_request=None, clear_sub_elements=True):
        """
        Adds category sub pages.
        :param category_data: Category data object (PornCatalogCategoryNode).
        :param sub_object_type: Sub object type.
        :param page_request: Page request if such exist. In case it doesn't exist we fetch the object's url.
        :param clear_sub_elements: Flag that indicates whether we clear previous sub elements.
        :return:
        """
        if category_data.object_type == PornCategories.PORN_STAR_MAIN:
            if clear_sub_elements is True:
                category_data.clear_sub_objects()
            page_request = self.get_object_request(category_data)
            tree = self.parser.parse(page_request.text)
            new_pages = [PornCatalogPageNode(catalog_manager=self.catalog_manager,
                                             obj_id=(IdGenerator.id_to_original_str(category_data.id), x.text),
                                             title='{c} | Page {p}'.format(c=category_data.title, p=x.text),
                                             url=(urljoin(page_request.url, x.attrib['href'])
                                                  if 'href' in x.attrib else page_request.url),
                                             raw_data=category_data.raw_data,
                                             additional_data=category_data.additional_data,
                                             object_type=sub_object_type,
                                             super_object=category_data,
                                             )
                         for x in tree.xpath('.//div[@id="content"]/div[@id="pagination"]/*')]
            category_data.add_sub_objects(new_pages)
        else:
            return super(YouJizz, self)._add_category_sub_pages(category_data, sub_object_type, page_request,
                                                                clear_sub_elements)

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        request_data = re.findall(r'(?:var encodings = )(\[.*?\])(?:;)', tmp_request.text)
        if request_data[0] == '[]':
            request_data = re.findall(r'(?:var dataEncodings = )(\[.*?\])(?:;)', tmp_request.text)

        new_video_data = json.loads(request_data[0])
        video_links = []
        for new_video_datum in new_video_data:
            url = urljoin(video_data.url, new_video_datum['filename'])
            file_type = re.findall(r'(?:\.)(\w+$)', url.split('?')[0])[0]
            if file_type == 'mp4':
                # MP4
                video_links.append(VideoSource(link=url, resolution=new_video_datum['quality'], codec=file_type,
                                               video_type=VideoTypes.VIDEO_REGULAR))
            elif file_type == 'm3u8':
                # HLS
                segment_request = self.session.get(url)
                video_m3u8 = m3u8.loads(segment_request.text)
                video_playlists = video_m3u8.playlists
                video_links.extend([VideoSource(link=urljoin(url, x.uri),
                                                video_type=VideoTypes.VIDEO_SEGMENTS,
                                                quality=x.stream_info.bandwidth,
                                                resolution=x.stream_info.resolution[1],
                                                codec=x.stream_info.codecs)
                                    for x in video_playlists])

        video_links.sort(key=lambda x: (x.resolution,
                                        self.video_format_order[x.codec]
                                        if x.codec in self.video_format_order else -1),
                         reverse=True)
        return VideoNode(video_sources=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type in (PornCategories.TAG_MAIN, PornCategories.CATEGORY_MAIN):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        our_page = category_data.page_number if category_data.page_number is not None else 1
        if len(pages) == 0:
            return 1
        if (max(pages) - our_page) < self._binary_search_page_threshold:
            return max(pages)

        page_request = self.get_object_request(category_data, self.max_pages)
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) > 0 and max(pages) >= self.max_pages:
            return self.max_pages

        return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 9

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//ul[@class="pagination"]/li/a/text()') if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="video-item"]')
        res = []
        for video_tree_data in videos:
            # todo: continue from here
            link_data = video_tree_data.xpath('./div[@class="frame-wrapper"]/a')
            assert len(link_data) >= 1

            image_data = video_tree_data.xpath('./div[@class="frame-wrapper"]/a/img')
            assert len(image_data) >= 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])
            flip_images = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                           for i in range(1, self.max_flip_images + 1)]

            video_preview_data = video_tree_data.xpath('./div[@class="frame-wrapper"]/a/@data-clip')
            video_preview = urljoin(self.base_url, video_preview_data[0]) if len(video_preview_data) > 0 else None

            is_hd = video_tree_data.xpath('./div[@class="frame-wrapper"]/a/span[@class="i-hd"]')
            is_hd = len(is_hd) > 0 and is_hd[0].text == 'HD'

            title = video_tree_data.xpath('./div[@class="video-title"]/a/text()')
            title = title[0] if len(title) == 1 else ''

            video_length = video_tree_data.xpath('./div[@class="video-content-wrapper text-center"]/'
                                                 'span[@class="time"]')
            video_length = self._format_duration(video_length[0].text) if video_length[0].text is not None else None

            rating = video_tree_data.xpath('./div[@class="video-content-wrapper text-center"]/'
                                           'select[@class="video-bar-rating-view"]')
            assert len(rating) == 1
            rating = rating[0].attrib['data-value']

            viewers = video_tree_data.xpath('./div[@class="video-content-wrapper text-center"]/'
                                            'span[@class="views format-views"]')
            assert len(viewers) == 1
            viewers = viewers[0].text

            res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                obj_id=link_data[0].attrib['data-video-id'],
                                                url=urljoin(self.base_url, link_data[0].attrib['href']),
                                                title=title,
                                                image_link=image,
                                                flip_images_link=flip_images,
                                                preview_video_link=video_preview,
                                                is_hd=is_hd,
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
        if true_object.object_type == PornCategories.VIDEO:
            return self.session.get(fetch_base_url, headers=headers, params=params)

        if page_number is None:
            page_number = 1
        if true_object.object_type in self._default_sort_by:
            # if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            conditions = self.get_proper_filter(page_data).conditions
            true_sort_filter_id = self._default_sort_by[true_object.object_type] \
                if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id

            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                if len(split_url) <= 3:
                    split_url.append(page_filter.sort_order.value)
                split_url[3] += '-{s}'.format(s=page_filter.period.value)
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            if page_filter.sort_order.value is not None:
                split_url[4] = page_filter.sort_order.value + '_' + split_url[4].split('_')[-1]
            if page_filter.added_before.value is not None:
                params.update(parse_qsl(page_filter.added_before.value))
            if page_filter.length.value is not None:
                params.update(parse_qsl(page_filter.length.value))
            if page_filter.quality.value is not None:
                params.update(parse_qsl(page_filter.quality.value))

        if re.findall(r'\d+.html', split_url[-1]):
            split_url[-1] = re.sub(r'\d+.html', '{p}.html'.format(p=page_number), split_url[-1])
        elif true_object.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN,
                                         PornCategories.PORN_STAR_MAIN, PornCategories.RANDOM_VIDEO):
            # Ad hoc solution for un-enumerated pages
            pass
        else:
            raise ValueError('Wrong format of the page suffix')

        program_fetch_url = '/'.join(split_url)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}-1.html?'.format(q=quote(query.replace('_', '-')))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('/tags/12-inch-1.html')
    module = YouJizz()
    # module.get_available_categories()
    # module.download_object(None, category_id, verbose=1)
    module.download_category_input_from_user(use_web_server=False)
