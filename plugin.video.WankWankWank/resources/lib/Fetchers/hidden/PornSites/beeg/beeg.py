from ....fetchers.porn_fetcher import PornFetcher

# Internet tools
from .... import urljoin, urlparse, quote_plus

# math
import math

# Regex
import re

# Nodes
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode, PornCatalogPageNode, \
    VideoNode, VideoSource
from ....catalogs.porn_catalog import PornCategories

# Generator id
from ....id_generator import IdGenerator


class Beeg(PornFetcher):
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 100

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://beeg.com/'

    @property
    def object_urls(self):
        return {
            PornCategories.TAG_MAIN: self.tag_json_url,
            PornCategories.CHANNEL_MAIN: self.channels_json_url,
            PornCategories.PORN_STAR_MAIN: self.porn_stars_json_url,
            PornCategories.SEARCH_MAIN: self.search_json_url,
        }

    @property
    def _default_sort_by(self):
        return {}

    @property
    def channels_json_url(self):
        if self.user_id is None:
            self._update_user_agent()
        return 'https://beeg.com/api/v6/{id}/channels'.format(id=self.user_id)

    @property
    def porn_stars_json_url(self):
        if self.user_id is None:
            self._update_user_agent()
        return 'https://beeg.com/api/v6/{id}/people'.format(id=self.user_id)

    @property
    def tag_json_url(self):
        if self.user_id is None:
            self._update_user_agent()
        return 'https://beeg.com/api/v6/{id}/tags'.format(id=self.user_id)

    @property
    def search_json_url(self):
        if self.user_id is None:
            self._update_user_agent()
        return 'https://beeg.com/api/v6/{id}/suggest'.format(id=self.user_id)

    @property
    def main_json_url(self):
        if self.user_id is None:
            self._update_user_agent()
        return 'https://beeg.com/api/v6/{id}/index/main/0/pc'.format(id=self.user_id)

    @property
    def channel_videos_json_url(self):
        if self.user_id is None:
            self._update_user_agent()
        return 'https://beeg.com/api/v6/{id}/index/channel/0/pc'.format(id=self.user_id)

    @property
    def tag_videos_json_url(self):
        if self.user_id is None:
            self._update_user_agent()
        return 'https://beeg.com/api/v6/{id}/index/tag/0/pc'.format(id=self.user_id)

    @property
    def porn_star_videos_json_url(self):
        if self.user_id is None:
            self._update_user_agent()
        return 'https://beeg.com/api/v6/{id}/index/people/0/pc'.format(id=self.user_id)

    @property
    def video_links_json_url(self):
        if self.user_id is None:
            self._update_user_agent()
        return 'https://beeg.com/api/v6/{id}/video/'.format(id=self.user_id) + '{vid}'

    @property
    def video_image_prefix(self):
        if self.user_id is None:
            self._update_user_agent()
        return 'https://img.beeg.com/264x198/4x3/160x22x584x438/'.format(id=self.user_id)

    @property
    def porn_star_image_prefix(self):
        if self.user_id is None:
            self._update_user_agent()
        return 'https://img.beeg.com/150x150/cast/'.format(id=self.user_id)

    def __init__(self, source_name='Beeg', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        self.bundle = None
        self.user_id = None
        self.tag_page_template = 'https://beeg.com/tag/{t}'
        super(Beeg, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                   session_id)

    def _update_user_agent(self):
        """
        Updates the user agent.
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Cache-Control': 'max-age=0',
            'Host': self.host_name,
            'Referer': self.base_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        page_request = self.session.get(self.base_url, headers=headers)
        self.user_id = re.findall(r'(?:beeg_version =* *)(\d+)(?:;)', page_request.text)[0]

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(channel_data)
        assert page_request.status_code == 200
        data = page_request.json()
        self.bundle = data['bundle_version']
        channels = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                            obj_id=x['id'],
                                            url=self.channel_videos_json_url + '?channel={c}'.format(c=x['channel']),
                                            title=x['ps_name'],
                                            image_link=urljoin(self.object_urls[PornCategories.CHANNEL_MAIN],
                                                               '/media/channels/{i}.png'.format(i=x['id'])),
                                            number_of_videos=int((x['videos'])),
                                            raw_data=x,
                                            object_type=PornCategories.CHANNEL,
                                            super_object=channel_data
                                            )
                    for x in data['channels']]

        channel_data.add_sub_objects(channels)
        return channels

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        assert page_request.status_code == 200
        data = page_request.json()
        self.bundle = data['bundle_version']
        porn_stars = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                              obj_id=x['id'],
                                              url=(self.porn_star_videos_json_url +
                                                   '?search_mode=code&people={c}'.format(c=x['code'])),
                                              title=x['name'],
                                              image_link=self.porn_star_image_prefix + '{i}.png'.format(i=x['id']),
                                              number_of_videos=int((x['videos'])),
                                              raw_data=x,
                                              object_type=PornCategories.PORN_STAR,
                                              super_object=porn_star_data
                                              )
                      for x in data['people']]

        porn_star_data.add_sub_objects(porn_stars)
        return porn_stars

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles. The fetched objects MUST be sorted wrt title.
        :param page_request: Page request.
        :return:
        """

        tags_json = page_request.json()
        links, titles, numbers_of_videos = zip(*[(self.tag_videos_json_url + '?tag={t}'
                                                                             ''.format(t=tag['tag']),
                                                  tag['tag'], tag['videos']) for tag in tags_json['tags']])
        return links, titles, numbers_of_videos

    def _add_tag_sub_pages(self, tag_data, object_type):
        # Took from PornRewind with slight modifications
        page_request = self.get_object_request(tag_data)
        links, titles, numbers_of_videos = self._get_tag_properties(page_request)
        partitioned_data = {
            chr(x): [(link, title, number_of_videos)
                     for link, title, number_of_videos in zip(links, titles, numbers_of_videos)
                     if title[0].upper() == chr(x)]
            for x in range(ord('A'), ord('Z')+1)
        }
        partitioned_data['#'] = [(link, title, number_of_videos)
                                 for link, title, number_of_videos in zip(links, titles, numbers_of_videos)
                                 if title[0].isdigit()]
        new_pages = [PornCatalogPageNode(catalog_manager=self.catalog_manager,
                                         obj_id=(IdGenerator.id_to_original_str(tag_data.id), k),
                                         title='{c} | Letter {p}'.format(c=tag_data.title, p=k),
                                         url=tag_data.url,
                                         # page_number=k,
                                         raw_data={'letter': k},
                                         object_type=object_type,
                                         super_object=tag_data,
                                         )
                     for k in sorted(partitioned_data.keys()) if len(partitioned_data[k]) > 0]
        for new_page in new_pages:
            sub_tags = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                obj_id=link,
                                                url=urljoin(tag_data.url, link),
                                                title=title,
                                                number_of_videos=number_of_videos,
                                                object_type=PornCategories.TAG,
                                                super_object=new_page,
                                                )
                        for link, title, number_of_videos in partitioned_data[new_page.raw_data['letter']]]
            new_page.add_sub_objects(sub_tags)

        tag_data.add_sub_objects(new_pages)

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        params = {
            'v': 2,
        }
        if 'start' in video_data.raw_data['thumbs'][0]:
            params['s'] = video_data.raw_data['thumbs'][0]['start']
        if 'end' in video_data.raw_data['thumbs'][0]:
            params['e'] = video_data.raw_data['thumbs'][0]['end']
        # todo: add crop to the wanted length...
        tmp_request = self.get_object_request(video_data, override_params=params)
        new_video_data = tmp_request.json()
        video_links = sorted([VideoSource(link='https:' +
                                               v.format(DATA_MARKERS='data=pc_US__{b}_'.format(b=self.bundle)),
                                          resolution=re.findall(r'\d+', k)[0])
                              for k, v in new_video_data.items()
                              if len(re.findall(r'\d+', k)) > 0 and v is not None],
                             key=lambda x: x.resolution, reverse=True)
        return VideoNode(video_sources=video_links)

    def _binary_search_max_number_of_porn_star_pages(self, category_data, last_available_number_of_pages):
        """
        Performs binary search in order to find the last available page.
        :param category_data: Category data.
        :param last_available_number_of_pages: Last available number of pages. Will be the pivot for our next search.
        By default is None, which mean the original pivot will be used...
        :return: Page request
        """
        left_page = 1
        right_page = self.max_pages
        page = last_available_number_of_pages if last_available_number_of_pages is not None \
            else int(math.ceil((right_page + left_page) / 2))
        while 1:
            if right_page == left_page:
                return left_page

            page_request = self._get_object_request_no_exception_check(category_data, override_page_number=page)
            if self._check_is_available_page(category_data, page_request):
                raw_data = page_request.json()
                if len(raw_data['people']) == 0:
                    # We also moved too far...
                    right_page = page - 1
                elif len(raw_data['people']) == 100:
                    # We also moved too far...
                    left_page = page
                else:
                    return page

            else:
                # We moved too far...
                right_page = page - 1
            page = int(math.ceil((right_page + left_page) / 2))

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Get number of pages from category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.true_object.object_type == PornCategories.PORN_STAR_MAIN:
            return self._binary_search_max_number_of_porn_star_pages(category_data, last_available_number_of_pages)
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        raw_data = page_request.json()
        return raw_data['pages'] if 'pages' in raw_data else 1

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        raw_data = page_request.json()
        videos = [PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                           obj_id=x['svid'],
                                           title=x['title'],
                                           url=self.video_links_json_url.format(vid=x['svid']),
                                           image_link=urljoin(self.video_image_prefix, x['thumbs'][0]['image']),
                                           flip_images_link=[urljoin(self.video_image_prefix, y['image'])
                                                             for y in x['thumbs']],
                                           raw_data=x,
                                           object_type=PornCategories.VIDEO,
                                           super_object=page_data,
                                           )
                  for x in raw_data['videos']]
        page_data.add_sub_objects(videos)
        return videos

    def get_search_data(self, page_data):
        """
        Gets search data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        raw_data = page_request.json()
        res = []
        for x in raw_data['items']:
            if x['type'] == 'people':
                object_type = PornCategories.PORN_STAR
                url = self.porn_star_videos_json_url + '?search_mode=code&people={c}'.format(c=x['code'])
                image = self.porn_star_image_prefix + '{id}.png'.format(id=x['id'])
            elif x['type'] == 'channel':
                object_type = PornCategories.CHANNEL
                url = self.channel_videos_json_url + '?channel={c}'.format(c=x['code'])
                image = None
            elif x['type'] == 'tag':
                object_type = PornCategories.TAG
                url = self.tag_videos_json_url + '?tag={t}'.format(t=x['code'])
                image = None
            else:
                raise ValueError('Unknown object type {ot}'.format(ot=x['type']))
            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=x['id'],
                                               title=x['name'],
                                               url=url,
                                               image_link=image,
                                               number_of_videos=x['videos'],
                                               number_of_photos=x['image'],
                                               rating=x['fs_score'],
                                               raw_data=x,
                                               object_type=object_type,
                                               super_object=page_data,
                                               )
                       )
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object,
                                page_filter, fetch_base_url):
        headers = {
            'Accept': '*/*',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        if page_data.true_object.object_type == PornCategories.PORN_STAR_MAIN:
            if page_number > 1:
                params['offset'] = 100 * (page_number-1)
        else:
            parsed_url = urlparse(page_data.url)
            split_url_path = parsed_url.path.split('/')
            if len(split_url_path) > 6 and page_number is not None and page_number > 1:
                split_url_path[6] = str(page_data.page_number-1)
                fetch_base_url = urljoin(page_data.url, '/'.join(split_url_path))

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return self.object_urls[PornCategories.SEARCH_MAIN] + '?q={q}'.format(q=quote_plus(query))

    @property
    def __version(self):
        return 1

    @property
    def _version_stack(self):
        return super(Beeg, self)._version_stack + [self.__version]
