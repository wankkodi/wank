# -*- coding: UTF-8 -*-
from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, quote, parse_qsl

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import *

# JSON
# import json
from ....tools.text_json_manioulations import prepare_json_from_not_formatted_text

# Playlist tools
import m3u8


class FreeOnes(PornFetcher):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.freeones.com/categories',
            PornCategories.CHANNEL_MAIN: 'https://www.freeones.com/channels',
            PornCategories.PORN_STAR_MAIN: 'https://www.freeones.com/babes',
            PornCategories.LATEST_VIDEO: 'https://www.freeones.com/videos?f%5BcontentType%5D=video&s=latest&o=desc',
            PornCategories.LONGEST_VIDEO: 'https://www.freeones.com/videos?f%5BcontentType%5D=video&s=duration&o=desc',
            PornCategories.TOP_RATED_VIDEO: 'https://www.freeones.com/videos?f%5BcontentType%5D=video&'
                                            's=votes.average&o=desc',
            PornCategories.RELEVANT_VIDEO: 'https://www.freeones.com/videos?f%5BcontentType%5D=video&'
                                           's=relevance&o=desc',
            PornCategories.HD_VIDEO: 'https://www.freeones.com/videos?f%5BcontentType%5D=video&'
                                     's=video.presets.height&o=desc',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.freeones.com/videos?f%5BcontentType%5D=video&s=views&o=desc',
            PornCategories.SEARCH_MAIN: 'https://www.freeones.com/videos',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.RELEVANT_VIDEO: PornFilterTypes.RelevanceOrder,
            PornCategories.HD_VIDEO: PornFilterTypes.ResolutionOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.freeones.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        # todo: add other filters, by parsing the page...
        added_before_values = [(PornFilterTypes.AllAddedBefore, 'All time', None),
                               (PornFilterTypes.OneAddedBefore, 'Last 3 months', 'd[createdAt]=last_3_months'),
                               (PornFilterTypes.TwoAddedBefore, 'Last 30 days', 'd[createdAt]=last_30_days'),
                               (PornFilterTypes.ThreeAddedBefore, 'Last 7 days', 'd[createdAt]=last_week'),
                               (PornFilterTypes.FourAddedBefore, 'Since yesterday', 'd[createdAt]=since_yesterday'),
                               (PornFilterTypes.FiveAddedBefore, 'Last Hour', 'd[createdAt]=last_hour'),
                               ]
        length_values = [(PornFilterTypes.AllLength, 'Any duration', None),
                         (PornFilterTypes.OneLength, '0-10 min', 'r[video.length]=10,600'),
                         (PornFilterTypes.TwoLength, '10-20 min', 'r[video.length]=600,1200'),
                         (PornFilterTypes.ThreeLength, '20+ min', 'r[video.length]=1200,1977'),
                         ]
        quality_values = [(PornFilterTypes.AllQuality, 'Any Quality', None),
                          (PornFilterTypes.HDQuality, 'HD', 'r[video.presets.height]=720,1080'),
                          ]
        porn_stars_filters = \
            {'sort_order': [(PornFilterTypes.RatingOrder, 'Babe rank', None),
                            (PornFilterTypes.DateOrder, 'Latest', 's=latest'),
                            (PornFilterTypes.AlphabeticOrder, 'Name', 's=name'),
                            (PornFilterTypes.RelevanceOrder, 'Relevance', 's=relevance'),
                            (PornFilterTypes.ViewsOrder, 'Views', 's=views'),
                            ],
             'added_before_filters': added_before_values,
             'profession_filters': [(PornFilterTypes.AllProfession, 'Any profession', None),
                                    (PornFilterTypes.ActorProfession, 'Actress', 'f[professions]=actresses'),
                                    (PornFilterTypes.AdultModelProfession, 'Adult Model',
                                     'f[professions]=adult_models'),
                                    (PornFilterTypes.CamGirlProfession, 'Centerfold', 'f[professions]=cam_girl'),
                                    (PornFilterTypes.CenterfoldProfession, 'Centerfold', 'f[professions]=centerfolds'),
                                    (PornFilterTypes.MusicianProfession, 'Musician', 'f[professions]=musicians'),
                                    (PornFilterTypes.PornStarProfession, 'Porn Star', 'f[professions]=porn_stars'),
                                    (PornFilterTypes.SportsmenProfession, 'Sportswoman', 'f[professions]=sportswomen'),
                                    (PornFilterTypes.SupermodelProfession, 'Supermodel', 'f[professions]=supermodels'),
                                    (PornFilterTypes.TVHostProfession, 'TV Host', 'f[professions]=tv_hosts'),
                                    ],
             }
        single_channel_filters = \
            {'sort_order': [(PornFilterTypes.DateOrder, 'Date', 's=channel-latest'),
                            (PornFilterTypes.RelevanceOrder, 'Relevance', 's=views'),
                            ],
             'added_before_filters': added_before_values,
             'length_filters': length_values,
             'quality_filters': quality_values,
             }
        single_porn_star_filters = \
            {'sort_order': [(PornFilterTypes.DateOrder, 'Date', 's=subject-latest'),
                            (PornFilterTypes.RelevanceOrder, 'Relevance', 's=subject-relevance'),
                            ],
             'added_before_filters': added_before_values,
             'length_filters': length_values,
             'quality_filters': quality_values,
             }
        video_filters = \
            {'sort_order': [(PornFilterTypes.DateOrder, 'Date', 's=latest&o=desc'),
                            (PornFilterTypes.LengthOrder, 'Duration', 's=duration&o=desc'),
                            (PornFilterTypes.RatingOrder, 'Rank', 's=votes.average&o=desc'),
                            (PornFilterTypes.RelevanceOrder, 'Relevance', 's=relevance&o=desc'),
                            (PornFilterTypes.ResolutionOrder, 'Resolution', 's=video.presets.height&o=desc'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Views', 's=views&o=desc'),
                            ],
             'added_before_filters': added_before_values,
             'length_filters': length_values,
             'quality_filters': quality_values,
             }
        # search_filters = \
        #     {'sort_order': [(PornFilterTypes.RelevanceOrder, 'Relevance', 's=relevance&o=desc'),
        #                     (PornFilterTypes.DateOrder, 'Date', 's=latest&o=desc'),
        #                     ],
        #      'added_before_filters': added_before_values,
        #      'length_filters': length_values,
        #      'quality_filters': quality_values,
        #      }
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filters,
                                         single_category_args=video_filters,
                                         single_porn_star_args=single_porn_star_filters,
                                         single_channel_args=single_channel_filters,
                                         video_args=video_filters,
                                         search_args=video_filters,
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
        categories = tree.xpath('.//div[@class="grid-item teaser  teaser-lg\n    "]')
        res = []
        for category in categories:
            link_data = category.xpath('./div[@class="position-relative image-meta d-block"]/a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            # title = self._clear_text(category.text)

            image_data = link_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-src'] \
                if 'data-src' in image_data[0].attrib else image_data[0].attrib['src']

            title = link_data[0].xpath('./span')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            stats_data = category.xpath('./div[@class="teaser-abstract p-2 font-size-sm"]/div/p/a/span')
            assert len(stats_data) == 3

            number_of_videos = int(stats_data[0].text)
            number_of_images = int(stats_data[1].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(category_data.url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               number_of_photos=number_of_images,
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
        categories = tree.xpath('.//div[@class="grid-item teaser teaser-subject teaser-lg\n    "]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            # title = self._clear_text(category.text)

            image_main_data = link_data[0].xpath('./div[@class="position-relative image-meta d-block image-link"]')
            image_data = image_main_data[0].xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-src'] \
                if 'data-src' in image_data[0].attrib else image_data[0].attrib['src']

            title = link_data[0].xpath('./div/div/p')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            ranking = image_main_data[0].xpath('./div/span/span')
            assert len(ranking) == 1
            ranking = int(ranking[0].text)

            stats_data = category.xpath('./div[@class="teaser-abstract px-2 pb-2 pt-0 font-size-sm"]/div/p/a/span')
            assert len(stats_data) == 3

            number_of_videos = int(stats_data[0].text)
            number_of_images = int(stats_data[1].text)

            additional_data = {}
            followers = category.xpath('./div[@class="teaser-abstract px-2 pb-2 pt-0 font-size-sm"]/'
                                       'div[@class="d-flex flex-column"]/p')
            assert len(followers) == 1
            additional_data['followers'] = self._clear_text(followers[0].text)
            country = followers[0].xpath('./a/i')
            additional_data['country'] = country[0].attrib['title'] \
                if len(country) == 1 and 'title' in country[0].attrib else None
            rating = image_main_data[0].xpath('./div[@class="position-absolute rating-row rating"]/*')
            additional_data['rating'] = len(rating)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(porn_star_data.url, link),
                                               title=title,
                                               image_link=image,
                                               rating=ranking,
                                               number_of_videos=number_of_videos,
                                               number_of_photos=number_of_images,
                                               additional_data=additional_data,
                                               object_type=PornCategories.PORN_STAR,
                                               super_object=porn_star_data,
                                               ))

        porn_star_data.add_sub_objects(res)
        return res

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="grid-item teaser teaser-channel teaser-lg"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            # title = self._clear_text(category.text)

            image_data = link_data[0].xpath('./div[@class="position-relative image-meta d-block image-link"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-src'] \
                if 'data-src' in image_data[0].attrib else image_data[0].attrib['src']

            title = link_data[0].xpath('./div[@class="teaser-abstract px-2 pt-2 pb-0 font-size-sm"]/div/p')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            stats_data = category.xpath('./div[@class="teaser-abstract px-2 pb-2 pt-0 font-size-sm"]/div/p/a/span')
            assert len(stats_data) == 3

            number_of_videos = int(stats_data[0].text.replace(',', ''))
            number_of_images = int(stats_data[1].text.replace(',', ''))

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(channel_data.url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               number_of_photos=number_of_images,
                                               object_type=PornCategories.CHANNEL,
                                               super_object=channel_data,
                                               ))

        channel_data.add_sub_objects(res)
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
            # split_link = category.attrib['href'].split('/')
            # split_link[2] = split_link[2].replace('videos', 'www')
            # split_link[3] = 'html/{l}_links'.format(l=split_link[-1][0].lower())
            # split_link[-1] = split_link[-1].replace(' ', '_')
            # split_link.append('videos')
            # split_link.append('')
            #
            # link = '/'.join(split_link)
            link = category.attrib['href']
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

    def _check_is_available_page(self, page_object, page_request=None):
        """
        In binary search performs test whether the current page is available.
        :param page_object: Page object.
        :param page_request: Page request.
        :return:
        """
        if page_request is None:
            page_request = self.get_object_request(page_object)
        return len(page_request.history) == 0

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        request_data = re.findall(r'(?:loadFOPlayer\(\'foplayer\', )({.*?})(?:\);)', tmp_request.text, re.DOTALL)
        assert len(request_data) == 1
        request_data = prepare_json_from_not_formatted_text(request_data[0])
        videos = []
        qualities = request_data['qualitySelector']['qualities'].split(',')
        for src in request_data['src']:
            if 'type' not in src:
                raise ValueError('No video type')
            correct_url = re.sub(r'\\/', '/', src['src'])
            correct_url = re.sub(r'\\u.{4}', lambda x: x[0].encode('utf-8').decode('unicode-escape'), correct_url)
            if src['type'] == 'application/x-mpegURL':
                # We have segments
                segment_request = self.session.get(correct_url, headers=headers)
                video_m3u8 = m3u8.loads(segment_request.text)
                video_playlists = video_m3u8.playlists
                videos.extend([VideoSource(link=urljoin(correct_url, x.uri),
                                           video_type=VideoTypes.VIDEO_SEGMENTS,
                                           quality=x.stream_info.bandwidth,
                                           resolution=x.stream_info.resolution[1],
                                           codec=x.stream_info.codecs)
                               for x in video_playlists])
            elif src['type'] == 'application/dash+xml':
                # We have dash (with highest quality)
                videos.append(VideoSource(link=correct_url,
                                          video_type=VideoTypes.VIDEO_DASH,
                                          resolution=re.findall(r'\d+', qualities[0])[0]))
            elif src['type'] == 'video/mp4':
                # We have mp4
                videos.extend([VideoSource(link=re.sub(r'\d+p.mp4$', '{q}.mp4'.format(q=q), correct_url),
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
        return [int(y.text)
                for x in tree.xpath('.//nav') if 'class' in x.attrib and 'pagination' in x.attrib['class']
                for y in x.xpath('./ul/li/a') if y.text.isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div/a[@class="d-block"]')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']
            if link == '/':
                continue

            image_data = video_tree_data.xpath('./div/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-src'] \
                if 'data-src' in image_data[0].attrib else image_data[0].attrib['src']
            preview = image_data[0].attrib['data-media'] if 'data-media' in image_data[0].attrib else None
            title = image_data[0].attrib['title'] if 'title' in image_data[0].attrib else None

            rating = video_tree_data.xpath('./div/div/div/span')
            assert len(rating) >= 1
            rating = rating[0].text

            video_length = [x for x in video_tree_data.xpath('./div/div/div')
                            if 'title' in x.attrib and 'Duration' in x.attrib['title']]
            video_length = video_length[0].text

            if title is None:
                title = video_tree_data.xpath('./div/div/span')
                if len(title) != 1:
                    # we try another method
                    assert len(title) == 1
                title = self._clear_text(title[0].text)

            number_of_views = video_tree_data.xpath('./div/div/div/p')
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].text)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  preview_video_link=preview,
                                                  rating=rating,
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
        split_url = fetch_base_url.split('/')
        is_video_page = true_object.object_type not in (PornCategories.CHANNEL_MAIN, PornCategories.CATEGORY_MAIN,
                                                        PornCategories.PORN_STAR_MAIN, PornCategories.VIDEO)
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
        if is_video_page:
            params['f[contentType]'] = 'video'
            params['l'] = 48

        if true_object.object_type in (PornCategories.PORN_STAR_MAIN,):
            if page_filter.period.value is not None:
                params.update(parse_qsl(page_filter.period.value))
            if page_filter.profession.value is not None:
                params.update(parse_qsl(page_filter.profession.value))
        elif true_object.object_type in (PornCategories.CHANNEL, ):
            split_url.insert(-1, 'videos')
            params['v'] = 'teasers'
            params['m[channelTitle]'] = true_object.title
            params['f[channel.title]'] = true_object.title
            params['m[route]'] = 'channel_video_list'
            params['m[channelScope]'] = 1
            params['m[hideTitle]'] = 1
            params['m[toggleSidebar]'] = 1
        elif true_object.object_type in (PornCategories.PORN_STAR,):
            split_url.append('videos')
            params['f[subjectLinks.name]'] = true_object.title
            params['m[subjectName]'] = true_object.title
            params['m[route]'] = 'subject_video_list'
            params['m[subjectScope]'] = 1
            params['m[hideTitle]'] = 1
            params['m[toggleSidebar]'] = 1
        elif true_object.object_type in (PornCategories.CATEGORY,):
            split_url = split_url[:3]
            split_url.append('videos')
            params['v'] = 'teaser'
            params['f[categories]'] = true_object.title
        elif true_object.object_type in (PornCategories.SEARCH_MAIN,):
            params['v'] = 'teasers'
            params['m[canPreviewFeatures]'] = 0

        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            params.update(parse_qsl(page_filter.sort_order.value))
        if page_filter.length.value is not None:
            params.update(parse_qsl(page_filter.length.value))
        if page_filter.quality.value is not None:
            params.update(parse_qsl(page_filter.quality.value))
        if page_filter.added_before.value is not None:
            params.update(parse_qsl(page_filter.added_before.value))

        if page_number is not None and page_number != 1:
            params['p'] = page_number

        fetch_base_url = '/'.join(split_url)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote(query))

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(FreeOnes, self)._version_stack + [self.__version]
