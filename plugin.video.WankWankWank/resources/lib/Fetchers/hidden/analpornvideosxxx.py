# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote_plus

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, VideoNode, \
    VideoSource
from ..catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter

# json
from ..tools.text_json_manioulations import prepare_json_from_not_formatted_text

# Generator id
from ..id_generator import IdGenerator


class AnalPornVideosXXX(PornFetcher):
    # todo: add live cams...
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.analpornvideos.xxx/categories/alphabetical/',
            PornCategories.PORN_STAR_MAIN: 'https://www.analpornvideos.xxx/models/popularity/',
            PornCategories.CHANNEL_MAIN: 'https://www.analpornvideos.xxx/channels/',
            PornCategories.LATEST_VIDEO: 'https://www.analpornvideos.xxx/latest/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.analpornvideos.xxx/top-rated/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.analpornvideos.xxx/most-viewed/',
            PornCategories.SEARCH_MAIN: 'https://www.analpornvideos.xxx/search/',
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
        return 'https://www.analpornvideos.xxx/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_params = {'sort_order': ((PornFilterTypes.DateOrder, 'Recent videos', 'most-recent'),
                                       (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                       (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                       (PornFilterTypes.LengthOrder, 'By duration', 'long-movies'),
                                       (PornFilterTypes.QualityOrder, 'High definition', 'high-definition'),
                                       (PornFilterTypes.FavorOrder, 'Most favorite', 'mostfavorites'),
                                       ),
                        }
        porn_stars_params = {'sort_order': ((PornFilterTypes.PopularityOrder, 'Videos popularity', 'popularity'),
                                            (PornFilterTypes.ViewsOrder, 'Videos', 'videos'),
                                            (PornFilterTypes.AlphabeticOrder, 'Alphabetic A-Z', 'alphabetical'),
                                            ),
                             }
        search_params = {'sort_order': ((PornFilterTypes.DateOrder, 'Most recent', 'latest'),
                                        (PornFilterTypes.ViewsOrder, 'Most viewed', 'most-viewed'),
                                        (PornFilterTypes.RatingOrder, 'Top rated', 'top-rated'),
                                        ),
                         }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_params,
                                         single_category_args=search_params,
                                         single_porn_star_args=search_params,
                                         single_channel_args=search_params,
                                         video_args=video_params,
                                         search_args=search_params,
                                         )

    def __init__(self, source_name='AnalPornVideosXXX', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):

        """
        C'tor
        :param source_name: save directory
        """
        super(AnalPornVideosXXX, self).__init__(source_name, source_id, store_dir, data_dir, source_type,
                                                use_web_server, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_obect(category_data,
                                                 './/div[@class="thumbs ctgs"]/div[@class="thumb"]/'
                                                 'div[@class="thumb-content"]/a',
                                                 PornCategories.CATEGORY)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_obect(porn_star_data,
                                                 './/div[@class="thumbs models"]/div[@class="thumb"]/'
                                                 'div[@class="thumb-content"]/a',
                                                 PornCategories.PORN_STAR)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        channels = tree.xpath('.//div[@class="thumbs playlists"]/div[@class="thumb"]/div[@class="thumb-content"]')
        res = []
        for channel in channels:
            link_data = channel.xpath('./a')
            link = link_data[0].attrib['href']

            title_data = channel.xpath('./span[@class="caption"]/span[@class="name"]')
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ))

        channel_data.add_sub_objects(res)
        return res

    def _update_available_base_obect(self, category_data, xpath, object_type):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link = category.attrib['href']
            image = category.xpath('./span[@class="preview"]/img')
            image = image[0].attrib['src'] if len(image) > 0 else None

            title_data = category.xpath('./span[@class="caption"]/span[@class="name"]')
            assert len(title_data) == 1
            title = self._clear_text(title_data[0].text)

            number_of_videos = category.xpath('./span[@class="caption"]/span[@class="count"]')
            number_of_videos = \
                int(re.findall(r'\d+', number_of_videos[0].text)[0]) if len(number_of_videos) > 0 else None

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=object_type,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
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
        tmp_request = self.session.get(video_data.url, headers=headers)
        assert tmp_request.ok
        request_data = re.findall(r'(?:var flashvars = )({.*?})(?:;)', tmp_request.text, re.DOTALL)
        assert len(request_data) == 1
        request_data = prepare_json_from_not_formatted_text(request_data[0])
        # request_data = re.sub(r'[\r\n\t]*', '', request_data[0])
        # request_data = re.sub(r'(\w+: )', lambda x: '\'' + x[0][:-2] + '\': ', request_data)
        # request_data = re.sub(r'\'', '"', request_data)
        # request_data = json.loads(request_data)
        assert len(request_data) > 0
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
        if category_data.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.CHANNEL_MAIN):
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
        return [int(x.text) for x in (tree.xpath('.//div[@class="pagination"]/div/a') +
                                      tree.xpath('.//div[@class="pagination"]/div/a/span'))
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumbs videos"]/div[@class="thumb"]/div[@class="thumb-content"]/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./span[@class="preview"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            title = image_data[0].attrib['alt']
            flip_images = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                           for d in range(1, int(re.findall(r'(\d+)(?:\)$)',
                                                            image_data[0].attrib['onmouseover'])[0]) + 1)]

            rating = video_tree_data.xpath('./span[@class="preview"]/span[@class="rating"]')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].text)

            number_of_views = video_tree_data.xpath('./span[@class="desc"]/span[@class="views"]')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            added_before = video_tree_data.xpath('./span[@class="desc"]/span[@class="data"]')
            assert len(added_before) == 1
            added_before = added_before[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  rating=rating,
                                                  number_of_views=number_of_views,
                                                  added_before=added_before,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')

        if page_number is not None and page_number != 1 and split_url[-1].isdigit():
            split_url.pop(-1)

        if true_object.object_type in (PornCategories.PORN_STAR_MAIN, PornCategories.CATEGORY,
                                       PornCategories.PORN_STAR, PornCategories.CHANNEL):
            sort_order = page_filter.sort_order
            split_url[-2] = sort_order.value
        elif true_object.object_type == PornCategories.SEARCH_MAIN:
            sort_order = page_filter.sort_order
            split_url.insert(-1, sort_order.value)

        if page_number is not None and page_number != 1:
            split_url.insert(-1, str(page_number))

        fetch_base_url = '/'.join(split_url)
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
    module = AnalPornVideosXXX()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=False)
