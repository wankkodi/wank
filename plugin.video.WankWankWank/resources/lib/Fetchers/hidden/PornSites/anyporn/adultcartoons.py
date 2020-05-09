import re
from .... import urljoin, parse_qsl

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornCatalogCategoryNode, PornCatalogVideoPageNode
from .pornbimbo import PornBimbo


class AdultCartoons(PornBimbo):
    max_flip_images = 30
    videos_per_video_page = 31

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.MOST_VIEWED_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.LONGEST_VIDEO: urljoin(self.base_url, '/longest/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
        }

    def _prepare_filters(self):
        """
        Prepares the filters
        :return:
        """
        video_sort_order = [(PornFilterTypes.DateOrder, 'New', 'post_date'),
                            (PornFilterTypes.RatingOrder, 'Top rated', 'rating'),
                            (PornFilterTypes.ViewsOrder, 'Most viewed', 'video_viewed'),
                            (PornFilterTypes.LengthOrder, 'Longest', 'duration'),
                            ]
        video_period = ([(PornFilterTypes.AllDate, 'All time', ''),
                         (PornFilterTypes.OneDate, 'This Month', '_month'),
                         (PornFilterTypes.TwoDate, 'This week', '_week'),
                         (PornFilterTypes.ThreeDate, 'Today', '_today'),
                         ],
                        [('sort_order', [PornFilterTypes.RatingOrder,
                                         PornFilterTypes.ViewsOrder])]
                        )
        search_sort_order = [(PornFilterTypes.RelevanceOrder, 'Most Relevant', '')] + video_sort_order

        category_params = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'avg_videos_popularity'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            ],
             }
        porn_stars_params = None
        actress_params = None
        channel_params = porn_stars_params
        tag_params = None
        video_params = {'sort_order': video_sort_order,
                        'period_filters': video_period,
                        }
        search_params = {'sort_order': search_sort_order,
                         'period_filters': video_period,
                         }

        return (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
                search_params)

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.adultcartoons.com/'

    @property
    def max_pages(self):
        return 2000

    def __init__(self, source_name='AdultCartoons', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(AdultCartoons, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                            session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        return self._update_available_base_object(category_data,
                                                  './/div[@class="thumbs category_list"]/'
                                                  'div[@class="thumb grid item"]/a',
                                                  PornCategories.CATEGORY)

    def _update_available_base_object(self, object_data, xpath, object_type, is_sort=False):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        res = []
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('div[@class="img"]/img')
            image = image_data[0].attrib['src'] if len(image_data) == 1 else None
            title = category.attrib['title'] if 'title' in category.attrib else \
                (image_data[0].attrib['alt'] if 'alt' in image_data[0].attrib else
                 image_data[0].xpath('./span[@class="author uppercase"]')[0].text)

            category_data = category.xpath('./span[@class="sub_info"]/span/span')
            if len(category_data) == 1:
                number_of_views = None
                number_of_videos = int(re.findall(r'\d+', category_data[0].text)[0])
                number_of_photos = None
            elif len(category_data) == 3:
                number_of_views = int(re.findall(r'\d+', category_data[0].text)[0])
                number_of_videos = int(re.findall(r'\d+', category_data[1].text)[0])
                number_of_photos = int(re.findall(r'\d+', category_data[2].text)[0])
            else:
                number_of_views = None
                number_of_videos = None
                number_of_photos = None

            sub_object_data = PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      number_of_views=number_of_views,
                                                      number_of_videos=number_of_videos,
                                                      number_of_photos=number_of_photos,
                                                      object_type=object_type,
                                                      super_object=object_data,
                                                      )
            res.append(sub_object_data)
        object_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_data = tree.xpath('.//div[@class="tags-holder"]//div[@class="item"]/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.xpath('./strong')[0].text,
                                                 int(re.findall(r'\d+', x.xpath('./span')[0].text)[0]))
                                                for x in raw_data])
        return links, titles, number_of_videos

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Extracts category number of videos out of category data.
        :param fetched_request:
        :param category_data: Category data (dict).
        :return:
        """
        if category_data.object_type in (PornCategories.TAG_MAIN, PornCategories.CATEGORY_MAIN, ):
            return 1
        page_request = self.get_object_request(category_data) if fetched_request is None else fetched_request
        tree = self.parser.parse(page_request.text)
        pages = self._get_available_pages_from_tree(tree)
        if len(pages) == 0:
            return 1
        if category_data.object_type in (PornCategories.SEARCH_MAIN, PornCategories.PORN_STAR_MAIN):
            return max(pages)
        else:
            if max(pages) - 1 < self._binary_search_page_threshold:
                return max(pages)
            else:
                return self._binary_search_max_number_of_pages(category_data, last_available_number_of_pages)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        res = ([int(x.attrib['data-parameters'].split(':')[-1])
                for x in tree.xpath('.//ul[@class="pagination"]/li/a')
                if 'data-parameters' in x.attrib and x.attrib['data-parameters'].split(':')[-1].isdigit()] +
               [int(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])[0])
                for x in tree.xpath('.//ul[@class="pagination"]/li/a')
                if 'href' in x.attrib and len(re.findall(r'(\d+)(?:/*$)', x.attrib['href'])) > 0]
               )
        if len(res) == 0:
            xpath = './/div[@class="load-more"]/a'
            return [int(re.findall(r'(?:from.*?:)(\d+)', x.attrib['data-parameters'])[0])
                    for x in tree.xpath(xpath)
                    if 'data-parameters' in x.attrib and
                    len(re.findall(r'(?:from.*?:)(\d+)', x.attrib['data-parameters'])) > 0]
        return res

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        # Took from AnyPorn module with somme modifications...
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumbs videos_list"]/div[@class="item thumb"]/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']
            title = video_tree_data.attrib['title'] if 'title' in video_tree_data.attrib else None

            image_data = video_tree_data.xpath('./div[@class="img wrap_image"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            flip_images = [re.sub(r'\d+.jpg', '{d}.jpg'.format(d=d), image) for d in range(1, self.flip_number + 1)]
            if title is None:
                title = image_data[0].attrib['alt']

            video_length = video_tree_data.xpath('./div[@class="img wrap_image"]/div[@class="sticky"]/'
                                                 'div[@class="time"]')
            assert len(video_length) == 1
            video_length = self._format_duration(self._clear_text(video_length[0].text))

            is_hd = video_tree_data.xpath('./div[@class="img wrap_image"]/div[@class="sticky"]/div[@class="quality"]')
            is_hd = len(is_hd) == 1 and is_hd[0].text == 'HD'

            if title is None:
                title = self._clear_text(video_tree_data.xpath('./div[@class="tools"]/div[@class="title"]')[0].text)

            uploader = self._clear_text(video_tree_data.xpath('./div[@class="tools"]/div[@class="columns"]/'
                                                              'div[@class="column"]/div[@class="name"]')[0].text)
            additional_data = {'uploader': uploader}
            rating = self._clear_text(video_tree_data.xpath('./div[@class="tools"]/div[@class="columns"]/'
                                                            'div[@class="column second"]/div[@class="rate"]/'
                                                            'span')[0].text)
            count_data = video_tree_data.xpath('./div[@class="tools"]/div[@class="info"]/div[@class="count"]')
            assert len(count_data) == 2
            number_of_views = int(''.join(re.findall(r'\d+', count_data[0].text)))
            added_before = count_data[1].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(self.base_url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  is_hd=is_hd,
                                                  duration=video_length,
                                                  number_of_views=number_of_views,
                                                  additional_data=additional_data,
                                                  rating=rating,
                                                  added_before=added_before,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        headers = {
            'Accept': '*.*',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        if page_number is None:
            page_number = 1
        params.update({
            'mode': 'async',
            'function': 'get_block',
        })
        if page_filter.length.value is not None:
            params.update(parse_qsl(page_filter.length.value))
        if page_number > 1:
            params['from'] = str(page_number).zfill(2)
        if true_object.object_type == PornCategories.LATEST_VIDEO:
            params['block_id'] = 'list_videos_common_videos_list'
            params['sort_by'] = page_filter.sort_order.value
            params['ipp'] = self.videos_per_video_page
        else:
            return super(AdultCartoons, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                      page_filter, fetch_base_url)

        page_request = self.session.get(fetch_base_url, headers=headers, params=params)
        return page_request
