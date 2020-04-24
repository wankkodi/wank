# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote_plus

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, VideoSource
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# Generator id
from ..id_generator import IdGenerator
from ..tools.text_json_manioulations import prepare_json_from_not_formatted_text


class DaChix(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/pornstars'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/videos'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/videos?sort=rated'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/videos?sort=viewed'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, '/videos?sort=popular'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/videos?sort=longest'),
            PornCategories.RECOMMENDED_VIDEO: urljoin(self.base_url, '/videos?sort=editorchoice'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/s'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.RECOMMENDED_VIDEO: PornFilterTypes.RecommendedOrder,
        }

    @property
    def possible_empty_pages(self):
        """
        Defines whether it is possible to have empty pages in the site.
        :return:
        """
        return True

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.dachix.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        porn_stars_filter = {'sort_order': [(PornFilterTypes.NumberOfVideosOrder, 'Most Medias', None),
                                            (PornFilterTypes.RatingOrder, 'Top Rated', 'rated'),
                                            (PornFilterTypes.ViewsOrder, 'Most Viewed', 'viewed'),
                                            (PornFilterTypes.PopularityOrder, 'Most Popular', 'popular'),
                                            (PornFilterTypes.AlphabeticOrder, 'Alphabetical', 'alphabetical'),
                                            ],
                             }
        single_porn_stars_filter = {'sort_order': [(PornFilterTypes.RecommendedOrder, 'Featured', None),
                                                   (PornFilterTypes.DateOrder, 'Most Recent', 'recent'),
                                                   (PornFilterTypes.RatingOrder, 'Top Rated', 'rated'),
                                                   (PornFilterTypes.ViewsOrder, 'Most Viewed', 'viewed'),
                                                   (PornFilterTypes.PopularityOrder, 'Most Popular', 'popular'),
                                                   (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                                   ],
                                    }
        search_filter = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Most Relevant', None),
                                        (PornFilterTypes.DateOrder, 'Most Recent', 'recent'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'rated'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'viewed'),
                                        (PornFilterTypes.PopularityOrder, 'Most Popular', 'popular'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        ],
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filter,
                                         single_category_args=single_porn_stars_filter,
                                         single_porn_star_args=single_porn_stars_filter,
                                         search_args=search_filter,
                                         )

    def __init__(self, source_name='DaChix', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(DaChix, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="listing-categories"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            image_data = category.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./span[@class="media-count"]/a[@class="vid"]')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].text)[0]) if len(number_of_videos) == 1 else None

            number_of_photos = category.xpath('./span[@class="media-count"]/a[@class="gal"]')
            number_of_photos = \
                int(re.findall(r'\d+', number_of_photos[0].text)[0]) if len(number_of_photos) == 1 else None

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link) + '/videos',
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               number_of_photos=number_of_photos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = tree.xpath('.//div[@class="main-sectioncontent"]/a')
        res = []
        for porn_star in porn_stars:
            link = porn_star.attrib['href']
            title = porn_star.attrib['title']

            image_data = porn_star.xpath('./span[@class="pic"]')
            assert len(image_data) == 1
            image = image_data[0].attrib['content']

            rating = porn_star.xpath('./span[@class="stats black_gradient"]/span[@class="rating"]/span')
            assert len(rating) == 1
            rating = re.findall(r'\d.*%', rating[0].attrib['style'])[0]

            number_of_videos = porn_star.xpath('./span[@class="stats black_gradient"]/span[@class="r"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            number_of_views = porn_star.xpath('./span[@class="stats black_gradient"]/span')
            assert len(number_of_views) > 0
            number_of_views = int(re.sub(r'[a-zA-Z, ]', '', number_of_views[-1].text))

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link) + '/videos',
                                               image_link=image,
                                               title=title,
                                               rating=rating,
                                               number_of_videos=number_of_videos,
                                               number_of_views=number_of_views,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        # tree = self.parser.parse(tmp_request.text)
        # videos = [VideoSource(link=x.attrib['src']) for x in tree.xpath('.//video/source')]
        raw_data = re.findall(r'(?:crakPlayer\()(.*?)(?:\))', tmp_request.text, re.DOTALL)
        raw_data = prepare_json_from_not_formatted_text(raw_data[0])
        videos = sorted((VideoSource(link=url, codec=codec, resolution=k.split('x')[0])
                         for k, v in raw_data['sizes'].items() for codec, url in v.items()),
                        key=lambda x: x.resolution, reverse=True)
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
        return [int(re.findall(r'(?:p=)(\d+)', x.attrib['href'])[0])
                for x in tree.xpath('.//div[@class="main-sectionpaging"]/a')
                if 'href' in x.attrib and len(re.findall(r'(?:p=)(\d+)', x.attrib['href'])) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = [x for x in tree.xpath('.//div[@class="main-sectioncontent"]/span')
                  if 'thumb_container_box' in x.attrib['class']]
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a[@class="thumb_container video"]')
            if len(link_data) != 1:
                continue
            link = link_data[0].attrib['href']
            title = self._clear_text(link_data[0].attrib['title'])

            author_data = video_tree_data.xpath('./a[@class="thumb_sponsor"]')
            assert len(author_data) == 1
            additional_data = {'author': (author_data[0].xpath('./span')[0].text
                                          if len(author_data[0].xpath('./span')) > 0 else author_data[0].text),
                               'url': author_data[0].attrib['href']}

            image_data = video_tree_data.xpath('./a[@class="thumb_container video"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            flip_images = (image_data[0].attrib['data-thumbs'][1:-1].split(',')
                           if 'data-thumbs' in image_data[0].attrib
                              and len(image_data[0].attrib['data-thumbs'][1:-1]) > 0 else None)
            if flip_images is None:
                # We give another try...
                if 'json' in image_data[0].attrib:
                    flip_images = prepare_json_from_not_formatted_text(image_data[0].attrib['json'])
            if flip_images is not None:
                flip_images = [re.sub(r'[\\"]', '', x) for x in flip_images]
            if len(image) == 0:
                image = flip_images[0] if flip_images is not None else None

            is_hd = video_tree_data.xpath('./a[@class="thumb_container video"]/span[@class="hd_icon"]')
            is_hd = len(is_hd) > 0

            video_length = video_tree_data.xpath('./a[@class="thumb_container video"]/span[@class="media_info"]/'
                                                 'span[@class="lenght_pics"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  is_hd=is_hd,
                                                  duration=self._format_duration(video_length),
                                                  additional_data=additional_data,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        if (
                true_object.object_type in (PornCategories.PORN_STAR_MAIN, PornCategories.PORN_STAR,
                                            PornCategories.CATEGORY, PornCategories.SEARCH_PAGE) and
                page_filter.sort_order.value is not None
        ):
            params['sort'] = page_filter.sort_order.value
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
            params['p'] = [page_number]
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw number, i.e. '7m:58s'.
        :return:
        """
        final_duration = 0
        hours = re.findall(r'(\d+)(?: *h)', raw_duration)
        minutes = re.findall(r'(\d+)(?: *m)', raw_duration)
        seconds = re.findall(r'(\d+)(?: *s)', raw_duration)
        if len(hours) > 0:
            final_duration += 3600 * int(hours[0])
        if len(minutes) > 0:
            final_duration += 60 * int(minutes[0])
        if len(seconds) > 0:
            final_duration += int(seconds[0])
        return final_duration

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '/{q}'.format(q=quote_plus(query.replace(' ', '-')))


class DeviantClip(DaChix):
    @property
    def object_urls(self):
        tmp_res = super(DeviantClip, self).object_urls
        tmp_res.pop(PornCategories.PORN_STAR_MAIN)
        return tmp_res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.deviantclip.com/'

    def __init__(self, source_name='DeviantClip', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(DeviantClip, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                          session_id)


class DaGay(DeviantClip):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'http://www.dagay.com/'

    def __init__(self, source_name='DaGay', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(DaGay, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                    session_id)


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    module = DaChix()
    # module = DeviantClip()
    # module = DaGay()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=False)
