from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornCatalogVideoPageNode
from .madthumbs import MadThumbs


class Xozilla(MadThumbs):
    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    @property
    def object_urls(self):
        return {
            PornCategories.CATEGORY_MAIN: 'https://www.xozilla.com/categories/',
            PornCategories.PORN_STAR_MAIN: 'https://www.xozilla.com/models/',
            PornCategories.CHANNEL_MAIN: 'https://www.xozilla.com/channels/',
            PornCategories.LATEST_VIDEO: 'https://www.xozilla.com/latest-updates/',
            PornCategories.MOST_VIEWED_VIDEO: 'https://www.xozilla.com/most-popular/',
            PornCategories.TOP_RATED_VIDEO: 'https://www.xozilla.com/top-rated/',
            PornCategories.SEARCH_MAIN: 'https://www.xozilla.com/search/',
        }

    @property
    def _default_sort_by(self):
        return {
            PornCategories.LATEST_VIDEO: PornFilterTypes.DateOrder,
            PornCategories.MOST_VIEWED_VIDEO: PornFilterTypes.ViewsOrder,
            PornCategories.TOP_RATED_VIDEO: PornFilterTypes.RatingOrder,
        }

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.xozilla.com/'

    @property
    def number_of_videos_per_page(self):
        """
        Base site url.
        :return:
        """
        return 30  # 5*6

    def __init__(self, source_name='Xozilla', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Xozilla, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="list-videos"]/div[@class="margin-fix"]/a')
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']
            video_preview = video_tree_data.attrib['vthumb'] if 'vthumb' in video_tree_data.attrib else None

            image_data = video_tree_data.xpath('./div[@class="img ithumb"]/img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            if 'data:image' in image:
                image = image_data[0].attrib['data-original']
            title = video_tree_data.attrib['title'] \
                if 'title' in video_tree_data.attrib else image_data[0].attrib['alt']

            is_hd = 'class="hd-label"' in video_tree_data.xpath('./div[@class="img ithumb"]/*')[1].text

            video_length = video_tree_data.xpath('./div[@class="img ithumb"]/div[@class="duration"]')
            assert len(video_length) == 1

            res.append(PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                obj_id=link,
                                                title=title,
                                                url=urljoin(page_data.url, link),
                                                image_link=image,
                                                preview_video_link=video_preview,
                                                is_hd=is_hd,
                                                duration=self._format_duration(video_length[0].text),
                                                object_type=PornCategories.VIDEO,
                                                super_object=page_data,
                                                ))

        if self.get_proper_filter(page_data).current_filters.quality.filter_id == PornFilterTypes.HDQuality:
            res = [x for x in res if x.is_hd is True]
        page_data.add_sub_objects(res)
        return res

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Xozilla, self)._version_stack + [self.__version]
