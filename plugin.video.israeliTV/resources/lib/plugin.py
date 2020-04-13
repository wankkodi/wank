# -*- coding: utf-8 -*-

# from routing import routing
import routing
# import logging
import xbmcaddon
# from resources.lib import kodiutils
from resources.lib import kodilogging
import xbmcgui
import xbmcplugin
import xbmc

# handlers
from Fetchers.handlers.vod_handler import HandlerManager

# Types
# from Fetchers.catalogs.vod_catalog import VODCategories

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
logo_dir = path.join(addon_dir, 'resources', 'lib', 'Fetchers', 'channels', 'Logos')
arrows_dir = path.join(logo_dir, 'Arrows')
user_data_dir = path.join(addon_dir, 'resources', 'lib', 'Data')
session_id_dir = path.join(user_data_dir, 'SessionID')
if not path.isdir(session_id_dir):
    makedirs(session_id_dir)

separator = "|"

prev_page_image = path.join(arrows_dir, 'Prev-Page-PNG-Image-Background2.png')
next_page_image = path.join(arrows_dir, 'Next-Page-PNG-Image-Background2.png')
jump_to_page_image = path.join(arrows_dir, 'Jump-To-Page-PNG-Image-Background2.png')

# GUI texts
manual_page_input = 'Please enter the page [{i}..{j}]'
live_tv_title = 'Live TV'
vod_title = 'VOD'
search_title = 'Search'
new_search = 'New search'
enter_search_input = 'Please enter the search input:'


class HandlerWrapper(object):
    handlers = None


handler_wrapper = HandlerWrapper()

search_history_path = path.join(session_id_dir, 'search.dat')
search_history = []


# Main page routing
@plugin.route('/')
def choose_handler():
    log('Welcome to Israeli tv!')
    items = []

    # Live TV
    u = plugin.url_for(choose_live)
    item = xbmcgui.ListItem(live_tv_title)
    item.setArt({'icon': "DefaultVideo.png"})
    items.append((u, item, True))

    # VOD
    u = plugin.url_for(choose_vod)
    item = xbmcgui.ListItem(vod_title)
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


@plugin.route('/choose_live/')
def choose_live():
    items = []
    for handler_id in handler_wrapper.handlers.handlers:
        handler = handler_wrapper.handlers.get_handler(int(handler_id))
        if handler.categories_enum.LIVE_VIDEO not in handler.object_urls:
            continue

        live_info = handler.get_live_stream_info()

        u = plugin.url_for(play_live_stream, handler_id=handler_id)
        try:
            item = xbmcgui.ListItem('{c}: {t}'.format(c=handler.source_name, t=live_info.title), )
            item.setArt({'icon': "DefaultTVShows.png", 'thumb': live_info.image_link})

            item.setInfo(type="Video", infoLabels={"Title": live_info.title, "Plotoutline": live_info.subtitle,
                                                   "Plot": live_info.description, 'Duration': live_info.duration})
            item.setProperty('IsPlayable', 'true')
            item.addAvailableArtwork(url=live_info.image_link, art_type="thumb")
            items.append((u, item, False))
        except AttributeError as err:
            raise AttributeError('Cannot fetch {s} live info!\n{e}'.format(s=handler.source_name, e=err.message))

    status = xbmcplugin.addDirectoryItems(handle=plugin.handle, items=items, totalItems=len(items))
    xbmcplugin.endOfDirectory(plugin.handle)

    # xbmcplugin.setContent(plugin.handle, 'episodes')
    # xbmc.executebuiltin("Container.SetViewMode(504)")
    # handler_wrapper.handlers.store_data_for_all_handlers()
    return status


@plugin.route('/choose_vod/')
def choose_vod():
    items = []
    for v in handler_wrapper.handlers.handlers.values():
        # u = plugin.url_for(choose_handler)
        u = plugin.url_for(show_vod_programs, handler_id=v.handler_id, args='_first_run', page_number=1)
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
    for handler_id, handler_data in handler_wrapper.handlers.handlers.items():
        handler = handler_wrapper.handlers.get_handler(int(handler_id))
        if handler.categories_enum.SEARCH_MAIN not in handler.object_urls:
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


# Vod routing
@plugin.route('/show_vod_programs/<handler_id>/<args>/<page_number>')
def show_vod_programs(handler_id, args, page_number):
    if args == '_first_run':
        args = ''
    handler = handler_wrapper.handlers.get_handler(int(handler_id))
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

    items = prepare_list_items(show_list, handler_id)
    # In case we have additional pages, we prepare another page
    additional_pages = prepare_additional_pages(show_list, handler_id, show_vod_programs, page_vod_input_window, args)
    items += additional_pages

    status = xbmcplugin.addDirectoryItems(handle=plugin.handle, items=items, totalItems=len(items))
    xbmcplugin.endOfDirectory(plugin.handle)

    # xbmcplugin.setContent(plugin.handle, 'episodes')
    # xbmc.executebuiltin("Container.SetViewMode(504)")

    handler_wrapper.handlers.store_data_for_handler(int(handler_id))
    return status


@plugin.route('/page_vod_input_window/<handler_id>/<args>/<page_number>/<start_page>/<end_page>')
def page_vod_input_window(handler_id, args, page_number, start_page, end_page):
    return page_input_window(handler_id, args, page_number, start_page, end_page, show_vod_programs)


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
        dialog = xbmcgui.Dialog()
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

    handler = handler_wrapper.handlers.get_handler(int(handler_id))
    search_results = handler.search_query(query)
    return show_search_programs(handler_id, str(search_results.id), str(1))


@plugin.route('/show_search_programs/<handler_id>/<args>/<page_number>')
def show_search_programs(handler_id, args, page_number):
    if args == '_first_run':
        args = ''
    handler = handler_wrapper.handlers.get_handler(int(handler_id))
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
    additional_pages = prepare_additional_pages(show_list, handler_id, show_search_programs, page_search_input_window,
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
    return page_input_window(handler_id, args, page_number, start_page, end_page, show_search_programs)


# Play routing
@plugin.route('/play_episode/<handler_id>/<args>')
def play_episode(handler_id, args):
    handler = handler_wrapper.handlers.get_handler(int(handler_id))
    log('Playing videos for handler {i} and ids: {ids}'.format(i=handler_id, ids=args))
    episode = handler.get_show_object(*(int(x) for x in args.split(separator)))
    log('Site video links {0}.'.format(episode.url if type(episode.url) == str else episode.url.encode('utf-8')))

    # import web_pdb
    # web_pdb.set_trace()

    video_data = handler.get_video_links_from_video_data(episode)
    play_video(handler, video_data)


@plugin.route('/play_live_stream/<handler_id>')
def play_live_stream(handler_id):
    handler = handler_wrapper.handlers.get_handler(int(handler_id))
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

    items = []
    # import web_pdb
    # web_pdb.set_trace()

    handler = handler_wrapper.handlers.get_handler(int(handler_id))
    for x in show_list.sub_objects:
        if x.object_type in (handler.categories_enum.VIDEO, ):
            func_call = play_episode
            is_playable = 'true'
            is_folder = False
            icon = 'DefaultTVShows.png'
        elif x.object_type in (handler.categories_enum.LIVE_VIDEO, ):
            func_call = play_live_stream
            is_playable = 'true'
            is_folder = False
            icon = 'DefaultTVShows.png'
        else:
            func_call = show_vod_programs
            is_playable = 'false'
            is_folder = True
            icon = 'DefaultFolder.png'

        ids = x.get_full_id_path()
        log('Ids for the title {t} are: {ids}'.format(t=x.title, ids=ids))
        args = separator.join([str(y) for y in ids])
        u = plugin.url_for(func_call, handler_id=handler_id, args=args, page_number=1)
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
    dialog = xbmcgui.Dialog()
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

    session_id_path = path.join(session_id_dir, 'id.dat')

    # import web_pdb
    # web_pdb.set_trace()

    current_id = plugin.handle
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
