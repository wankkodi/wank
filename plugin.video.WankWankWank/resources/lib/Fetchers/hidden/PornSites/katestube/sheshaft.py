import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornCatalogVideoPageNode
from .pornwhite import PornWhite


class SheShaft(PornWhite):
    # todo: to change the general object type to shemale...
    _pagination_class = 'pagination'
    _video_page_videos_xpath = './/div[@class="thumbs-list"]/div/a'
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
        filters = super(SheShaft, self)._prepare_filters()
        filters['porn_stars_args'] = None
        filters['single_porn_star_args'] = None
        return filters

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.sheshaft.com/'

    def __init__(self, source_name='SheShaft', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(SheShaft, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

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
            is_hd = image_data[0].xpath('./span[@class="hd"]')
            is_hd = len(is_hd) == 1 and is_hd[0].text == 'hd'

            video_length = video_tree_data.xpath('./span[@class="img"]/span[@itemprop="duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            number_of_views = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="views"]')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            title = video_tree_data.xpath('./span[@class="thumb-info"]/b')
            assert len(title) == 1
            title = title[0].text

            rating = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="rating-holder"]/'
                                           'span[@class="item-rating"]')
            assert len(rating) == 1
            rating = rating[0].text

            video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                  obj_id=link,
                                                  url=urljoin(page_data.url, link),
                                                  title=title,
                                                  image_link=image,
                                                  is_hd=is_hd,
                                                  flip_images_link=flip_images,
                                                  preview_video_link=video_preview,
                                                  duration=self._format_duration(video_length),
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
        return super(SheShaft, self)._version_stack + [self.__version]
