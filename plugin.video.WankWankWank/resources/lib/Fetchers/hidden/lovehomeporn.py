# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogVideoPageNode, VideoNode, VideoSource
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# Generator id
from ..id_generator import IdGenerator


class LoveHomePorn(PornFetcher):
    video_request_url = 'https://lovehomeporn.com/media/nuevo/config.php'

    @property
    def object_urls(self):
        return {
            PornCategories.BEING_WATCHED_VIDEO: 'https://lovehomeporn.com/videos?o=bw',
            PornCategories.LATEST_VIDEO: 'https://lovehomeporn.com/videos?o=mr',
            PornCategories.MOST_VIEWED_VIDEO: 'https://lovehomeporn.com/videos?o=mv',
            PornCategories.TOP_RATED_VIDEO: 'https://lovehomeporn.com/videos?o=tr',
            PornCategories.FAVORITE_VIDEO: 'https://lovehomeporn.com/videos?o=tf',
            PornCategories.MOST_DOWNLOADED_VIDEO: 'https://lovehomeporn.com/videos?o=md',
            PornCategories.SEARCH_MAIN: 'https://lovehomeporn.com/videos/category/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.BEING_WATCHED_VIDEO: PornFilterTypes.BeingWatchedOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.FAVORITE_VIDEO: PornFilterTypes.FavorOrder,
            PornCategories.MOST_DOWNLOADED_VIDEO: PornFilterTypes.DownloadsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://lovehomeporn.com/'

    def __init__(self, source_name='LoveHomePorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(LoveHomePorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                           session_id)

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        # todo: add support for premium content
        video_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Most Recent', 'mr'),
                                        (PornFilterTypes.BeingWatchedOrder, 'Being Watched', 'bw'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'mv'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'tr'),
                                        (PornFilterTypes.FavorOrder, 'Top Favorite', 'tf'),
                                        (PornFilterTypes.DownloadsOrder, 'Most Downloads', 'md'),
                                        ],
                         'period_filters': [(PornFilterTypes.AllDate, 'All Time', 'a'),
                                            (PornFilterTypes.OneDate, 'Today', 't'),
                                            (PornFilterTypes.TwoDate, 'Yesterday', 'y'),
                                            (PornFilterTypes.ThreeDate, 'This Week', 'w'),
                                            (PornFilterTypes.FourDate, 'This Month', 'm'),
                                            (PornFilterTypes.FiveDate, 'Last Month', 'lm'),
                                            (PornFilterTypes.SixDate, 'This Year', 'ty'),
                                            (PornFilterTypes.SevenDate, 'Last Year', 'ly'),
                                            ],
                         'quality_filters': [(PornFilterTypes.AllQuality, 'All quality', None),
                                             (PornFilterTypes.HDQuality, 'HD', 'hd'),
                                             ],
                         'length_filters': [(PornFilterTypes.AllLength, 'Any duration', None),
                                            (PornFilterTypes.OneLength, '10+ min', 'duration'),
                                            ],
                         # 'comments_filters': [(PornFilterTypes.AllLength, 'Any duration', None),
                         #                      (PornFilterTypes.OneLength, '10+ min', 'duration'),
                         #                      ],
                         }
        # search_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Most Recent', 'mr'),
        #                                  (PornFilterTypes.BeingWatchedOrder, 'Being Watched', 'bw'),
        #                                  (PornFilterTypes.ViewsOrder, 'Most Viewed', 'mv'),
        #                                  (PornFilterTypes.RatingOrder, 'Top Rated', 'tr'),
        #                                  (PornFilterTypes.FavorOrder, 'Top Favorite', 'tf'),
        #                                  ],
        #                   }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         video_args=video_filters,
                                         search_args=video_filters,
                                         )

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        split_url = video_data.url.split('/')
        headers = {
            'Accept': '*/*',
            'Cache-Control': 'max-age=0',
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }
        params = {'key': split_url[4]}
        tmp_request = self.session.get(self.video_request_url, headers=headers, params=params)
        tree = self.parser.parse(tmp_request.text)
        videos = tree.xpath('.//file')
        res = [VideoSource(link=x.text) for x in videos]
        return VideoNode(video_sources=res,)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
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
        return [int(re.findall(r'(\d+)(?:/*\?|/*$)', x.attrib['href'])[0])
                for x in tree.xpath('.//div[@class="pagination"]/ul/li/a')
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*\?|/*$)', x.attrib['href'])) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumbs-items"]/a')
        res = []
        for video_tree_data in videos:
            # is_premium = video_tree_data.xpath('./div[@class="img-holder"]/div[@class="premium"]')
            # if len(is_premium) > 0:
            #     # todo: add support for premium
            #     continue

            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./div[@class="img-holder"]/img')
            assert len(image_data) == 1
            title = image_data[0].attrib['title']
            image = image_data[0].attrib['data-original'] \
                if 'data-original' in image_data[0].attrib else image_data[0].attrib['src']

            is_hd = video_tree_data.xpath('./div[@class="img-holder"]/div[@class="quality"]')
            is_hd = len(is_hd) == 1 and is_hd[0].text == 'HD'

            video_length = video_tree_data.xpath('./div[@class="img-holder"]/div[@class="info"]')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0].text)

            rating = video_tree_data.xpath('./div[@class="img-holder"]/ul[@class="rating_small"]/li/span')
            assert len(rating) > 0
            rating_number = 0
            for loc_rating in rating:
                if 'class' not in loc_rating.attrib:
                    continue
                if loc_rating.attrib['class'] == 'half':
                    rating_number += 0.5
                if loc_rating.attrib['class'] == 'full':
                    rating_number += 0.5
            rating = '{d}%'.format(d=(rating_number / 5) * 100)

            info_data = video_tree_data.xpath('./div[@class="info-holder"]/div[@class="details"]/div[@class="item"]/'
                                              'span[@class="text"]')
            assert len(info_data) == 2
            added_before = info_data[0].text
            number_of_views = info_data[1].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  is_hd=is_hd,
                                                  duration=self._format_duration(video_length),
                                                  added_before=added_before,
                                                  number_of_views=number_of_views,
                                                  rating=rating,
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
            'Referer': page_data.url,
            # 'Host': urlparse(object_data.url).hostname,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_number is not None and page_number != 1:
            # params['page'] = page_number
            if split_url[-1].isdigit():
                split_url.pop()
            split_url.append(str(page_number))
        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            params['o'] = page_filter.sort_order.value
        if page_filter.period.value is not None:
            params['t'] = page_filter.period.value
        # todo: add support for premium content here
        other_filters = ['free']
        for x in (page_filter.quality.value, page_filter.length.value, page_filter.comments.value):
            if x is not None:
                other_filters.append(x)

        params['filters'] = ','.join(other_filters)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        true_query = re.sub(r'[^A-Za-z0-9 ]', '', query)
        true_query = re.sub(r'\s{2}\s*', ' ', true_query)
        true_query = re.sub(r'\s', '- ', true_query)
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}/'.format(q=true_query)


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    module = LoveHomePorn()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
