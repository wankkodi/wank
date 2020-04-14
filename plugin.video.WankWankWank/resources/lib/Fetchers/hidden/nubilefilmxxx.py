# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError

# Internet tools
from .. import urljoin, urlparse, quote_plus

# Generator id
from ..id_generator import IdGenerator

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# abstract
from abc import ABCMeta, abstractmethod


class BaseObject(PornFetcher):
    @property
    @abstractmethod
    def base_url(self):
        """
        Base site url.
        :return:
        """
        raise NotImplementedError

    metaclass = ABCMeta

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """

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
        tmp_request = self.session.get(video_data.url, headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)

        videos = [VideoSource(link=x) for x in tmp_tree.xpath('.//video/source/@src')]
        assert len(videos) > 0

        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'identity;q=1, *;q=0',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': urlparse(videos[0].link).hostname,
            'Range': 'bytes=0-',
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': self.user_agent
        }
        return VideoNode(video_sources=videos, headers=headers)

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
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
        if page_number is not None and page_number != 1:
            if len(split_url[-1]) > 0:
                split_url.append('')
            split_url.insert(-1, 'page')
            split_url.insert(-1, str(page_number))

        if page_filter.sort_order.value is not None:
            if true_object.object_type not in (PornCategories.LATEST_VIDEO, PornCategories.MOST_VIEWED_VIDEO,
                                               PornCategories.LONGEST_VIDEO, PornCategories.POPULAR_VIDEO,
                                               PornCategories.RANDOM_VIDEO):
                params['filter'] = [page_filter.sort_order.value]

        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?s={q}'.format(q=quote_plus(query))


class NubileFilmXXX(BaseObject):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '?filter=latest'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '?filter=most-viewed'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '?filter=longest'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, '?filter=popular'),
            PornCategories.RANDOM_VIDEO: urljoin(self.base_url, '?filter=random'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.RANDOM_VIDEO: PornFilterTypes.RandomOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.nubilefilm.xxx/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Latest Videos', 'latest'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed Videos', 'most-viewed'),
                                        (PornFilterTypes.LengthOrder, 'Longest Videos', 'longest'),
                                        (PornFilterTypes.PopularityOrder, 'Popular Videos', 'popular'),
                                        (PornFilterTypes.RandomOrder, 'Random Videos', 'random'),
                                        ),
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         single_channel_args=video_filters,
                                         video_args=video_filters,
                                         search_args=video_filters,
                                         )

    def __init__(self, source_name='NubileFilmXXX', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(NubileFilmXXX, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                            session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, './/section[@id="tag_cloud-7"]/div/a',
                                                  PornCategories.CATEGORY)

    def _update_available_porn_stars(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, './/section[@id="tag_cloud-6"]/div/a',
                                                  PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(channel_data, './/section[@id="extended-tags-3"]/p/a',
                                                  PornCategories.CHANNEL)

    def _update_available_base_object(self, base_object_data, xpath, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=category.attrib['href'],
                                       url=urljoin(base_object_data.url, category.attrib['href']),
                                       title=category.text
                                       if category.text is not None else category.xpath('./span')[0].text,
                                       number_of_videos=int(re.findall(r'\d+', category.attrib['title'])[0]),
                                       object_type=object_type,
                                       super_object=base_object_data,
                                       ) for category in categories]
        base_object_data.add_sub_objects(res)
        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.PORN_STAR_MAIN,
                                         PornCategories.CHANNEL_MAIN):
            return 1
        try:
            page_request = self.get_object_request(category_data, send_error=False) if fetched_request is None \
                else fetched_request
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
        return ([int(x.text) for x in tree.xpath('.//div[@class="pagination"]/ul/li/a') if x.text.isdigit()] +
                [int(re.findall(r'(?:page/)(\d+)', x.attrib['href'])[0])
                 for x in tree.xpath('.//div[@class="pagination"]/ul/li/a')
                 if 'href' in x.attrib and len(re.findall(r'(?:page/)(\d+)', x.attrib['href'])) > 0])

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        # videos = tree.xpath('.//div[@class="videos-list"]/article/a')
        videos = tree.xpath('.//div/article/a')
        res = []
        for video_tree_data in videos:
            title = video_tree_data.attrib['title'] \
                if 'title' in video_tree_data.attrib else video_tree_data.attrib['data-title']

            image = video_tree_data.xpath('./div[@class="post-thumbnail "]/img')
            image = (image[0].attrib['data-src'] if 'data-src' in image[0].attrib else image[0].attrib['src']) \
                if len(image) == 1 else None

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['href'],
                                                  url=urljoin(self.base_url, video_tree_data.attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
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
        if page_number is not None and page_number != 1:
            if len(split_url[-1]) > 0:
                split_url.append('')
            split_url.insert(-1, 'page')
            split_url.insert(-1, str(page_number))

        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            params['filter'] = [page_filter.sort_order.value]

        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?s={q}'.format(q=quote_plus(query))


class PlusOne8(NubileFilmXXX):
    max_flip_image = 16

    @property
    def object_urls(self):
        res = super(PlusOne8, self).object_urls
        res[PornCategories.CATEGORY_MAIN] = urljoin(self.base_url, '/porn-categories/')
        res[PornCategories.TAG_MAIN] = urljoin(self.base_url, '/porn-tags/')
        res[PornCategories.PORN_STAR_MAIN] = urljoin(self.base_url, '/pornstars/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://plusone8.com/'

    def __init__(self, source_name='PlusOne8', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PlusOne8, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
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
            try:
                page_request = self.get_object_request(category_data, override_page_number=page, send_error=False)
            except PornFetchUrlError:
                break
            tree = self.parser.parse(page_request.text)
            if max_page is None:
                available_pages = self._get_available_pages_from_tree(tree)
                max_page = max(available_pages) if len(available_pages) > 0 else 1

            categories = tree.xpath('.//div[@class="videos-list"]/article/a')
            for category in categories:
                image = category.xpath('./div/img')
                assert len(image) == 1

                object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=category.attrib['href'],
                                                      url=urljoin(self.base_url, category.attrib['href']),
                                                      title=category.attrib['title'],
                                                      image_link=image[0].attrib['src'],
                                                      object_type=PornCategories.CATEGORY,
                                                      super_object=category_data,
                                                      )
                res.append(object_data)
            if page == max_page:
                # We reached the last page
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
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="videos-list"]/article/a')
        res = []
        for category in categories:
            image = category.xpath('./div/img')
            assert len(image) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=category.attrib['title'],
                                                  image_link=image[0].attrib['src'],
                                                  raw_data=image[0].attrib,
                                                  object_type=PornCategories.PORN_STAR,
                                                  super_object=porn_star_data,
                                                  )
            res.append(object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return NotImplemented

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="tag-item"]/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.text, None) for x in raw_objects])
        assert len(titles) == len(links)
        assert len(titles) == len(number_of_videos)

        return links, titles, number_of_videos

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN, PornCategories.CATEGORY_MAIN):
            return 1
        try:
            page_request = self.get_object_request(category_data, send_error=False) if fetched_request is None \
                else fetched_request
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
        return set(([int(x.split('/')[-2]) for x in (tree.xpath('.//div[@class="pagination"]/ul/li/a/@href'))
                     if x.split('/')[-2].isdigit()] +
                    [int(x) for x in (tree.xpath('.//div[@class="pagination"]/ul/li/a/text()'))
                     if x.isdigit()]))

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div/article/a')
        res = []
        for video_tree_data in videos:
            flix_image = video_tree_data.xpath('./div[@class="post-thumbnail thumbs-rotation"]')
            assert len(flix_image) == 1

            image = video_tree_data.xpath('./div[@class="post-thumbnail thumbs-rotation"]/img')
            assert len(image) == 1

            video_length = video_tree_data.xpath('./div[@class="post-thumbnail thumbs-rotation"]/'
                                                 'span[@class="duration"]/i')
            video_length = \
                self._format_duration(self._clear_text(video_length[0].tail)) if len(video_length) == 1 else None

            rating = video_tree_data.xpath('./div[@class="rating-bar"]/span')
            # assert len(rating) == 1

            video_data = PornCatalogVideoPageNode(
                catalog_manager=self.catalog_manager,
                obj_id=video_tree_data.attrib['href'],
                url=urljoin(self.base_url, video_tree_data.attrib['href']),
                title=video_tree_data.attrib['title'],
                image_link=image[0].attrib['data-src']
                if 'data-src' in image[0].attrib else image[0].attrib['src'],
                flip_images_link=flix_image[0].attrib['data-thumbs'].split(','),
                duration=video_length,
                rating=self._clear_text(rating[0].text) if len(rating) > 0 else None,
                object_type=PornCategories.VIDEO,
                super_object=page_data,
            )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res


if __name__ == '__main__':
    # category_id = IdGenerator.make_id('/tag/mom')
    category_id = IdGenerator.make_id('/tag/wife')
    porn_star_id = IdGenerator.make_id('/pornstar/asa+akira')
    module = NubileFilmXXX()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['porn_stars']['obj'], (porn_star_id, ), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
