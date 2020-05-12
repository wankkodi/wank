# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote_plus

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ....catalogs.porn_catalog import PornCategories


class XPaja(PornFetcher):
    max_flip_images = 10
    _number_of_pages_from_first_page = 9

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 5000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.xpaja.net/categories/',
            PornCategories.LATEST_VIDEO: 'https://www.xpaja.net/videos',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.xpaja.net/most-viewed',
            PornCategories.TOP_RATED_VIDEO: 'https://www.xpaja.net/top-rated',
            PornCategories.RANDOM_VIDEO: 'https://www.xpaja.net/recommended',
            PornCategories.SEARCH_MAIN: 'https://www.xpaja.net/search/videos/',
        }

    @property
    def _default_sort_by(self):
        return {}

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.xpaja.net'

    @property
    def number_of_videos_per_page(self):
        """
        Base site url.
        :return:
        """
        return 30  # 5*6

    def __init__(self, source_name='XPaja', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(XPaja, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                    session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="contentWrap"]//div[@class="container"]/'
                                'div[@class="col-xs-6 col-sm-6 col-md-6 col-lg-3"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('.//div[@class="thumb-cat"]/img')
            assert len(image_data) == 1
            image = urljoin(category_data.url, image_data[0].attrib['src'])

            title = category.xpath('./div[@class="header-post-category"]/h2')
            assert len(title) == 1
            title = title[0].text

            number_of_videos = category.xpath('./div[@class="header-post-category"]/span/em')
            assert len(number_of_videos) == 1
            number_of_videos = int(''.join(re.findall(r'\d+', number_of_videos[0].text)))

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(category_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)

        category_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        videos = tmp_tree.xpath('.//video/source')
        video_links = sorted((VideoSource(link=urljoin(self.base_url, x.attrib['src']),
                                          resolution=re.findall(r'\d+', x.attrib['label'])[0]) for x in videos),
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
        videos = tree.xpath('.//div[@class="container"]/div[@class="col-xs-6 col-sm-6 col-md-6 col-lg-3"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./div[@class="embed-responsive embed-responsive-16by9"]//a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])
            flip_image = [re.sub(r'\d.jpg$', '{i}.jpg'.format(i=i), image)
                          for i in range(1, self.max_flip_images + 1)]
            preview_video = re.sub(r'[\w.]+$', 'v-preview.mp4', image)

            video_length = link_data[0].xpath('./div[@class="amount"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            content_data = video_tree_data.xpath('./div[@class="header-content"]')
            assert len(content_data) == 1
            title = content_data[0].xpath('./div[@class="header-post"]/a/h3')
            assert len(title) == 1
            title = title[0].attrib['title']

            number_of_viewers_data = content_data[0].xpath('./div[@class="header-post"]/div[@class="post-inf"]')
            assert len(number_of_viewers_data) == 1
            number_of_viewers = re.findall(r'(.*?)(?: *\|)', number_of_viewers_data[0].text)[0]

            number_of_likes_data = number_of_viewers_data[0].xpath('./span')
            assert len(number_of_likes_data) == 2
            number_of_likes = number_of_likes_data[0].text
            number_of_comments = number_of_likes_data[1].text

            uploader_data = number_of_viewers_data[0].xpath('./a')
            if len(uploader_data) == 1:
                additional_data = {'uploader': {'name': uploader_data[0].text, 'link': uploader_data[0].attrib['href']}}
                added_before = re.sub(r'^[\s|]*|[\s|]*$', '', uploader_data[0].tail)
            else:
                additional_data = None
                added_before = re.sub(r'^[\s|]*|[\s|]*$', '', number_of_viewers_data[0].xpath('./br')[0].tail)

            res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                obj_id=link,
                                                url=urljoin(self.base_url, link),
                                                title=title,
                                                image_link=image,
                                                flip_images_link=flip_image,
                                                preview_video_link=preview_video,
                                                duration=self._format_duration(video_length),
                                                number_of_views=number_of_viewers,
                                                number_of_likes=number_of_likes,
                                                number_of_comments=number_of_comments,
                                                added_before=added_before,
                                                additional_data=additional_data,
                                                object_type=PornCategories.VIDEO,
                                                super_object=page_data,
                                                ))
        page_data.add_sub_objects(res)
        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.RANDOM_VIDEO):
            return 1
        if fetched_request is None:
            fetched_request = self._get_object_request_no_exception_check(category_data)
        if not self._check_is_available_page(category_data, fetched_request):
            return 1
        tree = self.parser.parse(fetched_request.text)
        pages = self._get_available_pages_from_tree(tree)
        current_page = category_data.page_number if category_data.page_number is not None else 1
        if len(pages) == 0:
            return 1
        elif max(pages) - current_page < self._binary_search_page_threshold:
            return max(pages)
        elif current_page == 1 and max(pages) < self._number_of_pages_from_first_page:
            return max(pages)
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 4

    def _check_is_available_page(self, page_object, page_request=None):
        """
        In binary search performs test whether the current page is available.
        :param page_object: Page object.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        current_page = page_request.url.split('/')
        current_page = int(current_page[-2]) if current_page[-2].isdigit() else None
        available_pages = self._get_available_pages_from_tree(tree)
        if len(available_pages) > 0 and current_page is not None and max(available_pages) >= current_page:
            return True
        elif current_page is None:
            return True
        else:
            return False

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0])
                for x in tree.xpath('.//ul[@class="pagination"]/li/a')
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0] + \
               [int(x.text) for x in tree.xpath('.//ul[@class="pagination"]/li/a')
                if x.text.isdigit()]

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
            # 'Host': self.host_name,
            'Referer': page_data.url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_number is not None and page_number != 1:
            if split_url[-2] == 'page':
                if split_url[-1].isdigit():
                    split_url[-1] = str(page_number)
                else:
                    split_url.append(str(page_number))
            else:
                split_url.append('page')
                split_url.append(str(page_number))
        program_fetch_url = '/'.join(split_url)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=quote_plus(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(XPaja, self)._version_stack + [self.__version]
