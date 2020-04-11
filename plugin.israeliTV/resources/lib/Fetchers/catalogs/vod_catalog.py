from .base_catalog import *


class VODCategories(Enum):
    # Copy from BaseCategories :(
    PAGE = 0
    VIDEO = 1
    VIDEO_PAGE = 2
    SEARCH_MAIN = 3
    SEARCH_PAGE = 4
    GENERAL_MAIN = 5
    LIVE_VIDEO = 6
    LIVE_SCHEDULE = 7

    # Special VOD object types
    CHANNELS_MAIN = ('VOD', 0)
    GENERAL_CHANNEL_SUB_CATEGORY = (CHANNELS_MAIN, 0)
    SHOWS_MAIN = ('VOD', 1)
    MOVIES_MAIN = ('VOD', 2)
    SERIES_MAIN = ('VOD', 3)
    KIDS_MAIN = ('VOD', 4)
    SHOW_GENRE = ('VOD', 5)
    MOVIE_GENRE = ('VOD', 6)
    KIDS_GENRE = ('VOD', 7)
    SHOW_SEASON = ('VOD', 8)
    SHOW = ('VOD', 9)
    KIDS_SHOW = ('VOD', 10)
    KIDS_SHOW_SEASON = ('VOD', 11)
    TV_CHANNELS = ('VOD', 12)
    TV_CHANNEL = ('VOD', 13)


class VODFilter(object):
    @property
    def general_filters(self):
        return self._general_filter

    @property
    def channels_filters(self):
        return self._channels_filter

    @property
    def videos_filters(self):
        return self._video_filter

    @property
    def search_filters(self):
        return self._search_filter

    def __init__(self, data_dir, general_args=None, channels_args=None, video_args=None, search_args=None):
        if general_args is None:
            general_args = {}
        self._general_filter = VideoFilter(data_dir, 'general_filters.dat', **general_args)

        if channels_args is None:
            channels_args = {}
        self._channels_filter = VideoFilter(data_dir, 'channels_filters.dat', **channels_args)

        if video_args is None:
            video_args = {}
        self._video_filter = VideoFilter(data_dir, '_video_filters.dat', **video_args)

        if search_args is None:
            search_args = {}
        self._search_filter = VideoFilter(data_dir, 'search_filters.dat', **search_args)


class VODCatalogNode(CatalogNode):
    @property
    def _false_object_types(self):
        return VODCategories.PAGE, VODCategories.VIDEO_PAGE, VODCategories.SEARCH_PAGE
