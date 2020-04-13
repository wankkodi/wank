# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote_plus

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes

# JSON
from ..tools.text_json_manioulations import prepare_json_from_not_formatted_text

# Generator id
from ..id_generator import IdGenerator


class Netfapx(PornFetcher):
    max_flip_image = 10
    video_flix_template = 'https://netfapx.com/preview-thumb2/ID{id}_{i}.jpg'

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return False

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://netfapx.com/categories/',
            PornCategories.TAG_MAIN: 'https://netfapx.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://netfapx.com/pornstar',
            PornCategories.LATEST_VIDEO: 'https://netfapx.com/',
            PornCategories.POPULAR_VIDEO: 'https://netfapx.com/?orderby=popular',
            PornCategories.TOP_RATED_VIDEO: 'https://netfapx.com/?orderby=faps',
            PornCategories.RANDOM_VIDEO: 'https://netfapx.com/?orderby=random',
            PornCategories.SEARCH_MAIN: 'https://netfapx.com/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.FavorOrder,
            PornCategories.RANDOM_VIDEO: PornFilterTypes.RandomOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://netfapx.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        porn_stars_filters = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Popular', 'popular'),
                                             (PornFilterTypes.DateOrder, 'Newest', 'recently-added'),
                                             (PornFilterTypes.FavorOrder, 'Faps', 'faps'),
                                             (PornFilterTypes.RatingOrder, 'Ranking', 'ranking'),
                                             (PornFilterTypes.RandomOrder, 'Random', 'random-star'),
                                             ),
                              }
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Newest', 'newest'),
                                        (PornFilterTypes.PopularityOrder, 'Popular', 'popular'),
                                        (PornFilterTypes.FavorOrder, 'Faps', 'faps'),
                                        (PornFilterTypes.RandomOrder, 'Random', 'random'),
                                        ),
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filters,
                                         single_category_args=video_filters,
                                         single_porn_star_args=video_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='Netfapx', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Netfapx, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data, './/div[@class="cat-thumb"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available tags.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(tag_data, './/div[@class="infovideo-cat"]/a',
                                                  PornCategories.TAG)

    def _update_available_base_object(self, base_object_data, base_xpath, object_type):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(base_object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(base_xpath)
        res = []
        for category in categories:
            image = category.xpath('./img')
            title = category.attrib['href'].split('/')[-2].title().replace('-', ' ')

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=title,
                                                  image_link=image[0].attrib['src'] if len(image) > 0 else None,
                                                  object_type=object_type,
                                                  super_object=base_object_data,
                                                  )
            res.append(object_data)
        base_object_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = tree.xpath('.//div[@class="boxcontainer"]/article/div')
        res = []
        for porn_star in porn_stars:
            link_data = porn_star.xpath('./div[@class="preview"]/p[@class="thumb"]/a')
            assert len(link_data) == 1

            image_data = porn_star.xpath('./div[@class="preview"]/p[@class="thumb"]/a/img')
            assert len(image_data) == 1
            title = image_data[0].attrib['alt'] if 'alt' in image_data[0].attrib else None

            if title is None:
                title_data = porn_star.xpath('./div[@class="title"]/h3[@class="title-2"]/a')
                assert len(title_data) == 1
                title = title_data[0].attrib['title'] \
                    if 'title' in title_data[0].attrib else self._clear_text(title_data[0].text)

            info_data = porn_star.xpath('./div[@style]/img')
            assert len(info_data) == 4
            number_of_videos = int(self._clear_text(info_data[2].tail))
            additional_data = {'number_of_views': int(''.join(re.findall(r'\d+', info_data[0].tail))),
                               'number_of_faps': int(''.join(re.findall(r'\d+', info_data[1].tail))),
                               'rating': int(self._clear_text(info_data[3].tail)),
                               }
            split_url = urljoin(self.base_url, link_data[0].attrib['href']).split('/')
            split_url[3] = 'videos'
            url = '/'.join(split_url)
            object_data = \
                PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                        obj_id=link_data[0].attrib['href'],
                                        url=url,
                                        title=title,
                                        image_link=image_data[0].attrib['src'] if len(image_data) > 0 else None,
                                        number_of_videos=number_of_videos,
                                        additional_data=additional_data,
                                        object_type=PornCategories.PORN_STAR,
                                        super_object=porn_star_data,
                                        )
            res.append(object_data)
        porn_star_data.add_sub_objects(res)
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
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_url, headers=headers)
        # tmp_tree = self.parser.parse(tmp_request.text)
        # new_video_data = json.loads([x for x in tmp_tree.xpath('.//script/text()') if 'gvideo' in x][0])
        # video_suffix = video_suffix = urlparse(tmp_data['contentUrl']).path
        raw_data = re.findall(r'(?:Clappr.Player\()({.*?})(?:\))', tmp_request.text)
        raw_data = prepare_json_from_not_formatted_text(raw_data[0])
        videos = [VideoSource(link=raw_data['source'])]
        assert len(videos) > 0
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.TAG_MAIN):
            return 1
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        return self._binary_search_max_number_of_pages(category_data)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.split('/')[-2]) for x in tree.xpath('.//div[@class="posts-navigation clearfix "]/a/@href')
                if x.split('/')[-2].isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 1

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//article[@class="pinbox"]/div')
        res = []
        for video_tree_data in videos:
            preview = video_tree_data.xpath('./div[@class="preview"]/div[@class="playpreview"]')
            assert len(preview) == 1
            video_id = preview[0].attrib['id']

            link = video_tree_data.xpath('./div[@class="preview"]/a/@href')
            assert len(link) == 1

            image_data = video_tree_data.xpath('./div[@class="preview"]/a/img')
            assert len(image_data) == 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])
            flip_images = [self.video_flix_template.format(id=video_id, i=i)
                           for i in range(1, self.max_flip_image + 1)]

            title = video_tree_data.xpath('./div[@class="title"]/h3/a/@title')
            assert len(title) == 1

            numeric_data = video_tree_data.xpath('./div[3]/img')
            assert len(numeric_data) == 3
            number_of_views = re.sub(r'(^ *)|( *$)', '', numeric_data[0].tail)
            rating = re.sub(r'(^ *)|( *$)', '', numeric_data[1].tail)
            video_length = re.sub(r'(^ *)|( *$)', '', numeric_data[2].tail)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_id,
                                                  url=link[0],
                                                  title=title[0],
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  duration=self._format_duration(video_length),
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

        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            params['orderby'] = [page_filter.sort_order.value]

        if len(split_url[-1]) > 0:
            split_url.append('')

        if page_number is not None and page_number != 1:
            split_url.insert(-1, 'page')
            split_url.insert(-1, str(page_number))

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


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://netfapx.com/category/big-tits/')
    tag_id = IdGenerator.make_id('https://netfapx.com/tag/babysitter/')
    module = Netfapx()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
