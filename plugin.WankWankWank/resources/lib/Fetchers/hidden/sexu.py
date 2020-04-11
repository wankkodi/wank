# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote_plus, parse_qs

# Generator id
from ..id_generator import IdGenerator

# JSON
from ..tools.text_json_manioulations import prepare_json_from_not_formatted_text

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


class SexU(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://sexu.com/categories',
            PornCategories.PORN_STAR_MAIN: 'https://sexu.com/pornstars',
            PornCategories.LATEST_VIDEO: 'https://sexu.com/new',
            PornCategories.TOP_RATED_VIDEO: 'https://sexu.com/all',
            PornCategories.TRENDING_VIDEO: 'https://sexu.com/trending',
            PornCategories.INTERESTING_VIDEO: 'https://sexu.com/engaging',
            PornCategories.SEARCH_MAIN: 'https://sexu.com/search',
        }

    @property
    def _default_sort_by(self):
        return {PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
                PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
                PornCategories.TRENDING_VIDEO: PornFilterTypes.PopularityOrder,
                PornCategories.INTERESTING_VIDEO: PornFilterTypes.InterestOrder,
                }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://sexu.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        categories_filters = {'sort_order': ((PornFilterTypes.AlphabeticOrder, 'Alphabetical', 'sort=name'),
                                             (PornFilterTypes.PopularityOrder, 'Most Popular', 'sort=rating'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'sort=vcount'),
                                             ),
                              }
        porn_stars_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Most Popular', 'sort=rating'),
                                             (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'sort=vcount'),
                                             (PornFilterTypes.AlphabeticOrder, 'Alphabetical', 'sort=name'),
                                             ),
                              }
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Upload date', 'st=upload'),
                                        (PornFilterTypes.RatingOrder, 'Rating', 'st=rating'),
                                        (PornFilterTypes.PopularityOrder, 'Popularity', 'st=pop'),
                                        (PornFilterTypes.InterestOrder, 'Interest', 'st=interest'),
                                        ),
                         'added_before_filters':
                             ((PornFilterTypes.AllAddedBefore, 'All time', None),
                              (PornFilterTypes.OneAddedBefore, 'Today', 'su=today'),
                              (PornFilterTypes.TwoAddedBefore, 'This Week', 'su=week'),
                              (PornFilterTypes.ThreeAddedBefore, 'Past month', 'su=month'),
                              ),
                         'length_filters': ((PornFilterTypes.AllLength, 'Any duration', None),
                                            (PornFilterTypes.OneLength, 'Short', 'sd=short'),
                                            (PornFilterTypes.TwoLength, 'Long', 'sd=long'),
                                            (PornFilterTypes.ThreeLength, 'Full', 'sd=full'),
                                            ),
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         categories_args=categories_filters,
                                         porn_stars_args=porn_stars_filters,
                                         single_category_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         video_args=video_filters,
                                         search_args=video_filters,
                                         )

    def __init__(self, source_name='SexU', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SexU, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, PornCategories.CATEGORY)

    def _update_available_porn_stars(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, PornCategories.PORN_STAR)

    def _update_available_base_object(self, base_object_data, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//ul[@class="grid"]/li[@class="grid__item"]/a')
        res = []
        for category in categories:
            image = category.xpath('./div[@class="item__main"]/div[@class="item__image"]/img')
            assert len(image) == 1
            image = image[0].attrib['data-src'] \
                if 'data-src' in image[0].attrib else image[0].attrib['src']

            number_of_videos = category.xpath('./div[@class="item__main"]/div[@class="item__counter"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=category.attrib['title'],
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  object_type=object_type,
                                                  super_object=base_object_data,
                                                  )
            res.append(object_data)
        base_object_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)

        videos = tmp_tree.xpath('.//div[@class="player-block__item"]/video/source')
        if len(videos) > 0:
            video_links = sorted((VideoSource(link=urljoin(video_data.url, x.attrib['src']),
                                              resolution=int(x.attrib['title'][:-1])) for x in videos),
                                 key=lambda x: x.resolution, reverse=True)
        else:
            # Another version
            videos = tmp_tree.xpath('.//div[@class="player-block__item"]/video/script')
            assert len(videos) == 1
            raw_data = prepare_json_from_not_formatted_text(re.findall(r'(?:var playerSettings = )({.*}?)(?:;)',
                                                                       videos[0].text)[0])
            video_links = sorted((VideoSource(link=urljoin(video_data.url,
                                                           re.sub(raw_data['clip']['defaultQuality'], x,
                                                                  raw_data['clip']['downloadUrl']),
                                                           ),
                                              resolution=int(x[:-1]))
                                  for x in raw_data['clip']['qualities']),
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
        if not page_request.ok:
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
        return ([int(x) for x in tree.xpath('.//div[@class="pagination__list"]/a/text()') if x.isdigit()] +
                [int(x) for x in tree.xpath('.//div[@class="pagination__list"]/a/span/text()') if x.isdigit()])

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//ul[@class="grid"]/li[@class="grid__item"]/div')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1

            image = video_tree_data.xpath('./a/div[@class="item__image"]/img')
            assert len(image) == 1
            image = image[0].attrib['data-src'] \
                if 'data-src' in image[0].attrib else image[0].attrib['src']

            video_length = video_tree_data.xpath('./a/div[@class="item__counter"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            special_emojis = video_tree_data.xpath('./a/div[@class="item__reactions emoji emoji--sm"]/'
                                                   '/div[@class="emoji__item"]/div[@class="emoji__title"]')
            additional_data = {'special_descriptions': [x.text for x in special_emojis]}

            rating = video_tree_data.xpath('./div[@class="item__description"]/div[@class="item__line"]/'
                                           'div[@class="item__rate"]/span')
            rating = int(rating[0].text) if len(rating) == 1 else 0

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=link[0].attrib['title'],
                                                  image_link=image,
                                                  rating=rating,
                                                  duration=self._format_duration(video_length),
                                                  additional_data=additional_data,
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
        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            params.update(parse_qs(page_filter.sort_order.value))
        if page_filter.added_before.value is not None:
            params.update(parse_qs(page_filter.added_before.value))
        if page_filter.length.value is not None:
            params.update(parse_qs(page_filter.length.value))

        if page_number is not None and page_number != 1:
            split_url.append(str(page_number))
        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        if true_object.object_type == PornCategories.SEARCH_MAIN and len(page_request.history) > 0:
            # We have a category, thus we update the search element's url.
            page_data.url = page_request.url
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))


if __name__ == '__main__':
    # category_id = IdGenerator.make_id('/tag/mom')
    category_id = IdGenerator.make_id('/tag/wife')
    porn_star_id = IdGenerator.make_id('/pornstar/asa+akira')
    module = SexU()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['porn_stars']['obj'], (porn_star_id, ), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
