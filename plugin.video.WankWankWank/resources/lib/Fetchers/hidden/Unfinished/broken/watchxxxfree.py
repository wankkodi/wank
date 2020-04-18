# -*- coding: UTF-8 -*-
from porn_fetcher import PornFetcher

# Internet tools
from urllib.parse import urljoin

# Regex
import re

# Generator id
from ..id_generator import IdGenerator

# Nodes
from porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode
from porn_catalog import CategoryMain, ChannelMain, PornStarMain, LatestVideo, TopRatedVideo, MostViewedVideo, \
    LongestVideo, RandomVideo, Category, Video
from video_catalog import VideoNode


class WatchXXXFree(PornFetcher):
    # todo: to add CHANNEL_MAIN, PornStarMain
    @property
    def object_urls(self):
        return {
            CategoryMain: 'https://watchxxxfreeinhd.com/categories/',
            ChannelMain: 'https://watchxxxfreeinhd.com/category/studio/',
            PornStarMain: 'https://watchxxxfreeinhd.com/actress-performes/',
            LatestVideo: 'https://watchxxxfreeinhd.com/?filtre=date&cat=0',
            LongestVideo: 'https://watchxxxfreeinhd.com/?display=tube&filtre=duree',
            MostViewedVideo: 'https://watchxxxfreeinhd.com/?display=tube&filtre=views',
            TopRatedVideo: 'https://watchxxxfreeinhd.com/?display=tube&filtre=rate',
            RandomVideo: 'https://watchxxxfreeinhd.com/?display=tube&filtre=random',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://watchxxxfreeinhd.com/'

    def __init__(self, source_name='VPorn', source_id=0, store_dir='.', data_dir='../Data'):
        """
        C'tor
        :param source_name: save directory
        """
        super().__init__(source_name, source_id, store_dir, data_dir)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self._get_page_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//ul[@class="listing-cat"]/li')
        res = []
        for category in categories:
            link = category.xpath('./a[1]')
            assert len(link) == 1

            image = category.xpath('./img/@src')
            assert len(image) == 1

            number_of_videos = category.xpath('./span/text()')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0])[0])

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link[0].attrib['href'],
                                                  url=urljoin(self.base_url, link[0].attrib['href']),
                                                  title=link[0].attrib['title'],
                                                  image_link=urljoin(self.base_url, image[0]),
                                                  number_of_videos=number_of_videos,
                                                  object_type=Category,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)

        category_data.add_sub_objects(res)
        return res

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
        """
# todo: finish this...
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
        videos = tmp_tree.xpath('.//video/source')
        assert len(videos) > 0
        video_links = sorted(((x.attrib['src'], int(re.findall(r'\d+', x.attrib['label'])[0])) for x in videos),
                             key=lambda y: int(y[1]), reverse=True)
        video_links = [x[0] for x in video_links]
        return VideoNode(video_links=video_links)

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self._get_page_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//ul[@class="listing-videos listing-extract"]/li')
        res = []
        for video_tree_data in videos:
            left_a = video_tree_data.xpath('./div[@class="left"]/a')
            assert len(left_a) == 1

            image_data = video_tree_data.xpath('./div[@class="left"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            num_of_viewers = video_tree_data.xpath('./div[@class="left"]/div[@class="listing-infos"]/'
                                                   'div[@class="views-infos"]/text()')
            number_of_viewers = int(re.findall(r'\d+', num_of_viewers[0], re.DOTALL)[0])

            video_length = video_tree_data.xpath('./div[@class="left"]/div[@class="listing-infos"]/'
                                                 'div[@class="time-infos"]')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0].text)
            video_length = video_length if video_length != '-' else None

            rating = video_tree_data.xpath('./div[@class="left"]/div[@class="listing-infos"]/'
                                           'div[@class="rating-infos"]')
            rating = re.findall(r'\d+%', rating[0].text, re.DOTALL)[0] if len(rating) == 1 else None

            description = video_tree_data.xpath('./div[@class="right"]/p')
            assert len(description) == 1
            description = self._clear_text(description[0].text)

            res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                obj_id=left_a[0].attrib['href'],
                                                url=urljoin(self.base_url, left_a[0].attrib['href']),
                                                title=left_a[0].attrib['title'],
                                                image_link=image,
                                                description=description,
                                                duration=self._format_duration(video_length),
                                                number_of_views=number_of_viewers,
                                                rating=rating,
                                                object_type=Video,
                                                super_object=page_data,
                                                ))
        page_data.add_sub_objects(res)
        return res

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        if category_data.object_type in (CategoryMain, ):
            return 1
        else:
            page_request = self._get_page_request(category_data) if fetched_request is None else fetched_request
            tree = self.parser.parse(page_request.text)
            pages = self._get_available_pages_from_tree(tree)
            return max(pages) if len(pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(re.findall(r'(?:page/)(\d+)', x)[0])
                for x in tree.xpath('.//div[@class="pagination"]/ul/li/a/@href')
                if len(re.findall(r'(?:page/)(\d+)', x)) > 0]

    def _get_page_request(self, page_data, force_override_page=None):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        program_fetch_url = page_data.url.split('?')[0]
        if len(page_data.url.split('?')) > 1:
            params = page_data.url.split('?')[1]
            params = dict([x.split('=') if '=' in x else [x, ''] for x in params.split('&')])
        else:
            params = {}

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            # 'Referer': self.category_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        if page_data.page_number is not None and page_data.page_number != 1:
            program_fetch_url = re.sub(r'/*$', '', program_fetch_url)
            program_fetch_url += '/page/{p}/'.format(p=page_data.page_number)

        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request


if __name__ == '__main__':
    cat_id = IdGenerator.make_id('https://watchxxxfreeinhd.com/category/look/busty/')
    module = WatchXXXFree()
    module.get_available_categories()
    module.download_object(None, cat_id, verbose=1)
