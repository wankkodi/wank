import re
from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes, PornCatalogVideoPageNode
from .upornia import UPornia


class HotMovs(UPornia):
    number_of_flip_images = 15

    @property
    def object_urls(self):
        res = super(HotMovs, self).object_urls
        res[PornCategories.TAG_MAIN] = urljoin(self.base_url, '/categories/')
        return res

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://hotmovs.com/'

    def _prepare_filters(self):
        _, video_filters, video_filters, categories_filters, porn_stars_filters, channels_filters = \
            super(HotMovs, self)._prepare_filters()
        general_filters = {'general_filters': ((PornFilterTypes.StraightType, 'Heterosexual', '66'),
                                               (PornFilterTypes.GayType, 'Gay', '67'),
                                               (PornFilterTypes.ShemaleType, 'Transgender', '68'),
                                               ),
                           }
        return general_filters, video_filters, video_filters, categories_filters, porn_stars_filters, channels_filters

    def __init__(self, source_name='HotMovs', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(HotMovs, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                      session_id)

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return [int(self._clear_text(x.text).replace(' ', ''))
                for x in tree.xpath('.//ul[@class="pagination pagination-lg"]/li/*')
                if x.text is not None and self._clear_text(x.text).replace(' ', '').isdigit()]

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles.
        :param page_request: Page request.
        :return:
        """
        tree = self.parser.parse(page_request.text)
        links = tree.xpath('.//ul[@class="list-categories list-group list-group--minimalism"]//'
                           'li[@class="list-group-item"]/a/@href')
        titles = tree.xpath('.//ul[@class="list-categories list-group list-group--minimalism"]//'
                            'li[@class="list-group-item"]/a/text()')
        number_of_videos = [int(x.text.replace(',', ''))
                            for x in tree.xpath('.//ul[@class="list-categories list-group list-group--minimalism"]//'
                                                'li[@class="list-group-item"]//'
                                                'span[@class="list-group-item__action__count"]')]
        assert len(titles) == len(links)
        assert len(titles) == len(number_of_videos)

        return links, titles, number_of_videos

    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Page data.
        :return:
        """
        page_request = self.get_object_request(page_data)
        tree = self.parser.parse(page_request.text)
        video_preview_url = dict(
            re.findall(r'(?:\[)(\d+)(?:\])(?:.*?)(https://cdn\d+.ahacdn.me/c\d+/videos)', page_request.text))
        videos = (tree.xpath('.//div[@id="list_videos2_common_videos_list_items"]/article/a') +
                  tree.xpath('.//div[@id="sphinx_list_cat_videos_videos_list_items"]/article/a') +
                  tree.xpath('.//div[@id="list_videos_videos_list_search_result_items"]/article/a'))
        res = []
        for video_tree_data in videos:
            link = video_tree_data.attrib['href']

            video_id = video_tree_data.xpath('./div[@class="thumbnail__label thumbnail__label--watch-later"]')
            assert len(video_id) == 1
            video_id = video_id[0].attrib['data-video-id']

            image_data = video_tree_data.xpath('./img')
            assert len(image_data) == 1
            image = image_data[0].attrib['src']
            flix_image = [re.sub(r'\d+.jpg$', '{d}.jpg'.format(d=d), image)
                          for d in range(1, self.number_of_flip_images + 1)]
            video_source = image_data[0].attrib['data-custom3'].split(':')[-1]
            preview_link = (video_preview_url[video_source] +
                            '/{vid_prefix}/{vid}/{vid}_tr.mp4'
                            ''.format(vid_prefix=video_id[:-3]+'000', vid=video_id)) \
                if video_source in video_preview_url else None
            additional_info = {'video_id': video_id}

            video_length = video_tree_data.xpath('./div[@class="thumbnail__info"]/'
                                                 'div[@class="thumbnail__info__right"]')
            assert len(video_length) == 1
            video_length = video_length[0].text

            title = video_tree_data.xpath('./div[@class="thumbnail__info"]/div[@class="thumbnail__info__left"]/h5')
            assert len(title) == 1
            title = title[0].text

            rating = (video_tree_data.xpath('./div[@class="thumbnail__info__left"]/i'))
            rating = rating[0].tail if len(rating) == 1 else None

            number_of_views = (video_tree_data.xpath('./div[@class="thumbnail__info thumbnail__info--hover"]/'
                                                     'div[@class="thumbnail__info__right"]/i'))
            assert len(number_of_views) == 1
            number_of_views = self._clear_text(number_of_views[0].tail)

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
        return super(HotMovs, self)._version_stack + [self.__version]
