# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError

# Internet tools
from .. import urljoin, quote_plus, parse_qs

# Generator id
from ..id_generator import IdGenerator

# Regex
import re

# Math
import math

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


class TubeV(PornFetcher):
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 10000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.tubev.sex/',
            PornCategories.PORN_STAR_MAIN: 'https://www.tubev.sex/pornstars',
            PornCategories.CHANNEL_MAIN: 'https://www.tubev.sex/channels',
            PornCategories.LATEST_VIDEO: 'https://www.tubev.sex/videos?s=n',
            PornCategories.POPULAR_VIDEO: 'https://www.tubev.sex/videos',
            PornCategories.LONGEST_VIDEO: 'https://www.tubev.sex/videos?s=d',
            PornCategories.SEARCH_MAIN: 'https://www.tubev.sex/search',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.tubev.sex/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Popular', None),
                                        (PornFilterTypes.DateOrder, 'Latest', 's=n'),
                                        (PornFilterTypes.LengthOrder, 'Duration', 's=d'),
                                        ),
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         video_args=video_filters,
                                         search_args=video_filters,
                                         )

    def __init__(self, source_name='TubeV', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(TubeV, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                    session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumbs-layout thumb-category mouserotate"]/figure/a')
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x.attrib['href'],
                                       url=urljoin(category_data.url, x.attrib['href']),
                                       title=x.xpath('./span')[0].text,
                                       image_link=urljoin(category_data.url, x.xpath('./img')[0].attrib['src']),
                                       object_type=PornCategories.CATEGORY,
                                       super_object=category_data,
                                       ) for x in categories]
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="cat-list"]/ul[@id="all_list"]/li/a')
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x.attrib['href'],
                                       url=urljoin(porn_star_data.url, x.attrib['href']),
                                       title=re.findall(r'(\w+)(?::)', x.attrib['title'])[0],
                                       number_of_videos=int(re.findall(r'(?:: *)(\d+)', x.attrib['title'])[0]),
                                       object_type=PornCategories.PORN_STAR,
                                       super_object=porn_star_data,
                                       ) for x in categories]
        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="category-az-box cfix"]/div[@class="category-list cfix"]/ul/li/a')
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=x.attrib['href'],
                                       url=urljoin(channel_data.url, x.attrib['href']),
                                       title=re.findall(r'(.+)(?::)', x.attrib['title'])[0],
                                       number_of_videos=int(re.findall(r'(?:: *)(\d+)', x.attrib['title'])[0]),
                                       object_type=PornCategories.CHANNEL,
                                       super_object=channel_data,
                                       ) for x in categories]
        channel_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        video_links = [VideoSource(link='https://' + x)
                       for x in re.findall(r'(?:window.urrl = ")(.*)(?:";)', tmp_request.text)]
        return VideoNode(video_sources=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CHANNEL_MAIN, ):
            return 1
        try:
            page_request = self.get_object_request(category_data, send_error=False) if fetched_request is None \
                else fetched_request
        except PornFetchUrlError:
            return 1
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        elif len(pages) == 1:
            # We have only one option, thus we have the final page
            return pages[0]
        start_page = category_data.page_number if category_data.page_number is not None else 1
        max_page = max(pages)
        if (max_page - start_page) < self._binary_search_page_threshold:
            return max_page
        else:
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
            else int(math.ceil((right_page + left_page) / 2))
        while 1:
            if right_page < left_page:
                # Strange case where we don't have the particular page number,
                # so we move backward till we find the true page number
                left_page = right_page - self._binary_search_page_threshold
            try:
                page_request = self.get_object_request(category_data, override_page_number=page, send_error=False)
                tree = self.parser.parse(page_request.text)
                pages = self._get_available_pages_from_tree(tree)
                if len(pages) == 0:
                    # We also moved too far...
                    right_page = page - 1
                else:
                    max_page = min(max(pages), right_page)
                    if max_page - page < self._binary_search_page_threshold:
                        return max_page

                    left_page = max_page
            except PornFetchUrlError:
                # We moved too far...
                right_page = page - 1
            page = int(math.ceil((right_page + left_page) / 2))

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        total_number_of_pages = tree.xpath('.//div[@class="pager"]/span/i')
        if len(total_number_of_pages) == 1 and total_number_of_pages[0].tail is not None:
            final_page = [int(x) for x in re.findall(r'(?:from )(\d+)', total_number_of_pages[0].tail)]
            if len(final_page) > 0:
                return final_page
        return [int(x.text) for x in tree.xpath('.//div[@class="pager"]/*') if x.text is not None and x.text.isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 5

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        try:
            page_request = self.get_object_request(page_data)
        except PornFetchUrlError:
            return None
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//section[@class="throtate"]/figure')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            description = link_data[0].attrib['title']

            image_data = video_tree_data.xpath('./a/div[@class="tcontainer"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-src'] \
                if 'data-src' in image_data[0].attrib else image_data[0].attrib['src']
            image = urljoin(page_data.url, image)
            flip_images = [urljoin(page_data.url, x) for x in image_data[0].attrib['data-imgs'].split(',')]

            title_data = video_tree_data.xpath('./div/div[@class="drop"]')
            assert len(title_data) == 1
            title = title_data[0].text

            video_length = video_tree_data.xpath('./div[@class="label"]/div/i')
            assert len(video_length) == 2
            video_length = video_length[1].tail

            source = video_tree_data.xpath('./div[@class="label"]/div/a')
            assert len(source) == 1
            additional_data = {'channel': {'name': source[0].text, 'link': source[0].attrib['href']}}

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  description=description,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  additional_data=additional_data,
                                                  duration=self._format_duration(video_length),
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

        if page_number is not None and page_number != 1:
            params['p'] = page_number
        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            params.update(parse_qs(page_filter.sort_order.value))
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?search={q}'.format(q=quote_plus(query))


if __name__ == '__main__':
    # category_id = IdGenerator.make_id('/tag/mom')
    category_id = IdGenerator.make_id('/tag/wife')
    porn_star_id = IdGenerator.make_id('/pornstar/asa+akira')
    module = TubeV()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['porn_stars']['obj'], (porn_star_id, ), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
