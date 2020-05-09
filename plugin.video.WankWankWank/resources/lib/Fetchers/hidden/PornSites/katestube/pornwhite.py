import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornCatalogCategoryNode, PornCatalogVideoPageNode
from .katestube import KatesTube


class PornWhite(KatesTube):
    _pagination_class = 'pager'
    _video_page_videos_xpath = './/div[@class="thumbs-list"]/div/a'
    max_flip_images = 5

    @property
    def max_pages(self):
        return 8000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.pornwhite.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://www.pornwhite.com/models/',
            # VideoCategories.CHANNEL_MAIN: 'https://www.pornwhite.com/channels/',
            PornCategories.TAG_MAIN: 'https://www.pornwhite.com/tags/',
            PornCategories.LATEST_VIDEO: 'https://www.pornwhite.com/latest-updates/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.pornwhite.com/top-rated/',
            PornCategories.POPULAR_VIDEO: 'https://www.pornwhite.com/most-popular/',
            PornCategories.SEARCH_MAIN: 'https://www.pornwhite.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornwhite.com/'

    def _prepare_filters(self):
        filters = super(PornWhite, self)._prepare_filters()
        filters['single_tag_args']['sort_order'] = [(PornFilterTypes.DateOrder, 'Recent', None),
                                                    (PornFilterTypes.RatingOrder, 'Top Rated', 'top-rated'),
                                                    (PornFilterTypes.ViewsOrder, 'Most Viewed', 'most-viewed'),
                                                    (PornFilterTypes.LengthOrder, 'Longest', 'longest'),
                                                    ]
        filters['single_category_args']['sort_order'].append((PornFilterTypes.CommentsOrder, 'Commented', 'commented'))
        filters['channels_args'] = None
        filters['categories_args'] = \
            {'sort_order': [(PornFilterTypes.AlphabeticOrder, 'Alphabetically', None),
                            (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'total_videos'),
                            (PornFilterTypes.VideosRatingOrder, 'Video Rating', 'avg_videos_rating'),
                            (PornFilterTypes.VideosPopularityOrder, 'Video Popularity', 'avg_videos_popularity'),
                            ],
             }
        filters['porn_stars_args'] = \
            {'sort_order': [(PornFilterTypes.RatingOrder, 'Video Rating', 'rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.PopularityOrder, 'Popularity', 'model_viewed'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Number of Videos', 'total_videos'),
                            (PornFilterTypes.VideosRatingOrder, 'Video Rating', 'avg_videos_rating'),
                            (PornFilterTypes.VideosPopularityOrder, 'Video Popularity', 'avg_videos_popularity'),
                            ],
             }
        filters['single_porn_star_args'] = filters['single_category_args']

        return filters

    # def _set_video_filter(self):
    #     """
    #     Sets the video filters and the default values of the current filters
    #     :return:
    #     """
    #     ret super(PornWhite, self)._set_video_filter()

    def __init__(self, source_name='PornWhite', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PornWhite, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

    def _update_available_base_object(self, object_data, xpath, object_type):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath(xpath)
        res = []
        for category in categories:
            link = category.attrib['href']

            image_data = category.xpath('./span[@class="img"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-original'] \
                if 'data-original' in image_data[0].attrib else image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('.//span[@class="vids"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(object_data.url, link),
                                               title=title,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=object_type,
                                               super_object=object_data,
                                               ))

        object_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="tags-list"]/div[@class="item"]/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.attrib['title'],
                                                 int(re.findall(r'\d+', x.xpath('./b')[0].tail)[0]))
                                                for x in raw_objects])
        return links, titles, number_of_videos

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return 2

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath(self._video_page_videos_xpath)
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./span[@class="img"]')
            assert len(image_data) == 1
            video_preview = image_data[0].attrib['data-src']
            image = image_data[0].attrib['data-poster']
            flip_images = [re.sub(r'\d+.jpg', '{p}.jpg'.format(p=p), image)
                           for p in range(1, self.max_flip_images + 1)]

            is_hd = video_tree_data.xpath('./span[@class="img"]/span[@class="hd"]')
            is_hd = len(is_hd) == 1 and is_hd[0].text == 'HD'

            video_length = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="info-holder"]/'
                                                 'span[@class="length"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            number_of_views = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="info-holder"]/'
                                                    'span[@class="views"]')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            title = video_tree_data.xpath('./span[@class="thumb-info"]/b')
            assert len(title) == 1
            title = title[0].text

            rating = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="info-holder"]/'
                                           'span[@class="item-rating"]')
            assert len(rating) == 1
            rating = rating[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  is_hd=is_hd,
                                                  duration=self._format_duration(video_length),
                                                  number_of_views=number_of_views,
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        split_url = fetch_base_url.split('/')

        if true_object.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.PORN_STAR_MAIN):
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
            if page_filter.sort_order.value is not None:
                params['sort_by'] = [page_filter.sort_order.value]
            fetch_base_url = '/'.join(split_url)
            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            return super(PornWhite, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                                  page_filter, fetch_base_url)
