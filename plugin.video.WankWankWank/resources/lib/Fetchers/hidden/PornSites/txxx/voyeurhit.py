import re
from .... import urljoin, urlparse

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornCatalogCategoryNode, PornCatalogVideoPageNode
from .txxx import Txxx
from .upornia import UPornia


class VoyeurHit(UPornia):
    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://voyeurhit.com/categories/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://voyeurhit.com/most-popular/',
            PornCategories.TOP_RATED_VIDEO: 'https://voyeurhit.com/top-rated/',
            PornCategories.LATEST_VIDEO: 'https://voyeurhit.com/latest-updates/',
            PornCategories.LONGEST_VIDEO: 'https://voyeurhit.com/longest/',
            PornCategories.SEARCH_MAIN: 'https://voyeurhit.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://voyeurhit.com/'

    def _set_video_filter(self):
        return super(Txxx, self)._set_video_filter()

    def __init__(self, source_name='VoyeurHit', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(VoyeurHit, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="block-thumb"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span[@class="image"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']

            title_data = category.xpath('./span[@class="item-info"]/span')
            assert len(title_data) == 1
            title = title_data[0].text

            number_of_videos = category.xpath('./span[@class="date"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(x.text.replace(' ', ''))
                for x in (tree.xpath('.//div[@class="pagination"]/ul/li') +
                          tree.xpath('.//div[@class="pagination"]/ul/li/*'))
                if x.text is not None and x.text.replace(' ', '').isdigit()]

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        video_preview_url = dict(
            re.findall(r'(?:\[)(\d+)(?:\])(?:.*?)(https://[\w./-]*/videos)', page_request.text))
        videos = tree.xpath('.//div[@class="list-videos"]div/div/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./div[@class="img"]/img')
            assert len(image_data) == 1
            video_id = image_data[0].attrib['data-video-id'] if 'data-video-id' in image_data[0].attrib else None
            image = image_data[0].attrib['src']
            if video_id is None:
                # We get it from the image link
                video_id = image.split('/')[-3]
            flix_image = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                          for d in range(1, self.number_of_flip_images + 1)]
            video_source = image_data[0].attrib['data-sgid'].split(':')[-1] \
                if 'data-sgid' in image_data[0].attrib else image_data[0].attrib['data-custom3'].split(':')[-1]
            preview_link = (video_preview_url[video_source] +
                            '/{vid_prefix}/{vid}/{vid}_tr.mp4'
                            ''.format(vid_prefix=video_id[:-3]+'000', vid=video_id)) \
                if video_source in video_preview_url else None
            additional_info = {'video_id': video_id}

            title = video_tree_data.xpath('./strong[@class="title"]')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            video_length = video_tree_data.xpath('./div[@class="wrap"]/div[@class="duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            rating = (video_tree_data.xpath('./div[@class="wrap"]/div[@class="rating positive"]') +
                      video_tree_data.xpath('./div[@class="wrap"]/div[@class="rating negative"]'))
            rating = self._clear_text(rating[0].text) if len(rating) == 1 else None

            added_before = (video_tree_data.xpath('./div[@class="wrap"]/div[@class="added"]/em') +
                            video_tree_data.xpath('./div[@class="wrap date-views__wrap"]/div[@class="added"]/em'))
            assert len(added_before) == 1
            added_before = added_before[0].text

            number_of_views = (video_tree_data.xpath('./div[@class="wrap"]/div[@class="views ico ico-eye"]') +
                               video_tree_data.xpath('./div[@class="wrap date-views__wrap"]/'
                                                     'div[@class="views ico ico-eye"]'))
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flix_image,
                                                  preview_video_link=preview_link,
                                                  additional_data=additional_info,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  number_of_views=number_of_views,
                                                  added_before=added_before,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :return: Page request
        """
        if true_object.object_type in self._default_sort_by:
            split_url = fetch_base_url.split('/')
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
            # if true_object.object_type == PornCategories.VIDEO:
            #     page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            #     return page_request

            if self.general_filter.current_filters.general.value is not None:
                self.session.cookies.set(name='category_group_id',
                                         value=self.general_filter.current_filters.general.value,
                                         domain=urlparse(self.base_url).netloc,
                                         )

            if page_number is None:
                page_number = 1
            if split_url[-2].isdigit():
                split_url.pop(-2)
            if page_number > 1:
                split_url.insert(-1, str(page_number))

            program_fetch_url = '/'.join(split_url)
            page_request = self.session.post(program_fetch_url, headers=headers, data=params)
            return page_request
        else:
            return super(VoyeurHit, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                  page_filter, fetch_base_url)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(VoyeurHit, self)._version_stack + [self.__version]
