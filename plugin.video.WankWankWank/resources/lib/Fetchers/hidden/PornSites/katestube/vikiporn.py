import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornCatalogCategoryNode, PornCatalogVideoPageNode
from .pornwhite import PornWhite


class VikiPorn(PornWhite):
    _pagination_class = 'paging-area'
    _video_page_videos_xpath = './/div[@class="thumbs-list"]/div/a'
    max_flip_images = 5

    @property
    def max_pages(self):
        return 8000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.vikiporn.com/categories/',
            PornCategories.TAG_MAIN: 'https://www.vikiporn.com/tags/',
            PornCategories.LATEST_VIDEO: 'https://www.vikiporn.com/latest-updates/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.vikiporn.com/top-rated/',
            PornCategories.POPULAR_VIDEO: 'https://www.vikiporn.com/most-popular/',
            PornCategories.SEARCH_MAIN: 'https://www.vikiporn.com/search/',
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
        return 'https://www.vikiporn.com/'

    def __init__(self, source_name='VikiPorn', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(VikiPorn, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                       session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@class="categories-thumbs"]/div/a')
        res = []
        for category in categories:
            link = category.attrib['href']
            # title = category.attrib['title']

            image_data = category.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['data-original'] \
                if 'data-original' in image_data[0].attrib else image_data[0].attrib['src']
            title = image_data[0].attrib['alt']

            number_of_videos = category.xpath('./i')
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
        tree = self.parser.parse(page_request.text)
        raw_objects = tree.xpath('.//div[@class="tags-list"]/div[@class="item"]/a')
        links, titles, number_of_videos = zip(*[(x.attrib['href'], x.attrib['title'],
                                                 int(re.findall(r'\d', x.xpath('./span')[0].text)[0]))
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
            link = video_tree_data.attrib['href']

            image_data = video_tree_data.xpath('./span[@class="img"]')
            assert len(image_data) == 1
            video_preview = image_data[0].attrib['data-src']
            image = image_data[0].attrib['data-poster']
            flip_images = [re.sub(r'\d+.jpg', '{p}.jpg'.format(p=p), image)
                           for p in range(1, self.max_flip_images + 1)]

            is_hd = video_tree_data.xpath('./span[@class="img"]/span[@class="hd"]')
            is_hd = len(is_hd) == 1 and is_hd[0].text == 'HD'

            video_length = video_tree_data.xpath('./span[@class="img"]/span[@itemprop="duration"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            number_of_views = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="views"]/span')
            assert len(number_of_views) == 1
            number_of_views = number_of_views[0].text

            title = video_tree_data.xpath('./span[@class="thumb-info"]/b')
            assert len(title) == 1
            title = title[0].text

            rating = video_tree_data.xpath('./span[@class="thumb-info"]/span[@class="item-rating"]/span')
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

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(VikiPorn, self)._version_stack + [self.__version]
