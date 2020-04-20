# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urlparse, urljoin

# Regex
import re

# Warnings
import warnings

# M3U8
import m3u8

# External fetchers
from ..tools.external_fetchers import ExternalFetcher

# Generator id
from ..id_generator import IdGenerator

# Nodes
from ..catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, \
    VideoSource, VideoNode, VideoTypes
from ..catalogs.porn_catalog import PornCategories


class VePorns(PornFetcher):
    @property
    def video_request_url(self):
        return urljoin(self.base_url, '/ajax.php')

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/pornstars'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-videos'),
            PornCategories.UPCOMING_VIDEO: urljoin(self.base_url, '/upcoming'),
            PornCategories.RANDOM_VIDEO: urljoin(self.base_url, '/random'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/porn/'),
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
        return 'http://www.veporns.com/'

    def __init__(self, source_name='VePorns', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(VePorns, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)
        self.external_fetchers = ExternalFetcher(session=self.session, user_agent=self.user_agent,
                                                 parser=self.parser)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="box categoriesText"]/ul/li/a')
        res = []
        for category in categories:
            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=category.text,
                                                  object_type=PornCategories.CATEGORY,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)

        res.sort(key=lambda x: x.title)
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = tree.xpath('.//ul[@class="listContent stars size200"]/li')
        res = []
        for porn_star in porn_stars:
            link_data = porn_star.xpath('./a')
            assert len(link_data) == 1

            image = re.findall(r'(?:url\()(.*?)(\))', link_data[0].attrib['style'])[0]

            rating = porn_star.xpath('./span[@class="rating"]/span')
            assert len(rating) == 1
            rating = int(self._clear_text(rating[0].tail))

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(self.base_url, link_data[0].attrib['href']),
                                                  title=link_data[0].attrib['title'],
                                                  image_link=image,
                                                  rating=rating,
                                                  object_type=PornCategories.PORN_STAR,
                                                  super_object=porn_star_data,
                                                  )
            res.append(object_data)

        porn_star_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        tmp_tree = self.parser.parse(tmp_request.text)
        commands = [x for x in tmp_tree.xpath('.//div[@class="r"]/a') if 'onclick' in x.attrib]
        res = []
        for command in commands:
            arguments = re.findall(r'(?:\()(.*)(?:\))', command.attrib['onclick'])
            assert len(arguments) == 1
            thumb, theme, video, vid, catid, tip, server = arguments[0].replace('\'', '').split(',')
            headers = {
                'Accept': '*/*',
                'Cache-Control': 'max-age=0',
                'Host': self.host_name,
                'Referer': video_data.url,
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
            params = {
                'page': 'video_play',
                'thumb': thumb,
                'theme': theme,
                'video': video,
                'id': vid,
                'catid': catid,
                'tip': tip,
                'server': server,
            }
            tmp_request = self.session.get(self.video_request_url, headers=headers, params=params)
            tmp_tree = self.parser.parse(tmp_request.text)
            video_links = tmp_tree.xpath('.//iframe/@src')
            if urlparse(video_links[0]).hostname == 'woof.tube':
                res.extend([VideoSource(link=x[0], resolution=x[1])
                            for x in self.external_fetchers.get_video_link_from_woof_tube(video_links[0])]
                           )
            elif urlparse(video_links[0]).hostname == 'gounlimited.to':
                res.extend([VideoSource(link=x[0], resolution=x[1])
                            for x in self.external_fetchers.get_video_link_from_gotounlimited(video_links[0])]
                           )
            elif urlparse(video_links[0]).hostname == 'vidlox.me':
                tmp_res = self.external_fetchers.get_video_link_from_vidlox(video_links[0], video_data.url)
                for link, resolution in tmp_res:
                    file_type = re.findall(r'(?:\.)(\w+$)', link)[0]
                    if file_type == 'm3u8':
                        headers = {
                            'Accept': '*/*',
                            # 'Accept-Encoding': 'gzip, deflate, br',
                            'Cache-Control': 'max-age=0',
                            # 'Referer': self.shows_url,
                            'Sec-Fetch-Mode': 'cors',
                            'Sec-Fetch-Site': 'same-origin',
                            # 'Sec-Fetch-User': '?1',
                            'User-Agent': self.user_agent,
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                        req = self.session.get(link, headers=headers)
                        video_m3u8 = m3u8.loads(req.text)
                        video_playlists = video_m3u8.playlists
                        if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
                            video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)

                        video_objects = [VideoSource(link=urljoin(link, x.uri),
                                                     video_type=VideoTypes.VIDEO_SEGMENTS,
                                                     quality=x.stream_info.bandwidth,
                                                     resolution=x.stream_info.resolution[1],
                                                     codec=x.stream_info.codecs)
                                         for x in video_playlists]

                        res.extend(video_objects)
                    elif file_type == 'mp4':
                        res.append(VideoSource(link=link, resolution=int(re.findall(r'\d+', resolution)[0])))
                    else:
                        warnings.warn('Unsupported file type {ft} for source vidlox.me')

            else:
                warnings.warn('Unknown Server {s}'.format(s=urlparse(video_links[0]).hostname))
        res.sort(key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=res)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        page_request = self._get_object_request_no_exception_check(category_data) if fetched_request is None \
            else fetched_request
        if not self._check_is_available_page(category_data, page_request):
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
        return [int(re.findall(r'(?:p=)(\d+)', x)[0]) for x in tree.xpath('.//p[@class="sayfalama"]/a/@href')
                if len(re.findall(r'(?:p=)(\d+)', x)) > 0] + \
               [int(re.findall(r'(\d+)(?:/*$)', x)[0]) for x in tree.xpath('.//p[@class="sayfalama"]/a/@href')
                if len(re.findall(r'(\d+)(?:/*$)', x)) > 0]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        res = []
        videos = tree.xpath('.//ul[@class="listContent stars sizeDVDLarge"]/li[@class="dvd-new"]')
        if len(videos) > 0:
            # option 1
            for video_tree_data in videos:
                link = video_tree_data.xpath('./a')
                assert len(link) == 1
                image = re.findall(r'(?:url\()(.*)(?:\))', link[0].attrib['style'])[0]

                title = video_tree_data.xpath('./span[@class="title"]/a')
                assert len(title) == 1
                title = title[0].attrib['title']

                uploader = video_tree_data.xpath('./span[@class="date"]/a')
                additional_data = {'uploader': {'url': uploader[0].attrib['href'], 'name': uploader[0].text}} \
                    if len(uploader) > 0 else None

                added_before = video_tree_data.xpath('./span[@class="datetime"]/text()')
                assert len(added_before) == 1

                number_of_viewers = video_tree_data.xpath('./span[@class="views"]/span')
                assert len(number_of_viewers) == 1
                number_of_viewers = self._clear_text(number_of_viewers[0].tail)

                res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                    obj_id=link[0].attrib['href'],
                                                    url=urljoin(self.base_url, link[0].attrib['href']),
                                                    title=title,
                                                    image_link=image,
                                                    added_before=added_before[0],
                                                    number_of_views=number_of_viewers,
                                                    additional_data=additional_data,
                                                    object_type=PornCategories.VIDEO,
                                                    super_object=page_data,
                                                    ))
            page_data.add_sub_objects(res)
            return res
        else:
            # Option 2
            videos = tree.xpath('.//ul[@class="listContent video size232"]/li/ul[@class="listContent video size232"]/'
                                'li')
            for video_tree_data in videos:
                link = video_tree_data.xpath('./a')
                assert len(link) == 1
                title = link[0].attrib['title']

                image_data = video_tree_data.xpath('./img')
                assert len(image_data) == 1
                image = image_data[0].attrib['src']

                number_of_viewers = video_tree_data.xpath('./span[@class="views"]/span')
                assert len(number_of_viewers) == 1
                number_of_viewers = int(self._clear_text(number_of_viewers[0].tail))

                video_length = video_tree_data.xpath('./a/span[@class="duration"]')
                assert len(video_length) == 1

                res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                    obj_id=link[0].attrib['href'],
                                                    url=urljoin(self.base_url, link[0].attrib['href']),
                                                    title=title,
                                                    image_link=image,
                                                    number_of_views=number_of_viewers,
                                                    duration=self._format_duration(video_length[0].text),
                                                    object_type=PornCategories.VIDEO,
                                                    super_object=page_data,
                                                    ))
            page_data.add_sub_objects(res)
            return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
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
        split_url = fetch_base_url.split('/')
        if page_number is not None and page_number != 1:
            if true_object.object_type == PornCategories.LATEST_VIDEO:
                if split_url[-2] == 'videos':
                    # We override the previous value
                    split_url[-1] = str(page_number)
                else:
                    split_url.insert(-1, 'videos')
                    split_url[-1] = str(page_number)
            elif true_object.object_type == PornCategories.PORN_STAR_MAIN:
                params['p'] = page_data.page_number
                params['l'] = ''
            else:
                if split_url[-1].isdigit():
                    split_url[-1] = str(page_number)
                else:
                    split_url.append(str(page_number))
        program_fetch_url = '/'.join(split_url)
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '{q}'.format(q=query.replace(' ', '-'))


if __name__ == '__main__':
    cat_id = IdGenerator.make_id('/category/fakeagent/1')
    module = VePorns()
    # module.get_available_categories()
    # module.download_object(None, cat_id, verbose=1)
    module.download_category_input_from_user(use_web_server=True)
