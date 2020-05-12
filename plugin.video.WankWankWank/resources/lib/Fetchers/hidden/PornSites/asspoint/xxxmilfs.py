from . import Base2
import re

from .... import urljoin

from ....catalogs.porn_catalog import PornCategories, PornCatalogCategoryNode, PornCatalogVideoPageNode


class XXXMilfs(Base2):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.xxxmilfs.com/'

    def __init__(self, source_name='XXXMilfs', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super().__init__(source_name, source_id, store_dir, data_dir, source_type,
                         use_web_server, session_id)

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (JSON).
        """
        page_request = self.get_object_request(category_data)
        tree = self.parser.parse(page_request.text)
        categories = tree.xpath('.//div[@style="width: 1000px"]/div[@style="width: 240px; float: left; text-align: '
                                'center; margin: 4px; padding: 0px; border: 1px solid #ECECD3"]')
        res = []
        for category in categories:
            link_data = category.xpath('./a')
            assert len(link_data) > 0
            link = link_data[0].attrib['href']

            title_data = category.xpath('./a/font/b')
            assert len(title_data) > 0
            title = self._clear_text(title_data[0].text) if title_data[0].text is not None else 'Unknown category'

            image = category.xpath('./a/img')
            assert len(image) == 1
            image = image[0].attrib['src']

            res.append(PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                               obj_id=link,
                                               url=urljoin(self.base_url, link),
                                               image_link=image,
                                               title=title,
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
        return [int(x.text) for x in tree.xpath('.//div[@class="pages2"]/ul/li/a')
                if x.text is not None and x.text.isdigit()]

    def get_videos_data(self, object_data):
        """
        Gets videos data for the given category.
        :param object_data: Page data.
        :return:
        """
        page_request = self.get_object_request(object_data)
        tree = self.parser.parse(page_request.text)
        videos = tree.xpath('.//div[@class="thumbs"]/div[@class="th"]/div[@class="thumb"]')
        if len(videos) > 0:
            method = 1
        else:
            # We try another method
            videos = [x for x in tree.xpath('.//div[@class="left-6"]/div')
                      if 'class' in x.attrib and 'group' in x.attrib['class']]
            method = 2
        res = []
        if method == 1:
            for video_tree_data in videos:
                link_data = video_tree_data.xpath('./a')
                if len(link_data) != 1:
                    continue
                link = link_data[0].attrib['href']

                image_data = video_tree_data.xpath('./div[@class="t"]/a/img')
                assert len(image_data) == 1
                image = image_data[0].attrib['src']
                flip_images = [re.sub(r'main.jpg$', '{d}.jpg'.format(d=d), image)
                               for d in range(1, int(re.findall(r'(?:\')(\d+)(?:\')',
                                                                image_data[0].attrib['onmouseover'])[0]))]
                title = image_data[0].attrib['alt']

                rating = video_tree_data.xpath('./div[@class="desc"]/div[@class="star_static"]/ul/li')
                assert len(rating) == 1
                rating = re.findall(r'\d+%', rating[0].attrib['style'])[0]

                video_length = video_tree_data.xpath('./div[@class="desc"]/p[@class="lenght"]')
                assert len(video_length) == 1
                video_length = video_length[0].text

                number_of_views = video_tree_data.xpath('./div[@class="desc"]/p[@class="views"]')
                assert len(number_of_views) == 1
                number_of_views = number_of_views[0].text + number_of_views[0].xpath('./span')[0].text

                added_before = video_tree_data.xpath('./div[@class="desc"]/p[@class="ago"]')
                assert len(added_before) == 1
                added_before = added_before[0].text

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      flip_images_link=flip_images,
                                                      duration=self._format_duration(video_length),
                                                      number_of_views=number_of_views,
                                                      rating=rating,
                                                      added_before=added_before,
                                                      object_type=PornCategories.VIDEO,
                                                      super_object=object_data,
                                                      )
                res.append(video_data)
        else:
            for video_tree_data in videos:
                link_data = video_tree_data.xpath('./div[@class="gr-l"]/div[@class="grab-lx"]/a')
                if len(link_data) != 1:
                    continue
                link = link_data[0].attrib['href']

                image_data = video_tree_data.xpath('./div[@class="gr-l"]/div[@class="grab-lx"]/a/img')
                assert len(image_data) == 1
                image = image_data[0].attrib['src']
                title = image_data[0].attrib['alt']
                flip_images = [re.sub(r'main.jpg$', '{d}.jpg'.format(d=d), image)
                               for d in range(1, int(re.findall(r'(?:\')(\d+)(?:\')',
                                                                image_data[0].attrib['onmouseover'])[0]) + 1)]

                video_info = video_tree_data.xpath('./div[@class="gr-l"]/div[@class="grab-rx"]/'
                                                   'p[@class="gr-st2"]//span')
                assert len(video_info) == 3
                video_length = video_info[0].text
                added_before = video_info[1].text
                number_of_views = video_info[2].text

                rating = video_tree_data.xpath('./div[@class="gr-l"]/div[@class="grab-rx"]/div[@class="star_static"]/'
                                               'ul/li')
                assert len(rating) == 1
                rating = re.findall(r'\d%', rating[0].attrib['style'])[0]

                category_data = video_tree_data.xpath('./div[@class="gr-r"]/p//a')
                assert len(category_data) >= 2
                tag_data = video_tree_data.xpath('./div[@class="gr-r"]/div[@class="tags2"]/div/a')
                assert len(category_data) > 0
                additional_data = {'main_category': {'title': category_data[0].text,
                                                     'link': category_data[0].attrib['href']},
                                   'categories': [{'title': x.text,
                                                   'link': x.attrib['href']} for x in category_data[1:]],
                                   'tags': [{'title': x.xpath('./span')[0].text,
                                             'link': x.attrib['href']} for x in tag_data]
                                   }

                video_data = PornCatalogVideoPageNode(catalog_manager=self.catalog_manager,
                                                      obj_id=link,
                                                      url=urljoin(self.base_url, link),
                                                      title=title,
                                                      image_link=image,
                                                      flip_images_link=flip_images,
                                                      duration=self._format_duration(video_length),
                                                      number_of_views=number_of_views,
                                                      rating=rating,
                                                      added_before=added_before,
                                                      additional_data=additional_data,
                                                      object_type=PornCategories.VIDEO,
                                                      super_object=object_data,
                                                      )
                res.append(video_data)

        object_data.add_sub_objects(res)
        return res

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(XXXMilfs, self)._version_stack + [self.__version]
