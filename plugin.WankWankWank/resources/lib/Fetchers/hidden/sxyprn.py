# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher, PornValueError

# Internet tools
from .. import urljoin, parse_qs

# Regex
import re

# JSON
import json

# Generator id
from ..id_generator import IdGenerator

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, PornCatalogPageNode, \
    VideoSource, VideoNode
from ..catalogs.porn_catalog import PornCategories, PornFilter, PornFilterTypes


class SexyPorn(PornFetcher):
    main_js = 'https://sxyprn.com/js/main.js?38'

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://sxyprn.com/',
            PornCategories.PORN_STAR_MAIN: 'https://sxyprn.com/pornstars/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://sxyprn.com/popular/top-viewed.html',
            PornCategories.POPULAR_VIDEO: 'https://sxyprn.com/popular/top-pop.html',
            PornCategories.ORGASMIC_VIDEO: 'https://sxyprn.com/orgasm/',
            PornCategories.SEARCH_MAIN: 'https://sxyprn.com/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.ORGASMIC_VIDEO: PornFilterTypes.OrgasmicOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://sxyprn.com/'

    @property
    def number_of_videos_per_video_page(self):
        """
        Base site url.
        :return:
        """
        return 30  # 20

    @property
    def number_of_videos_per_blog_page(self):
        """
        Base site url.
        :return:
        """
        return 20  # 20

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        # todo: Single category has some weird filters. To check later...
        single_category_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Latest', 'sm=latest'),
                                                  (PornFilterTypes.ViewsOrder, 'Views', 'sm=views'),
                                                  (PornFilterTypes.RatingOrder, 'Views', 'sm=rating'),
                                                  (PornFilterTypes.OrgasmicOrder, 'Orgasmic', 'sm=orgasmic'),
                                                  ),
                                   }
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Latest', 'sm=latest'),
                                        (PornFilterTypes.TrendingOrder, 'Trending', 'sm=trending'),
                                        (PornFilterTypes.ViewsOrder, 'Views', 'sm=views'),
                                        (PornFilterTypes.OrgasmicOrder, 'Orgasmic', 'sm=orgasmic'),
                                        ),
                         }

        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         single_category_args=single_category_filters,
                                         single_porn_star_args=video_filters,
                                         video_args=video_filters,
                                         search_args=video_filters,
                                         )

    def __init__(self, source_name='SxyPrn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SexyPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, session_id)
        headers = {
            'Accept': '*.*',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent,
        }
        main_server = self.session.get(self.main_js, headers=headers)
        try:
            self.server_number = re.findall(r'(?:tmp\[1\]\+= ")(\d+)(?:")', main_server.text)[0]
        except IndexError:
            raise PornValueError('Wrong server number')

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="block_header"]/a[@class="tdn"]')
        res = []
        for category in categories:
            image = category.xpath('./div[@class="htag_el"]/img/@src')
            assert len(image) == 1

            title = category.xpath('./div[@class="htag_el"]/span[@class="htag_el_tag"]/text()')
            assert len(title) == 1

            number_of_videos = category.xpath('./div[@class="htag_el"]/span[@class="htag_el_count"]/text()')
            assert len(number_of_videos) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(category_data.url, category.attrib['href']),
                                                  title=title[0],
                                                  image_link=urljoin(category_data.url, image[0]),
                                                  number_of_videos=int(re.findall(r'\d+', number_of_videos[0])[0]),
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = tree.xpath('.//div[@id="pstars_container"]/a')
        res = []
        for porn_star in porn_stars:
            title = porn_star.xpath('./div/text()')
            assert len(title) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=porn_star.attrib['href'],
                                                  url=urljoin(porn_star_data.url, porn_star.attrib['href']),
                                                  title=title[0],
                                                  object_type=PornCategories.PORN_STAR,
                                                  super_object=porn_star_data,
                                                  )
            res.append(object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def _add_category_sub_pages(self, category_data, sub_object_type, page_request=None, clear_sub_elements=True):
        """
        Adds category sub pages.
        :param category_data: Category data object (PornCatalogCategoryNode).
        :param sub_object_type: Sub object type.
        :param page_request: Page request if such exist. In case it doesn't exist we fetch the object's url.
        :param clear_sub_elements: Flag that indicates whether we clear previous sub elements.
        :return:
        """
        if category_data.object_type == PornCategories.PORN_STAR_MAIN:
            if clear_sub_elements is True:
                category_data.clear_sub_objects()
            return self._add_porn_star_sub_pages(category_data, sub_object_type)
        else:
            return super(SexyPorn, self)._add_category_sub_pages(category_data, sub_object_type, page_request,
                                                                 clear_sub_elements)

    def _add_porn_star_sub_pages(self, porn_star_data, sub_object_type):
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_star_page_links = tree.xpath('.//div[@id="center_control"]/a')
        porn_star_page_names = tree.xpath('.//div[@id="center_control"]/a/div/text()')
        assert len(porn_star_page_links) == len(porn_star_page_names)
        new_pages = [PornCatalogPageNode(catalog_manager=self.catalog_manager,
                                         obj_id=(IdGenerator.id_to_original_str(porn_star_data.id), name),
                                         title='{c} | Letter {p}'.format(c=porn_star_data.title, p=name),
                                         url=urljoin(porn_star_data.url, link.attrib['href']),
                                         page_number=None,
                                         raw_data=porn_star_data.raw_data,
                                         object_type=sub_object_type,
                                         super_object=porn_star_data,
                                         )
                     for i, (link, name) in enumerate(zip(porn_star_page_links, porn_star_page_names))]
        porn_star_data.add_sub_objects(new_pages)

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        video_id = re.findall(r'(?:/)(\w+)(?:.html)', video_data.url)[0]
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)

        request_data = tmp_tree.xpath('.//span[@class="vidsnfo"]/@data-vnfo')
        assert len(request_data) == 1
        new_video_data = json.loads(request_data[0])
        # suffix = re.findall(r'(?:/cdn/c)(\d*)', new_video_data[video_id])[0]
        video_links = [VideoSource(link=urljoin(self.base_url,
                                                re.sub('^/cdn/', '/cdn{n}/'.format(n=self.server_number),
                                                       new_video_data[video_id])))]

        video_header = {
            'Accept': '*/*',
            'Accept-Encoding': 'identity;q=1, *;q=0',
            # 'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Range': 'bytes=0-',
            'Referer': video_data.url,
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        }

        return VideoNode(video_sources=video_links, headers=video_header)

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
        return [int(x) for x in tree.xpath('.//div[@id="center_control"]/a/div/text()')
                if x.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        if self._is_blog_format_page(page_data.url):
            return self._get_videos_data_from_blog_page(page_data, tree)
        else:
            return self._get_videos_data_from_regular_page(page_data, tree)

    def _get_videos_data_from_regular_page(self, page_data, tree):
        error_message = tree.xpath('.//span[@class="page_message"]')
        if len(error_message) == 1 and error_message[0].text == 'Nothing Found. See More...':
            res = []
            page_data.add_sub_objects(res)
            return res

        videos = tree.xpath('.//div[@class="post_el_small"]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1

            img = video_tree_data.xpath('.//div[@class="post_vid_thumb"]//img/@src')
            if len(img) != 1:
                # We don't have the video link...
                continue

            preview = video_tree_data.xpath('.//div[@class="post_vid_thumb"]//video/@src')
            preview = preview[0] if len(preview) > 0 else None

            video_length = video_tree_data.xpath('.//div[@class="post_vid_thumb"]/span[@class="duration_small"]/'
                                                 'text()')
            if len(video_length) != 1:
                # We have removed content...
                continue
            try:
                video_length = self._format_duration(video_length[0])
            except ValueError:
                video_length = None

            is_hd = video_tree_data.xpath('.//div[@class="post_vid_thumb"]/span[@class="shd_small"]/text()')

            # Text
            additional_categories = video_tree_data.xpath('.//div[@class="post_text"]/a')
            additional_data = {'additional_categories': [{'name': x.text,
                                                          'url': urljoin(page_data.url, x.attrib['href'])}
                                                         for x in additional_categories]
                               } if len(additional_categories) > 0 else {}

            added_before = video_tree_data.xpath('.//div[@class="post_control"]//div[@class="post_control_time"]/'
                                                 'span/text()')
            assert len(added_before) == 1

            number_of_views = video_tree_data.xpath('.//div[@class="post_control"]//div[@class="post_control_time"]'
                                                    '/strong')
            assert len(number_of_views) == 1

            title = video_tree_data.xpath('.//div[@class="post_control"]/a/@title')
            assert len(title) == 1

            likes = (video_tree_data.xpath('.//div[@class="post_control"]/'
                                           'span[@class="vid_like_blog small_post_control"]/text()') +
                     video_tree_data.xpath('.//div[@class="post_control"]/'
                                           'span[@class="vid_like_blog_hl small_post_control"]/text()')
                     )
            assert len(likes) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=title[0],
                                                  image_link=urljoin(page_data.url, img[0]),
                                                  preview_video_link=urljoin(page_data.url, preview),
                                                  is_hd=len(is_hd) > 0 and is_hd[0] == 'HD',
                                                  duration=video_length,
                                                  added_before=added_before[0],
                                                  number_of_views=number_of_views[0].tail,
                                                  additional_data=additional_data,
                                                  rating=likes[0],
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_videos_data_from_blog_page(self, page_data, tree):
        videos = tree.xpath('.//div[@class="post_el_wrap"]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.xpath('./a')
            assert len(link) == 1

            img = video_tree_data.xpath('.//div[@class="post_vid_thumb"]//img/@src')
            if len(img) != 1:
                # We don't have the video link...
                continue

            preview = video_tree_data.xpath('.//div[@class="post_vid_thumb"]//video/@src')
            preview = urljoin(page_data.url, preview[0]) if len(preview) > 0 else None

            additional_categories = video_tree_data.xpath('.//div[@class="post_vid_thumb"]/a[2]')
            additional_data = {'additional_categories': [{'name': additional_categories[0].xpath('./span/text()')[0],
                                                          'url': additional_categories[0].attrib['href']}]
                               } if len(additional_categories) > 0 else {}

            video_length = video_tree_data.xpath('.//div[@class="post_vid_thumb"]/span[@class="duration_small"]/'
                                                 'text()')
            if len(video_length) != 1:
                # We have removed content...
                continue
            try:
                video_length = self._format_duration(video_length[0])
            except ValueError:
                video_length = None

            is_hd = video_tree_data.xpath('.//div[@class="post_vid_thumb"]/span[@class="shd_small"]/text()')

            # Text
            additional_categories = video_tree_data.xpath('.//div[@class="post_text "]/a')
            for additional_category in additional_categories:
                if 'additional_categories' not in additional_data:
                    additional_data['additional_categories'] = []
                additional_data['additional_categories'].append(
                    {'name': additional_category.text, 'url': additional_category.attrib['href']}
                )

            added_before = video_tree_data.xpath('.//div[@class="post_control"]//div[@class="post_control_time"]/'
                                                 'span/text()')
            assert len(added_before) == 1

            number_of_views = video_tree_data.xpath('.//div[@class="post_control"]//div[@class="post_control_time"]'
                                                    '/strong')
            assert len(number_of_views) == 1

            title = video_tree_data.xpath('.//div[@class="post_control"]/a/@title')
            assert len(title) == 1

            likes = video_tree_data.xpath('.//div[@class="post_control"]/'
                                          'span[@class="vid_like_blog small_post_control"]/text()')
            assert len(likes) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=title[0],
                                                  image_link=urljoin(page_data.url, img[0]),
                                                  preview_video_link=preview,
                                                  is_hd=len(is_hd) > 0 and is_hd[0] == 'HD',
                                                  duration=video_length,
                                                  added_before=added_before[0],
                                                  number_of_views=number_of_views[0].tail,
                                                  additional_data=additional_data,
                                                  rating=likes[0],
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    @staticmethod
    def _is_blog_format_page(page_url):
        url_prefix = page_url.split('?')[0]
        url_prefix = re.sub(r'/*$', '', url_prefix)
        split_url_prefix = url_prefix.split('/')
        return len(re.findall(r'^\d+.html$', split_url_prefix[-1])) > 0

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
            # 'Referer': self.base_url,
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            params.update(parse_qs(page_filter.sort_order.value))
        if page_number is not None and page_number != 1:
            if true_object.object_type in (PornCategories.PORN_STAR, PornCategories.SEARCH_MAIN):
                params['page'] = (page_number - 1) * self.number_of_videos_per_video_page
            else:
                if split_url[-1].isdigit():
                    split_url.pop()
                if len(re.findall(r'\d+.html', split_url[-1])) > 0:
                    # We have a blog page
                    split_url[-1] = \
                        '{n}.html'.format(n=(page_number - 1) * self.number_of_videos_per_blog_page)
                else:
                    split_url.append('{p}'.format(p=(page_number - 1) * self.number_of_videos_per_video_page))
        program_fetch_url = '/'.join(split_url)
        if page_data.url[-3:] == '&ht':
            params['ht'] = ''
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}.html'.format(q=re.sub(r'[;/?:@&=+$]+', '-', query))


if __name__ == '__main__':
    tag_id = IdGenerator.make_id('/blog/BigTits/0.html?sm=orgasmic&ht')
    porn_star_id = IdGenerator.make_id('/Bozena.html?ps&sm=orgasmic')
    module = SexyPorn()
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['porn_stars']['obj'], (porn_star_id, ), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=True)
