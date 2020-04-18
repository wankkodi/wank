# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError

# Internet tools
from .. import urljoin, quote_plus, parse_qs

# Regex
import re

# Generator id
from ..id_generator import IdGenerator

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


class SexTvX(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.sextvx.com/en/categories/',
            PornCategories.TAG_MAIN: 'https://www.sextvx.com/en/tags/',
            PornCategories.PORN_STAR_MAIN: 'https://www.sextvx.com/en/pornstars/',
            PornCategories.LATEST_VIDEO: 'https://www.sextvx.com/en/recent/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.sextvx.com/en/popular/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.sextvx.com/en/best/',
            # PornCategories.TOP_RATED_VIDEO: 'https://www.sextvx.com/en/best/month/',
            PornCategories.HD_VIDEO: 'https://www.sextvx.com/en/hd_porn/',
            PornCategories.SEARCH_MAIN: 'https://www.sextvx.com/en/results',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.HD_VIDEO: PornFilterTypes.QualityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.sextvx.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Latest', 'recent'),
                                        (PornFilterTypes.BestOrder, 'Best', 'best'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'popular'),
                                        (PornFilterTypes.CommentsOrder, 'Most commented', 'commented'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'rated'),
                                        ),
                         'length_filters': ((PornFilterTypes.AllLength, 'Any duration', 'all-time'),
                                            (PornFilterTypes.OneLength, '0-10 min', 'ten-min'),
                                            (PornFilterTypes.TwoLength, '10+ min', 'ten-more'),
                                            ),
                         }
        search_filters = {'sort_order': ((PornFilterTypes.RelevanceOrder, 'All', 'sortby='),
                                         (PornFilterTypes.ViewsOrder, 'Most Viewed', 'sortby=v'),
                                         (PornFilterTypes.RatingOrder, 'Top Rated', 'sortby=r'),
                                         ),
                          'period_filters': ((PornFilterTypes.AllDate, 'All time', 'uploaded='),
                                             (PornFilterTypes.TwoDate, 'This Week', 'uploaded=w'),
                                             (PornFilterTypes.OneDate, 'This Month', 'uploaded=m'),
                                             ),
                          'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', 'is_hd='),
                                              (PornFilterTypes.HDQuality, 'HD quality', 'is_hd=y'),
                                              ),
                          'length_filters': ((PornFilterTypes.AllLength, 'Any duration', 'search_duration='),
                                             (PornFilterTypes.OneLength, 'Short (4 min)', 'search_duration=short'),
                                             (PornFilterTypes.TwoLength, '10+ min', 'search_duration=long'),
                                             ),
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_tag_args=video_filters,
                                         single_category_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='SexTvX', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SexTvX, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="panes ptube carousel"]/div[@class="video rotate"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-src']

            title_data = category.xpath('./div[@class="thumb-info"]')
            assert len(title_data) == 1
            title = title_data[0].xpath('./h3/a')
            assert len(title) == 1
            title = title[0].text

            number_of_videos = title_data[0].xpath('./span[@class="duration"]/i')
            assert len(number_of_videos) == 1
            number_of_videos = int(self._clear_text(number_of_videos[0].tail))

            rating = title_data[0].xpath('./span[@class="rating"]/i')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].tail)

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  image_link=image,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  number_of_videos=number_of_videos,
                                                  rating=rating,
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
        porn_stars = tree.xpath('.//div[@class="video rotate pstar"]')
        res = []
        for porn_star in porn_stars:
            link_data = porn_star.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = porn_star.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            video_preview = porn_star.xpath('./a/div')
            video_preview = video_preview[0].attrib['data-url'] if len(video_preview) == 1 else None

            title = porn_star.xpath('./div[@class="thumb-info"]/h3/a')
            assert len(title) == 1
            title = title[0].text

            number_of_videos = porn_star.xpath('./div[@class="thumb-info"]/span[@class="nbvids"]/*')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].tail)[0])

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link) + 'video/all',
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  video_preview_link=video_preview,
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
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//ul/li[@class="tag"]/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, int(re.findall(r'\d+', x.tail)[0]))
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
        videos = tmp_tree.xpath('.//video/source')
        videos = sorted((VideoSource(link=x.attrib['src'], resolution=int(re.findall(r'\d+', x.attrib['title'])[0]))
                         for x in videos),
                        key=lambda y: y.resolution, reverse=True)
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1
        try:
            page_request = self.get_object_request(category_data, override_page_number=2) \
                if fetched_request is None else fetched_request
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
        return [int(x) for x in tree.xpath('.//div[@class="navbar pagination pagination-centered"]/ul/li/a/text()') +
                tree.xpath('.//div[@class="navbar search-nav pagination pagination-centered"]/ul/li/a/text()')
                if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = (tree.xpath('.//div[@class="panes ptube carousel"]/div') +
                  tree.xpath('.//div[@class="panes carousel ptubenew"]/div'))
        res = []
        for video_tree_data in videos:
            if page_data.true_object.object_type == PornCategories.PORN_STAR:
                link_data = video_tree_data.xpath('./div[@class="video_thumb"]/a')
            else:
                link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1

            link = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            title = image_data[0].attrib['alt']
            image = image_data[0].attrib['src'] if 'src' in image_data[0].attrib else image_data[0].attrib['data-src']

            video_preview = (video_tree_data.xpath('./a/div[@class="videoprev"]') +
                             video_tree_data.xpath('./a/div[@class="videoprev hide"]'))
            video_preview = video_preview[0].attrib['data-url'] \
                if len(video_preview) == 1 and 'data-url' in video_preview[0].attrib else None

            resolution_data = video_tree_data.xpath('./a/span[@class="hd-res"]')
            resolution = resolution_data[0].text if len(resolution_data) > 0 else None
            is_hd = len(resolution_data) > 0

            video_length_data = video_tree_data.xpath('./div[@class="thumb-info"]/span[@class="duration"]')
            assert len(video_length_data) == 1
            video_length = self._format_duration(video_length_data[0].tail) \
                if video_length_data[0].tail is not None else None

            rating_data = video_tree_data.xpath('./div[@class="thumb-info"]/span[@class="rating"]')
            assert len(rating_data) == 1
            rating = self._clear_text(rating_data[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  preview_video_link=video_preview,
                                                  is_hd=is_hd,
                                                  resolution=resolution,
                                                  duration=video_length,
                                                  rating=rating,
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
        last_slash = fetch_base_url[-1] == '/'
        if not last_slash:
            split_url.append('')
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
        if true_object.object_type == PornCategories.SEARCH_MAIN:
            if page_filter.sort_order.value is not None:
                params.update(parse_qs(page_filter.sort_order.value, keep_blank_values=True))
            if page_filter.period.value is not None:
                params.update(parse_qs(page_filter.period.value, keep_blank_values=True))
            if page_filter.length.value is not None:
                params.update(parse_qs(page_filter.length.value, keep_blank_values=True))
            if page_filter.quality.value is not None:
                params.update(parse_qs(page_filter.quality.value, keep_blank_values=True))
            if page_number is not None and page_number != 1:
                params['page'] = page_number

            program_fetch_url = fetch_base_url
        else:
            # if page_filter.sort_order.value is not None:
            if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
                split_url.insert(-1, page_filter.sort_order.value)
                last_slash = True
            if page_filter.length.value is not None:
                split_url.insert(-1, page_filter.length.value)
                last_slash = True
            if page_number is not None and page_number != 1:
                split_url.insert(-1, str(page_number))
            if last_slash is False:
                split_url.pop()
            program_fetch_url = '/'.join(split_url)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw number, i.e. '7m:58s'.
        :return:
        """
        final_duration = 0
        hours = re.findall(r'(\d+)(?: *h)', raw_duration)
        minutes = re.findall(r'(\d+)(?: *m)', raw_duration)
        seconds = re.findall(r'(\d+)(?: *s)', raw_duration)
        if len(hours) > 0:
            final_duration += 3600 * int(hours[0])
        if len(minutes) > 0:
            final_duration += 60 * int(minutes[0])
        if len(seconds) > 0:
            final_duration += int(seconds[0])
        return raw_duration

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?search_query={q}'.format(q=quote_plus(query))


if __name__ == '__main__':
    # category_id = IdGenerator.make_id('/search/biggest-tits/')
    category_id = IdGenerator.make_id('/en/category/vintage')
    porn_star_id = IdGenerator.make_id('/en/pornstar/76351/alana-evans/')
    module = SexTvX()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['porn_stars']['obj'], (porn_star_id, ), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
