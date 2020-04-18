# -*- coding: UTF-8 -*-
from ..fetchers.porn_fetcher import PornFetcher

# Internet tools
from .. import urljoin, quote_plus

# Regex
import re

# Nodes
from ..catalogs.porn_catalog import *

# JSON
# import json
from ..tools.text_json_manioulations import prepare_json_from_not_formatted_text

# Generator id
from ..id_generator import IdGenerator

# Playlist tools
import m3u8


class FreeOnes(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://videos.freeones.com/categories',
            PornCategories.TAG_MAIN: 'https://videos.freeones.com/tagcloud/',
            PornCategories.PORN_STAR_MAIN: 'https://www.freeones.com/baberank/',
            PornCategories.LATEST_VIDEO: 'https://videos.freeones.com/all-videos/date',
            PornCategories.POPULAR_VIDEO: 'https://videos.freeones.com/all-videos/rank',
            PornCategories.MOST_VIEWED_VIDEO: 'https://videos.freeones.com/all-videos/views',
            PornCategories.FULL_MOVIE_VIDEO: 'https://videos.freeones.com/full-videos/',
            PornCategories.SEARCH_MAIN: 'https://www.freeones.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.FULL_MOVIE_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://videos.freeones.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        # todo: add other filters, by parsing the page...
        porn_stars_filters = {'period_filters': [(PornFilterTypes.OneDate, 'Yesterday', 'y'),
                                                 (PornFilterTypes.TwoDate, 'Last Week', 'lw'),
                                                 (PornFilterTypes.ThreeDate, 'Last 30 days', 'lm'),
                                                 (PornFilterTypes.FourDate, 'Last 90 days', 'l3m'),
                                                 (PornFilterTypes.FiveDate, 'Last year', 'ly'),
                                                 ],
                              'profession_filters': [(PornFilterTypes.AllProfession, 'Any profession', ''),
                                                     (PornFilterTypes.ActorProfession, 'Actress', 'A'),
                                                     (PornFilterTypes.AdultModelProfession, 'Adult Model', 'U'),
                                                     (PornFilterTypes.CenterfoldProfession, 'Centerfold', 'C'),
                                                     (PornFilterTypes.MusicianProfession, 'Musician', 'M'),
                                                     (PornFilterTypes.PornStarProfession, 'Porn Star', 'P'),
                                                     (PornFilterTypes.SportsmenProfession, 'Sportswoman', 'H'),
                                                     (PornFilterTypes.SupermodelProfession, 'Supermodel', 'S'),
                                                     (PornFilterTypes.TVHostProfession, 'TV Host', 'T'),
                                                     ],
                              }
        video_filters = {'sort_order': [(PornFilterTypes.DateOrder, 'Date', 'date'),
                                        (PornFilterTypes.RatingOrder, 'Rank', 'rank'),
                                        (PornFilterTypes.NumberOfVideosOrder, 'Views', 'views'),
                                        (PornFilterTypes.LengthOrder, 'Duration', 'duration'),
                                        ],
                         }
        search_filters = {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Relevance', 'relevance'),
                                         (PornFilterTypes.DateOrder, 'Date', 'date'),
                                         (PornFilterTypes.RatingOrder, 'Rank', 'rank'),
                                         (PornFilterTypes.NumberOfVideosOrder, 'Views', 'views'),
                                         (PornFilterTypes.LengthOrder, 'Duration', 'duration'),
                                         ],
                          }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filters,
                                         single_category_args=video_filters,
                                         video_args=video_filters,
                                         search_args=search_filters,
                                         )

    def __init__(self, source_name='FreeOnes', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(FreeOnes, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="catBlock"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            title = self._clear_text(category.text)

            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(category_data.url, link),
                                               title=title,
                                               image_link=image,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(tag_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//ul[@class="cloud-tags"]/li/a')
        res = []
        for category in categories:
            split_link = category.attrib['href'].split('/')
            split_link[2] = split_link[2].replace('videos', 'www')
            split_link[3] = 'html/{l}_links'.format(l=split_link[-1][0].lower())
            split_link[-1] = split_link[-1].replace(' ', '_')
            split_link.append('videos')
            split_link.append('')

            link = '/'.join(split_link)
            # link = category.attrib['href']
            title = self._clear_text(category.text)
            number_of_videos = int(re.findall(r'(?:\()(\d+)(?:\)$)', title)[0])
            title = re.findall(r'(.*)(?: *\(\d+\)$)', title)[0]

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(tag_data.url, link),
                                               title=title,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.TAG,
                                               super_object=tag_data,
                                               ))

        tag_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="ContentBlockBody"]/div[@style="float: left; width: '
                                '125px; height: 135px; text-align: center;"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a[1]')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            title = category.xpath('./a[1]/small')
            assert len(title) == 1
            title = title[0].text

            image = category.xpath('./a[2]/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(porn_star_data.url, link) + 'videos/',
                                               title=title,
                                               image_link=image,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return False

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
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
        request_data = re.findall(r'(?:loadFOPlayer\(\'foplayer\', )({.*?})(?:\);)', tmp_request.text, re.DOTALL)
        assert len(request_data) == 1
        request_data = prepare_json_from_not_formatted_text(request_data[0])
        videos = []
        qualities = request_data['qualitySelector']['qualities'].split(',')
        for src in request_data['src']:
            if 'type' not in src:
                raise ValueError('No video type')
            if src['type'] == 'application/x-mpegURL':
                # We have segments
                segment_request = self.session.get(src['src'], headers=headers)
                video_m3u8 = m3u8.loads(segment_request.text)
                video_playlists = video_m3u8.playlists
                videos.extend([VideoSource(link=urljoin(src['src'], x.uri),
                                           video_type=VideoTypes.VIDEO_SEGMENTS,
                                           quality=x.stream_info.bandwidth,
                                           resolution=x.stream_info.resolution[1],
                                           codec=x.stream_info.codecs)
                               for x in video_playlists])
            elif src['type'] == 'application/dash+xml':
                # We have dash (with highest quality)
                videos.append(VideoSource(link=src['src'],
                                          video_type=VideoTypes.VIDEO_DASH,
                                          resolution=re.findall(r'\d+', qualities[0])[0]))
            elif src['type'] == 'video/mp4':
                # We have mp4
                videos.extend([VideoSource(link=re.sub(r'\d+p.mp4$', '{q}.mp4'.format(q=q), src['src']),
                                           video_type=VideoTypes.VIDEO_REGULAR,
                                           resolution=re.findall(r'\d+', q)[0])
                               for q in qualities])
            else:
                raise ValueError('Unsupported video format {vf}'.format(vf=src['type']))
        videos.sort(key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=videos)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN, PornCategories.CATEGORY_MAIN):
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
        return ([int(re.findall(r'(?:pagesize=)(\d+)', x.attrib['href'])[0])
                for x in tree.xpath('.//span[@class="Paging"]/span/a')
                if 'href' in x.attrib and len(re.findall(r'(?:pagesize=)(\d+)', x.attrib['href'])) > 0] +
                [int(re.findall(r'(?:page=)(\d+)', x.attrib['href'])[0])
                for x in tree.xpath('.//span[@class="Paging"]/span/a')
                if 'href' in x.attrib and len(re.findall(r'(?:page=)(\d+)', x.attrib['href'])) > 0] +
                [int(re.findall(r'(\d+)(?:.html)', x.attrib['href'])[0])
                 for x in tree.xpath('.//span[@class="Paging"]/span/a')
                 if 'href' in x.attrib and len(re.findall(r'(\d+)(?:.html)', x.attrib['href'])) > 0]
                )

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        if page_data.object_type == PornCategories.SEARCH_PAGE:
            videos = tree.xpath('.//div[@class="video_thumb videothumb"]')
        else:
            videos = tree.xpath('.//div[@class="videolist"]/div[@class="video_thumb videothumb"]')
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./a')
            assert len(link_data)
            link = link_data[0].attrib['href']

            image_data = video_tree_data.xpath('./a/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image)
                           for d in image_data[0].attrib['data-thumblist'].split(',')]
            additional_info = {'data_path': image_data[0].attrib['data-path'],
                               }

            info_data = video_tree_data.xpath('./div[@class="video-info"]')
            if len(info_data) != 1:
                # we try another method
                info_data = video_tree_data.xpath('./span[@class="video-info video-meta"]')
                assert len(info_data) == 1

            video_length = re.findall(r'(?:Duration )(\d+:\d+)', info_data[0].text)[0]
            number_of_views = re.findall(r'(Views \d+)', info_data[0].text)[0]

            title = video_tree_data.xpath('./div[@class="video-info"]/span[@class="video-title"]')
            if len(title) != 1:
                # we try another method
                title = video_tree_data.xpath('./span[@class="video-info video-title"]')
                assert len(title) == 1

            title = title[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  additional_data=additional_info,
                                                  number_of_views=number_of_views,
                                                  duration=self._format_duration(video_length),
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
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
        if true_object.object_type in (PornCategories.CATEGORY, PornCategories.TAG):
            if page_filter.sort_order.value != '':
                fetch_base_url += page_filter.sort_order.value + '/'
        elif true_object.object_type in (PornCategories.PORN_STAR_MAIN,):
            params['t'] = page_filter.period.value
            params['p'] = page_filter.profession.value
        elif true_object.object_type in (PornCategories.SEARCH_MAIN,):
            params['filter'] = [page_filter.sort_order.value]

        if page_number is not None and page_number != 1:
            if page_data.super_object.object_type in (PornCategories.PORN_STAR, PornCategories.TAG):
                params['pagesize'] = [len(page_data.super_object.sub_objects)]
                params['page'] = [page_number]
            elif page_data.super_object.object_type in (PornCategories.SEARCH_MAIN,):
                params['page'] = [page_number]
            else:
                fetch_base_url += '{d}.html'.format(d=page_number)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}&sq=&t=8'.format(q=quote_plus(query))


if __name__ == '__main__':
    category_id = IdGenerator.make_id('https://www.pornrewind.com/categories/amateur/')
    tag_id = IdGenerator.make_id('https://www.pornrewind.com/tags/sarah-vandella/')
    module = FreeOnes()
    # module.download_object(module.objects['categories']['obj'], (category_id, ), verbose=1)
    # module.download_object(module.objects['tags']['obj'], (tag_id, ), verbose=1)
    # module.download_object(module.objects['latest_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_viewed_videos']['obj'], (), verbose=1)
    # module.download_object(module.objects['most_rated_videos']['obj'], (), verbose=1)
    module.download_category_input_from_user(use_web_server=False)
