import re
from .... import urljoin, parse_qs

from ....catalogs.base_catalog import VideoNode
from ....catalogs.porn_catalog import PornCatalogCategoryNode, PornCatalogVideoPageNode

from .extremetube import ExtremeTube


class KeezMoovies(ExtremeTube):
    video_request_format = 'https://www.spankwire.com/api/video/{vid}.json'

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 50000

    @property
    def object_urls(self):
        return {
            CategoryMain: urljoin(self.base_url, '/categories'),
            TagMain: urljoin(self.base_url, '/tags'),
            PornStarMain: urljoin(self.base_url, '/pornstar'),
            LatestVideo: urljoin(self.base_url, '/videos'),
            BeingWatchedVideo: urljoin(self.base_url, '/videos?o=bw'),
            MostViewedVideo: urljoin(self.base_url, '/videos?o=mv'),
            TopRatedVideo: urljoin(self.base_url, '/videos?o=tr'),
            LongestVideo: urljoin(self.base_url, '/videos?o=lg'),
            SearchMain: urljoin(self.base_url, '/video'),
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.keezmovies.com/'

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        self._video_filters = VideoFilter(data_dir=self.fetcher_data_dir,
                                          sort_order=((RelevanceOrder, 'Most relevant', ''),
                                                      (DateOrder, 'Most recent', 'mr'),
                                                      (ViewsOrder, 'Most viewed', 'mv'),
                                                      (RatingOrder, 'Top rated', 'tr'),
                                                      (LengthOrder, 'Longest', 'lg'),
                                                      ),
                                          period_filter=((AllDate, 'All time', ''),
                                                         (OneDate, 'This week', 'w'),
                                                         (TwoDate, 'This month', 'm'),
                                                         ),
                                          )

    def __init__(self, source_name='KeezMoovies', source_id=0, store_dir='.', data_dir='../Data'):
        """
        C'tor
        :param source_name: save directory
        """
        super(KeezMoovies, self).__init__(source_name, source_id, store_dir, data_dir)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)

        headers = tree.xpath('.//div[@class="block_heading"]//h2[@class="h2cat"]')
        bodies = tree.xpath('.//div[@class="float-left"]/a[@class="category_img"]')
        assert len(headers) == len(bodies)
        res = []
        for header, body in zip(headers, bodies):
            title = self._clear_text(header.text)

            number_of_videos = header.xpath('./span[@class="inhsp"]/text()')
            assert len(number_of_videos) == 1
            number_of_videos = re.findall(r'(?:\()(\d*,*\d*)(?: Videos\))', number_of_videos[0])
            assert len(number_of_videos) == 1
            number_of_videos = int(re.sub(',', '', number_of_videos[0]))

            link = urljoin(self.base_url, body.attrib['href'])
            cat_id = body.attrib['href']
            image = body.xpath('./img/@src')
            assert len(image) == 1
            image = image[0]

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=cat_id,
                                                  url=link,
                                                  title=title,
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  object_type=Category,
                                                  super_object=category_data,
                                                  )
            res.append(object_data)
        category_data.add_sub_objects(res)
        return res

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available porn stars.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(porn_star_data)
        tree = self.parser.parse(page_request.text)
        porn_stars = [x for x in tree.xpath('.//ul[@class="all-ps-list main_pornst_block"]/li')
                      if 'class' in x.attrib and 'allpornstars' in x.attrib['class']]
        res = []
        for porn_star in porn_stars:
            link_data = porn_star.xpath('./a')
            assert len(link_data)

            image_data = porn_star.xpath('./a/div/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'blank_pornstarimage.jpg' in image and 'data-srcsmall' in image_data[0].attrib:
                # We fetch another image
                image = image_data[0].attrib['data-srcsmall']
            image = urljoin(porn_star_data.url, image)

            additional_info = porn_star.xpath('./div[@class="pornstar_item_bottom"]/div/span')
            assert len(additional_info) == 6
            number_of_videos = int(additional_info[3].text)
            number_of_photos = int(additional_info[1].text)
            number_of_views = int(re.sub(',', '', additional_info[5].text))

            object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link_data[0].attrib['href'],
                                                  url=urljoin(porn_star_data.url, link_data[0].attrib['href']),
                                                  title=link_data[0].attrib['title'],
                                                  image_link=image,
                                                  number_of_videos=number_of_videos,
                                                  number_of_photos=number_of_photos,
                                                  number_of_views=number_of_views,
                                                  object_type=PornStar,
                                                  super_object=porn_star_data,
                                                  )
            res.append(object_data)
        porn_star_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles. The fetched objects MUST be sorted wrt title.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        links = tree.xpath('.//div[@style="padding:10px;"]/ul[@class="auto"]/a/@href')
        titles = [x.title() for x in tree.xpath('.//div[@style="padding:10px;"]/ul[@class="auto"]/a/li/text()')]
        assert len(links) == len(titles)
        numbers_of_videos = [None] * len(titles)
        return links, titles, numbers_of_videos

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data.
        :return:
        """
        page_request = self.get_object_request(video_data)
        raw_url = re.findall(r'(?:var htmlStr.*ArticleId=")(\d+?)(?:[&"])', page_request.text)
        if len(raw_url) == 0:
            raise RuntimeError('Could not fetch video from page {p}!'.format(p=video_data.url))
        data_url = self.video_request_format.format(vid=raw_url[0])
        headers = {
            'Accept': 'application/json, text/plain, */*, image/webp',
            'Cache-Control': 'max-age=0',
            'Host': 'www.spankwire.com',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(data_url, headers=headers)
        video_data = tmp_request.json()
        if video_data is False:
            raise RuntimeError('Could not fetch video from page {p}!'.format(p=video_data.url))

        video_sources = sorted(((int(re.findall(r'(?:quality_)(\d*)(?:p)', k)[0]), v)
                              for k, v in video_data['videos'].items()),
                             key=lambda y: int(y[0]), reverse=True)
        video_sources = [x[1] for x in video_sources]
        return VideoNode(video_sources=video_sources)

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        # We perform binary search
        start_page = category_data.page_number if category_data.page_number is not None else 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        max_page = max(pages)
        if (max_page - start_page) < self._binary_search_page_threshold:
            return max_page
        else:
            return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _check_is_available_page(self, page_request):
        """
        In binary search performs test whether the current page is available.
        :param page_request: Page request.
        :return:
        """
        return page_request.ok

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        pages = (tree.xpath('.//ul[@class="pagination"]/li/*/text()') +
                 tree.xpath('.//ul[@class="pagination"]/li/text()'))
        return [int(x) for x in pages if x.isdigit()]

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 5

    def get_videos_data(self, object_data):
        """
        Gets videos data for the given category.
        :param object_data: Page data.
        :return:
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        videos = [x for x in tree.xpath('.//ul[@class="ul_video_block"]/li') if 'id' in x.attrib] + \
                 [x for x in tree.xpath('.//ul[@class="ul_ps_video_block videos-pagination"]/li') if 'id' in x.attrib]
        res = []
        for video_tree_data in videos:
            link_data = video_tree_data.xpath('./div[@class="hoverab"]/a')
            assert len(link_data) >= 1
            link = link_data[0].attrib['href']

            image_data = link_data[0].xpath('./img')
            assert len(image_data) >= 1
            image = urljoin(self.base_url, image_data[0].attrib['src'])
            flip_images = [image_data[0].attrib['data-flipbook'].format(index=i)
                           for i in image_data[0].attrib['data-flipbook-values'].split(',')]

            vd_data = video_tree_data.xpath('./div[@class="hoverab"]/div[@class="vd_dr"]/span')
            is_hd = [x for x in vd_data if 'class' in x.attrib]
            is_hd = len(is_hd) > 0 and is_hd[0].attrib['class'] == 'vdIsHD'

            video_length = [x for x in vd_data if 'class' not in x.attrib]
            assert len(video_length) == 1
            video_length = video_length[0].text

            title = video_tree_data.xpath('./div[@class="video_name"]/a')
            assert len(title) == 1
            title = title[0].text if title[0].text is not None else ''

            rating = video_tree_data.xpath('./div[@class="video_extra"]/span[@class="liked_span"]')
            assert len(rating) == 1
            rating = rating[0].text

            viewers = video_tree_data.xpath('./div[@class="video_extra"]/span[@class="views"]')
            assert len(viewers) == 1
            viewers = viewers[0].text

            additional_data = {'id': video_tree_data.attrib['id']}

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  is_hd=is_hd,
                                                  duration=self._format_duration(video_length),
                                                  rating=rating,
                                                  number_of_views=viewers,
                                                  additional_data=additional_data,
                                                  object_type=Video,
                                                  super_object=object_data,
                                                  )
            res.append(video_data)
        object_data.add_sub_objects(res)
        return res

    def get_object_request(self, object_data, override_page_number=None, page_type='regular'):
        """
        Fetches the page number with respect to base url.
        :param object_data: Page data.
        :param override_page_number: Override page number.
        :param page_type: Indicates whether we want to have 'regular' or 'json' page.
        :return: Page request
        """
        if page_type == 'json':
            url, additional_params = self._prepare_request_params(object_data)
            headers = {
                'Accept': '*/*',
                'Cache-Control': 'max-age=0',
                # 'Host': self.host_name,
                'Referer': object_data.url,
                # 'Sec-Fetch-Mode': 'navigate',
                # 'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'X-Requested-With': 'XMLHttpRequest',
            }
        else:
            url = object_data.url
            additional_params = {}
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3',
                'Cache-Control': 'max-age=0',
                # 'Host': self.host_name,
                'Referer': object_data.url,
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent
            }

        if len(object_data.url.split('?')) > 1:
            url = object_data.url.split('?')[0]
            params = object_data.url.split('?')[1]
            params = parse_qs(params)
        else:
            params = {}

        if all(x not in (LatestVideo, BeingWatchedVideo, LongestVideo)
               for x in (object_data.object_type, object_data.super_object.object_type)):
            if all(x not in (MostViewedVideo, TopRatedVideo,)
                   for x in (object_data.object_type, object_data.super_object.object_type)):
                additional_params['o'] = self._video_filters.current_filter_values['sort_order'].value
            additional_params['t'] = self._video_filters.current_filter_values['period'].value

        if object_data.object_type != Video:
            params.update({k: [v] for k, v in additional_params.items() if k not in params})
        page_number = object_data.page_number if override_page_number is None else override_page_number
        if page_number is not None and page_number != 1:
            params['page'] = [page_number]

        page_request = self.session.get(url, headers=headers, params=params)
        return page_request