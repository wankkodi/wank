# -*- coding: utf-8 -*-

# from routing import routing
import routing
# import logging
import xbmcaddon
# from resources.lib import kodiutils
from . import kodilogging
import xbmcgui
import xbmcplugin
import xbmc

# Sub modules
from .plugin_porn_settings import Settings

# handlers
from Fetchers.handlers.porn_handler import HandlerManager

# Types
from Fetchers.catalogs.porn_catalog import PornCategories

# import sys
from os import path, makedirs

# datetime
from datetime import datetime

# pickle
import pickle

# Internet tools
import sys
if sys.version_info >= (3, 0):
    from urllib.parse import urlparse, quote_plus
else:
    from urlparse import urlparse
    from urllib import quote_plus


# tmp
# import html5lib
# from my_parser_wrapper import MyParser


ADDON = xbmcaddon.Addon()
# logger = logging.getLogger(ADDON.getAddonInfo('id'))
kodilogging.config()
plugin = routing.Plugin()
player = xbmc.Player()
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

addon_dir = xbmc.translatePath(ADDON.getAddonInfo('path'))
logo_dir = path.join(addon_dir, 'resources', 'lib', 'Fetchers', 'hidden', 'Logos')
arrows_dir = path.join(logo_dir, 'Arrows')
user_data_dir = path.join(addon_dir, 'resources', 'lib', 'Data')
user_data_filename = path.join(user_data_dir, 'user_data.dat')
session_id_dir = path.join(user_data_dir, 'SessionID')
if not path.isdir(session_id_dir):
    makedirs(session_id_dir)

separator = "|"

prev_page_image = path.join(arrows_dir, 'Prev-Page-PNG-Image-Background2.png')
next_page_image = path.join(arrows_dir, 'Next-Page-PNG-Image-Background2.png')
jump_to_page_image = path.join(arrows_dir, 'Jump-To-Page-PNG-Image-Background2.png')

# GUI texts
manual_page_input = 'Please enter the page [{i}..{j}]'
live_porn_title = 'Live Porn Sites'
porn_title = 'Porn Sites'
search_title = 'Search'
new_search = 'New search'
enter_search_input = 'Please enter the search input:'


class HandlerWrapper(object):
    handlers = None


handler_wrapper = HandlerWrapper()

search_history_path = path.join(session_id_dir, 'search.dat')
search_history = []

# XML dialog window
# dialog_xml = xbmcgui.WindowXMLDialog('dialogs.xml', xbmcaddon.Addon().getAddonInfo('path').decode('utf-8'))


# Settings
# @plugin.route('/')
# def initialize_settings():
#     log('Setting up the settings')
#     # Initialize setting
#
#     # xbmcplugin.setContent(plugin.handle, 'episodes')
#     # xbmc.executebuiltin("Container.SetViewMode(504)")
#     return settings


# Main page routing
@plugin.route('/')
def choose_handler():
    log('Welcome to Wank! Wank! Wank!')
    items = []

    # Main Porn
    u = plugin.url_for(choose_porn)
    item = xbmcgui.ListItem(porn_title)
    item.setArt({'icon': "DefaultFolder.png"})
    items.append((u, item, True))

    # Search
    u = plugin.url_for(choose_search)
    item = xbmcgui.ListItem(search_title)
    item.setArt({'icon': "DefaultAddonsSearch.png"})
    items.append((u, item, True))

    status = xbmcplugin.addDirectoryItems(handle=plugin.handle, items=items,
                                          totalItems=len(handler_wrapper.handlers.handlers))
    xbmcplugin.endOfDirectory(plugin.handle)

    # xbmcplugin.setContent(plugin.handle, 'episodes')
    # xbmc.executebuiltin("Container.SetViewMode(504)")
    return status


# @plugin.route('/update_settings/<setting_id>')
# def update_settings(setting_id):
#     settings.update_settings_gui()
#

@plugin.route('/update_settings/<setting_id>')
def update_settings(setting_id):
    if setting_id == 'update_is_pin_code':
        value = ADDON.getSetting('is_pin_code')
        settings.update_is_pin_code(value)
    elif setting_id == 'update_pin_code':
        value = settings.update_pin_code()
    elif setting_id == 'update_send_data':
        value = ADDON.getSetting('is_send_data')
        settings.update_is_send_data(value)
    else:
        raise ValueError('Unknown setting id {sid}'.format(sid=setting_id))
    log('Changing setting {s} to value {v}'.format(s=setting_id, v=value))


@plugin.route('/choose_porn/')
def choose_porn():
    items = []
    handlers = sorted(handler_wrapper.handlers.handlers.items(), key=lambda x: -x[0])
    for _, v in handlers:
        # u = plugin.url_for(choose_handler)
        u = plugin.url_for(show_porn_programs, handler_id=v.handler_id, args='_first_run',
                           page_number=1)
        item = xbmcgui.ListItem(v.title,)
        item.setArt({'icon': "DefaultFolder.png", 'thumb': v.image})
        item.addAvailableArtwork(url=v.image, art_type="thumb")
        items.append((u, item, True))
    status = xbmcplugin.addDirectoryItems(handle=plugin.handle, items=items, totalItems=len(items))
    xbmcplugin.endOfDirectory(plugin.handle)

    # xbmcplugin.setContent(plugin.handle, 'episodes')
    # xbmc.executebuiltin("Container.SetViewMode(504)")
    # handler_wrapper.handlers.store_data_for_all_handlers()
    return status


@plugin.route('/choose_search/')
def choose_search():
    # import web_pdb
    # web_pdb.set_trace()

    items = []
    handlers = sorted(handler_wrapper.handlers.handlers.items(), key=lambda x: -x[0])
    for handler_id, handler_data in handlers:
        handler = handler_wrapper.handlers.get_handler(handler_id=int(handler_id),
                                                       use_web_server=bool(ADDON.getSetting('is_send_data')))
        if PornCategories.SEARCH_MAIN not in handler.object_urls:
            continue

        u = plugin.url_for(prepare_search_sources, handler_id=handler_id)
        item = xbmcgui.ListItem(handler.source_name, )
        item.setArt({'icon': "DefaultTVShows.png", 'thumb': handler_data.image})
        item.addAvailableArtwork(url=handler_data.image, art_type="thumb")
        items.append((u, item, True))

    status = xbmcplugin.addDirectoryItems(handle=plugin.handle, items=items, totalItems=len(items))
    xbmcplugin.endOfDirectory(plugin.handle)

    # xbmcplugin.setContent(plugin.handle, 'episodes')
    # xbmc.executebuiltin("Container.SetViewMode(504)")
    # handler_wrapper.handlers.store_data_for_all_handlers()
    return status


# Porn routing
@plugin.route('/show_porn_programs/<handler_id>/<args>/<page_number>')
def show_porn_programs(handler_id, args, page_number):
    if args == '_first_run':
        args = ''
    handler = handler_wrapper.handlers.get_handler(handler_id=int(handler_id),
                                                   use_web_server=bool(ADDON.getSetting('is_send_data')))
    log('Showing programs for handler {i} and ids: {ids}'.format(i=handler_id, ids=args))
    if len(args) > 0:
        # log(str([int(x) for x in args.split(separator)]))
        # import web_pdb
        # web_pdb.set_trace()
        show_list = handler.get_show_object(*(int(x) for x in args.split(separator)))
        if show_list.page_number is not None and show_list.page_number != int(page_number):
            new_object = [x for x in show_list.super_object.sub_objects if x.page_number == int(page_number)]
            new_args = separator.join(args.split(separator)[:-1]) + separator + str(new_object[0].id)
            show_list = handler.get_show_object(*(int(x) for x in new_args.split(separator)))

    else:
        # import web_pdb
        # web_pdb.set_trace()
        show_list = handler.get_show_object(*())

    if len(show_list.sub_objects) == 1:
        # We go straight ahead to its subcategory
        new_id = separator.join([str(y) for y in show_list.sub_objects[0].get_full_id_path()])
        return show_porn_programs(handler_id, new_id,
                                  show_list.sub_objects[0].page_number)
    items = prepare_list_items(show_list, handler_id)
    # In case we have additional pages, we prepare another page
    additional_pages = prepare_additional_pages(show_list, handler_id, show_porn_programs, page_porn_input_window,
                                                args)
    items += additional_pages

    status = xbmcplugin.addDirectoryItems(handle=plugin.handle, items=items, totalItems=len(items))
    xbmcplugin.endOfDirectory(plugin.handle)

    # xbmcplugin.setContent(plugin.handle, 'episodes')
    # xbmc.executebuiltin("Container.SetViewMode(504)")

    handler_wrapper.handlers.store_data_for_handler(int(handler_id))
    return status


@plugin.route('/page_porn_input_window/<handler_id>/<args>/<page_number>/<start_page>/<end_page>')
def page_porn_input_window(handler_id, args, page_number, start_page, end_page):
    return page_input_window(handler_id, args, page_number, start_page, end_page, show_porn_programs)


# Search routing
@plugin.route('/prepare_search_sources/<handler_id>')
def prepare_search_sources(handler_id):
    # import web_pdb
    # web_pdb.set_trace()
    # Create Options
    search_icon = 'DefaultAddonsSearch.png'
    items = []
    u = plugin.url_for(perform_search, handler_id=handler_id, search_flag='new_search')
    item = xbmcgui.ListItem(new_search)
    item.setArt({'icon': "DefaultTVShows.png", 'thumb': search_icon})
    items.append((u, item, True))
    for i, query in enumerate(search_history):
        u = plugin.url_for(perform_search, handler_id=handler_id, search_flag=i)
        item = xbmcgui.ListItem(query, 'new_search')
        item.setArt({'icon': "DefaultTVShows.png", 'thumb': search_icon})
        items.append((u, item, True))

    status = xbmcplugin.addDirectoryItems(handle=plugin.handle, items=items, totalItems=len(items))
    xbmcplugin.endOfDirectory(plugin.handle)
    return status


@plugin.route('/perform_search/<handler_id>/<search_flag>')
def perform_search(handler_id, search_flag):
    # import web_pdb
    # web_pdb.set_trace()
    if search_flag == 'new_search':
        query = dialog.input(enter_search_input)
        if query in search_history:
            # We pop it from the list, since it will be added to the top of the list anyway...
            i = search_history.index(query)
            search_history.pop(i)

        search_history.insert(0, query)
        with open(search_history_path, 'wb') as fl:
            pickle.dump(search_history, fl)
    else:
        query = search_history[int(search_flag)]

    handler = handler_wrapper.handlers.get_handler(handler_id=int(handler_id),
                                                   use_web_server=bool(ADDON.getSetting('is_send_data')))
    search_results = handler.search_query(query)
    return show_search_history(handler_id, str(search_results.id), str(1))


@plugin.route('/show_search_history/<handler_id>/<args>/<page_number>')
def show_search_history(handler_id, args, page_number):
    if args == '_first_run':
        args = ''
    handler = handler_wrapper.handlers.get_handler(handler_id=int(handler_id),
                                                   use_web_server=bool(ADDON.getSetting('is_send_data')))
    log('Showing programs for handler {i} and ids: {ids}'.format(i=handler_id, ids=args))
    if len(args) > 0:
        # log(str([int(x) for x in args.split(separator)]))
        # import web_pdb
        # web_pdb.set_trace()
        show_list = handler.get_show_object(int(args))
        if show_list.page_number is not None and show_list.page_number != int(page_number):
            new_object = [x for x in show_list.super_object.sub_objects if x.page_number == int(page_number)]
            show_list = handler.get_search_object(new_object[0].id)

    else:
        # import web_pdb
        # web_pdb.set_trace()
        raise ValueError('Args length must be greater than 0!')

    items = prepare_list_items(show_list, handler_id)
    # In case we have additional pages, we prepare another page
    additional_pages = prepare_additional_pages(show_list, handler_id, show_search_history, page_search_input_window,
                                                args)
    items += additional_pages

    status = xbmcplugin.addDirectoryItems(handle=plugin.handle, items=items, totalItems=len(items))
    xbmcplugin.endOfDirectory(plugin.handle)

    # xbmcplugin.setContent(plugin.handle, 'episodes')
    # xbmc.executebuiltin("Container.SetViewMode(504)")

    handler_wrapper.handlers.store_data_for_handler(int(handler_id))
    return status


@plugin.route('/page_search_input_window/<handler_id>/<args>/<page_number>/<start_page>/<end_page>')
def page_search_input_window(handler_id, args, page_number, start_page, end_page):
    return page_input_window(handler_id, args, page_number, start_page, end_page, show_search_history)


# Play routing
@plugin.route('/play_episode/<handler_id>/<args>')
def play_episode(handler_id, args):
    handler = handler_wrapper.handlers.get_handler(handler_id=int(handler_id),
                                                   use_web_server=bool(ADDON.getSetting('is_send_data')))
    log('Playing videos for handler {i} and ids: {ids}'.format(i=handler_id, ids=args))
    episode = handler.get_show_object(*(int(x) for x in args.split(separator)))
    log('Site video links {0}.'.format(episode.url if type(episode.url) == str else episode.url.encode('utf-8')))

    # import web_pdb
    # web_pdb.set_trace()

    video_data = handler.get_video_links_from_video_data(episode)
    play_video(handler, video_data)


@plugin.route('/play_live_stream/<handler_id>')
def play_live_stream(handler_id):
    handler = handler_wrapper.handlers.get_handler(handler_id=int(handler_id),
                                                   use_web_server=bool(ADDON.getSetting('is_send_data')))
    log('Playing live stream for handler {i}'.format(i=handler_id))

    video_data = handler.get_live_stream_video_link()
    play_video(handler, video_data)


def play_video(handler, video_data):
    if len(video_data.video_sources) > 1:
        video_i = xbmcgui.Dialog().select('Please select the stream: ',
                                          ['; '.join(['{q}: {v}'.format(q=x, v=y.__dict__[x])
                                                     for x in ('resolution', 'quality', 'codec', 'size',)
                                                     if y.__dict__[x] is not None])
                                           for y in video_data.video_sources])
    else:
        video_i = 0

    log('Video page links {0}.'.format(video_data.video_sources[video_i]))
    video_link = video_data.video_sources[video_i].link

    fetched_cookies = handler.session.cookies if video_data.cookies is None else video_data.cookies
    fetched_cookies_str = ';'.join(['{0}={1}'.format(quote_plus(k), quote_plus(v))
                                    for k, v in fetched_cookies.items()])
    fetched_user_agent = handler.user_agent
    additional_headers = {}
    if video_data.headers is not None:
        additional_headers = {k: v for k, v in video_data.headers.items()
                              if k not in ('User-Agent', 'Cookie')}

    player.stop()
    playlist.clear()
    if 'https://www.youtube.com/embed' in video_link:
        # In case we have embed youtube url
        # We correct the url
        video_url = correct_youtube_url(video_link)
    else:
        video_url = '{0}|User-Agent={1}&Cookie={2}' \
                    ''.format(video_link.encode('utf-8'), fetched_user_agent, fetched_cookies_str)
        for k, v in additional_headers.items():
            video_url += '&{0}={1}'.format(k, v)
    # play_item = xbmcgui.ListItem(path=video_url)
    log('Video link {0}.'.format(video_url))

    # import web_pdb
    # web_pdb.set_trace()
    play_item = xbmcgui.ListItem(path=video_url)
    xbmcplugin.setResolvedUrl(handle=plugin.handle, succeeded=True, listitem=play_item)
    # player.play(video_url)


# General routing
def prepare_list_items(show_list, handler_id):
    if show_list.sub_objects is None:
        return []

    handler = handler_wrapper.handlers.get_handler(handler_id=int(handler_id),
                                                   use_web_server=bool(ADDON.getSetting('is_send_data')))
    items = []
    # import web_pdb
    # web_pdb.set_trace()

    if show_list.object_type == handler.categories_enum.GENERAL_MAIN:
        # We sort the main page
        sub_objects = sorted((x for x in show_list.sub_objects),
                             key=lambda y: (y.object_type.value[0].value, y.object_type.value[1]))
    else:
        sub_objects = show_list.sub_objects

    for x in sub_objects:
        if x.object_type in (PornCategories.VIDEO, ):
            func_call = play_episode
            is_playable = 'true'
            is_folder = False
            icon = 'DefaultTVShows.png'
        elif x.object_type in (PornCategories.LIVE_VIDEO, ):
            func_call = play_live_stream
            is_playable = 'true'
            is_folder = False
            icon = 'DefaultTVShows.png'
        else:
            func_call = show_porn_programs
            is_playable = 'false'
            is_folder = True
            icon = 'DefaultFolder.png'

        ids = x.get_full_id_path()
        log('Ids for the title {t} are: {ids}'.format(t=x.title, ids=ids))
        args = separator.join([str(y) for y in ids])
        u = plugin.url_for(func_call, handler_id=handler_id, args=args, page_number=x.page_number)
        item = xbmcgui.ListItem(x.title)
        item.setArt({'icon': icon, 'thumb': x.image_link})

        item.setInfo(type="Video", infoLabels={"Title": x.title, "Plotoutline": x.subtitle, "Plot": x.description,
                                               'Duration': x.duration})
        item.setProperty('IsPlayable', is_playable)
        item.addAvailableArtwork(url=x.image_link, art_type="thumb")
        items.append((u, item, is_folder))
    return items


def prepare_additional_pages(show_list, handler_id, func_call, page_func_call, args):
    def _prepare_additional_object_link(_additional_object, _is_playable, _func_call, _args, _page_number, _image):
        _u = plugin.url_for(_func_call, handler_id=handler_id, args=_args, page_number=_page_number)
        _item = xbmcgui.ListItem(_additional_object.title + ' page {i}'.format(i=_additional_object.page_number))
        _item.setArt({'icon': "DefaultFolder.png", 'thumb': _image})

        _item.setInfo(type="Video", infoLabels={"Title": _additional_object.title,
                                                "Plotoutline": _additional_object.subtitle,
                                                "Plot": _additional_object.description,
                                                })
        _item.setProperty('IsPlayable', _is_playable)
        # _item.addAvailableArtwork(url=_additional_object.image_link, art_type="thumb")
        return _u, _item

    items = []
    if show_list.super_object is not None and show_list.super_object.sub_objects is not None:
        prev_object = [x for x in show_list.super_object.sub_objects
                       if x.page_number is not None and x.page_number + 1 == show_list.page_number]
        prev_object = prev_object[0] if len(prev_object) else None
        next_object = [x for x in show_list.super_object.sub_objects
                       if x.page_number is not None and x.page_number - 1 == show_list.page_number]
        next_object = next_object[0] if len(next_object) else None
    else:
        prev_object = None
        next_object = None

    # import web_pdb
    # web_pdb.set_trace()
    is_playable = 'false'
    is_folder = True
    if prev_object is not None:
        u, item = _prepare_additional_object_link(prev_object, is_playable, func_call, args, prev_object.page_number,
                                                  prev_page_image)
        items.append((u, item, is_folder))
    # We also try to create the manual input from the user
    if prev_object is not None or next_object is not None:
        u = plugin.url_for(page_func_call, handler_id=handler_id, args=args, page_number=show_list.page_number,
                           start_page=1, end_page=len(show_list.super_object.sub_objects) + 1)
        item = xbmcgui.ListItem('Jump to page...')
        item.setArt({'icon': "DefaultFolder.png", 'thumb': jump_to_page_image})

        item.setInfo(type="Video", infoLabels={"Title": 'Jump to page...'})
        item.setProperty('IsPlayable', 'false')
        items.append((u, item, is_folder))
    if next_object is not None:
        u, item = _prepare_additional_object_link(next_object, is_playable, func_call, args, next_object.page_number,
                                                  next_page_image)
        items.append((u, item, is_folder))
    return items


def page_input_window(handler_id, args, page_number, start_page, end_page, func_call):
    while 1:
        res = dialog.numeric(0, manual_page_input.format(i=start_page, j=end_page))
        if len(res) == 0:
            return None
        res = int(res)
        if res not in range(int(start_page), int(end_page)+1):
            dialog.notification('Wrong page number.',
                                'The page must be between [{i}..{j}]. Got {k} instead.'
                                ''.format(i=start_page, j=end_page, k=res))
        else:
            break

    # import web_pdb
    # web_pdb.set_trace()
    if res == int(page_number):
        return None
    else:
        return func_call(handler_id, args, res)


def correct_youtube_url(embed_url):
    """
    Corrects the embed youtube url into normal one...
    :param embed_url: Embed youtube url (i.e. https://www.youtube.com/embed/uRp9un7ixsw).
    :return: Correct Youtube url (i.e. https://www.youtube.com/watch?v=uRp9un7ixsw).
    """
    split_url = urlparse(embed_url)
    return 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % split_url.path.split('/')[-1]


def log(txt):
    if sys.version_info < (3, 0):
        # Log admits both unicode strings and str encoded with "utf-8" (or ascii). will fail with other str encodings.
        if isinstance(txt, str):
            # if it is str we assume it's "utf-8" encoded.
            # will fail if called with other encodings (latin, etc) BE ADVISED!
            txt = txt.decode("utf-8")
        # At this point we are sure txt is a unicode string.
        message = u'%s: %s' % (ADDON.getAddonInfo('id'), txt)
        xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)
        # I reencode to utf-8 because in many xbmc versions log doesn't admit unicode.
    else:
        message = '%s: %s' % (ADDON.getAddonInfo('id'), txt)
        xbmc.log(msg=message, level=xbmc.LOGDEBUG)


def run():
    if settings.must_enter_pin or settings.is_blocked:
        return None

    session_id_path = path.join(session_id_dir, 'id.dat')
    # import web_pdb
    # web_pdb.set_trace()
    if current_id != 1 and path.isfile(session_id_path):
        with open(session_id_path, 'rb') as fl:
            session_id = pickle.load(fl)
    else:
        # We have a new session, so we create a new file
        session_id = id(datetime.now())
        with open(session_id_path, 'wb') as fl:
            pickle.dump(session_id, fl)

    # Load history
    if path.isfile(search_history_path):
        with open(search_history_path, 'rb') as fl:
            search_history.extend(pickle.load(fl))

    handler_wrapper.handlers = HandlerManager(logo_dir, user_data_dir, session_id)

    plugin.run()
    handler_wrapper.handlers.store_data_for_all_handlers()


# Dialog
dialog = xbmcgui.Dialog()
current_id = plugin.handle
settings = Settings(user_data_filename, dialog, ADDON.getLocalizedString, current_id == 1)
# Initialize setting
ADDON.setSetting('is_pin_code', str(bool(settings.is_use_pin) is True).lower())
log('is_pin_code: {r}, {b}'.format(r=settings.is_use_pin, b=bool(settings.is_use_pin)))
ADDON.setSetting('set_pin_code', str(settings.pin_code).zfill(4))
log('set_pin_code: {r}, {b}'.format(r=settings.is_use_pin, b=settings.pin_code))
ADDON.setSetting('is_send_data', str(bool(settings.is_send_data) is True).lower())
log('is_send_data: {r}, {b}'.format(r=settings.is_send_data, b=bool(settings.is_send_data)))
