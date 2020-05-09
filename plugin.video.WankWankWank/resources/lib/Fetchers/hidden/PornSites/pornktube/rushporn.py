import re
from .... import urljoin, quote_plus

import m3u8

from ....catalogs.base_catalog import VideoSource, VideoTypes, VideoNode
from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornFilter, PornCatalogCategoryNode
from .pornktube import PornKTube


class RushPorn(PornKTube):
    # Many similarities with ponktube module
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories'),
            PornCategories.CHANNEL_MAIN: urljoin(self.base_url, '/channels'),
            PornCategories.PORN_STAR_MAIN: urljoin(self.base_url, '/pornstars'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/recent-videos'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-viewed'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/longest'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.rushporn.xxx/'

    @staticmethod
    def _prepare_filters():
        video_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Newest', 'recent-videos'),
                                        (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                        (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                        (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                        ),
                         'period_filters': ([(PornFilterTypes.AllDate, 'All time', None),
                                             (PornFilterTypes.TwoDate, 'Week', 'week'),
                                             (PornFilterTypes.OneDate, 'Month', 'month'),
                                             (PornFilterTypes.ThreeDate, 'Today', 'today'),
                                             ],
                                            [('sort_order', [PornFilterTypes.ViewsOrder])]),
                         }
        single_category_filters = {'sort_order': ((PornFilterTypes.DateOrder, 'Recent', None),
                                                  (PornFilterTypes.RatingOrder, 'Top Rated', 'rated'),
                                                  (PornFilterTypes.ViewsOrder, 'Most Viewed', 'views'),
                                                  (PornFilterTypes.LengthOrder, 'Longest', 'long'),
                                                  ),
                                   }

        (_, _, single_porn_star_filters, categories_filters,
         porn_stars_filters, channels_filters) = PornKTube._prepare_filters()

        return (video_filters, single_category_filters, single_porn_star_filters, categories_filters,
                porn_stars_filters, channels_filters)

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        video_filters, single_category_filters, single_porn_star_filters, _, porn_stars_filters, channels_filters = \
            self._prepare_filters()
        self._video_filters = PornFilter(data_dir=self.fetcher_data_dir,
                                         porn_stars_args=porn_stars_filters,
                                         channels_args=channels_filters,
                                         single_category_args=single_category_filters,
                                         single_porn_star_args=single_porn_star_filters,
                                         video_args=video_filters,
                                         )

    def __init__(self, source_name='RushPorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(RushPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_category(channel_data, PornCategories.CHANNEL)

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="pornstar"]/div[@class="wrap"]/div[@class="pornstars"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']
            description = link_data[0].attrib['title'] if 'title' in link_data[0].attrib else None

            image_data = category.xpath('./a/img')
            assert len(image_data) == 1
            image = urljoin(porn_star_data.url, image_data[0].attrib['src'])
            title = image_data[0].attrib['alt']

            additional_data = {}
            likes = category.xpath('./div[@class="likes"]/text()')
            additional_data['likes'] = int(likes[0]) if len(likes) > 0 else None
            dislikes = category.xpath('./div[@class="dislikes"]/text()')
            additional_data['dislikes'] = int(dislikes[0]) if len(dislikes) > 0 else None
            rating = category.xpath('./div[@class="vsaw"]/text()')
            additional_data['rating'] = int(rating[0]) if len(rating) > 0 else None

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(porn_star_data.url, link),
                                                  image_link=image,
                                                  title=title,
                                                  description=description,
                                                  additional_data=additional_data,
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
        org_request = self.get_object_request(video_data)
        org_tree = self.parser.parse(org_request.text)
        tmp_url = org_tree.xpath('.//video[@id="main_video"]/source')
        videos = sorted((VideoSource(link=x.attrib['src'],  quality=int(re.findall(r'\d+', x.attrib['title'])[0]))
                         for x in tmp_url),
                        key=lambda x: x.quality, reverse=True)

        if len(videos) == 0:
            # Probably we have video from xvideos source. In such case we copy the code from their module.
            video_embed_url = re.findall(r'(?:video_embed_url *= *\')(.*?)(?:\')', org_request.text)
            if len(video_embed_url) == 1:
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                              'q=0.8,application/signed-exchange;v=b3*',
                    'Cache-Control': 'max-age=0',
                    'Referer': video_data.url,
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': self.user_agent
                }
                xvideo_req = self.session.get(video_embed_url[0], headers=headers)
                request_data = re.findall(r'(?:html5player.setVideoHLS\(\')(.*?)(?:\'\);)', xvideo_req.text)
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                              'q=0.8,application/signed-exchange;v=b3*',
                    'Cache-Control': 'max-age=0',
                    'Referer': video_data.url,
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': self.user_agent
                }
                m3u8_req = self.session.get(request_data[0], headers=headers)
                video_m3u8 = m3u8.loads(m3u8_req.text)
                video_playlists = video_m3u8.playlists
                if all(vp.stream_info.bandwidth is not None for vp in video_playlists):
                    video_playlists.sort(key=lambda k: k.stream_info.bandwidth, reverse=True)
                videos = sorted((VideoSource(link=urljoin(request_data[0], x.uri),
                                             video_type=VideoTypes.VIDEO_SEGMENTS,
                                             quality=x.stream_info.bandwidth,
                                             resolution=x.stream_info.resolution[1],
                                             codec=x.stream_info.codecs)
                                 for x in video_playlists),
                                key=lambda x: x.quality, reverse=True)

        return VideoNode(video_sources=videos)

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
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
        conditions = self.get_proper_filter(page_data).conditions
        if true_object.object_type in (PornCategories.CATEGORY, PornCategories.SEARCH_MAIN, PornCategories.VIDEO):
            last_slash = True
        else:
            last_slash = False
        fetch_base_url = self._prepare_request(page_number, true_object, page_filter, fetch_base_url, last_slash,
                                               conditions)
        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        if not page_request.ok:
            # Sometimes we try another fetch
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_request(self, page_number, true_object, page_filter, fetch_base_url, use_last_slash, conditions):
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id
        split_url = fetch_base_url.split('/')
        if len(split_url[-1]) == 0:
            # We remove the last slash
            split_url.pop()
        if page_filter.sort_order.value is not None and true_object.object_type not in self._default_sort_by:
            tmp_value = page_filter.sort_order.value
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                tmp_value = page_filter.period.value + '-' + tmp_value

            split_url.append(tmp_value)

        if page_number is not None and page_number != 1:
            split_url.append(str(page_number))

        if use_last_slash is True:
            split_url.append('')

        fetch_base_url = '/'.join(split_url)
        return fetch_base_url

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))
