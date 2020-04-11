# Sys
import sys

# OS
from os import path

# Warnings and exceptions
import warnings

# Heritages
from abc import ABCMeta, abstractmethod

# Base fetcher
from .base_fetcher import BaseFetcher

# Regex
import re

# Datetime
from datetime import datetime

# Video catalog
from ..catalogs.vod_catalog import VODCatalogNode, VODFilter, VODCategories
from ..id_generator import IdGenerator


class VODFetcher(BaseFetcher):
    metaclass = ABCMeta
    _catalog_node_object = VODCatalogNode

    @property
    def categories_enum(self):
        """
        Base site url.
        :return:
        """
        return VODCategories

    def __init__(self, vod_name, vod_id, store_dir, data_dir, source_type, session_id):
        super(VODFetcher, self).__init__(vod_name, vod_id, store_dir, data_dir, source_type, session_id)
        self.available_shows_id = (self.source_id, 'available_shows')
        self.search_id = (self.source_id, 'search')

        self.show_data = {}
        self.live_data = {}

    def _prepare_main_sub_objects(self):
        """
        Prepares main sub objects.
        :return:
        """
        self.objects = {
            self.categories_enum.CHANNELS_MAIN:
                self._prepare_main_single_sub_object(self.source_name, self.categories_enum.CHANNELS_MAIN),
            self.categories_enum.SEARCH_MAIN:
                self._prepare_main_single_sub_object('Search', self.categories_enum.SEARCH_MAIN),
            self.categories_enum.LIVE_VIDEO:
                self._prepare_main_single_sub_object('Live', self.categories_enum.LIVE_VIDEO),
        }

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        self._video_filters = VODFilter(self.fetcher_data_dir)

    def get_proper_filter(self, object_data):
        """
        Returns proper filter for current object data type.
        :param object_data: Data object.
        :return:
        """
        true_object = object_data.true_object
        if true_object.object_type == self.categories_enum.CHANNELS_MAIN:
            return self._video_filters.channels_filters
        elif true_object.object_type == self.categories_enum.SEARCH_MAIN:
            return self._video_filters.search_filters
        else:
            return self._video_filters.videos_filters

    def _prepare_main_single_sub_object(self, title, object_type):
        """
        Prepares the object out of object url and object type and title.
        :return: Dictionary object with fields 'obj' and 'update_function'.
        """
        return self._catalog_node_object(catalog_manager=self.catalog_manager,
                                         obj_id='-'+str(object_type),
                                         super_object=self.dummy_super_object,
                                         title=title,
                                         url=self.object_urls[object_type],
                                         object_type=object_type,
                                         ) if object_type in self.object_urls else None

    def get_live_stream_info(self):
        """
        Fetches the live stream data.
        :return: VODCatalogNode object.
        """
        return NotImplemented

    @abstractmethod
    def _update_base_categories(self, base_object):
        """
        Fetches all the available base categories (mostly shows).
        :return: Object of all available shows (JSON).
        """
        raise NotImplementedError

    def search_show(self, show_id):
        """
        Searches for available show.
        :param show_id: Show id.
        :return: Show data.
        """
        available_shows = self.object_urls[self.categories_enum.CHANNELS_MAIN]
        fit_shows = [x for x in available_shows.sub_objects if show_id == x.id]
        return fit_shows

    def _add_category_sub_pages(self, category_data, sub_object_type, page_request=None, clear_sub_elements=True):
        """
        Adds category sub pages.
        :param category_data: Category data object (PornCatalogCategoryNode).
        :param sub_object_type: Sub object type.
        :param page_request: Page request if such exist. In case it doesn't exist we fetch the object's url.
        :return:
        """
        if clear_sub_elements is True:
            category_data.clear_sub_objects()
        if self._use_web_server is True:
            raw_num_of_pages = self.data_server.fetch_request(category_data.url)
            if raw_num_of_pages['status'] is True:
                num_of_pages = raw_num_of_pages['value']['num_of_pages']
            else:
                num_of_pages = self._get_number_of_sub_pages(category_data, page_request)
                push_data = {'num_of_pages': num_of_pages}
                push_result = self.data_server.push_request(category_data.url, push_data)
                if push_result['status'] is False:
                    warnings.warn(push_result['err'])
        else:
            num_of_pages = self._get_number_of_sub_pages(category_data, page_request)

        new_pages = [self._catalog_node_object(catalog_manager=self.catalog_manager,
                                               obj_id=(IdGenerator.id_to_original_str(category_data.id), i),
                                               title=category_data.title + ' | Page {p}'.format(p=i),
                                               url=category_data.url,
                                               page_number=i,
                                               raw_data=category_data.raw_data,
                                               additional_data=category_data.additional_data,
                                               object_type=sub_object_type,
                                               super_object=category_data,
                                               )
                     for i in range(1, num_of_pages + 1)]
        category_data.add_sub_objects(new_pages)

    def _get_video_initials_from_video_data(self, video_data):
        """
        Returns video initials from the given video data.
        :return: Tuple of (name, season, title, filename_title).
        """
        if video_data.object_type == self.categories_enum.LIVE_VIDEO:
            now_time = str(datetime.now())
            title = 'live_' + now_time
            filename_title = title
            save_path = [self._clear_invalid_chars_from_filename(
                self.objects[self.categories_enum.CHANNELS_MAIN].title)]

        else:
            title = video_data.title

            episode_number = video_data.number
            if (title is None or len(title) == 0) and (episode_number is None or len(episode_number) == 0):
                raise RuntimeError('Wrong filename for element {i}.'.format(i=video_data.id))
            elif title is None or len(title) == 0:
                filename_title = episode_number
            elif episode_number is None or len(episode_number) == 0:
                filename_title = title
            else:
                filename_title = ' - '.join((episode_number, title))
            save_path = []

        filename_title = self._clear_invalid_chars_from_filename(filename_title)
        tmp_super_object = video_data.super_object
        while tmp_super_object.object_type != self.categories_enum.GENERAL_MAIN:
            save_path.append(self._clear_invalid_chars_from_filename(tmp_super_object.title))
            tmp_super_object = tmp_super_object.super_object
        save_path.append(self.store_dir)
        save_path = save_path[::-1]
        save_path.append(filename_title)
        filename_title = path.join(*save_path)
        return title, filename_title

    @staticmethod
    def _clear_invalid_chars_from_filename(filename):
        """
        Clears the invalid characters, namely '?', '\', '/', '"', '*', '<', '>', '|', from the filename:
        :param filename: filename
        :return:
        """
        if sys.version_info < (3, 0) and type(filename) == unicode:
            filename = filename.encode('utf-8')
        filename = re.sub(r'[?\\/"*<>|:]', '', filename)
        return filename
