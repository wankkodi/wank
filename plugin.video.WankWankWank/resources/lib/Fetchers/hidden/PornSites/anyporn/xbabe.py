import math
import re
from .... import urljoin, quote_plus

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .anyporn import AnyPorn


class XBabe(AnyPorn):
    max_flip_images = 10
    videos_per_video_page = 100

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
            PornCategories.TAG_MAIN: 'https://xbabe.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://xbabe.com/models/',
            PornCategories.LATEST_VIDEO: 'https://xbabe.com/videos/',
            PornCategories.BEING_WATCHED_VIDEO: 'https://xbabe.com/videos/watched-now/',
            PornCategories.TOP_RATED_VIDEO: 'https://xbabe.com/videos/top-rated/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://xbabe.com/videos/most-viewed/',
            PornCategories.LONGEST_VIDEO: 'https://xbabe.com/videos/longest/',
            PornCategories.SEARCH_MAIN: 'https://xbabe.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.BEING_WATCHED_VIDEO: PornFilterTypes.BeingWatchedOrder,
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        model_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Recently updated', 'last_content_date'),
                                       (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'model_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       ],
                        }
        video_params = {'period_filters': [(PornFilterTypes.ThreeDate, 'Today', '_today'),
                                           (PornFilterTypes.TwoDate, 'This week', '_week'),
                                           (PornFilterTypes.OneDate, 'This Month', '_month'),
                                           (PornFilterTypes.AllDate, 'All time', ''),
                                           ],
                        }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=model_params,
                                         video_args=video_params,
                                         )

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://xbabe.com/'

    @property
    def max_pages(self):
        return 2000

    def __init__(self, source_name='XBabe', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(XBabe, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                    session_id)

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//div[@class="categories-paragraph"]/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, None)
                                                for x in raw_data])
        return links, titles, number_of_videos

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
        return super(AnyPorn, self)._add_tag_sub_pages(tag_data, sub_object_type)

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="item-ourgirls ourgirls-thumb"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            title = link_data[0].text

            image_data = category.xpath('./em/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(porn_star_data.url, link),
                                                      title=title,
                                                      image_link=image,
                                                      object_type=PornCategories.PORN_STAR,
                                                      super_object=porn_star_data,
                                                      )
            res.append(sub_object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        return self._get_video_links_from_video_data3(video_data)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN,):
            return 1
        page_request = self._get_object_request_no_exception_check(category_data) if fetched_request is None \
            else fetched_request
        if not self._check_is_available_page(category_data, page_request):
            return 1
        tree = self.parser.parse(page_request.text)
        if category_data.object_type in (PornCategories.TAG, PornCategories.PORN_STAR):
            available_pages = self._get_available_pages_from_tree(tree)
            return max(available_pages) if len(available_pages) > 0 else 1
        # elif category_data.object_type in (LatestVideo, BeingWatchedVideo, TopRatedVideo, MostViewedVideo,
        #                                    LongestVideo):
        #     total_number_of_videos = tree.xpath('.//ul[@class="site-stats"]/li[2]/a/span')
        #     total_number_of_videos = (int(total_number_of_videos[0].text) +
        #                               (int(total_number_of_videos[1].text[1:])
        #                                if len(total_number_of_videos[1].text[1:]) > 0 else 0)
        #                               )
        #     return math.ceil(total_number_of_videos / self.videos_per_video_page)
        else:
            # We have a porn star page
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _binary_search_max_number_of_pages(self, category_data, last_available_number_of_pages):
        """
        Performs binary search in order to find the last available page.
        :param category_data: Category data.
        :param last_available_number_of_pages: Last available number of pages. Will be the pivot for our next search.
        By default is None, which mean the original pivot will be used...
        :return: Page request
        """
        left_page = 1
        right_page = self.max_pages
        page = last_available_number_of_pages if last_available_number_of_pages is not None \
            else math.ceil((right_page + left_page) / 2)
        while 1:
            page_request = self._get_object_request_no_exception_check(category_data, override_page_number=page)
            if self._check_is_available_page(category_data, page_request):
                left_page = page
                if left_page == right_page:
                    return left_page
            else:
                # We moved too far...
                right_page = page - 1
            page = math.ceil((right_page + left_page) / 2)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text)
                for x in tree.xpath('.//div[@class="pagination"]/*') +
                tree.xpath('.//div[@class="pagination-bar"]/ul/li/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        res = []
        videos = tree.xpath('.//div[@class="thumb-big"]')
        method = 1
        if len(videos) == 0:
            method = 2
            videos = tree.xpath('.//div[@class="videos-related-holder"]/div[@class="block_content"]/a')
        if len(videos) == 0:
            method = 3
            videos = tree.xpath('.//div[@class="block_content"]/a')
        if len(videos) == 0:
            method = 4
            videos = tree.xpath('.//div[@class="thumb-holder"]/div')

        if method == 1:
            # Method 1
            for video_tree_data in videos:
                link_data = video_tree_data.xpath('./a')
                assert len(link_data) == 1
                link = link_data[0].attrib['href']
                title = link_data[0].text

                image_data = video_tree_data.xpath('./div[@class="image"]/span[@class="image-holder"]/img')
                assert len(image_data) == 1
                image = image_data[0].attrib['src']
                flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                               for d in range(1, int(re.findall(r'(\d+)(?:\)$)',
                                                                image_data[0].attrib['onmouseover'])[0]) + 1)] \
                    if 'onmouseover' in image_data[0].attrib else None

                video_length = video_tree_data.xpath('./div[@class="image"]/span[@class="duration"]')
                assert len(video_length) == 1
                video_length = video_length[0].text

                added_before = video_tree_data.xpath('./div[@class="info"]/span[@class="added"]')
                assert len(added_before) == 1
                added_before = added_before[0].text

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(page_data.url, link),
                                                      title=title,
                                                      image_link=image,
                                                      flip_images_link=flip_images,
                                                      duration=self._format_duration(video_length),
                                                      added_before=added_before,
                                                      object_type=PornCategories.VIDEO,
                                                      super_object=page_data,
                                                      )
                res.append(video_data)
        elif method in (2, 3):
            # Method 2
            for video_tree_data in videos:
                link = video_tree_data.attrib['href']

                image_data = video_tree_data.xpath('./span[@class="image"]/span[@class="image-holder"]/img')
                assert len(image_data) == 1
                image = image_data[0].attrib['src']
                flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                               for d in range(1, int(re.findall(r'(\d+)(?:\)$)',
                                                                image_data[0].attrib['onmouseover'])[0]) + 1)]

                video_length = video_tree_data.xpath('./span[@class="image"]/span[@class="duration"]')
                assert len(video_length) == 1
                video_length = video_length[0].text

                title = video_tree_data.xpath('./span[@class="info"]/h3')
                assert len(title) == 1
                title = title[0].text

                added_before = video_tree_data.xpath('./span[@class="info"]/span[@class="added"]')
                assert len(added_before) == 1
                added_before = added_before[0].text

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(page_data.url, link),
                                                      title=title,
                                                      image_link=image,
                                                      flip_images_link=flip_images,
                                                      duration=self._format_duration(video_length),
                                                      added_before=added_before,
                                                      object_type=PornCategories.VIDEO,
                                                      super_object=page_data,
                                                      )
                res.append(video_data)

        elif method == 4:
            # Method 3
            for video_tree_data in videos:
                link_data = video_tree_data.xpath('./a')
                assert len(link_data) == 1
                link = link_data[0].attrib['href']

                title_data = video_tree_data.xpath('./a/span')
                assert len(title_data) == 1
                title = title_data[0].text

                image_data = video_tree_data.xpath('./span[@class="img"]/img')
                assert len(image_data) == 1
                image = image_data[0].attrib['src']
                description = image_data[0].attrib['alt']

                preview_data = video_tree_data.xpath('./span[@class="video"]/video')
                assert len(preview_data) == 1
                preview_link = preview_data[0].attrib['src']

                number_of_views = video_tree_data.xpath('./span[@class="info"]/span[@class="views"]')
                assert len(number_of_views) == 1
                number_of_views = number_of_views[0].text

                rating = video_tree_data.xpath('./span[@class="info"]/span[@class="rating"]')
                assert len(rating) == 1
                rating = rating[0].text

                is_hd = video_tree_data.xpath('./span[@class="info"]/span[@class="quality"]')
                assert len(is_hd) == 1
                is_hd = is_hd[0].text == 'HD'

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(page_data.url, link),
                                                      title=title,
                                                      description=description,
                                                      image_link=image,
                                                      preview_video_link=preview_link,
                                                      number_of_views=number_of_views,
                                                      is_hd=is_hd,
                                                      rating=rating,
                                                      object_type=PornCategories.VIDEO,
                                                      super_object=page_data,
                                                      )
                res.append(video_data)

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        if true_object.object_type in (PornCategories.TAG, PornCategories.TAG_MAIN,
                                       PornCategories.SEARCH_MAIN, PornCategories.VIDEO):
            # params['block_id'] = 'list_content_sources_sponsors_list'
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3*',
                'Cache-Control': 'max-age=0',
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }
            if page_number is not None and page_number > 1:
                fetch_base_url = (fetch_base_url + ('/' if fetch_base_url[-1] != '/' else '') +
                                  '{d}/'.format(d=page_number))

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        elif true_object.object_type in (PornCategories.PORN_STAR, PornCategories.PORN_STAR_MAIN,
                                         PornCategories.MOST_VIEWED_VIDEO, PornCategories.LONGEST_VIDEO,
                                         PornCategories.LATEST_VIDEO, PornCategories.BEING_WATCHED_VIDEO,
                                         PornCategories.TOP_RATED_VIDEO,):
            # return super(XBabe, self).get_object_request(object_data, override_page)
            # Slight change: instead of the 'function' param, here it is 'action'...
            conditions = self.get_proper_filter(page_data).conditions
            true_sort_filter_id = self._default_sort_by[true_object.object_type] \
                if true_object.object_type in self._default_sort_by \
                else page_filter.sort_order.filter_id

            headers = {
                'Accept': '*.*',
                'Cache-Control': 'max-age=0',
                'Referer': self.base_url,
                'Host': self.host_name,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
            if page_number is None:
                page_number = 1
            params.update({
                'mode': 'async',
                'action': 'get_block',
            })
            if page_number > 1:
                params['from'] = str(page_number).zfill(2)

            fetch_base_url = 'https://xbabe.com/content_load.php'
            if true_object.object_type == PornCategories.PORN_STAR:
                params['block_id'] = 'list_videos_model_videos'
                params['dir'] = page_data.url.split('/')[-2]
                fetch_base_url = 'https://xbabe.com/view_model_2.php'
            elif true_object.object_type == PornCategories.PORN_STAR_MAIN:
                params['block_id'] = 'list_models_models_list'
                params['sort_by'] = page_filter.sort_order.value
            elif true_object.object_type == PornCategories.LONGEST_VIDEO:
                params['block_id'] = 'list_videos_common_videos_list'
                params['sort_by'] = 'duration'
            elif true_object.object_type == PornCategories.LATEST_VIDEO:
                params['block_id'] = 'list_videos_common_videos_list'
                params['sort_by'] = 'post_date'
            elif true_object.object_type == PornCategories.BEING_WATCHED_VIDEO:
                params['block_id'] = 'list_videos_common_videos_list'
                params['sort_by'] = 'last_time_view_date'
            elif true_object.object_type == PornCategories.TOP_RATED_VIDEO:
                params['block_id'] = 'list_videos_common_videos_list'
                params['sort_by'] = 'rating'
            elif true_object.object_type == PornCategories.MOST_VIEWED_VIDEO:
                params['block_id'] = 'list_videos_common_videos_list'
                params['sort_by'] = 'video_viewed'

            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            raise ValueError('Wrong object type {ot}!'.format(ot=true_object.object_type))

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        self._search_query = query
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))
