import re
from .... import urljoin

from ....catalogs.base_catalog import VideoNode
from ....catalogs.vod_catalog import VODCategories, VODCatalogNode
from .base import Base


class Bip(Base):
    time_format = '%M:%S'
    season1_title = 'עונה 1'

    def __init__(self, vod_name='Bip', vod_id=-2, store_dir='.', data_dir='../../Data', source_type='VOD',
                 use_web_server=False, session_id=None):
        super(Bip, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, use_web_server, session_id)

    @property
    def object_urls(self):
        return {
            VODCategories.CHANNELS_MAIN: 'https://www.mako.co.il/bip-programs',
        }

    def _update_base_categories(self, base_object):
        """
        Fetches all the available shows.
        :return: Object of all available shows (JSON).
        """
        req = self.get_object_request(base_object)
        # tree = etree.fromstring(req.text, self.parser)
        tree = self.parser.parse(req.text)
        xpath = './/div[@class="cards main category"]/ol/li'
        show_trees = tree.xpath(xpath)
        sub_objects = []
        for tree in show_trees:

            url = urljoin(self.base_url, tree.xpath('./a')[0].attrib['href'])
            title = tree.xpath('./a/b/strong/text()')[0]
            image_link = urljoin(base_object.url, tree.xpath('./img/@src')[0])

            # obj = {'title': title, 'url': url, 'guid': i}
            obj = VODCatalogNode(catalog_manager=self.catalog_manager,
                                 obj_id=url,
                                 title=title,
                                 url=urljoin(base_object.url, url),
                                 super_object=base_object,
                                 image_link=image_link,
                                 object_type=VODCategories.SHOW,
                                 )

            sub_objects.append(obj)

        base_object.add_sub_objects(sub_objects)

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data (dict).
        :return:
        """
        # We get the data of the page
        # req = self.session.get(video_data.url)
        req = self.get_object_request(video_data)
        # tree = etree.fromstring(req.text, self.parser)
        tree = self.parser.parse(req.text)
        xpath = './/div[@id="main_player"]/ul/li/script/text()'
        script = tree.xpath(xpath)
        assert len(script) == 1
        params = re.findall(r'(?:params=)({.*})(?:;)', script[0], flags=re.DOTALL)
        assert len(params) == 1
        params = [re.sub(r'[\s\']', '', x) for x in params[0].split('\n')][1:-1]
        params = [re.sub('^,', '', x) for x in params]
        params = dict((x.split(':')[0], ':'.join(x.split(':')[1:])) for x in params)

        # print(params)
        channel_id = params['videoChannelId']
        gallery_channel_id = params['galleryChannelId']
        guid = gallery_channel_id
        video_links = self._fetch_best_video_links_from_channel_data(channel_id, gallery_channel_id, guid)
        return VideoNode(video_sources=video_links, raw_data=req)

    def _get_show_from_show_object(self, show_object):
        """
        Fetches the show seasons from show object.
        :param show_object: Show object.
        :return: list of Season objects.
        """
        # In case we have it in our db, we fetch it from, there
        if show_object.id in self.show_data:
            return self.show_data[show_object.id]

        req = self.get_object_request(show_object)
        # Show's data
        # tree = etree.fromstring(req.text, self.parser)
        tree = self.parser.parse(req.text)
        show_data = {'seasons': []}
        # Main info
        xpath = './/div[@class="mako_main_portlet_container"]/div[@id="program_info"]'
        main_program_info_tree = tree.xpath(xpath)[0]
        xpath = './img/@src'
        image_url = main_program_info_tree.xpath(xpath)
        xpath = './div[@id="desc"]/h4/text()'
        program_title = main_program_info_tree.xpath(xpath)
        xpath = './div[@id="desc"]/p/text()'
        program_description = main_program_info_tree.xpath(xpath)
        xpath = './div[@id="desc"]/span/text()'
        program_additional_info = main_program_info_tree.xpath(xpath)

        show_data['imageUrl'] = urljoin(self.base_url, image_url[0])
        show_data['title'] = program_title[0]
        show_data['description'] = program_description[0]
        show_data['additionalInfo'] = program_additional_info[0]

        # Update the missed values
        if show_object.title is None:
            show_object.title = show_data['title']
        if show_object.image_link is None:
            show_object.image_link = show_data['imageUrl']
        if show_object.subtitle is None:
            show_object.subtitle = show_data['description']
        if show_object.description is None:
            show_object.description = show_data['additionalInfo']
        # Mandatory update the new fields
        show_object.raw_data = show_data

        # Episode info
        show_trees = []
        for x in ('cards main category', 'cards main program'):
            for y in ('ol', 'ul'):
                show_trees.extend(tree.xpath('.//div[@class="{x}"]/{y}/li'.format(x=x, y=y)))
        sub_objects = []
        for tree in show_trees:
            url = urljoin(show_object.url, tree.xpath('./a')[0].attrib['href'])
            image_link = urljoin(show_object.url, tree.xpath('./img')[0].attrib['src'])
            title = tree.xpath('./a/b/strong/text()')[0]
            split_title = title.split(' - ')
            description = tree.xpath('./a/b/span/text()')[0]
            duration = self._format_duration(tree.xpath('./a/u/text()')[0]) \
                if len(tree.xpath('./a/u/text()')) > 0 else None
            episode_obj = VODCatalogNode(catalog_manager=self.catalog_manager,
                                         obj_id=url,
                                         title=title,
                                         number=split_title[1],
                                         url=url,
                                         image_link=image_link,
                                         duration=duration,
                                         super_object=show_object,
                                         description=description,
                                         object_type=VODCategories.VIDEO,
                                         )
            sub_objects.append(episode_obj)

        sub_objects.sort(key=lambda z: int(re.findall(r'\d+', z.title)[0])
                         if len(re.findall(r'\d+', z.title)) > 0 else 1000)
        show_object.add_sub_objects(sub_objects)
        # Stores the new fetched data.
        self.show_data[show_object.id] = show_object
        # with open(self.shows_data_filename, 'wb') as fl:
        #     pickle.dump(self.category_data, fl)
        return show_data

    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        raise NotImplementedError

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        pass

    def _update_live_show_data(self):
        raise NotImplementedError

    def _update_live_page_data(self):
        raise NotImplementedError

    def get_object_request(self, page_data, override_page_number=None, override_params=None, override_url=None):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :param override_page_number: Override page number.
        :param override_params: Override params.
        :param override_url: Override url.
        :return: Page request
        """
        url = page_data.url
        req = self.session.get(url)

        return req

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(Bip, self)._version_stack + [self.__version]
