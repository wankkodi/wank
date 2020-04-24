# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote_plus

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, PornCatalogPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# Generator id
from ..id_generator import IdGenerator


class Porn300(PornFetcher):
    tag_main_page = 'https://www.porn300.com/tags/'
    max_flip_image = 16

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 20000

    @property
    def object_urls(self):
        return {
            # PornCategories.CATEGORY_MAINy: 'https://www.porn300.com/en_US/ajax/page/list_categories/',
            PornCategories.CATEGORY_MAIN: 'https://www.porn300.com/ajax/categories',
            # PornCategories.TAG_MAIN: 'https://www.porn300.com/tags/',
            PornCategories.TAG_MAIN: 'https://www.porn300.com/ajax/tags',
            PornCategories.CHANNEL_MAIN: 'https://www.porn300.com/channels/',
            # PornCategories.CHANNEL_MAIN: 'https://www.porn300.com/ajax/channels/',
            # PornCategories.PORN_STAR_MAIN: 'https://www.porn300.com/pornstars/',
            PornCategories.PORN_STAR_MAIN: 'https://www.porn300.com/ajax/pornstars',
            PornCategories.LATEST_VIDEO: 'https://www.porn300.com/videos/',
            PornCategories.SEARCH_MAIN: 'https://www.porn300.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.porn300.com'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        general_filter_params = {'general_filters': [(PornFilterTypes.StraightType, 'Straight', None),
                                                     (PornFilterTypes.GayType, 'Gay', 'gay'),
                                                     ],
                                 }
        video_filters = {'sort_order': ((PornFilterTypes.RelevanceOrder, 'Most Relevant', None),
                                        (PornFilterTypes.PopularityOrder, 'Most Popular', 'top-rated'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                        ),
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         general_args=general_filter_params,
                                         single_category_args=video_filters,
                                         single_tag_args=video_filters,
                                         )

    def __init__(self, source_name='Porn300', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Porn300, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page = 1
        max_page = None
        res = []
        while 1:
            page_request = self._get_object_request_no_exception_check(category_data)
            if not self._check_is_available_page(category_data, page_request):
                break
            page_json = page_request.json()
            if max_page is None:
                max_page = page_json['last_page']
            res.extend([PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                obj_id=x['url'],
                                                url=x['url'],
                                                title=x['name'],
                                                image_link=x['thumbnail'],
                                                number_of_videos=int(re.sub(',', '', x['video_count'])),
                                                raw_data=x,
                                                object_type=PornCategories.CATEGORY,
                                                super_object=category_data,
                                                ) for x in page_json['items']])
            if page == max_page:
                break
            page += 1

        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        page_json = page_request.json()
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x['url'],
                                       url=x['url'],
                                       title=x['name'],
                                       image_link=x['thumbnail'],
                                       number_of_videos=int(re.sub(',', '', x['video_count'])),
                                       raw_data=x,
                                       object_type=PornCategories.PORN_STAR,
                                       super_object=porn_star_data,
                                       ) for x in page_json['items']]
        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page = 1
        max_page = None
        res = []
        while 1:
            page_request = self._get_object_request_no_exception_check(tag_data)
            if not self._check_is_available_page(tag_data, page_request):
                break

            page_json = page_request.json()
            if max_page is None:
                max_page = page_json['last_page']
            res.extend([PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                obj_id=x['url'],
                                                url=x['url'],
                                                title=x['name'],
                                                number_of_videos=int(re.sub(',', '', x['video_count'])),
                                                raw_data=x,
                                                object_type=PornCategories.TAG,
                                                super_object=tag_data,
                                                ) for x in page_json['items']])
            if page == max_page:
                break
            page += 1

        tag_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        channels = tree.xpath('.//ul[@class="grid grid--producers js-append-producers"]/li/a')
        res = []
        for channel in channels:
            image_data = channel.xpath('./figure[@class="grid__item__img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image or '.gif' in image:
                image = image_data[0].attrib['data-src']
            title = image_data[0].attrib['alt']

            number_of_videos = channel.xpath('./figure[@class="grid__item__img"]/'
                                             'figcaption[@class="grid__item__caption-producer"]/small/*')
            assert len(number_of_videos) == 1
            number_of_videos = int(self._clear_text(number_of_videos[0].tail))

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=channel.attrib['href'],
                                                  url=urljoin(channel_data.url, channel.attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.CHANNEL,
                                                  super_object=channel_data,
                                                  )
            res.append(object_data)
        channel_data.add_sub_objects(res)
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
            return super(Porn300, self)._add_category_sub_pages(category_data, sub_object_type, page_request,
                                                                clear_sub_elements)

    def _add_tag_sub_pages(self, tag_data, sub_object_type):
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
        page_request = self.session.get(self.tag_main_page, headers=headers)
        tree = self.parser.parse(page_request.text)
        tags = tree.xpath('.//ul[@class="alphabet js-alphabet-carousel"]/li/a')
        new_pages = [PornCatalogPageNode(catalog_manager=self.catalog_manager,
                                         obj_id=(IdGenerator.id_to_original_str(tag_data.id), i),
                                         title='{c} | Letter {p}'.format(c=tag_data.title, p=x.text),
                                         url=urljoin(tag_data.url, x.attrib['href']),
                                         page_number=None,
                                         raw_data=tag_data.raw_data,
                                         additional_data=tag_data.additional_data,
                                         object_type=sub_object_type,
                                         super_object=tag_data,
                                         ) for i, x in enumerate(tags)]
        tag_data.add_sub_objects(new_pages)

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        video_resolutions = tmp_tree.xpath('.//video[@id="video-js"]')
        videos = sorted((VideoSource(link=x.xpath('./source')[0].attrib['src'], resolution=x.attrib['width'])
                         for x in video_resolutions),
                        key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=videos)

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
        elif category_data.object_type == PornCategories.PORN_STAR_MAIN:
            page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
            json_data = page_request.json()
            return json_data['last_page']
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//ul[@class="pagination"]/li/a/text()') if x.isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 7

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//li[@class="grid__item grid__item--video-thumb "]/a')
        res = []
        for video_tree_data in videos:
            image_data = video_tree_data.xpath('./figure/img')
            assert len(image_data) == 1
            title = image_data[0].attrib['alt']
            image = urljoin(self.base_url, image_data[0].attrib['data-src'])
            flip_images = [re.sub(r'thumb\d+', 'thumb{i}'.format(i=i), image)
                           for i in range(self.max_flip_image + 1)]

            video_length = video_tree_data.xpath('./ul/li[@class="duration-video"]/*[@aria-label="Clock"]')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0].tail)

            number_of_viewers = video_tree_data.xpath('./ul/li[2]/*[@aria-label="Eye"]')
            assert len(number_of_viewers) == 1
            number_of_viewers = self._convert_raw_number_to_true_number(number_of_viewers[0].tail)

            rating = video_tree_data.xpath('./ul/li[@class="data__vote"]/*[@aria-label="Thumb up"]')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].tail)

            upload_date = video_tree_data.xpath('./meta[@itemprop="uploadDate"]')
            assert len(upload_date) == 1
            upload_date = upload_date[0].attrib['content']

            description = video_tree_data.xpath('./meta[@itemprop="description"]')
            assert len(description) == 1
            description = description[0].attrib['content']

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['data-video-id'],
                                                  url=urljoin(self.base_url, video_tree_data.attrib['href']),
                                                  title=title,
                                                  subtitle=description,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  duration=self._format_duration(video_length),
                                                  number_of_views=number_of_viewers,
                                                  rating=rating,
                                                  added_before=upload_date,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _convert_raw_number_to_true_number(self, raw_number):
        """
        Converts the raw number into integer.
        :param raw_number: Raw number, i.e. '4.87K'.
        :return:
        """
        raw_number_of_videos = self._clear_text(raw_number.replace(',', '.'))
        if 'K' in raw_number_of_videos:
            number_of_videos = int(float(raw_number_of_videos[:-1]) * 10**3)
        elif 'M' in raw_number_of_videos:
            number_of_videos = int(float(raw_number_of_videos[:-1]) * 10**6)
        else:
            number_of_videos = int(raw_number_of_videos)
        return number_of_videos

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')
        # if len(split_url) >= 5 and split_url[3] == 'tags' and split_url[4] != '':
        if true_object.object_type == PornCategories.TAG_MAIN:
            if len(split_url) >= 5 and split_url[3] == 'tags' and split_url[4] != '':
                # Special treatment for tags
                params['character'] = split_url[4]
                params['elements'] = 200
            fetch_base_url = self.object_urls[PornCategories.TAG_MAIN]
            split_url = fetch_base_url.split('/')
        elif true_object.object_type in (PornCategories.PORN_STAR_MAIN, PornCategories.CATEGORY_MAIN,):
            # Special threat for categories and porn stars
            params['elements'] = 50

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
        if self.general_filter.current_filters.general.value is not None:
            if split_url[3] != self.general_filter.current_filters.general.value:
                split_url.insert(3, self.general_filter.current_filters.general.value)
        if page_filter.sort_order.value is not None:
            split_url.insert(-1, str(page_filter.sort_order.value))
        if page_number is not None and page_number != 1:
            params['page'] = page_number

        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}&bus={q}'.format(q=quote_plus(query))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.porn300.com/category/mom-and-son/')
    porn_star_id = IdGenerator.make_id('https://www.porn300.com/pornstar/carmella-bing/')
    tag_id = IdGenerator.make_id('https://www.porn300.com/tag/arab/')
    channel_id = IdGenerator.make_id('/channel/drunksexorgy/')
    module = Porn300()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['porn_stars']['obj'], (porn_star_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['channels']['obj'], (channel_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
