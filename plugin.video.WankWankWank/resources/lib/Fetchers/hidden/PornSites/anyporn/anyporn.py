# -*- coding: UTF-8 -*-
# Internet tools
from .... import urljoin, parse_qsl

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogPageNode, PornCatalogVideoPageNode
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# ID generator
from ....id_generator import IdGenerator

# Base class
from .base import Base


class AnyPorn(Base):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://anyporn.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://anyporn.com/models/',
            PornCategories.TAG_MAIN: 'https://anyporn.com/categories/',
            PornCategories.CHANNEL_MAIN: 'https://anyporn.com/channels/',
            PornCategories.LATEST_VIDEO: 'https://anyporn.com/newest/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://anyporn.com/popular/',
            PornCategories.SEARCH_MAIN: 'https://anyporn.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://anyporn.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        # general_filter_params = {'general_filters': [(StraightType, 'Straight', ''),
        #                                              (GayType, 'Gay', 'gay'),
        #                                              (ShemaleType, 'Shemale', 'shemale'),
        #                                              ],
        #                          }
        category_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Recently updated', 'last_content_date'),
                                          (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'name'),
                                          (PornFilterTypes.ViewsOrder, 'Most viewed', 'avg_videos_popularity'),
                                          (PornFilterTypes.RatingOrder, 'Top rated', 'avg_videos_rating'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                                          ],
                           }
        video_params = {'sort_order': [(PornFilterTypes.DateOrder, 'Latest', 'post_date'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                       (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                                       ],
                        'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', ''),
                                            (PornFilterTypes.HDQuality, 'HD quality', 'hd'),
                                            ],
                        }
        search_params = video_params.copy()
        search_params['sort_order'] = [(PornFilterTypes.RelevanceOrder, 'By relevance', ''),
                                       (PornFilterTypes.DateOrder, 'Recent videos', 'most-recent'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                       (PornFilterTypes.LengthOrder, 'By duration', 'long-movies'),
                                       ]

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=category_params,
                                         channels_args=category_params,
                                         single_category_args=video_params,
                                         single_channel_args=video_params,
                                         single_tag_args=search_params,
                                         search_args=search_params,
                                         video_args=video_params,
                                         )

    def __init__(self, source_name='AnyPorn', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(AnyPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="list-categories"]/div[@class="margin-fix"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_channels(self, channel_data):
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="list-sponsors"]/div[@class="margin-fix"]/a',
                                                  PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(porn_star_data,
                                                  './/div[@class="list-models"]/div[@class="margin-fix"]/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        tag_properties = self._get_tag_properties(page_request)
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=link,
                                       url=urljoin(tag_data.url, link),
                                       title=title,
                                       number_of_videos=number_of_videos,
                                       object_type=self._get_tag_true_object_type(link.split('/')[1]),
                                       super_object=tag_data,
                                       )
               for link, title, number_of_videos in zip(*tag_properties)]
        tag_data.add_sub_objects(res)
        return res

    def _update_available_base_object(self, object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./div[@class="img"]/img')
            image = urljoin(self.base_url,
                            image_data[0].attrib['src'] if 'data:image' not in image_data[0].attrib['src']
                            else image_data[0].attrib['data-original']) if len(image_data) == 1 else None
            title = category.attrib['title'] if 'title' in category.attrib else image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="wrap"]/div[@class="videos"]')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].text)[0]) if len(number_of_videos) > 0 else None

            rating = (category.xpath('./div[@class="wrap"]/div[@class="rating positive"]') +
                      category.xpath('./div[@class="wrap"]/div[@class="rating negative"]'))
            rating = re.findall(r'\d+%', rating[0].text, re.DOTALL)[0] if len(rating) > 0 else None

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_videos=number_of_videos,
                                                      rating=rating,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        if is_sort:
            res.sort(key=lambda x: x.title)
        object_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//div[@class="tagslist"]/ul/li/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.attrib['title'], None)
                                                for x in raw_data])
        return links, titles, number_of_videos

    @staticmethod
    def _get_tag_true_object_type(url_section):
        """
        Rerurns tag's true object type according to it's url section
        :param url_section: Url substring responsible for recognizing the object type.
        :return: PornCategories enumeration object.
        """
        if url_section == 'search':
            return PornCategories.TAG
        elif url_section == 'channel':
            return PornCategories.CHANNEL
        elif url_section == 'models':
            return PornCategories.PORN_STAR
        elif url_section == 'categories':
            return PornCategories.CATEGORY
        else:
            raise ValueError('Unknown url substring responsible for object type, {s}'.format(s=url_section))

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
        number_of_pages = self._get_number_of_sub_pages(tag_data, page_request)
        links, titles, numbers_of_videos = self._get_tag_properties(page_request)
        for i in range(2, number_of_pages + 1):
            page_request = self.get_object_request(tag_data, override_page_number=i)
            loc_links, loc_titles, loc_numbers_of_videos = self._get_tag_properties(page_request)
            links += loc_links
            titles += loc_titles
            numbers_of_videos += loc_numbers_of_videos
        partitioned_data = {
            chr(x): [(link, title, number_of_videos)
                     for link, title, number_of_videos in zip(links, titles, numbers_of_videos)
                     if title[0].upper() == chr(x)]
            for x in range(ord('A'), ord('Z')+1)
        }
        partitioned_data['#'] = [(link, title, number_of_videos)
                                 for link, title, number_of_videos in zip(links, titles, numbers_of_videos)
                                 if title[0].isdigit()]
        new_pages = [PornCatalogPageNode(catalog_manager=self.catalog_manager,
                                         obj_id=(IdGenerator.id_to_original_str(tag_data.id), k),
                                         title='{c} | Letter {p}'.format(c=tag_data.title, p=k),
                                         url=tag_data.url,
                                         raw_data=tag_data.raw_data,
                                         additional_data={'letter': k},
                                         object_type=sub_object_type,
                                         super_object=tag_data,
                                         )
                     for k in sorted(partitioned_data.keys()) if len(partitioned_data[k]) > 0]
        for new_page in new_pages:
            sub_tags = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                obj_id=link,
                                                url=urljoin(tag_data.url, link),
                                                title=title,
                                                number_of_videos=number_of_videos,
                                                object_type=self._get_tag_true_object_type(link.split('/')[1]),
                                                super_object=new_page,
                                                )
                        for link, title, number_of_videos in partitioned_data[new_page.additional_data['letter']]]
            new_page.add_sub_objects(sub_tags)

        tag_data.add_sub_objects(new_pages)

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
        """
        return self._get_video_links_from_video_data1(video_data)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN):
            return 1
        page_request = self._get_object_request_no_exception_check(category_data) if fetched_request is None \
            else fetched_request
        if not self._check_is_available_page(category_data, page_request):
            return 1
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return (max(available_pages)
                if category_data.object_type not in (PornCategories.TAG, PornCategories.SEARCH_MAIN)
                else min(self.max_search_pages, max(available_pages))) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.attrib['data-parameters'].split(':')[-1])
                for x in tree.xpath('.//div[@class="nopop pagination-holder"]/ul/li/a')
                if x.attrib['data-parameters'].split(':')[-1].isdigit()]

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        # New
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
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        if page_number is None:
            page_number = 1
        params.update({
                'mode': 'async',
                'function': 'get_block',
            })
        if page_filter.length.value is not None:
            params.update(parse_qsl(page_filter.length.value))
        if page_number > 1:
            params['from'] = str(page_number).zfill(2)

        if true_object.object_type == PornCategories.CATEGORY_MAIN:
            params['block_id'] = 'list_categories_categories_list'
            params['sort_by'] = page_filter.sort_order.value
        elif true_object.object_type == PornCategories.CHANNEL_MAIN:
            params['block_id'] = 'list_content_sources_sponsors_list'
            params['sort_by'] = page_filter.sort_order.value
        elif true_object.object_type == PornCategories.PORN_STAR_MAIN:
            params['block_id'] = 'list_models_models_list'
            params['sort_by'] = page_filter.sort_order.value
            params['gender_id'] = page_filter.general.value
        elif true_object.object_type == PornCategories.ACTRESS_MAIN:
            params['block_id'] = 'list_models_models_list'
            params['sort_by'] = page_filter.sort_order.value
            params['gender_id'] = page_filter.general.value
        elif true_object.object_type == PornCategories.TAG_MAIN:
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
            page_request = self.session.get(page_data.url, headers=headers)
            return page_request
        elif true_object.object_type == PornCategories.VIDEO:
            # Right now like TagMain,but could easily change...
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
            page_request = self.session.get(page_data.url, headers=headers)
            return page_request

        elif true_object.object_type in (PornCategories.SEARCH_MAIN, PornCategories.TAG):
            params['block_id'] = 'list_videos_v2_videos_list_search_result'
            params['category_ids'] = ''
            params['sort_by'] = page_filter.sort_order.value
            if 'from' in params:
                params.pop('from')
            params['from_videos'] = str(page_number).zfill(2)
            params['from_albums'] = str(page_number).zfill(2)
            params['q'] = self._search_query if true_object.object_type == PornCategories.SEARCH_MAIN \
                else fetch_base_url.split('/')[-2]

        elif true_object.object_type in (PornCategories.CATEGORY, PornCategories.CHANNEL,
                                         PornCategories.PORN_STAR, PornCategories.ACTRESS):
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = page_filter.sort_order.value
        elif true_object.object_type in (PornCategories.MOST_VIEWED_VIDEO, PornCategories.POPULAR_VIDEO):
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = 'video_viewed'
            if page_filter.period.value is not None:
                params['sort_by'] += page_filter.period.value
        elif true_object.object_type == PornCategories.LATEST_VIDEO:
            params['block_id'] = 'list_videos_latest_videos_list'
            params['sort_by'] = 'post_date'
        elif true_object.object_type == PornCategories.TOP_RATED_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = 'rating'
            if page_filter.period.value is not None:
                params['sort_by'] += page_filter.period.value
        elif true_object.object_type == PornCategories.LONGEST_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = 'duration'
        elif true_object.object_type == PornCategories.MOST_DISCUSSED_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = 'most_commented'
        elif true_object.object_type == PornCategories.FAVORITE_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = 'most_favourited'
        elif true_object.object_type == PornCategories.RECOMMENDED_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = 'last_time_view_date'
        else:
            raise ValueError('Wrong category type {c}'.format(c=true_object.object_type))

        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            params['sort_by'] += page_filter.period.value
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div[@class="margin-fix"]/div[@class="item  "]/'
                            'div[@class="thmbclck"]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1

            image = video_tree_data.xpath('./div[@class="img"]/a/img')
            assert len(image) == 1

            is_hd = video_tree_data.xpath('./div[@class="img"]/div[@class="hdpng"]')

            video_length = video_tree_data.xpath('./div[@class="wrap"]/div[@class="added"]/em/script')
            assert len(video_length) == 1

            rating = (video_tree_data.xpath('./div[@class="wrap"]/div[@class="rating positive"]/script') +
                      video_tree_data.xpath('./div[@class="wrap"]/div[@class="rating negative"]/script'))
            rating = re.findall(r'\d+%', rating[0].text) if len(rating) > 0 else '0'

            video_data = PornCatalogVideoPageNode(
                catalog_manager=self.catalog_manager,
                obj_id=re.findall(r'\d+', link[0].attrib['href'])[0],
                title=image[0].attrib['alt'],
                url=urljoin(self.base_url, link[0].attrib['href']),
                image_link=urljoin(self.base_url, image[0].attrib['data-original']),
                preview_video_link=image[0].attrib['data-preview'] if 'data-preview' in image[0].attrib else None,
                is_hd=len(is_hd) > 0,
                duration=self._format_duration(video_length[0].text),
                rating=rating[0] if len(rating) > 0 else None,
                object_type=PornCategories.VIDEO,
                super_object=page_data,
            )
            res.append(video_data)

        page_filter = self.get_proper_filter(page_data).current_filters
        if page_filter.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw number, i.e. '7m:58s'.
        :return:
        """
        return self._format_duration1(raw_duration)
