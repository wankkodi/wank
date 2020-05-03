# Internet tools
from .. import urljoin

# # OS
# from os import path, makedirs
# import pickle

# Regex
import re

# Warnings and exceptions
import warnings

# Heritages
from abc import ABCMeta, abstractmethod

# External Fetchers
from ..tools.external_fetchers import NoVideosException

# Math
import math

# JSON exceptions
try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

# Sys
import sys
import time

# Video catalog
# from video_catalog import GeneralMainDummy
from ..catalogs.porn_catalog import PornCatalogPageNode, PornCatalogMainCategoryNode, PornCatalogCategoryNode
from ..catalogs.porn_catalog import PornCategories, PornCategoryTypes, PornFilter

from ..id_generator import IdGenerator

# Base fetcher
from ..fetchers.base_fetcher import BaseFetcher


class PornErrorModule(object):
    def __init__(self, server, error_mode, site_name, url, message, page_filters, general_filters):
        self.server = server
        self.error_mode = error_mode
        self.site_name = site_name
        self.url = url
        self.message = message
        self.page_filters = page_filters
        self.general_filters = general_filters


class PornError(ValueError):
    def __init__(self, request, error_module=None):
        super(PornError, self).__init__(request)
        if error_module is not None and error_module.server is not None:
            error_module.server.push_error(error_module.error_mode, error_module.site_name, error_module.url,
                                           error_module.message,
                                           error_module.page_filters, error_module.general_filters)


class PornFetchUrlError(PornError):
    def __init__(self, request, error_module=None):
        super(PornFetchUrlError, self).__init__(request, error_module)
        self.request = request

    def __str__(self):
        return repr('Could not fetch {url}'.format(url=self.request.url))


class PornValueError(PornError):
    def __init__(self, err, error_module=None):
        super(PornValueError, self).__init__(err, error_module)
        self.message = err

    def __str__(self):
        return repr(self.message)


class PornNoVideoError(PornError):
    def __init__(self, err, error_module=None):
        super(PornNoVideoError, self).__init__(err, error_module)
        self.message = err

    def __str__(self):
        return repr(self.message)


class PornFetcher(BaseFetcher):
    # todo: to outsource the url link to outer method instead of get_object_request
    metaclass = ABCMeta
    __time_format = '%H:%M:%S'
    __time_format_2 = '%M:%S'

    @property
    def categories_enum(self):
        """
        Base site url.
        :return:
        """
        return PornCategories

    @property
    @abstractmethod
    def _default_sort_by(self):
        raise NotImplementedError

    @property
    def video_filters(self):
        """
        Dictionary with available categories and the values of (title, value).
        :return:
        """
        return self._video_filters

    @property
    def possible_empty_pages(self):
        """
        Defines whether it is possible to have empty pages in the site.
        :return:
        """
        return False

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return NotImplemented

    def __init__(self, source_name, source_id, store_dir, data_dir, source_type, use_web_server=True, session_id=None):
        super(PornFetcher, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                          session_id)

    def _set_video_filter(self):
        """
        Sets the video filters and the default values of the current filters
        :return:
        """
        self._video_filters = PornFilter(self.fetcher_data_dir)

    @property
    def general_filter(self):
        """
        Returns proper general for current object data type.
        :return:
        """
        return self._video_filters[PornCategories.GENERAL_MAIN]

    def get_proper_filter(self, object_data):
        """
        Returns proper filter for current object data type.
        :param object_data: Data object.
        :return:
        """
        true_object = object_data.true_object
        if true_object.object_type in (PornCategories.CATEGORY_MAIN,
                                       PornCategories.PORN_STAR_MAIN,
                                       PornCategories.ACTRESS_MAIN,
                                       PornCategories.CHANNEL_MAIN,
                                       PornCategories.TAG_MAIN,
                                       PornCategories.CATEGORY,
                                       PornCategories.PORN_STAR,
                                       PornCategories.CHANNEL,
                                       PornCategories.SEARCH_MAIN,
                                       PornCategories.VIDEO,
                                       PornCategories.TAG,
                                       ):
            return self._video_filters[true_object.object_type]
        else:
            return self._video_filters[PornCategories.VIDEO_PAGE]

    def _prepare_main_sub_objects(self):
        """
        Prepares main sub objects.
        :return:
        """
        # We add categories subnode
        self.objects = {
            PornCategories.CATEGORY_MAIN:
                self._prepare_main_single_sub_object('Categories', PornCategories.CATEGORY_MAIN),
            PornCategories.TAG_MAIN:
                self._prepare_main_single_sub_object('Tags', PornCategories.TAG_MAIN),
            PornCategories.CHANNEL_MAIN:
                self._prepare_main_single_sub_object('Channels', PornCategories.CHANNEL_MAIN),
            PornCategories.PORN_STAR_MAIN:
                self._prepare_main_single_sub_object('Porn Stars', PornCategories.PORN_STAR_MAIN),
            PornCategories.ACTRESS_MAIN:
                self._prepare_main_single_sub_object('Actresses', PornCategories.ACTRESS_MAIN),
            PornCategories.LATEST_VIDEO:
                self._prepare_main_single_sub_object('Latest Videos', PornCategories.LATEST_VIDEO),
            PornCategories.MOST_VIEWED_VIDEO:
                self._prepare_main_single_sub_object('Most Viewed Videos', PornCategories.MOST_VIEWED_VIDEO),
            PornCategories.TOP_RATED_VIDEO:
                self._prepare_main_single_sub_object('Top Rated Videos', PornCategories.TOP_RATED_VIDEO),
            PornCategories.POPULAR_VIDEO:
                self._prepare_main_single_sub_object('Popular Videos', PornCategories.POPULAR_VIDEO),
            PornCategories.LONGEST_VIDEO:
                self._prepare_main_single_sub_object('Longest Videos', PornCategories.LONGEST_VIDEO),
            PornCategories.HD_VIDEO:
                self._prepare_main_single_sub_object('HD Videos', PornCategories.HD_VIDEO),
            PornCategories.ALL_VIDEO:
                self._prepare_main_single_sub_object('All Videos', PornCategories.ALL_VIDEO),
            PornCategories.MOST_DISCUSSED_VIDEO:
                self._prepare_main_single_sub_object('Most Discussed Videos', PornCategories.MOST_DISCUSSED_VIDEO),
            PornCategories.LIVE_VIDEO:
                self._prepare_main_single_sub_object('Live Videos', PornCategories.LIVE_VIDEO),
            PornCategories.RECOMMENDED_VIDEO:
                self._prepare_main_single_sub_object('Recommended Videos', PornCategories.RECOMMENDED_VIDEO),
            PornCategories.HOTTEST_VIDEO:
                self._prepare_main_single_sub_object('Hottest Videos', PornCategories.HOTTEST_VIDEO),
            PornCategories.RANDOM_VIDEO:
                self._prepare_main_single_sub_object('Random Videos', PornCategories.RANDOM_VIDEO),
            PornCategories.INTERESTING_VIDEO:
                self._prepare_main_single_sub_object('Interesting Videos', PornCategories.INTERESTING_VIDEO),
            PornCategories.TRENDING_VIDEO:
                self._prepare_main_single_sub_object('Trending Videos', PornCategories.TRENDING_VIDEO),
            PornCategories.UPCOMING_VIDEO:
                self._prepare_main_single_sub_object('Upcoming Videos', PornCategories.UPCOMING_VIDEO),
            PornCategories.ORGASMIC_VIDEO:
                self._prepare_main_single_sub_object('Orgasmic Videos', PornCategories.ORGASMIC_VIDEO),
            PornCategories.USER_UPLOADED_VIDEO:
                self._prepare_main_single_sub_object('User Uploaded Videos', PornCategories.USER_UPLOADED_VIDEO),
            PornCategories.FAVORITE_VIDEO:
                self._prepare_main_single_sub_object('Favorite Videos', PornCategories.FAVORITE_VIDEO),
            PornCategories.VERIFIED_VIDEO:
                self._prepare_main_single_sub_object('Verified Videos', PornCategories.VERIFIED_VIDEO),
            PornCategories.BEING_WATCHED_VIDEO:
                self._prepare_main_single_sub_object('Being Watched Videos', PornCategories.BEING_WATCHED_VIDEO),
            PornCategories.JUST_LOGGED_IN_VIDEO:
                self._prepare_main_single_sub_object('Just Logged in Videos', PornCategories.JUST_LOGGED_IN_VIDEO),
            PornCategories.NEW_MODEL_VIDEO:
                self._prepare_main_single_sub_object('New Models Videos', PornCategories.NEW_MODEL_VIDEO),
            PornCategories.MOST_DOWNLOADED_VIDEO:
                self._prepare_main_single_sub_object('Most Downloaded Videos', PornCategories.MOST_DOWNLOADED_VIDEO),
            PornCategories.MOST_WATCHED_VIDEO:
                self._prepare_main_single_sub_object('Most Watched Videos', PornCategories.MOST_WATCHED_VIDEO),
            PornCategories.FULL_MOVIE_VIDEO:
                self._prepare_main_single_sub_object('Full Movies Videos', PornCategories.FULL_MOVIE_VIDEO),
            PornCategories.SHORTEST_VIDEO:
                self._prepare_main_single_sub_object('Shortest Videos', PornCategories.SHORTEST_VIDEO),
            PornCategories.RELEVANT_VIDEO:
                self._prepare_main_single_sub_object('Relevant Videos', PornCategories.RELEVANT_VIDEO),
            PornCategories.SEARCH_MAIN:
                self._prepare_main_single_sub_object('Search', PornCategories.SEARCH_MAIN),
        }
        self.dummy_super_object.add_sub_objects([obj for x, obj in self.objects.items() if x in self.object_urls])

    @property
    def _main_update_methods(self):
        """
        Returns a dictionary with object type as a key and a proper update method as a value
        :return:
        """
        return {
            PornCategories.CATEGORY_MAIN: self._update_available_categories,
            PornCategories.TAG_MAIN: self._update_available_tags,
            PornCategories.CHANNEL_MAIN: self._update_available_channels,
            PornCategories.PORN_STAR_MAIN: self._update_available_porn_stars,
            PornCategories.ACTRESS_MAIN: self._update_available_actresses,
            PornCategories.SEARCH_MAIN: self._prepare_new_search_query,
        }

    def _prepare_main_single_sub_object(self, title, object_type):
        """
        Prepares the object out of object url and object type and title.
        :return: Dictionary object with fields 'obj' and 'update_function'.
        """
        return PornCatalogMainCategoryNode(catalog_manager=self.catalog_manager,
                                           obj_id='-'+str(object_type),
                                           super_object=self.dummy_super_object,
                                           title=title,
                                           url=self.object_urls[object_type],
                                           object_type=object_type,
                                           ) if object_type in self.object_urls else None

    def fetch_sub_objects(self, element_object):
        # sub_objects -> None
        """
        Fetches object's sub objects.
        :param element_object: Object element we want to fetch.
        :return:
        """
        try:
            if element_object.sub_objects is not None:
                return element_object.sub_objects
            if element_object.object_type.category_type == PornCategoryTypes.MAIN_CATEGORY:
                self._add_category_sub_pages(element_object, PornCategories.PAGE)
            elif element_object.object_type.category_type == PornCategoryTypes.SECONDARY_CATEGORY:
                self._add_category_sub_pages(element_object, PornCategories.VIDEO_PAGE)
            elif element_object.object_type.category_type == PornCategoryTypes.VIDEO_CATEGORY:
                self._add_category_sub_pages(element_object, PornCategories.VIDEO_PAGE)
            elif element_object.object_type in (PornCategories.PAGE,):
                # We climb up to decide what is the ancestor true object type
                true_object = element_object.true_object
                self._main_update_methods[true_object.object_type](element_object)
            elif element_object.object_type in (PornCategories.SEARCH_MAIN,):
                self._add_category_sub_pages(element_object, PornCategories.SEARCH_PAGE)
            elif element_object.object_type in (PornCategories.VIDEO_PAGE,):
                self.get_videos_data(element_object)
            elif element_object.object_type in (PornCategories.SEARCH_PAGE,):
                self.get_search_data(element_object)
            else:
                raise ValueError('Wrong type of the object {ot}!'.format(ot=element_object.object_type))
            # We check whether a mandatory category doesn't have any sub-elements and in this case send the proper
            # exception
            if (
                    element_object.true_object.object_type.category_type in (PornCategoryTypes.MAIN_CATEGORY,
                                                                             PornCategoryTypes.SECONDARY_CATEGORY,
                                                                             PornCategoryTypes.VIDEO_CATEGORY,
                                                                             )
                    and self.possible_empty_pages is False
                    and (element_object.sub_objects is None or len(element_object.sub_objects) == 0)):
                error_module = self._prepare_porn_error_module(element_object, 1, element_object.url,
                                                               'No sub-pages for object {obj} of the site {s}'
                                                               ''.format(obj=element_object.title, s=self.source_name))
                self.data_server.push_error(error_module.error_mode, error_module.site_name, error_module.url,
                                            error_module.message,
                                            error_module.page_filters, error_module.general_filters)

            return element_object.sub_objects
        except (ValueError, IndexError) as err:
            error_module = self._prepare_porn_error_module(element_object, 1, element_object.url,
                                                           'Got the following err {r}.\nPage url {u}'
                                                           ''.format(r=err, u=element_object.url))
            raise PornValueError(error_module.message, error_module)

    # def fetch_sub_objects(self, element_object):
    #     """
    #     Fetches object's sub objects.
    #     :param element_object: Object element we want to fetch.
    #     :return:
    #     """
    #     if element_object.sub_objects is not None:
    #         return element_object.sub_objects
    #
    #     if element_object.object_type in (PornCategories.CATEGORY_MAIN, PornCategories.PORN_STAR_MAIN,
    #                                       PornCategories.CHANNEL_MAIN, PornCategories.TAG_MAIN,):
    #         self._add_category_sub_pages(element_object, PornCategories.PAGE)
    #
    #     elif element_object.object_type in (PornCategories.CATEGORY, PornCategories.PORN_STAR,
    #                                         PornCategories.CHANNEL, PornCategories.TAG,):
    #         self._add_category_sub_pages(element_object, PornCategories.VIDEO_PAGE)
    #
    #     elif element_object.object_type in (PornCategories.PAGE,):
    #         # We climb up to decide what is the ancestor true object type
    #         true_object = element_object.true_object
    #         self._main_update_methods[true_object.object_type](element_object)
    #
    #     elif element_object.object_type in (PornCategories.LATEST_VIDEO, PornCategories.MOST_VIEWED_VIDEO,
    #                                         PornCategories.TOP_RATED_VIDEO, PornCategories.POPULAR_VIDEO,
    #                                         PornCategories.LONGEST_VIDEO, PornCategories.HD_VIDEO,
    #                                         PornCategories.ALL_VIDEO, PornCategories.MOST_DISCUSSED_VIDEO,
    #                                         PornCategories.LIVE_VIDEO, PornCategories.RECOMMENDED_VIDEO,
    #                                         PornCategories.HOTTEST_VIDEO, PornCategories.RANDOM_VIDEO,
    #                                         PornCategories.INTERESTING_VIDEO, PornCategories.TRENDING_VIDEO,
    #                                         PornCategories.UPCOMING_VIDEO, PornCategories.ORGASMIC_VIDEO,
    #                                         PornCategories.USER_UPLOADED_VIDEO, PornCategories.FAVORITE_VIDEO,
    #                                         PornCategories.VERIFIED_VIDEO, PornCategories.BEING_WATCHED_VIDEO,
    #                                         PornCategories.JUST_LOGGED_IN_VIDEO, PornCategories.NEW_MODEL_VIDEO,
    #                                         PornCategories.MOST_DOWNLOADED_VIDEO, PornCategories.MOST_WATCHED_VIDEO,
    #                                         PornCategories.FULL_MOVIE_VIDEO, PornCategories.SHORTEST_VIDEO):
    #         self._add_category_sub_pages(element_object, PornCategories.VIDEO_PAGE)
    #
    #     elif element_object.object_type in (PornCategories.SEARCH_MAIN,):
    #         self._add_category_sub_pages(element_object, PornCategories.SEARCH_PAGE)
    #
    #     elif element_object.object_type in (PornCategories.VIDEO_PAGE,):
    #         self.get_videos_data(element_object)
    #
    #     elif element_object.object_type in (PornCategories.SEARCH_PAGE,):
    #         self.get_search_data(element_object)
    #
    #     else:
    #         raise ValueError('Wrong type of the object {ot}!'.format(ot=element_object.object_type))
    #     return element_object.sub_objects

    def _update_available_categories(self, category_data):
        """
        Fetches all the available categories.
        :return: Object of all available shows (PornCatalogCategoryNode).
        """
        return NotImplemented

    def _update_available_tags(self, tag_data):
        """
        Fetches all the available tags.
        :return: Object of all available shows (PornCatalogCategoryNode).
        """
        return NotImplemented

    def _update_available_channels(self, channel_data):
        """
        Fetches all the available channels.
        :return: Object of all available shows (PornCatalogCategoryNode).
        """
        return NotImplemented

    def _update_available_porn_stars(self, porn_star_data):
        """
        Fetches all the available pornstars.
        :return: Object of all available shows (PornCatalogCategoryNode).
        """
        return NotImplemented

    def _update_available_actresses(self, actress_data):
        """
        Fetches all the available actresses.
        :return: Object of all available shows (PornCatalogCategoryNode).
        """
        return NotImplemented

    def search_sub_object_from_query(self, object_data, sub_object_id):
        """
        Searches for available show.
        :param object_data: Object data.
        :param sub_object_id: Sub object id.
        :return: Show data.
        """
        if object_data.sub_objects is None:
            self.fetch_sub_objects(object_data)
        fit_shows = [y for y in object_data.sub_objects if sub_object_id == y.id]
        return fit_shows

    def get_video_links_from_video_data(self, video_data):
        """
        Extracts episode link from episode data.
        :param video_data: Video data (dict).
        :return:
        """
        try:
            videos = self._get_video_links_from_video_data_no_exception_check(video_data)
            if len(videos.video_sources) == 0:
                error_module = self._prepare_porn_error_module_for_video_page(video_data)
                raise PornNoVideoError(error_module.message, error_module)
            return videos
        except (IndexError, KeyError):
            error_module = self._prepare_porn_error_module_for_video_page(
                video_data, video_data.url,
                'Cannot parse request data or request hash for url {u}.'.format(u=video_data.url))
            raise PornNoVideoError(error_module.message, error_module)
        except NoVideosException as err:
            error_module = self._prepare_porn_error_module_for_video_page(video_data, err.error_module.url,
                                                                          err.error_module.message)
            raise PornNoVideoError(error_module.message, error_module)
        except JSONDecodeError:
            err_str = 'Cannot parse the JSON from the url {u}'.format(u=video_data.url)
            error_module = self._prepare_porn_error_module_for_video_page(video_data, video_data.url, err_str)
            raise PornNoVideoError(error_module.message, error_module)
        except TypeError as err:
            str_err = 'No Video link for url {u}, got error {e}'.format(u=video_data.url, e=err)
            error_module = self._prepare_porn_error_module_for_video_page(video_data, video_data.url, str_err)
            raise PornNoVideoError(error_module.message, error_module)

    @abstractmethod
    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def get_videos_data(self, page_data):
        """
        Gets videos data for the given category.
        :param page_data: Category data.
        :return:
        """
        raise NotImplementedError

    def get_search_data(self, page_data):
        """
        Gets search data for the given category.
        By default has the same implementation as get_videos_data, unless willbe override...
        :param page_data: Category data.
        :return:
        """
        return self.get_videos_data(page_data)

    @property
    def _make_tag_pages_by_letter(self):
        """
        Indicates whether we split the tags by letters.
        :return:
        """
        return True

    def _get_tag_properties(self, page_request):
        """
        Fetches tag links and titles. The fetched objects MUST be sorted wrt title.
        :param page_request: Page request.
        :return:
        """
        return NotImplemented

    def _add_tag_sub_pages(self, tag_data, sub_object_type):
        """
        Adds sub pages to the tags according to the first letter of the title. Stores all the tags to the proper pages.
        Notice that the current method contradicts with the _get_tag_properties method, thus you must use either of
        them, according to the way you want to implement the parsing (Use the _make_tag_pages_by_letter property to
        indicate which of the methods you are about to use...)
        :param tag_data: Tag data.
        :param sub_object_type: Object types of the sub pages (either Page or VideoPage).
        :return:
        """
        page_request = self.get_object_request(tag_data)
        number_of_pages = self._get_number_of_sub_pages(tag_data, page_request)
        links, titles, numbers_of_videos = self._get_tag_properties(page_request)
        for i in range(2, number_of_pages + 1):
            page_request = self.get_object_request(tag_data, override_page_number=i)
            loc_links, loc_titles, loc_numbers_of_videos = self._get_tag_properties(page_request)
            links += loc_links
            titles += loc_titles
            numbers_of_videos += loc_numbers_of_videos
        partitioned_data = {
            chr(x): [(link, title, number_of_videos)
                     for link, title, number_of_videos in zip(links, titles, numbers_of_videos)
                     if title[0].upper() == chr(x)]
            for x in range(ord('A'), ord('Z')+1)
        }
        partitioned_data['#'] = [(link, title, number_of_videos)
                                 for link, title, number_of_videos in zip(links, titles, numbers_of_videos)
                                 if title[0].isdigit()]
        new_pages = [PornCatalogPageNode(catalog_manager=self.catalog_manager,
                                         obj_id=(IdGenerator.id_to_original_str(tag_data.id), k),
                                         title='{c} | Letter {p}'.format(c=tag_data.title, p=k),
                                         url=tag_data.url,
                                         raw_data=tag_data.raw_data,
                                         additional_data={'letter': k},
                                         object_type=sub_object_type,
                                         super_object=tag_data,
                                         )
                     for k in sorted(partitioned_data.keys()) if len(partitioned_data[k]) > 0]
        for new_page in new_pages:
            sub_tags = [PornCatalogCategoryNode(catalog_manager=self.catalog_manager,
                                                obj_id=link,
                                                url=urljoin(tag_data.url, link),
                                                title=title,
                                                number_of_videos=number_of_videos,
                                                object_type=self._get_tag_true_object_type_from_url(
                                                    urljoin(tag_data.url, link)),
                                                super_object=new_page,
                                                )
                        for link, title, number_of_videos in partitioned_data[new_page.additional_data['letter']]]
            new_page.add_sub_objects(sub_tags)

        tag_data.add_sub_objects(new_pages)

    def _get_tag_true_object_type_from_url(self, url):
        """
        Returns tag true object type. By default returns PornCategories.TAG.
        :param url:
        :return:
        """
        return PornCategories.TAG

    def _add_category_sub_pages(self, category_data, sub_object_type, page_request=None, clear_sub_elements=True):
        """
        Adds category sub pages.
        :param category_data: Category data object (PornCatalogCategoryNode).
        :param sub_object_type: Sub object type.
        :param page_request: Page request if such exist. In case it doesn't exist we fetch the object's url.
        :param clear_sub_elements: Flag that indicates whether we clear previous sub elements.
        :return:
        """
        if category_data.object_type == PornCategories.TAG_MAIN and self._make_tag_pages_by_letter is True:
            category_data.clear_sub_objects()
            return self._add_tag_sub_pages(category_data, sub_object_type)
        # elif category_data.object_type == SearchMain:
        #     # We have the search option, thus we don't use the web server
        #     use_web_server = False

        if clear_sub_elements is True:
            category_data.clear_sub_objects()
        if self._use_web_server is True:
            current_page_filters = self.get_proper_filter(category_data).current_filters_text()
            general_filters = self.general_filter.current_filters_text()
            raw_num_of_pages = self.data_server.fetch_request(category_data.url,
                                                              current_page_filters,
                                                              general_filters)
            if raw_num_of_pages['status'] is True:
                num_of_pages = int(raw_num_of_pages['value']['number_of_pages'])
            else:
                # If we have obsolete data we start our search from the last available page
                last_available_number_of_pages = int(raw_num_of_pages['value']['number_of_pages']) \
                    if raw_num_of_pages['status'] == 'Obsolete' else None
                num_of_pages = self._get_number_of_sub_pages(category_data, page_request,
                                                             last_available_number_of_pages)
                push_result = self.data_server.push_request(self.source_name,
                                                            category_data.url,
                                                            current_page_filters,
                                                            general_filters,
                                                            num_of_pages)
                if push_result['status'] is False:
                    warnings.warn(push_result['err'])
        else:
            num_of_pages = self._get_number_of_sub_pages(category_data, page_request)

        new_pages = [PornCatalogPageNode(catalog_manager=self.catalog_manager,
                                         obj_id=(IdGenerator.id_to_original_str(category_data.id), i),
                                         title='{c} | Page {p}'.format(c=category_data.title, p=i),
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
        name = video_data.title
        return name, self._clear_invalid_chars_from_filename(name)

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

    def _binary_search_max_number_of_pages(self, category_data, last_available_number_of_pages):
        """
        Performs binary search in order to find the last available page.
        :param category_data: Category data.
        :param last_available_number_of_pages: Last available number of pages. Will be the pivot for our next search.
        By default is None, which mean the original pivot will be used...
        :return: Page request
        """
        left_page = 1
        right_page = self.max_pages
        page = last_available_number_of_pages if last_available_number_of_pages is not None \
            else int(math.ceil((right_page + left_page) / 2))
        while 1:
            if right_page == left_page:
                return left_page

            page_request = self._get_object_request_no_exception_check(category_data, override_page_number=page)
            if self._check_is_available_page(category_data, page_request):
                tree = self.parser.parse(page_request.text)
                pages = self._get_available_pages_from_tree(tree)
                if len(pages) == 0:
                    # We also moved too far...
                    right_page = page - 1
                else:
                    max_page = max(pages)
                    if max_page - page < self._binary_search_page_threshold:
                        return max_page

                    left_page = max_page
            else:
                # We moved too far...
                right_page = page - 1
            page = int(math.ceil((right_page + left_page) / 2))

    def _binary_search_max_number_of_pages_with_broken_pages(self, category_data, last_available_number_of_pages):
        """
        Performs binary search in order to find the last available page.
        :param category_data: Category data.
        :param last_available_number_of_pages: Last available number of pages. Will be the pivot for our next search.
        By default is None, which mean the original pivot will be used...
        :return: Page request
        """
        left_page = 1
        right_page = self.max_pages
        page = last_available_number_of_pages if last_available_number_of_pages is not None \
            else int(math.ceil((right_page + left_page) / 2))
        while 1:
            if right_page == left_page:
                return left_page

            page_request = self._get_object_request_no_exception_check(category_data, override_page_number=page)
            if self._check_is_available_page(category_data, page_request):
                tree = self.parser.parse(page_request.text)
                pages = self._get_available_pages_from_tree(tree)
                if len(pages) == 0:
                    # We also moved too far...
                    right_page = page - 1
                else:
                    # Sometimes we have mistaken max page, so we take it only it is is lower then the right page.
                    pages = [x for x in sorted(pages, reverse=True) if x <= right_page]
                    max_page = pages[-1]
                    for p in pages:
                        page_request = self._get_object_request_no_exception_check(category_data,
                                                                                   override_page_number=p)
                        if self._check_is_available_page(category_data, page_request):
                            # The page is valid for left page
                            max_page = p
                            break

                    left_page = max_page
            else:
                # We moved too far...
                right_page = page - 1
            page = int(math.ceil((right_page + left_page) / 2))

    def _check_is_available_page(self, page_object, page_request=None):
        """
        In binary search performs test whether the current page is available.
        :param page_object: Page object.
        :param page_request: Page request.
        :return:
        """
        if page_request is None:
            page_request = self.get_object_request(page_object)
        return page_request.ok

    def _get_available_pages_from_tree(self, tree):
        """
        In binary looks for the available pages from current page tree.
        :param tree: Current page tree.
        :return: List of available trees
        """
        return NotImplemented

    @property
    def _binary_search_page_threshold(self):
        """
        Available pages threshold. 1 by default.
        """
        return NotImplemented

    def get_object_request(self, object_data, override_page_number=None, override_params=None, override_url=None):
        """
        Fetches the page number with respect to base url.
        :param object_data: Page data.
        :param override_page_number: Override page number.
        :param override_params: Override params.
        :param override_url: Override url.
        :return: Page request
        """
        res = self._get_object_request_no_exception_check(object_data, override_page_number, override_params,
                                                          override_url)
        if not self._check_is_available_page(object_data, res):
            # We give it another try
            time.sleep(1)
            res = self._get_object_request_no_exception_check(object_data, override_page_number, override_params,
                                                              override_url)
            if not self._check_is_available_page(object_data, res):
                error_module = self._prepare_porn_error_module(
                    object_data, 0, res.url,
                    'Could not fetch {url} in object {obj}'.format(url=res.url, obj=object_data.title))
                raise PornFetchUrlError(res, error_module)
        return res

    def _prepare_porn_error_module(self, object_data, error_mode, url, title):
        current_page_filters = self.get_proper_filter(object_data).current_filters_text()
        general_filters = self.general_filter.current_filters_text()
        error_module = PornErrorModule(self.data_server,
                                       error_mode,
                                       self.source_name,
                                       url,
                                       title,
                                       current_page_filters,
                                       general_filters
                                       )
        return error_module

    def _prepare_porn_error_module_for_video_page(self, video_data, url=None, title=None):
        if title is None:
            title = 'Cannot fetch video links from the url {u}'.format(u=url)
        if url is None:
            url = video_data.url
        error_module = PornErrorModule(self.data_server, 0, self.source_name, url, title, None, None)
        return error_module

    def _format_duration(self, raw_duration):
        """
        Converts the raw number into integer.
        :param raw_duration: Raw duration.
        :return:
        """
        if len(raw_duration.split(':')) == 1:
            hours = 0
            minutes = raw_duration
            seconds = 0
        elif len(raw_duration.split(':')) == 2:
            hours = 0
            minutes, seconds = raw_duration.split(':')
        elif len(raw_duration.split(':')) == 3:
            hours, minutes, seconds = raw_duration.split(':')
        else:
            raise ValueError('Wrong time format!')
        try:
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        except ValueError:
            return None
