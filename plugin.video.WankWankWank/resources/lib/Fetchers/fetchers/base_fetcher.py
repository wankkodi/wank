# Internet tools
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# OS
from os import path, makedirs
import pickle

# Parsing tool
from ..tools.my_parser_wrapper import MyParser, html5lib

# Heritages
from abc import ABCMeta, abstractmethod

# Video fetcher
from ..tools.video_tools import VideoFetchTools

# User-Agent fetcher
from ..tools.user_agents import UserAgents

# System sleep
# from time import sleep

# Video catalog
from ..catalogs.base_catalog import CatalogNoSubObjectsError, CatalogManager, CatalogNode, VideoTypes
from ..id_generator import IdGenerator

# Datetime
from datetime import datetime

# Regex
import re

# Data server
from ..tools.data_server import DataServer

# Internet tools
from .. import urlparse, parse_qs

# Warnings and exceptions
import warnings


class BaseFetcher(object):
    metaclass = ABCMeta

    @property
    @abstractmethod
    def object_urls(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def base_url(self):
        """
        Base site url.
        :return:
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def categories_enum(self):
        """
        Base site url.
        :return:
        """
        raise NotImplementedError

    def __init__(self, source_name, source_id, store_dir, data_dir, source_type, use_web_server=False,
                 session_id=None):
        retries = 3
        backoff_factor = 0.3
        status_forcelist = (500, 502, 504)

        self.session = requests.session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        # self.parser = html5lib.html5parser.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("lxml"),
        #                                               namespaceHTMLElements=False)
        # self.parser = html5lib.html5parser.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("dom"),
        #                                               namespaceHTMLElements=False)
        # self.parser = html5lib.html5parser.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("etree"),
        #                                               namespaceHTMLElements=False)
        self.parser = MyParser(tree=html5lib.treebuilders.getTreeBuilder("etree"), namespaceHTMLElements=False)
        self.host_name = urlparse(self.base_url).hostname
        self.video_fetcher = VideoFetchTools(self.session)
        self.source_name = source_name
        self.source_id = source_id
        self.store_dir = store_dir
        self.general_data_dir = data_dir
        self.fetcher_data_dir = path.join(self.general_data_dir, source_type, source_name)
        if not path.isdir(self.general_data_dir):
            makedirs(self.general_data_dir)
        if not path.isdir(self.fetcher_data_dir):
            makedirs(self.fetcher_data_dir)

        # Takes care about user agents
        self.user_agents_manager = UserAgents(self.general_data_dir)
        self.user_agent = self.user_agents_manager.get_user_agent()
        self.session.headers['User-Agent'] = self.user_agent
        self.data_server = DataServer(session=self.session)

        # todo: make more precise way to include filters as well...
        # self._use_web_server = True
        self._use_web_server = use_web_server

        self.session_id = session_id if session_id is not None else IdGenerator.make_id(datetime.now())
        self.catalog_manager = CatalogManager(self.session_id, self.fetcher_data_dir)

        self._previous_search_query = None
        self.objects = None
        self._video_filters = None
        self._set_video_filter()

        self.dummy_super_object = None
        self._prepare_main_object()
        self.first_run = True

    def _prepare_main_object(self):
        """
        Prepares main sub objects.
        :return:
        """
        if self.dummy_super_object is None:
            self.dummy_super_object = CatalogNode(catalog_manager=self.catalog_manager, obj_id=self.source_id,
                                                  title=self.source_name, object_type=self.categories_enum.GENERAL_MAIN,
                                                  url=self.base_url)
        else:
            self.dummy_super_object.clear_sub_objects()
        self._prepare_main_sub_objects()
        self.dummy_super_object.add_sub_objects([obj for x, obj in self.objects.items() if x in self.object_urls])

    @abstractmethod
    def _prepare_main_sub_objects(self):
        """
        Prepares main sub objects.
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def _prepare_main_single_sub_object(self, title, object_type):
        """
        Prepares the object out of object url and object type and title.
        :return: Dictionary object with fields 'obj' and 'update_function'.
        """
        raise NotImplementedError

    @abstractmethod
    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def get_proper_filter(self, object_data):
        """
        Returns proper filter for current object data type.
        :param object_data: Data object.
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def _clear_text(text):
        """
        Cleans the given text from whitespaces at the beginning and ending.
        """
        return re.sub(r'^\s*|\s*$', '', text)

    def get_show_object(self, *ids):
        """
        Searchers all the way down for the proper element.
        :param ids: tuple of ids where each id represents the id of that level.
        :return:
        """
        nodes_flags = [self.catalog_manager.is_node(x, True) for x in ids]
        if len(nodes_flags) > 0 and all(x for x in nodes_flags):
            # We have all the nodes in our db.
            search_element = self.catalog_manager.get_node(ids[-1], True)
        else:
            # we find the last object before the first that is found in our db.
            first_not_found_index = min(i for i, x in enumerate(nodes_flags) if x is False) \
                if len(nodes_flags) > 0 else 0
            last_found_node_index = first_not_found_index - 1
            if last_found_node_index == -1:
                # We have a first call, otherwise we are sure that last_found_node_index >= 0,
                # otherwise it would be the first call, so self.first_run wasTrue and
                # self._update_base_categories() was called.
                search_element = self.dummy_super_object
                i = 0
            else:
                search_element = self.catalog_manager.get_node(ids[last_found_node_index], True)
                i = first_not_found_index

            for obj_id in ids[first_not_found_index:]:
                if search_element.object_type is self.categories_enum.VIDEO and i < len(ids) - 1:
                    raise RuntimeError('The element {id} is final, while we have deeper search.'
                                       ''.format(id=search_element.id))
                if search_element.sub_objects is None and search_element.object_type != self.categories_enum.VIDEO:
                    # We try to fetch them
                    self.fetch_sub_objects(search_element)
                try:
                    # We try to look for it in the additional pages of the sub_object
                    search_element = search_element.search_sub_object(obj_id)
                except CatalogNoSubObjectsError:
                    search_element = search_element.search_additional_object(obj_id)
                i += 1

        if search_element.sub_objects is None and search_element.object_type != self.categories_enum.VIDEO:
            # We try to fetch them
            self.fetch_sub_objects(search_element)
        return search_element

    @abstractmethod
    def fetch_sub_objects(self, element_object):
        """
        Fetches object's sub objects.
        :param element_object: Object element we want to fetch.
        :return:
        """
        return NotImplemented

    @abstractmethod
    def _add_category_sub_pages(self, category_data, sub_object_type, page_request=None, clear_sub_elements=True):
        """
        Adds category sub pages.
        :param category_data: Category data object (PornCatalogCategoryNode).
        :param sub_object_type: Sub object type.
        :param page_request: Page request if such exist. In case it doesn't exist we fetch the object's url.
        :param clear_sub_elements: Flag that indicates whether we clear previous sub elements.
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def _get_number_of_sub_pages(self, category_data, fetched_request=None, last_available_number_of_pages=None):
        """
        Get number of pages from category data.
        :param category_data: Category data (dict).
        :param fetched_request: Fetched url. In case such doesn't exist, we fetch it.
        :param last_available_number_of_pages: Last available number of pages. Will be the pivot for our next search.
        By default is None, which mean the original pivot will be used...
        :return:
        """
        return NotImplemented

    def download_live_stream(self, video_links, video_i=0, verbose=0):
        """
        Fetches Show episode.
        :param video_links: Video links (VideoNode object).
        :param video_i: Video stream index.
        :param verbose: Verbose indicator.
        :return: Shows video.
        """
        video_data = self.objects[self.categories_enum.LIVE_VIDEO]
        name, filename_title = self._get_video_initials_from_video_data(video_data)

        save_video_filename = path.join(self.store_dir, '{t}.ts'.format(t=filename_title))
        save_data_filename = path.join(self.store_dir, '{t}.dat'.format(t=filename_title))
        if not path.isdir(path.dirname(save_video_filename)):
            makedirs(path.dirname(save_video_filename))

        if path.isfile(save_data_filename) and path.isfile(save_video_filename):
            if verbose > 0:
                print('The file {n} already exist.'.format(n=name))
        else:
            if verbose > 0:
                print('Downloading the file {n}'.format(n=name))

            # We get the params of the video
            try:
                self.get_video(video_links, video_i, save_video_filename)
            except RuntimeError:
                raise RuntimeError('Cannot fetch the video {n}.'.format(n=name))

            with open(save_data_filename, 'wb') as fl:
                pickle.dump(video_data, fl)

    def download_video(self, video_data, video_links, video_i=0, verbose=0):
        """
        Fetches Show episode.
        :param video_data: Video data.
        :param video_links: Video links (VideoNode object).
        :param video_i: Video stream index.
        :param verbose: Verbose indicator.
        :return: Shows video.
        """
        try:
            name, filename_title = self._get_video_initials_from_video_data(video_data)
        except RuntimeError as err:
            # todo: take care with proper exception
            raise err
        save_video_filename = path.join(self.store_dir, '{t}.ts'.format(t=filename_title))
        save_data_filename = path.join(self.store_dir, '{t}.dat'.format(t=filename_title))
        if not path.isdir(path.dirname(save_video_filename)):
            makedirs(path.dirname(save_video_filename))

        if path.isfile(save_data_filename) and path.isfile(save_video_filename):
            if verbose > 0:
                print('The file {n} already exist.'.format(n=name))
        else:
            if verbose > 0:
                print('Downloading the file {n}'.format(n=name))

            # We get the params of the video
            try:
                self.get_video(video_links, video_i, save_video_filename)
            except RuntimeError:
                raise RuntimeError('Cannot fetch the video {n}.'.format(n=name))

            with open(save_data_filename, 'wb') as fl:
                pickle.dump(video_data, fl)

    def get_video(self, video_data, video_i, filename):
        """
        Runs over the given links and fetches the video from the first available.
        :param video_data: Video data (VideoNode).
        :param video_i: Video stream index.
        :param filename: Store filename.
        :return: Video object.
        """
        if video_data.video_sources[video_i].video_type == VideoTypes.VIDEO_SEGMENTS:
            return self.video_fetcher.get_video_from_segments(video_data, video_i, filename)
        elif video_data.video_sources[video_i].video_type == VideoTypes.VIDEO_REGULAR:
            return self.video_fetcher.get_video(video_data, video_i, filename)
        elif video_data.video_sources[video_i].video_type == VideoTypes.VIDEO_YOUTUBE:
            video_links, audio_links = self._get_playlist_of_youtube_source(video_data.video_sources[video_i], False)
            return self.video_fetcher.combine_youtube_video(video_links, audio_links, filename)
        else:
            raise RuntimeError('Wrong video type {ad}.'.format(ad=video_data.video_type))

    def test_video_link(self, video_data, video_i):
        """
        Runs over the given links and fetches the video from the first available.
        :param video_data: Video data (VideoNode).
        :param video_i: Video stream index.
        :return: Video object.
        """
        video_link = video_data.video_sources[video_i]
        if video_data.video_sources[video_i].video_type == VideoTypes.VIDEO_SEGMENTS:
            req = self.session.get(url=video_link.link,
                                   headers=video_data.headers if video_data.headers is None else self.session.headers,
                                   json=video_data.json,
                                   params=video_data.params,
                                   data=video_data.query_data,
                                   verify=video_data.verify)
            return req.ok
        elif video_data.video_sources[video_i].video_type == VideoTypes.VIDEO_REGULAR:
            req = self.session.get(video_link.link,
                                   headers=video_data.headers
                                   if video_data.headers is not None else self.session.headers,
                                   stream=True,
                                   json=video_data.json,
                                   cookies=video_data.cookies if video_data.json is not None else self.session.cookies,
                                   params=video_data.params,
                                   data=video_data.query_data,
                                   verify=video_data.verify)
            return req.ok
        elif video_data.video_sources[video_i].video_type == VideoTypes.VIDEO_YOUTUBE:
            video_status = False
            audio_status = False
            video_link = re.sub(r'\?.*$', '', video_link)
            videos, audios = self.video_fetcher.get_playlist_of_youtube_source(video_link, False)
            # Fetching video
            for stream in videos:
                url = stream['url']
                response = self.session.get(url, headers={'Range': 'bytes=' + VideoFetchTools.CHUNK_SIZE})
                if response.ok:
                    video_status = response.ok
                    break

            # Fetching audio
            for stream in audios:
                url = stream['url']
                response = self.session.get(url, headers={'Range': 'bytes=' + VideoFetchTools.CHUNK_SIZE})
                if response.ok:
                    audio_status = response.ok
                    break
            return video_status and audio_status

        else:
            raise RuntimeError('Wrong video type {ad}.'.format(ad=video_data.video_type))

    def _get_playlist_of_youtube_source(self, url, must_combine_audio):
        """
        Returns the playlist of YouTube source.
        :param url: video URL.
        :param must_combine_audio: Flag that indicates whether we need the combine audio (used mainly for YouTube).
        :return: list of links to video, sorted by bandwidth.
        """
        video_url = re.sub(r'\?.*$', '', url)
        videos, audios = self.video_fetcher.get_playlist_of_youtube_source(video_url, must_combine_audio)
        return videos, audios

    @abstractmethod
    def _get_video_initials_from_video_data(self, video_data):
        """
        Returns video initials from the given video data.
        :return: Tuple of (name, season, title, filename_title).
        """
        raise NotImplementedError

    @abstractmethod
    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data (dict).
        :return:
        """
        raise NotImplementedError

    def get_object_request(self, object_data, override_page_number=None, override_params=None, override_url=None):
        """
        Fetches the page number with respect to base url.
        :param object_data: Page data.
        :param override_page_number: Override page number.
        :param override_params: Override params.
        :param override_url: Override url.
        :return: Page request
        """
        # todo: add filter condition check!
        true_object = object_data.true_object

        page_filter = self.get_proper_filter(object_data).current_filters

        program_fetch_url = object_data.url.split('?')[0]
        if len(object_data.url.split('?')) > 1:
            params = object_data.url.split('?')[1]
            params = parse_qs(params)
        else:
            params = {}
        page_number = object_data.page_number if override_page_number is None else override_page_number
        if override_params is not None:
            params.update(override_params)
        if override_url is not None:
            program_fetch_url = override_url

        return self._get_page_request_logic(object_data, params, page_number, true_object,
                                            page_filter, program_fetch_url)

    @abstractmethod
    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        """
        Fetches the page number with respect to base url.
        :param page_data: Page data.
        :param params: Page params.
        :param page_number: Page number.
        :param true_object: True object.
        :param page_filter: Page filter.
        :param fetch_base_url: Page base url.
        :return: Page request
        """
        raise NotImplementedError

    def download_category_input_from_user(self, use_web_server=True):
        """
        Downloads the proper file according to user's input.
        :param use_web_server: Indicates whether we want to use the web server in order to store/fetch the data from.
        """
        # fixme: could make some problems in parallel implementation. Fina a bette way...
        org_use_web_server = self._use_web_server
        self._use_web_server = use_web_server
        object_data = self.dummy_super_object
        while 1:
            if object_data == self.dummy_super_object:
                print('Welcome to the UI of the {h} parser. To change the filter setting choose -2.'
                      ''.format(h=self.source_name)
                      )
            input_title = ('Please choose the wanted category. ' +
                           ('To return to previous page, enter -1' if object_data == self.dummy_super_object else ''))
            print(input_title)
            if object_data.sub_objects is not None:
                for i, sub_object in enumerate(object_data.sub_objects):
                    print('{i}: {t}'.format(i=i, t=(sub_object.title if type(sub_object.title) == str
                                                    else sub_object.title.encode('utf-8'))))
            res = input()
            res = self._check_correct_user_input(res, object_data.sub_objects, True)
            if res == -1:
                object_data = object_data.super_object
            elif res == -2:
                # Update the filters
                status = self._update_filters_input_from_user()
                if status is True:
                    # We clean all the prepared categories
                    self._prepare_main_object()
                    object_data = self.dummy_super_object
                    continue
            elif res in range(len(object_data.sub_objects)):
                object_data = object_data.sub_objects[res]
                if object_data.object_type in (self.categories_enum.VIDEO, self.categories_enum.LIVE_VIDEO):
                    if object_data.object_type in (self.categories_enum.VIDEO,):
                        new_video_links = self.get_video_links_from_video_data(object_data)
                    else:
                        # object_data.object_type in (LiveVideo,)
                        new_video_links = self.get_live_stream_video_link()

                    if len(new_video_links.video_sources) > 1:
                        print('Choose the wanted source:')
                        for i, sub_object in enumerate(new_video_links.video_sources):
                            print('{i}: {t}'.format(i=i, t=sub_object))
                        video_i = input('Please select the wanted source:')
                        video_i = self._check_correct_user_input(video_i, new_video_links.video_sources, False)
                        if video_i == -1:
                            continue
                    else:
                        video_i = 0
                    # We check whether we reached the final object!
                    if object_data.object_type in (self.categories_enum.VIDEO,):
                        self.download_video(object_data, new_video_links, video_i)
                    else:
                        self.download_live_stream(new_video_links, video_i)
                    self._use_web_server = org_use_web_server
                    return
                elif object_data.object_type == self.categories_enum.SEARCH_MAIN:
                    query = input('Enter the search query: ')
                    self.search_query(query)
                if object_data.sub_objects is None:
                    self.fetch_sub_objects(object_data)

            else:
                raise ValueError('Got index outside of the range [0..{r}]!'.format(r=len(object_data.sub_objects) - 1))

    def _update_filters_input_from_user(self):
        """
        Updates the filters from user interface
        :return: True if update was made, False otherwise.
        """
        status = False
        while 1:
            print('Current settings are:\n{s}'.format(s=self._video_filters))
            print('Choose which filter you would like to update. To back to previous menu, please choose -1.')
            fields = [x for x in self._video_filters]
            for i, sub_object in enumerate(fields):
                print('{i}: {t}'.format(i=i, t=sub_object))
            res = input()
            res = self._check_correct_user_input(res, fields, False)

            if res == -1:
                break
            field_id = fields[res]
            while 1:
                main_filter = self._video_filters[field_id]
                # main_filter = getattr(self._video_filters, field_id)
                print('Choose which field you would like to update. To back to previous menu, please choose -1.')
                fields = [x for x in main_filter]
                for i, sub_object in enumerate(fields):
                    print('{i}: {t}'.format(i=i, t=sub_object))
                res = input()
                res = self._check_correct_user_input(res, fields, False)

                if res == -1:
                    break
                field_sub_id = fields[res]
                while 1:
                    available_values = main_filter.filters[field_sub_id]
                    # available_values = getattr(main_filter.filters, field_sub_id)
                    available_indices = list(available_values.keys())
                    print('Choose the available filter. To back to previous menu, please choose -1.')
                    for i, sub_object in enumerate(available_indices):
                        print('{i}: {t}'.format(i=i, t=available_values[sub_object].title))
                    res = input()
                    res = self._check_correct_user_input(res, available_indices, False)
                    if res == -1:
                        break
                    elif res in range(len(available_values)):
                        status = True
                        main_filter.set_current_filter(field_sub_id, available_indices[res])
                        break
        return status

    @staticmethod
    def _check_correct_user_input(user_input, available_values, is_available_filter=False):
        """
        Checks whether the user input is falling inside the wanted range. In case no, ValueErroe will be raised
        :param user_input: User input raw value
        :param available_values: Available values
        :param is_available_filter: In case this flag is true, we can accept the special value of -2.
        :return: Index (integer) of the given input value.
        """
        try:
            float(user_input)
        except ValueError:
            raise ValueError('Got not index!')
        res = int(user_input)

        if res == -1:
            return res
        elif res == -2 and is_available_filter is True:
            return res
        elif res in range(len(available_values)):
            return res
        else:
            raise ValueError(
                'Got index outside of the range [0..{r}]!'.format(r=len(available_values) - 1))

    def download_objects(self, *ids, **kwargs):
        """
        Recursively download all the given files start from the given node.
        We assume that there is no cycles in our database!
        :param ids: tuple of ids where each id represents the id of that level.
        :param kwargs: additional arguments.
        :return:
        """
        verbose = 'verbose' in kwargs and kwargs['verbose'] is True
        start_object = self.get_show_object(*ids)
        self._download_sub_objects(start_object, len(ids), verbose)

    def _download_sub_objects(self, node, verbose, finished_nodes=None):
        """
        Recursively download all the available videos from all available subtrees.
        :param node: Download node
        :param verbose: Verbose indicator.
        :param finished_nodes: Stores all the finished nodes in order to prevent double download.
        :return:
        """
        if finished_nodes is None:
            finished_nodes = set()
        if node.is_final_object:
            try:
                self.download_video(node, verbose)
            except RuntimeError as err:
                warnings.warn(str(err))
        else:
            if node.sub_objects is None:
                self.fetch_sub_objects(node)
            for sub_node in node.sub_objects:
                self._download_sub_objects(sub_node, verbose, finished_nodes)
            finished_nodes.add(node)

    def search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        if self._previous_search_query == query:
            search_element = self.objects[self.categories_enum.SEARCH_MAIN]
            if search_element.sub_objects is not None:
                return search_element

        self._previous_search_query = query
        search_element = self.objects[self.categories_enum.SEARCH_MAIN]
        search_element.clear_additional_objects()
        search_element.clear_sub_objects()
        search_element.url = self._prepare_new_search_query(query)
        # request = self.get_object_request(search_element)

        return search_element

    def _prepare_new_search_query(self, query):
        """
        Searches for the wanted episode.
        :param query: Search query.
        :return: List of Video objects.
        """
        return NotImplemented

    def get_live_stream_video_link(self):
        """
        Fetches the live stream video_link.
        :return: VideoNode object.
        """
        return NotImplemented
