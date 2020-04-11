# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError

# Internet tools
from .. import urljoin, quote_plus

# Regex
import re

# Generator id
from ..id_generator import IdGenerator

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# Math
import math


# todo: the orientation is partly implemented in the site. Check for later support...
class VPorn(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.vporn.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://www.vporn.com/pornstars/',
            PornCategories.LATEST_VIDEO: 'https://www.vporn.com/newest/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.vporn.com/views/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.vporn.com/rating/',
            PornCategories.FAVORITE_VIDEO: 'https://www.vporn.com/favorites/',
            PornCategories.MOST_DISCUSSED_VIDEO: 'https://www.vporn.com/comments/',
            PornCategories.POPULAR_VIDEO: 'https://www.vporn.com/votes/',
            PornCategories.LONGEST_VIDEO: 'https://www.vporn.com/longest/',
            PornCategories.SEARCH_MAIN: 'https://www.vporn.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.VotesOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.vporn.com'

    @property
    def number_of_videos_per_page(self):
        """
        Base site url.
        :return:
        """
        return 30  # 5*6

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': ((PornFilterTypes.FeaturedOrder, 'Selected', None),
                                        (PornFilterTypes.DateOrder, 'Newest', 'newest'),
                                        (PornFilterTypes.ViewsOrder, 'Views', 'views'),
                                        (PornFilterTypes.RatingOrder, 'Rating', 'rating'),
                                        (PornFilterTypes.FavorOrder, 'Favorite', 'favorites'),
                                        (PornFilterTypes.CommentsOrder, 'Comments', 'comments'),
                                        (PornFilterTypes.VotesOrder, 'Votes', 'votes'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        ),
                         'period_filters': ((PornFilterTypes.AllDate, 'All time', None),
                                            (PornFilterTypes.OneDate, 'Last Month', 'month'),
                                            (PornFilterTypes.TwoDate, 'Last Week', 'week'),
                                            (PornFilterTypes.ThreeDate, '24H', 'today'),
                                            ),
                         'length_filters': ((PornFilterTypes.AllLength, 'Any duration', None),
                                            (PornFilterTypes.OneLength, '0-15 min', 'duration/0~15'),
                                            (PornFilterTypes.TwoLength, '15-30', 'duration/15~30'),
                                            (PornFilterTypes.ThreeLength, '30+ min', 'duration/30~90'),
                                            ),
                         'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', None),
                                             (PornFilterTypes.HDQuality, 'HD quality', 'hd'),
                                             ),
                         }
        search_filters = {'sort_order': (((PornFilterTypes.RelevanceOrder, 'Relevance', None), ) +
                                         video_filters['sort_order'][1:]),
                          'period_filters': video_filters['period_filters'],
                          # 'length_filters': video_filters['length_filters'],
                          'quality_filters': video_filters['quality_filters'],
                          }
        porn_stars_filters = \
            {'sort_order': ((PornFilterTypes.PopularityOrder, 'Popular', None),
                            (PornFilterTypes.ViewsOrder, 'Views', 'views'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetic', 'alphabetic'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'videos'),
                            (PornFilterTypes.SubscribersOrder, 'Subscribers', 'subscribed'),
                            ),
             }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filters,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='VPorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(VPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="categories"]/a')
        res = []
        for category in categories:
            image = category.xpath('./img/@src')
            assert len(image) == 1

            title = category.xpath('./span[@class="details"]/span[@class="title"]/text()')
            assert len(title) == 1

            number_of_videos = category.xpath('./span[@class="details"]/span[@class="videos"]/text()')
            assert len(number_of_videos) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=title[0],
                                                  image_link=image[0],
                                                  number_of_videos=int(number_of_videos[0]),
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
        categories = tree.xpath('.//div[@class="pornstars-list"]/div[@class="star"]/a')
        res = []
        for category in categories:
            image_data = category.xpath('./div[@style="position: relative;"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            nationality = category.xpath('./div[@style="position: relative;"]/span[@class="flag-infolist"]/img')
            additional_data = {'nationality': re.findall(r'(\w+)(?:\.png$)', nationality[0].attrib['src'])[0]} \
                if len(nationality) == 1 else {}

            is_verified = category.xpath('./div[@style="position: relative;"]/span[@class="verify-infolist"]')
            additional_data['is_verified'] = (len(is_verified) == 1 and 'alt' in is_verified[0].attrib and
                                              is_verified[0].attrib['alt'] == 'Verified')

            rank = category.xpath('./div[@style="position: relative;"]/span[@class="rank-infolist"]/span')
            assert len(rank) == 1
            additional_data['rank'] = int(self._clear_text(rank[0].text))

            number_of_videos = category.xpath('./div[@class="star-infolist"]/span[2]')
            assert len(number_of_videos) == 1
            additional_data['number_of_views'] = re.findall(r'(?: +)(\d+.*?)(?: views)', number_of_videos[0].text)
            number_of_videos = re.findall(r'(\d+.*?)(?: Videos)', number_of_videos[0].text)

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=int(number_of_videos[0]),
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
        videos = tmp_tree.xpath('.//video/source')
        assert len(videos) > 0
        video_links = sorted((VideoSource(link=x.attrib['src'], resolution=re.findall(r'\d+', x.attrib['label'])[0])
                              for x in videos),
                             key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=video_links)

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumblist videos"]/div[@class="video"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = [x for x in video_tree_data.xpath('./a/div[@class="thumb videothumb"]/img')
                          if 'id' in x.attrib]
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            flip_image = ['{s}d{pid}.jpg'.format(s=image_data[0].attrib['data-path'], pid=x)
                          for x in re.findall(r'\d+', image_data[0].attrib['data-thumbs'])]

            video_length = video_tree_data.xpath('./a/div[@class="thumb videothumb"]/span[@class="thumb-time"]/'
                                                 'span[@class="time"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            is_hd = video_tree_data.xpath('./a/div[@class="thumb videothumb"]/span[@class="thumb-time"]/'
                                          'span[@class="hd-marker is-hd"]')

            title = video_tree_data.xpath('./a/div[@class="thumb-info"]/span[@class="cwrap"]/text()')
            assert len(title) == 1
            title = self._clear_text(title[0])

            uploader = video_tree_data.xpath('./a/div[@class="thumb-info"]/p/span/text()')
            assert len(uploader) == 1
            additional_data = {'uploader': uploader[0]}

            number_of_viewers = video_tree_data.xpath('./a/div[@class="thumb-info"]/span[@class="views"]/img')
            assert len(number_of_viewers) == 1
            number_of_viewers = self._clear_text(number_of_viewers[0].tail)

            rating = video_tree_data.xpath('./a/div[@class="thumb-info"]/span[@class="likes"]/img')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].tail)

            added_before = video_tree_data.xpath('./a/div[@class="thumb-info"]/span[@class="added"]/img')
            assert len(added_before) == 1
            added_before = self._clear_text(added_before[0].tail)

            res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                obj_id=link,
                                                url=urljoin(page_data.url, link),
                                                title=title,
                                                image_link=image,
                                                flip_images_link=flip_image,
                                                is_hd=len(is_hd) > 0,
                                                duration=self._format_duration(video_length[0]),
                                                number_of_views=number_of_viewers,
                                                rating=rating,
                                                added_before=added_before,
                                                additional_data=additional_data,
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
        # At first we try to check whether we have max page from the initial page.
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        else:
            current_page = category_data.page_number if category_data.page_number is not None else 1
            max_page = max(pages)
            if max_page - current_page < self._binary_search_page_threshold:
                return max_page

        if self._binary_search_check_is_available_page(category_data, self.max_pages)[0]:
            return self.max_pages
        # We perform binary search
        return self._binary_search_max_number_of_pages(category_data)

    def _binary_search_max_number_of_pages(self, category_data):
        """
        Slightly modified version...
        Performs binary search in order to find the last available page.
        :param category_data: Category data.
        :return: Page request
        """
        left_page = 1
        right_page = self.max_pages
        page = math.ceil((right_page + left_page) / 2)
        # prev_referer = None
        while 1:
            is_available, page_request = self._binary_search_check_is_available_page(category_data, page)
            if not is_available:
                # We moved too far...
                right_page = page - 1
                page = math.ceil((right_page + left_page) / 2)
            else:
                tree = self.parser.parse(page_request.text)
                pages = self._get_available_pages_from_tree(tree)
                if len(pages) == 0:
                    # We also moved too far...
                    right_page = page - 1
                    page = math.ceil((right_page + left_page) / 2)
                else:
                    max_page = max(pages)
                    if max_page - page < self._binary_search_page_threshold:
                        return max_page

                    left_page = max_page
                    page = math.ceil((right_page + left_page) / 2)

    def _binary_search_check_is_available_page(self, category_data, page):
        """
        In binary search performs test whether the current page is available.
        :return:
        """
        try:
            page_request = self.get_object_request(category_data, page)
        except PornFetchUrlError as err:
            return False, err.request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return False, page_request
        return page <= max(pages), page_request

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in (tree.xpath('.//div[@class="pages"]/a/text()') +
                                 tree.xpath('.//div[@class="pages"]/span/text()')) if x.isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 9

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Referer': page_data.url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        split_url = split_url[:4]
        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            split_url.append(page_filter.sort_order.value)
        if page_filter.period.value is not None:
            split_url.append(page_filter.period.value)
        if page_filter.quality.value is not None:
            split_url.append(page_filter.quality.value)
        if page_filter.length.value is not None:
            split_url.append(page_filter.length.value)
        if page_number is not None and page_number != 1:
            split_url.append(str(page_number))
        split_url.append('')
        program_fetch_url = '/'.join(split_url)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


if __name__ == '__main__':
    cat_id = IdGenerator.make_id('/mom/')
    module = VPorn()
    # module.get_available_categories()
    # module.download_object(None, cat_id, verbose=1)
    module.download_category_input_from_user(use_web_server=True)
