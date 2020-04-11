# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornFetchUrlError

# Internet tools
from .. import urljoin

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# Generator id
from ..id_generator import IdGenerator


class PornGo(PornFetcher):
    max_flip_images = 15

    @property
    def object_urls(self):
        return {
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/models/'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/sites/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.porngo.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        channels_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Popular', None),
                                           (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                           (PornFilterTypes.AlphabeticOrder, 'Alphabetical', 'alphabetical'),
                                           ),
                            }
        porn_stars_filters = {'sort_order': ((PornFilterTypes.TrendingOrder, 'Top Trending', None),
                                             (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                             (PornFilterTypes.AlphabeticOrder, 'Alphabetical', 'alphabetical'),
                                             ),
                              }
        base_video_filters = {'quality_filters': ((PornFilterTypes.AllQuality, 'All Qualities', None),
                                                  (PornFilterTypes.UHDQuality, '4K', '4k'),
                                                  )
                              }
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Newest', None),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-popular'),
                                        ),
                         'quality_filters': base_video_filters['quality_filters']
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         channels_args=channels_filters,
                                         porn_stars_args=porn_stars_filters,
                                         single_porn_star_args=base_video_filters,
                                         single_channel_args=video_filters,
                                         single_tag_args=video_filters,
                                         video_args=video_filters,
                                         # search_args=video_filters,
                                         )

    def __init__(self, source_name='PornGo', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornGo, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="thumbs-list thumbs-list_model"]/div/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            title = category.attrib['title']

            image_data = category.xpath('./div[@class="thumb__img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            rating = category.xpath('.//div[@class="thumb__img"]/span[@class="thumb__count"]')
            assert len(rating) == 1
            rating = rating[0].text

            number_of_videos = category.xpath('.//div[@class="thumb__img"]/span[@class="thumb__duration"]/span[2]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(porn_star_data.url, link),
                                               title=title,
                                               image_link=image,
                                               rating=rating,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))
        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@data-ajax]/div[@class="main__row"]')
        res = []
        for category in categories:
            title_data = category.xpath('./div[@class="headline"]/div/h2/span')
            assert len(title_data) == 1
            title = title_data[0].text

            children_data = category.xpath('./div[@class="thumbs-list desktop-row"]/div[@class="thumb item"]')
            assert len(children_data) > 0
            image = children_data[0].xpath('./a/div[@class="thumb__img"]/img')[0].attrib['src']

            link_data = category.xpath('./div[@class="block-related__bottom"]/a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            number_of_videos = int(re.findall(r'(\d+)(?: video)', link_data[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(channel_data.url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ))
        channel_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="letter-section"]/div[@class="letter-block"]')[1:]
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.xpath('./span')[0].text, None)
                                                for y in raw_objects
                                                for x in y.xpath('./div[@class="letter-items"]/'
                                                                 'div[@class="letter-block__item"]/a')
                                                if x.xpath('./span')[0].text])
        return links, titles, number_of_videos

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

        video_links = sorted((VideoSource(link=x.attrib['src'],
                                          resolution=re.findall(r'(\d+)(?:p)', x.attrib['label'])[0])
                              for x in tmp_tree.xpath('.//video/source')),
                             key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=video_links)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        if not self._check_is_available_page(page_request):
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
        return [int(re.findall(r'(\d+)(?:/\?*)', x.attrib['href'])[0])
                for x in tree.xpath('.//div[@class="pagination"]/div/a')
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/\?*)', x.attrib['href'])) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        try:
            page_request = self.get_object_request(page_data)
        except PornFetchUrlError:
            return []
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumbs-list"]/div[@class="thumb item "]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            preview_data = link_data[0].xpath('./div[@class="thumb__img"]')
            assert len(preview_data) == 1
            preview_link = preview_data[0].attrib['data-preview'] if 'data-preview' in preview_data[0].attrib else None

            image_data = preview_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            flip_images = [re.sub(r'\d+.jpg$', '{p}.jpg'.format(p=p), image)
                           for p in range(1, self.max_flip_images + 1)]

            video_length_data = preview_data[0].xpath('./span[@class="thumb__duration"]')
            assert len(video_length_data) == 1
            video_length = video_length_data[0].text

            resolution_data = link_data[0].xpath('./span[@class="thumb__bage"]')
            assert len(resolution_data) == 1
            resolution = resolution_data[0].text
            is_hd = int(re.findall(r'\d+', resolution)[0]) >= 720

            actors_data = video_tree_data.xpath('./div[@class="thumb__info"]/div[@class="thumb-models"]/a')
            assert len(actors_data) >= 1
            additional_data = {'actors': [{'name': x.text,
                                           'link': x.attrib['href'] if 'href' in x.attrib else None}
                                          for x in actors_data]
                               }

            rating_data = video_tree_data.xpath('./div[@class="thumb__info"]/div[@class="thumb__bottom"]/'
                                                'div[@class="thumb__box"]/span[@class="thumb__text"]')
            assert len(rating_data) >= 1
            rating = rating_data[0].text
            number_of_views = rating_data[1].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=preview_link,
                                                  duration=self._format_duration(video_length),
                                                  resolution=resolution,
                                                  is_hd=is_hd,
                                                  additional_data=additional_data,
                                                  rating=rating,
                                                  number_of_views=number_of_views,
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
        if len(split_url[-1]) > 0:
            split_url.append('')

        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            split_url.insert(-1, page_filter.sort_order.value)

        if page_filter.quality.value is not None:
            self.session.cookies.set(name='quality',
                                     value=page_filter.quality.value,
                                     domain='www.porngo.com')
        else:
            # We want to remove the obsolete cookies
            if 'quality' in self.session.cookies:
                self.session.cookies.pop('quality')

        if page_number is not None and page_number != 1:
            split_url.insert(-1, str(page_number))

        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return (self.object_urls[PornCategories.SEARCH_MAIN] +
                '/{q}/'.format(q=query.replace('-', '--').replace(' ', '-')))


class XXXFiles(PornGo):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.porngo.com/'

    def __init__(self, source_name='XXXFiles', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(XXXFiles, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)


if __name__ == '__main__':
    # category_id = IdGenerator.make_id('/tag/mom')
    category_id = IdGenerator.make_id('/tag/wife')
    porn_star_id = IdGenerator.make_id('/pornstar/asa+akira')
    module = PornGo()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['porn_stars']['obj'], (porn_star_id, ), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
