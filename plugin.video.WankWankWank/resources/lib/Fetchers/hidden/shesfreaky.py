# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# Generator id
from ..id_generator import IdGenerator


class ShesFreaky(PornFetcher):
    video_request_base_url = 'https://mydaddy.cc/'

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
            PornCategories.CATEGORY_MAIN: 'https://www.shesfreaky.com/channels/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.shesfreaky.com/top-rated/',
            PornCategories.LATEST_VIDEO: 'https://www.shesfreaky.com/videos/',
            PornCategories.RECOMMENDED_VIDEO: 'https://www.shesfreaky.com/featured/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.shesfreaky.com/most-viewed/',
            PornCategories.SEARCH_MAIN: 'https://www.shesfreaky.com/search/videos/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.RECOMMENDED_VIDEO: PornFilterTypes.FeaturedOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.shesfreaky.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'sort_order': ((PornFilterTypes.FeaturedOrder, 'Featured', 'featured'),
                                        (PornFilterTypes.DateOrder, 'Latest', 'videos'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                        ),
                         'period_filters': ([(PornFilterTypes.TwoDate, 'Week', None),
                                             (PornFilterTypes.AllDate, 'All', 'all'),
                                             (PornFilterTypes.OneDate, 'Month', 'month'),
                                             ],
                                            [('sort_order', [PornFilterTypes.ViewsOrder,
                                                             PornFilterTypes.RatingOrder,
                                                             ])]
                                            ),
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='ShesFreaks', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(ShesFreaky, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="channelsMedia"]')
        res = []
        for category in categories:
            title = category.xpath('./div[@class="channelsection"]/h2')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            link_data = category.xpath('./div[@class="channelsection"]/h2/a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image = category.xpath('./div[@class="block"]/div/div/a/span/img')
            assert len(image) > 0
            image = urljoin(category_data.url, image[0].attrib['src'])

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      object_type=PornCategories.CATEGORY,
                                                      super_object=category_data,
                                                      )
            res.append(sub_object_data)
        category_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """

        video_url = video_data.url
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_url, headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)
        videos = [VideoSource(link=x) for x in tmp_tree.xpath('.//video/source/@src')]
        assert len(videos) > 0
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, ):
            return 1
        start_page = category_data.page_number if category_data.page_number is not None else 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            # We have no pages at all!
            return 1
        max_page = max(pages)
        if max_page - start_page < self._binary_search_page_threshold:
            return max_page
        # We perform binary search
        return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x) for x in tree.xpath('.//div[@class="pagination"]/*/text()') if x.isdigit()]

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
        videos = tree.xpath('.//section[@class="content"]//div[@class="block"]/div[@class="blockItem blockItemBox"]/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            preview_video_data = video_tree_data.xpath('./span[@class="thumb"]')
            assert len(preview_video_data) == 1
            preview_video = preview_video_data[0].attrib['data-preview'] \
                if 'data-preview' in preview_video_data[0].attrib else None

            is_locked = preview_video_data[0].xpath('./span[@class="locked"]')
            if len(is_locked) > 0:
                # todo: add option to login to the site, so the user could watch some locked videos
                continue

            number_of_flip_images = preview_video_data[0].xpath('./script')
            if len(number_of_flip_images) == 0:
                # gallery
                continue

            number_of_flip_images = len(re.findall(r'(?:Array\()(.*?)(?:\))',
                                                   number_of_flip_images[-1].text)[-1].split(','))

            image_data = preview_video_data[0].xpath('./img')
            image = urljoin(self.base_url, image_data[0].attrib['data-src'])
            flip_images = [re.sub(r'\d+.jpg', '{i}.jpg'.format(i=i), image)
                           for i in range(1, number_of_flip_images + 1)]

            video_length = video_tree_data.xpath('./strong[@class="itemLength"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            title = video_tree_data.xpath('./span[@class="details"]/em')
            assert len(title) == 1
            title = title[0].text if title[0].text is not None else title[0].attrib['title']

            number_of_views = video_tree_data.xpath('./span[@class="details"]/small')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=preview_video,
                                                  duration=self._format_duration(video_length),
                                                  number_of_views=number_of_views,
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
            'Host': self.host_name,
            'Referer': page_data.url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }

        filter_conditions = self.get_proper_filter(page_data).conditions
        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            raise RuntimeError('You not suppose to be here!')
        if page_filter.period.value is not None:
            true_sort_filter_id = self._default_sort_by[true_object.object_type] \
                if true_object.object_type in self._default_sort_by \
                else page_filter.sort_order.filter_id
            if true_sort_filter_id in filter_conditions.period.sort_order:
                split_url[-2] += '-' + page_filter.period.value

        if page_data.page_number is not None and page_data.page_number != 1:
            if re.findall(r'page\d+.html', split_url[-1]) or len(split_url[-1]) == 0:
                split_url[-1] = 'page{d}.html'.format(d=page_number)
            else:
                split_url.append('page{d}.html'.format(d=page_number))
        program_fetch_url = '/'.join(split_url)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/page1.html'.format(q=quote(query.replace(' ', '-')))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('/category/1080p-porn')
    module = ShesFreaky()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user()
