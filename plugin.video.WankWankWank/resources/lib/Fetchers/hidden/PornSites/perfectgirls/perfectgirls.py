# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, PornCatalogPageNode, \
    VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# Generator id
from ....id_generator import IdGenerator


class PerfectGirls(PornFetcher):
    # todo: add support for VR

    max_flip_image = 25
    min_tags_subcategories = 23  # 3*5 + 2*4

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'http://www.perfectgirls.net/',
            PornCategories.TAG_MAIN: 'http://www.perfectgirls.net/tags/',
            PornCategories.PORN_STAR_MAIN: 'http://www.perfectgirls.net/pornstars/',
            PornCategories.TOP_RATED_VIDEO: 'http://www.perfectgirls.net/top/',
            PornCategories.LATEST_VIDEO: 'http://www.perfectgirls.net/',
            PornCategories.SEARCH_MAIN: 'http://www.perfectgirls.net/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.perfectgirls.net/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Latest', None),
                                        (PornFilterTypes.RatingOrder, 'Top', 'top'),
                                        ),
                         'period_filters': ([(PornFilterTypes.OneDate, 'Last 3 days', '3days'),
                                             (PornFilterTypes.TwoDate, 'Last week', 'week'),
                                             (PornFilterTypes.ThreeDate, 'Last Month', 'month'),
                                             (PornFilterTypes.AllDate, 'All time', 'all'),
                                             ],
                                            [('sort_order', [PornFilterTypes.RatingOrder])]),
                         'quality_filters': ((PornFilterTypes.AllQuality, 'All quality', None),
                                             (PornFilterTypes.HDQuality, 'HD quality', '1'),
                                             ),
                         }
        single_porn_star_filters = {'quality_filters': video_filters['quality_filters']}
        single_tag_filters = single_porn_star_filters
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=video_filters,
                                         single_tag_args=single_tag_filters,
                                         single_porn_star_args=single_porn_star_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='PerfectGirls', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PerfectGirls, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                           session_id)

    def _add_category_sub_pages(self, category_data, sub_object_type, page_request=None, clear_sub_elements=True):
        """
        Adds category sub pages.
        :param category_data: Category data object (PornCatalogCategoryNode).
        :param sub_object_type: Sub object type.
        :param page_request: Page request if such exist. In case it doesn't exist we fetch the object's url.
        :param clear_sub_elements: Flag that indicates whether we clear previous sub elements.
        :return:
        """
        if clear_sub_elements is True:
            category_data.clear_sub_objects()
        if category_data.object_type == PornCategories.TAG_MAIN:
            return self._add_tag_sub_pages(category_data, sub_object_type)
        elif category_data.object_type == PornCategories.PORN_STAR_MAIN:
            return self._add_pornstars_sub_pages(category_data, sub_object_type)
        else:
            return super(PerfectGirls, self)._add_category_sub_pages(category_data, sub_object_type, page_request,
                                                                     clear_sub_elements)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        # tree = self.parser.parse(page_request.text)
        tree = self.parser.parse(re.findall(r'<div class="header-submenu__items_container">.*?</div>',
                                            page_request.text, re.DOTALL)[0])
        categories = tree.xpath('.//li[@class="header-submenu__item"]/a')
        res = []
        for category in categories:
            if 'category' not in category.attrib['href']:
                continue

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=self._clear_text(category.text)
                                                  if category.text is not None else None,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_object(tag_data, PornCategories.TAG)

    def _update_available_porn_stars(self, pornstar_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_object(pornstar_data, PornCategories.PORN_STAR)

    def _update_available_object(self, object_data, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        # tree = self.parser.parse(page_request.text)
        tree = self.parser.parse(re.findall(r'(<div class="wrapper">.*?</div>.*)(?:<!-- /container -->)',
                                            page_request.text, re.DOTALL)[0])
        tags = tree.xpath('.//div[@class="categories__list col-5"]/ul[@class="categories__items_group"]/li/a')
        res = []
        for tag in tags:
            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=tag.attrib['href'],
                                                      url=urljoin(self.base_url, tag.attrib['href']),
                                                      title=self._clear_text(tag.text)
                                                      if tag.text is not None else None,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        object_data.add_sub_objects(res)
        return res

    def _add_tag_sub_pages(self, tag_data, object_type):
        return self._add_object_sub_pages(tag_data, PornCategories.TAG, object_type)

    def _add_pornstars_sub_pages(self, tag_data, object_type):
        return self._add_object_sub_pages(tag_data, PornCategories.PORN_STAR, object_type)

    def _add_object_sub_pages(self, object_data, object_type, sub_object_type):
        page_request = self.get_object_request(object_data)
        # tree = self.parser.parse(page_request.text)
        tree = self.parser.parse(re.findall(r'(<div class="wrapper">.*?</div>.*)(?:<!-- /container -->)',
                                            page_request.text, re.DOTALL)[0])
        titles = tree.xpath('.//div[@class="categories__title"]/h2')
        tags = tree.xpath('.//div[@class="categories__list col-5"]/ul[@class="categories__items_group"]')
        if len(titles) != len(tags):
            raise RuntimeError('There is incorrectness between the titles and the sub_objects')

        new_pages = []
        for title, tag in zip(titles, tags):
            sub_tags = tag.xpath('./li/a')
            new_page_url = [x.attrib['href']
                            for x in sub_tags if 'class' in x.attrib and x.attrib['class'] == 'view_more']
            assert len(new_page_url) == 1

            new_page = PornCatalogPageNode(catalog_manager=self.catalog_manager,
                                           obj_id=(IdGenerator.id_to_original_str(object_data.id), title.text),
                                           title='{c} | Letter {p}'.format(c=object_data.title, p=title.text),
                                           url=urljoin(object_data.url, new_page_url[0]),
                                           page_number=title.text,
                                           raw_data=object_data.raw_data,
                                           object_type=sub_object_type,
                                           super_object=object_data,
                                           )
            # We try if we have enough all the sub pages. In that case we update the subpage right now
            if len(sub_tags) < self.min_tags_subcategories + 1:
                true_raw_sub_tags = [x for x in sub_tags
                                     if 'class' not in x.attrib or x.attrib['class'] != 'view_more']
                true_sub_tags = []
                for raw_sub_tag in true_raw_sub_tags:
                    sub_tag = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=raw_sub_tag.attrib['href'],
                                                      url=urljoin(self.base_url, raw_sub_tag.attrib['href']),
                                                      title=self._clear_text(raw_sub_tag.text)
                                                      if raw_sub_tag.text is not None else None,
                                                      object_type=object_type,
                                                      super_object=new_page,
                                                      )
                    true_sub_tags.append(sub_tag)
                new_page.add_sub_objects(true_sub_tags)

            new_pages.append(new_page)

        object_data.add_sub_objects(new_pages)

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse('\n'.join(re.findall(r'<source.*/>', tmp_request.text)))
        videos = tmp_tree.xpath('.//source')
        videos = sorted((VideoSource(link=x.attrib['src'], resolution=x.attrib['res']) for x in videos),
                        key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type == PornCategories.CATEGORY_MAIN:
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        raw_pagination = re.findall(r'<ul class="pagination">.*?</ul>', page_request.text, re.DOTALL)
        if len(raw_pagination) == 0:
            return 1
        tree = self.parser.parse(raw_pagination[0])
        pages = self._get_available_pages_from_tree(tree)
        return max(pages) if len(pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        pages = tree.xpath('.//ul[@class="pagination"]/li/*/text()')
        return [int(x) for x in pages if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse('\n'.join(re.findall(r'<div class="list__item"><div class="list__item_link">.*?'
                                                      r'</div>\n*</div>', page_request.text, re.DOTALL)))
        # tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list__item_link"]/a')
        res = []
        for video_tree_data in videos:
            image_data = video_tree_data.xpath('./div/img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['data-original'])
            flip_images = [re.sub(r'thumb\d+', 'thumb{i}'.format(i=i), image) for i in range(self.max_flip_image + 1)]

            video_length = video_tree_data.xpath('./time')
            assert len(video_length) == 1

            is_hd = video_tree_data.xpath('./div[@class="hd"]')

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['href'],
                                                  url=urljoin(self.base_url, video_tree_data.attrib['href']),
                                                  title=video_tree_data.attrib['title'],
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  duration=self._format_duration(video_length[0].text),
                                                  is_hd=len(is_hd) > 0,
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
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        if split_url[-1].isdigit() or len(split_url[-1]) == 0:
            # Override previous value (we will do it at the page stage)
            split_url.pop()

        if true_object.object_type == PornCategories.LATEST_VIDEO:
            if page_number is not None:
                split_url.append('p')

        if page_filter.sort_order.value is not None:
            split_url.append(page_filter.sort_order.value)

        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            split_url.append(page_filter.period.value)

        if page_filter.quality.value is not None:
            self.session.cookies.set(name='hdonly',
                                     value=page_filter.quality.value,
                                     domain='www.perfectgirls.net')
        else:
            # We want to remove the obsolete cookies
            if 'hdonly' in self.session.cookies:
                self.session.cookies.pop('hdonly')

        if true_object.object_type not in (PornCategories.PORN_STAR_MAIN, PornCategories.CATEGORY_MAIN,
                                           PornCategories.TAG_MAIN,):
            if page_number is not None:
                split_url.append(str(page_number))
                # program_fetch_url = re.sub(r'(/p)?/\d+$', '', program_fetch_url)
                # split_path = urlparse(program_fetch_url).path.split('/')
                # if len(split_path) > 1:
                #     program_fetch_url += '/{i}'.format(i=page_data.page_number)
                # else:
                #     program_fetch_url += '/p/{i}'.format(i=page_data.page_number)

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
        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote(query))
