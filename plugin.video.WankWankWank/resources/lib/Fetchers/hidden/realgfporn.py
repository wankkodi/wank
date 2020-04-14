# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError

# Internet tools
from .. import urljoin, quote

# Generator id
from ..id_generator import IdGenerator

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogVideoPageNode, VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories


class RealGfPorn(PornFetcher):
    max_flip_images = 9

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
            PornCategories.LATEST_VIDEO: 'https://www.realgfporn.com/most-recent/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.realgfporn.com/top-rated/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.realgfporn.com/most-viewed/',
            PornCategories.LONGEST_VIDEO: 'https://www.realgfporn.com/longest/',
            PornCategories.MOST_DISCUSSED_VIDEO: 'https://www.realgfporn.com/most-discussed/',
            PornCategories.SEARCH_MAIN: 'https://www.realgfporn.com/search/',
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
        return 'https://www.realgfporn.com/'

    def __init__(self, source_name='RealGfPorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(RealGfPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        tree = self.parser.parse(tmp_request.text)
        video_links = [VideoSource(link=x) for x in tree.xpath('.//video/source/@src')]
        return VideoNode(video_sources=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        try:
            page_request = self.get_object_request(category_data, send_error=False) if fetched_request is None \
                else fetched_request
        except PornFetchUrlError:
            return 1
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        start_page = category_data.page_number if category_data.page_number is not None else 1
        max_page = max(pages)
        if (max_page - start_page) < self._binary_search_page_threshold:
            return max_page
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text)
                for x in tree.xpath('.//div[@class="pagination pagination-centered pagination-inverse"]/ul/li/*')
                if x.text is not None and x.text.isdigit()]

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
        videos = (tree.xpath('.//div[@class="video-spot exoPu"]/div[@class="post"]') +
                  tree.xpath('.//div[@class="video-spot "]/div[@class="post"]'))
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./div/a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./span/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-src'] \
                if 'data-src' in image_data[0].attrib else image_data[0].attrib['src']
            image = urljoin(page_data.url, image)
            flip_images = [re.sub(r'\d*.jpg', '{i}.jpg'.format(i=i), image)
                           for i in range(1, self.max_flip_images + 1)]

            title_data = video_tree_data.xpath('./strong[@class="post-title"]/a')
            assert len(title_data) == 1
            title = title_data[0].text

            video_length = video_tree_data.xpath('./div/div[@class="post-det"]/b[@class="post-duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            number_of_views = video_tree_data.xpath('./div/div[@class="post-det"]/b[@class="post-views"]')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            rating = video_tree_data.xpath('./div/div[@class="post-det"]/span[@class="rating-holder"]/i')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].tail)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  number_of_views=number_of_views,
                                                  rating=rating,
                                                  duration=self._format_duration(video_length)
                                                  if video_length is not None else None,
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
            if re.findall(r'(page\d+.html)*$', split_url[-1]) or len(split_url[-1]) == 0:
                split_url.pop(-1)
            split_url.append('page{d}.html'.format(d=page_number))
        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/page1.html'.format(q=quote(query.replace(' ', '-')))


if __name__ == '__main__':
    # category_id = IdGenerator.make_id('/tag/mom')
    category_id = IdGenerator.make_id('/tag/wife')
    porn_star_id = IdGenerator.make_id('/pornstar/asa+akira')
    module = RealGfPorn()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['porn_stars']['obj'], (porn_star_id, ), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
