import re
from .... import urljoin, parse_qs, quote

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode, \
    PornCatalogVideoPageNode
from .upornia import UPornia


class TubePornClassic(UPornia):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
        }

    def _prepare_filters(self):
        _, video_filters, video_filters, categories_filters, porn_stars_filters, _ = \
            super(TubePornClassic, self)._prepare_filters()
        video_filters.pop('quality_filters')
        return None, video_filters, video_filters, categories_filters, porn_stars_filters, None

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        _, video_filters, search_filter, categories_filters, porn_stars_filters, _ = \
            self._prepare_filters()

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=categories_filters,
                                         porn_stars_args=porn_stars_filters,
                                         single_porn_star_args=video_filters,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filter,
                                         )

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://tubepornclassic.com/'

    def __init__(self, source_name='TubePornClassic', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(TubePornClassic, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                              session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, './/div[@class="list-categories"]/div/a',
                                                  PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data, './/div[@class="list-models"]/div/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_base_object(self, object_data, xpath, object_type):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            title_data = (category.xpath('./strong[@class="title"]') +
                          category.xpath('./div[@class="item__title clearfix"]/strong[@class="model-name"]'))
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos = category.xpath('./div[@class="wrap"]/div[@class="videos"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            rating = (category.xpath('./div[@class="wrap"]/div[@class="rating positive"]') +
                      category.xpath('./div[@class="wrap"]/div[@class="rating negative"]')
                      )
            assert len(rating) == 1
            rating = self._clear_text(rating[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               rating=rating,
                                               object_type=object_type,
                                               super_object=object_data,
                                               ))

        object_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return ([int(self._clear_text(x.text))
                for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/*')
                if x.text is not None and self._clear_text(x.text).isdigit()] +
                [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0])
                 for x in tree.xpath('.//div[@class="pagination-holder"]/ul/li/a')
                 if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0])

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        video_preview_url = dict(
            re.findall(r'(?:\[)(\d+)(?:\])(?:.*?)(https://[\w./-]*/videos)', page_request.text))
        videos = tree.xpath('.//div[@class="list-videos"]div/div/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./div[@class="img"]/img')
            assert len(image_data) == 1
            video_id = image_data[0].attrib['data-video-id']
            image = image_data[0].attrib['src']
            flix_image = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                          for d in range(1, self.number_of_flip_images + 1)]
            video_source = image_data[0].attrib['data-sgid'].split(':')[-1]
            preview_link = (video_preview_url[video_source] +
                            '/{vid_prefix}/{vid}/{vid}_tr.mp4'
                            ''.format(vid_prefix=video_id[:-3]+'000', vid=video_id)) \
                if video_source in video_preview_url else None
            additional_info = {'video_id': video_id}

            title = video_tree_data.xpath('./strong[@class="title"]')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            video_length = video_tree_data.xpath('./div[@class="wrap"]/div[@class="duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            rating = (video_tree_data.xpath('./div[@class="wrap"]/div[@class="rating positive"]') +
                      video_tree_data.xpath('./div[@class="wrap"]/div[@class="rating negative"]'))
            rating = self._clear_text(rating[0].text) if len(rating) == 1 else None

            added_before = (video_tree_data.xpath('./div[@class="wrap"]/div[@class="added"]/em') +
                            video_tree_data.xpath('./div[@class="wrap date-views__wrap"]/div[@class="added"]/em'))
            assert len(added_before) == 1
            added_before = added_before[0].text

            number_of_views = (video_tree_data.xpath('./div[@class="wrap"]/div[@class="views ico ico-eye"]') +
                               video_tree_data.xpath('./div[@class="wrap date-views__wrap"]/'
                                                     'div[@class="views ico ico-eye"]'))
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  preview_video_link=preview_link,
                                                  additional_data=additional_info,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  number_of_views=number_of_views,
                                                  added_before=added_before,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw number, i.e. '7m:58s'.
        :return:
        """
        res = 0
        hours = re.findall(r'(\d+)(?:h)', raw_duration)
        if len(hours) > 0:
            res += 3600 * int(hours[0])
        minutes = re.findall(r'(\d+)(?:m)', raw_duration)
        if len(minutes) > 0:
            res += 60 * int(minutes[0])
        seconds = re.findall(r'(\d+)(?:s)', raw_duration)
        if len(seconds) > 0:
            res += int(seconds[0])
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
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if true_object.object_type == PornCategories.VIDEO:
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request

        if page_number is None:
            page_number = 1
        conditions = self.get_proper_filter(page_data).conditions
        sort_filter_type = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by else page_filter.sort_order.filter_id
        params.update({
            'mode': 'async',
            'action': 'get_block',
            'from': str(page_number).zfill(2)
        })
        params.update(parse_qs(self.get_proper_filter(page_data).filters.sort_order[sort_filter_type].value))

        if split_url[-2].isdigit():
            split_url.pop(-2)
        if page_number > 1:
            split_url.insert(-1, str(page_number))

        if true_object.object_type == PornCategories.CATEGORY_MAIN:
            params['block_id'] = ['list_categories_categories_list']
            params.pop('from')
        elif true_object.object_type == PornCategories.PORN_STAR_MAIN:
            params['block_id'] = ['list_models2_models_list']
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            params['block_id'] = ['list_videos_videos_list_search_result']
            params.pop('from')
            params['from_videos'] = str(page_number).zfill(2)
        elif true_object.object_type == PornCategories.CATEGORY:
            params['block_id'] = ['list_videos2_videos_list']
        elif true_object.object_type == PornCategories.PORN_STAR:
            params['block_id'] = ['list_videos2_common_videos_list']
        else:
            params['block_id'] = ['list_videos2_common_videos_list']

        if page_filter.period.value is not None and sort_filter_type in conditions.period.sort_order:
            params['sort_by'][0] += ('_' + page_filter.period.value)
        if page_filter.quality.value is not None:
            params.update(parse_qs(page_filter.quality.value))
        if page_filter.length.value is not None:
            params.update(parse_qs(page_filter.length.value))

        program_fetch_url = '/'.join(split_url)
        page_request = self.session.post(program_fetch_url, headers=headers, data=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote(query))
