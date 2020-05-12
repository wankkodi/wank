import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornCatalogCategoryNode, PornCatalogVideoPageNode
from .pornwhite import PornWhite


class PorniCom(PornWhite):
    _pagination_class = 'pagination'
    _video_page_videos_xpath = './/div[@class="thumbs-holder"]/div/div/div'
    max_flip_images = 5

    @property
    def max_pages(self):
        return 8000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: urljoin(self.base_url, '/categories/'),
            PornCategories.TAG_MAIN: urljoin(self.base_url, '/tags/'),
            PornCategories.LATEST_VIDEO: urljoin(self.base_url, '/latest-updates/'),
            PornCategories.TOP_RATED_VIDEO: urljoin(self.base_url, '/top-rated/'),
            PornCategories.POPULAR_VIDEO: urljoin(self.base_url, '/most-popular/'),
            PornCategories.SEARCH_MAIN: urljoin(self.base_url, '/search/'),
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
            PornCategories.POPULAR_VIDEO: PornFilterTypes.PopularityOrder,
        }

    def _prepare_filters(self):
        filters = super(PorniCom, self)._prepare_filters()
        filters['porn_stars_args'] = None
        filters['single_porn_star_args'] = None
        return filters

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.pornicom.com/'

    def __init__(self, source_name='PorniCom', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(PorniCom, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="items-list"]/div/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            # title = category.attrib['title']

            image_data = category.xpath('./div[@class="img-holder"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-original'] \
                if 'data-original' in image_data[0].attrib else image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./div[@class="title-holder"]/div[@class="quantity-videos"]/'
                                              'span[@class="quantity"]')
            assert len(number_of_videos) == 1
            number_of_videos = int(re.findall(r'\d+', number_of_videos[0].text)[0])

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(category_data.url, link),
                                               title=title,
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
        links, titles, number_of_videos = zip(*[(x.attrib['href'], self._clear_text(x.text),
                                                 int(x.xpath('./span')[0].text[1:-1]))
                                                for x in raw_objects])
        return links, titles, number_of_videos

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
            image_data = video_tree_data.xpath('./div[@class="img-holder image"]')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-poster']
            video_preview = image_data[0].attrib['data-src'] if 'data-src' in image_data[0].attrib else None
            flip_images = [re.sub(r'\d+.jpg', '{p}.jpg'.format(p=p), image)
                           for p in range(1, self.max_flip_images + 1)]

            is_hd = image_data[0].xpath('./div[@class="hd-holder"]/span')
            is_hd = len(is_hd) == 1 and 'class' in is_hd[0].attrib and is_hd[0].attrib['class'] == 'hd'

            video_length = image_data[0].xpath('./div[@class="time-holder"]/span[@class="time"]/meta')
            assert len(video_length) == 1
            video_length = self._format_duration(video_length[0].attrib['content'])

            link_data = video_tree_data.xpath('./a')
            assert len(link_data) == 1
            link = link_data[0].attrib['href']

            title = link_data[0].xpath('./p')
            assert len(title) == 1
            title = self._clear_text(title[0].text)

            added_before = link_data[0].xpath('./meta')
            assert len(added_before) == 1
            added_before = added_before[0].attrib['content']

            info_data = link_data[0].xpath('./div[@class="item-info"]')
            assert len(info_data) == 1

            rating = info_data[0].xpath('./span[@class="rating-info"]/span[@class="rating"]/i')
            assert len(rating) == 1
            rating = self._clear_text(rating[0].tail)

            number_of_views = info_data[0].xpath('./span[@class="views-info"]/i')
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].tail)

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  is_hd=is_hd,
                                                  added_before=added_before,
                                                  duration=video_length,
                                                  number_of_views=number_of_views,
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
        return super(PorniCom, self)._version_stack + [self.__version]
