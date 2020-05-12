import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornCatalogCategoryNode, PornCatalogVideoPageNode
from .katestube import KatesTube


class PervClips(KatesTube):
    _pagination_class = 'pagination'
    _video_page_videos_xpath = './/div[@class="thumbs-holder"]/div/div/a'
    max_flip_images = 5

    @property
    def max_pages(self):
        return 8000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.pervclips.com/tube/categories/',
            # VideoCategories.CHANNEL_MAIN: 'https://www.pervclips.com/tube/channels/',
            PornCategories.TAG_MAIN: 'https://www.pervclips.com/tube/tags/',
            PornCategories.LATEST_VIDEO: 'https://www.pervclips.com/tube/latest-updates/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.pervclips.com/tube/top-rated/',
            PornCategories.POPULAR_VIDEO: 'https://www.pervclips.com/tube/most-popular/',
            PornCategories.LONGEST_VIDEO: 'https://www.pervclips.com/tube/longest/',
            PornCategories.MOST_DISCUSSED_VIDEO: 'https://www.pervclips.com/tube/commented/',
            PornCategories.SEARCH_MAIN: 'https://www.pervclips.com/tube/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
            PornCategories.LONGEST_VIDEO: PornFilterTypes.LengthOrder,
            PornCategories.MOST_DISCUSSED_VIDEO: PornFilterTypes.CommentsOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pervclips.com/'

    def _prepare_filters(self):
        filters = super(PervClips, self)._prepare_filters()
        filters['single_category_args']['sort_order'].append((PornFilterTypes.CommentsOrder, 'Commented', 'commented'))
        filters['single_category_args']['sort_order'][0] = (PornFilterTypes.DateOrder, 'Recent', 'latest')
        filters['channels_args'] = None
        return filters

    def __init__(self, source_name='PervClips', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PervClips, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                        session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="items-list new_cat"]/div[@class="item"]/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            description = category.attrib['title']

            image_data = category.xpath('./div[@class="img-holder"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-original'] \
                if 'data-original' in image_data[0].attrib else image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="title-holder"]/div[@class="quantity-videos"]/'
                                              'span[@class="quantity"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(number_of_videos[0].text)

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(category_data.url, link),
                                               title=title,
                                               description=description,
                                               image_link=image,
                                               number_of_videos=number_of_videos,
                                               object_type=PornCategories.CATEGORY,
                                               super_object=category_data,
                                               ))

        category_data.add_sub_objects(res)
        return res

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="list-tags"]/div[@class="item"]/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.attrib['title'], int(x.xpath('./span')[0].text))
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
            video_preview = video_tree_data.attrib['data-src']
            image = video_tree_data.attrib['data-poster']
            flip_images = [re.sub(r'\d+.jpg', '{p}.jpg'.format(p=p), image)
                           for p in range(1, self.max_flip_images + 1)]

            is_hd = video_tree_data.xpath('./div[@class="img-holder"]/div[@class="hd-holder"]')
            is_hd = len(is_hd) == 1

            video_length = video_tree_data.xpath('./div[@class="img-holder"]/div[@class="time-holder"]')
            assert len(video_length) == 1
            video_length = self._clear_text(video_length[0].text)

            number_of_views = video_tree_data.xpath('./div[@class="title-item"]/div[@class="item-info"]/'
                                                    'span[@class="views-info"]/i')
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].tail)

            added_before = video_tree_data.xpath('./div[@class="title-item"]/div[@class="item-info"]/'
                                                 'meta[@itemprop="datePublished"]')
            assert len(added_before) == 1
            added_before = added_before[0].attrib['content']

            rating = video_tree_data.xpath('./div[@class="title-item"]/div[@class="item-info"]/'
                                           'span[@class="rating-info"]/span[@class="rating"]/i')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].tail)

            title = video_tree_data.xpath('./div[@class="title-item"]/p')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

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
                                                  added_before=added_before,
                                                  rating=rating,
                                                  object_type=PornCategories.VIDEO,
                                                  super_object=page_data,
                                                  )
            res.append(video_data)
        page_data.add_sub_objects(res)
        return res

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(PervClips, self)._version_stack + [self.__version]
