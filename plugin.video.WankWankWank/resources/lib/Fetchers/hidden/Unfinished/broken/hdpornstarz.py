# -*- coding: UTF-8 -*-
from porn_fetcher import PornFetcher
from ..tools.external_fetchers import ExternalFetcher

# Internet tools
from urllib.parse import urlparse, urljoin

# Regex
import re

# Nodes
from porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode
from porn_catalog import CategoryMain, TagMain, PornStarMain, Category, Tag, LatestVideo, Video
from video_catalog import VideoNode

# Generator id
from ..id_generator import IdGenerator


# todo: in case back to life, unite with hidden/nubilefilmxxx.py
class HDPornStarz(PornFetcher):
    flip_number = 11

    @property
    def object_urls(self):
        return {
            CategoryMain: 'https://www.hdpornstarz.com/categories/',
            TagMain: 'https://www.hdpornstarz.com/tags/',
            PornStarMain: 'https://www.hdpornstarz.com/pornstar-list/',
            LatestVideo: 'https://www.hdpornstarz.com/?filter=latest',
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.hdpornstarz.com/'

    def __init__(self, source_name='HDPornStarz', source_id=0, store_dir='.', data_dir='../Data'):
        """
        C'tor
        :param source_name: save directory
        """
        super(HDPornStarz, self).__init__(source_name, source_id, store_dir, data_dir)
        self.external_fetchers = ExternalFetcher(session=self.session, user_agent=self.user_agent,
                                                 parser=self.parser)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self._get_page_request(category_data)
        tree = self.parser.parse(page_request.text)

        categories = tree.xpath('.//div[@class="videos-list"]/article/a')
        res = []
        for category in categories:
            image = category.xpath('./div[@class="post-thumbnail"]/img')
            assert len(image) == 1

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(self.base_url, category.attrib['href']),
                                                  title=category.attrib['title'],
                                                  image_link=urljoin(self.base_url, image[0].attrib['src']),
                                                  object_type=Category,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available tags.
        :return: Object of all available shows (JSON).
        """
        page_request = self._get_page_request(tag_data)
        tree = self.parser.parse(page_request.text)

        categories = tree.xpath('.//div[@class="content-area with-sidebar-right categories-list"]/main/a')
        res = []
        for category in categories:

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=category.attrib['href'],
                                                  url=urljoin(tag_data.url, category.attrib['href']),
                                                  title=category.attrib['aria-label'],
                                                  object_type=Tag,
                                                  super_object=tag_data,
                                                  )
            res.append(object_data)
        tag_data.add_sub_objects(res)
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
        tree = self.parser.parse(tmp_request.text)
        video_ext_link = tree.xpath('.//div[@class="responsive-player"]/noscript/iframe')
        if len(video_ext_link) != 1:
            raise RuntimeError('Broken link {u}!'.format(u=video_url))
        video_ext_link = video_ext_link[0].attrib['src']
        if urlparse(video_ext_link).hostname == 'www.fembed.com':
            videos = self.external_fetchers.get_video_link_fembed(video_ext_link)
        else:
            raise RuntimeError('Unknowwn host {h}'.format(h=urlparse(video_ext_link).hostname))

        videos = sorted(((x['file'], x['label']) for x in videos), key=lambda y: int(y[1][:-1]), reverse=True)
        videos = [x[0] for x in videos]
        return VideoNode(video_links=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        page_request = self._get_page_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        available_pages = self._get_available_pages_from_tree(tree)
        return max(available_pages) if len(available_pages) > 0 else 1

    def _get_available_pages_from_tree(self, tree):
        """
        Finds the number of pages for the given parsed object.
        :param tree: Page tree.
        :return: number of pages (int).
        """
        pages = tree.xpath('.//div[@class="pagination"]/ul/li/a')
        pages = [int(x.attrib['href'].split('/')[-2]) for x in pages if 'href' in x.attrib]
        return pages

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self._get_page_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="videos-list"]/article/a')
        res = []
        for video_tree_data in videos:
            title = video_tree_data.attrib['title'] \
                if 'title' in video_tree_data.attrib else video_tree_data.attrib['data-title']

            image = video_tree_data.xpath('./div[@class="post-thumbnail thumbs-rotation"]/img')
            assert len(image) == 1
            image = image[0].attrib['data-src'] if 'data-src' in image[0].attrib else image[0].attrib['src']

            number_of_viewers = video_tree_data.xpath('./div[@class="post-thumbnail thumbs-rotation"]/'
                                                      'span[@class="views"]/i')
            assert len(number_of_viewers) == 1
            number_of_viewers = int(''.join(re.findall(r'\d+', number_of_viewers[0].tail, re.DOTALL)))

            video_length = video_tree_data.xpath('./div[@class="post-thumbnail thumbs-rotation"]/'
                                                 'span[@class="duration"]/i')
            assert len(video_length) == 1
            video_length = re.findall(r'\d+:\d+:*\d*', video_length[0].tail)[0]

            rating = video_tree_data.xpath('./div[@class="rating-bar "]/span')
            assert len(rating) == 1

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=video_tree_data.attrib['href'],
                                                  url=urljoin(self.base_url, video_tree_data.attrib['href']),
                                                  title=title,
                                                  image_link=image,
                                                  number_of_views=number_of_viewers,
                                                  rating=rating[0].text,
                                                  duration=self._format_duration(video_length),
                                                  object_type=Video,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request(self, page_data):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        program_fetch_url = page_data.url.split('?')[0]
        if len(page_data.url.split('?')) > 1:
            params = page_data.url.split('?')[1]
            params = parse_qs(params)
        else:
            params = None
        program_fetch_url = program_fetch_url + 'page/{p}/'.format(p=page_data.page_number)
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
        page_request = self.session.get(program_fetch_url, headers=headers, params=params)
        return page_request


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.hdpornstarz.com/category/bbc/')
    tag_id = IdGenerator.make_id('https://www.hdpornstarz.com/tag/affair/')
    module = HDPornStarz()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
