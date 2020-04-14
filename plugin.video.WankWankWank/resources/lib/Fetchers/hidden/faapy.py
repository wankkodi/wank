# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote_plus

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# JSON
from ..tools.text_json_manioulations import prepare_json_from_not_formatted_text

# Generator id
from ..id_generator import IdGenerator


class Faapy(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://faapy.com/',
            PornCategories.CHANNEL_MAIN: 'https://faapy.com/channels/',
            PornCategories.TOP_RATED_VIDEO: 'https://faapy.com/top-rated/',
            PornCategories.POPULAR_VIDEO: 'https://faapy.com/most-popular/',
            PornCategories.SEARCH_MAIN: 'https://faapy.com/searchone.php',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://faapy.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters = {'period_filters': ([(PornFilterTypes.AllAddedBefore, 'All time', None),
                                             (PornFilterTypes.OneAddedBefore, 'Today', 'today'),
                                             (PornFilterTypes.TwoAddedBefore, 'This week', 'week'),
                                             (PornFilterTypes.ThreeAddedBefore, 'This month', 'month'),
                                             ],
                                            [('sort_order', [PornFilterTypes.RatingOrder,
                                                             PornFilterTypes.ViewsOrder])]
                                            ),
                         }
        channels_filter = {'sort_order': [(PornFilterTypes.DateOrder, 'Last video added', None),
                                          (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                                          (PornFilterTypes.ViewsOrder, 'Most viewed', 'popularity'),
                                          (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                                          (PornFilterTypes.NumberOfVideosOrder, 'Most videos', 'total-videos'),
                                          ],
                           }
        single_category_filter = {'sort_order': [(PornFilterTypes.DateOrder, 'New', None),
                                                 (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                                 (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-popular'),
                                                 (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                                 (PornFilterTypes.FavorOrder, 'Trending', 'most-favourited'),
                                                 ],
                                  'period_filters': video_filters['period_filters']
                                  }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         channels_args=channels_filter,
                                         single_category_args=single_category_filter,
                                         single_channel_args=single_category_filter,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='Faapy', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Faapy, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                    session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="block-categories"]/ul/li/a')
        res = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                       obj_id=category.attrib['href'],
                                       url=urljoin(self.base_url, category.attrib['href']),
                                       title=category.text,
                                       object_type=PornCategories.CATEGORY,
                                       super_object=category_data,
                                       ) for category in categories]

        category_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        channels = tree.xpath('.//div[@class="thumbs channels"]/a')
        res = []
        for channel in channels:
            link = channel.attrib['href']

            image_data = channel.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = channel.xpath('./span/i')
            assert len(number_of_videos) == 1
            number_of_videos = int(self._clear_text(number_of_videos[0].tail))

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ))

        channel_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        request_data = re.findall(r'(?:var flashvars = )({.*?})(?:;)', tmp_request.text, re.DOTALL)
        assert len(request_data) == 1
        request_data = prepare_json_from_not_formatted_text(request_data[0])
        videos = [VideoSource(link=re.findall(r'http.*$', request_data['video_url'])[0],
                              resolution=re.findall(r'\d+', request_data['video_url_text'])[0])]
        i = 1
        while 1:
            new_video_field = 'video_alt_url{i}'.format(i=i if i != 1 else '')
            new_text_field = 'video_alt_url{i}_text'.format(i=i if i != 1 else '')
            is_redirect_field = 'video_alt_url{i}_redirect'.format(i=i if i != 1 else '')
            if new_video_field in request_data:
                if is_redirect_field not in request_data:
                    videos.append(VideoSource(link=re.findall(r'http.*$', request_data[new_video_field])[0],
                                              resolution=re.findall(r'\d+', request_data[new_text_field])[0]))
                i += 1
            else:
                break

        videos.sort(key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.CATEGORY_MAIN,):
            return 1

        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        return max(pages) if len(pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text) for x in tree.xpath('.//ul[@class="pagination"]/li/*')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumb-wrap"]/div[@class="thumb"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']
            # title = link_data[0].attrib['title']

            image_data = video_tree_data.xpath('./a/div[@class="thumb-img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            video_preview_data = video_tree_data.xpath('./a/div[@class="thumb-img"]/video')
            assert len(video_preview_data) == 1
            video_preview = \
                video_preview_data[0].attrib['data-preview'] if 'data-preview' in link_data[0].attrib else None

            title = video_tree_data.xpath('./a/em[@class="info"]/span[@class="thumb-name"]')
            assert len(title) == 1
            title = title[0].text

            number_of_views = video_tree_data.xpath('./a/em[@class="info"]/span[@class="date"]/i')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].tail

            rating = video_tree_data.xpath('./a/em[@class="info"]/span[@class="video-rating"]/span')
            assert len(rating) == 1
            rating = re.findall(r'\d+%', rating[0].attrib['style'])[0]

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  preview_video_link=video_preview,
                                                  rating=rating,
                                                  number_of_views=number_of_views,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
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
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id
        split_url = fetch_base_url.split('/')
        if page_filter.sort_order.value is not None:
            if true_object.object_type not in self._default_sort_by:
                split_url.insert(-1, page_filter.sort_order.value)
        if (
                page_filter.period.value is not None and
                (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
        ):
            split_url.insert(-1, page_filter.period.value)

        fetch_base_url = '/'.join(split_url)
        if page_number is not None and page_number != 1:
            fetch_base_url = re.sub(r'/*\d*/$', '/{d}/'.format(d=page_number), fetch_base_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    module = Faapy()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=False)
