# -*- coding: utf-8 -*-

# from routing import routing
import routing
# import logging
import xbmcaddon
# from resources.lib import kodiutils
# from resources.lib import kodilogging
from xbmcgui import ListItem
import xbmcplugin
import xbmc

from Channels.mako import Mako, Bip
from Channels.reshet import Reshet
from Channels.sport5 import Sport5
from Channels.kan import Kan, KanEducation
from Channels.hot import Hot, HotBidur, HotEight, HotThree, HotYoung, HotZoom
from Channels.walla import Walla
from Channels.channel20 import Channel20
import urllib

# import sys
from os import path

# tmp
# from my_parser_wrapper import MyParser


ADDON = xbmcaddon.Addon()
# logger = logging.getLogger(ADDON.getAddonInfo('id'))
# kodilogging.config()
plugin = routing.Plugin()

addon_dir = xbmc.translatePath(ADDON.getAddonInfo('path'))
# addon_save_dir = xbmc.translatePath(ADDON.getAddonInfo('profile'))
logo_dir = path.join(addon_dir, 'resources', 'lib', 'Logos')
user_data_dir = path.join(addon_dir, 'resources', 'lib', 'Data')
separator = "|"


class SourceHandler(object):
    def __init__(self, source_name):
        if source_name == 'mako':
            self.handler_id = -1
            self.main_module = Mako(vod_id=self.handler_id, data_dir=user_data_dir)
            self.sub_modules = [SourceHandler('bip'), ]
            self.image = path.join(logo_dir, 'makoTV_200X200.jpg')
        elif source_name == 'bip':
            self.handler_id = -2
            self.main_module = Bip(vod_id=self.handler_id, data_dir=user_data_dir)
            self.sub_modules = None
            self.image = path.join(logo_dir, 'Bip_Logo1.jpg')
        elif source_name == 'reshet':
            self.handler_id = -3
            self.main_module = Reshet(vod_id=self.handler_id, data_dir=user_data_dir)
            self.sub_modules = None
            self.image = path.join(logo_dir, 'reshet.png')
        elif source_name == 'kan':
            self.handler_id = -4
            self.main_module = Kan(vod_id=self.handler_id, data_dir=user_data_dir)
            self.sub_modules = [self, SourceHandler('kan_education')]
            self.image = path.join(logo_dir, 'logo_ogImageKan.jpg')
        elif source_name == 'kan_education':
            self.handler_id = -5
            self.main_module = KanEducation(vod_id=self.handler_id, data_dir=user_data_dir)
            self.sub_modules = None
            self.image = path.join(logo_dir, 'lan1084_img.jpg')
        elif source_name == 'hot':
            self.handler_id = -6
            self.main_module = Hot(vod_id=self.handler_id, data_dir=user_data_dir)
            self.sub_modules = [SourceHandler('hot_three'), SourceHandler('hot_bidur'), SourceHandler('hot_eight'),
                                SourceHandler('hot_young'), SourceHandler('hot_zoom'), ]
            self.image = path.join(logo_dir, '1200px-HotNewLogo.svg.png')
        elif source_name == 'hot_three':
            self.handler_id = -7
            self.main_module = HotThree(vod_id=self.handler_id, data_dir=user_data_dir)
            self.sub_modules = None
            self.image = path.join(logo_dir, '250px-HOT3_logo_2010.svg.png')
        elif source_name == 'hot_bidur':
            self.handler_id = -8
            self.main_module = HotBidur(vod_id=self.handler_id, data_dir=user_data_dir)
            self.sub_modules = None
            self.image = path.join(logo_dir, '250px-הוט_בידור_ישראלי.jpeg')
        elif source_name == 'hot_eight':
            self.handler_id = -9
            self.main_module = HotEight(vod_id=self.handler_id, data_dir=user_data_dir)
            self.sub_modules = None
            self.image = path.join(logo_dir, 'hot8.jpg')
        elif source_name == 'hot_young':
            self.handler_id = -10
            self.main_module = HotYoung(vod_id=self.handler_id, data_dir=user_data_dir)
            self.sub_modules = None
            self.image = path.join(logo_dir, 'unnamed.jpg')
        elif source_name == 'hot_zoom':
            self.handler_id = -11
            self.main_module = HotZoom(vod_id=self.handler_id, data_dir=user_data_dir)
            self.sub_modules = None
            self.image = path.join(logo_dir, 'H69111167_logos_510X1478.jpg')
        elif source_name == 'sport5':
            self.handler_id = -12
            self.main_module = Sport5(vod_id=self.handler_id, data_dir=user_data_dir)
            self.sub_modules = None
            self.image = path.join(logo_dir, '424px-Sport5ch.svg.png')
        elif source_name == 'walla':
            self.handler_id = -13
            self.main_module = Walla(vod_id=self.handler_id, data_dir=user_data_dir)
            self.sub_modules = None
            self.image = path.join(logo_dir, 'logo_vod.png')
        elif source_name == 'channel20':
            self.handler_id = -14
            self.main_module = Channel20(vod_id=-14, data_dir=user_data_dir)
            self.sub_modules = None
            self.image = path.join(logo_dir, 'ch20.png')
        else:
            raise ValueError('Wrong source type {s}'.format(s=source_name))
        self.title = source_name


class HandlerManager(object):
    def __init__(self):
        self.handlers = {}
        sources = ('mako', 'reshet', 'kan', 'hot', 'sport5', 'walla', 'channel20')
        xbmc.log('Preparing handlers for sources {s}'.format(s=sources))
        for _x in sources:
            _h = SourceHandler(_x)
            assert _h.handler_id not in self.handlers
            self.handlers[_h.handler_id] = _h
            if _h.sub_modules is not None:
                for _y in _h.sub_modules:
                    assert _y.handler_id not in self.handlers
                    self.handlers[_y.handler_id] = _y

# import web_pdb
# with web_pdb.catch_post_mortem():
#     # Some error-prone code
#     # web_pdb.set_trace()
#     tree = html5lib.treebuilders.getTreeBuilder("etree")
#     raise RuntimeError('Oops!')


@plugin.route('/')
def choose_handler():
    xbmc.log('Welcome to Israeli tv!')
    items = []
    handlers = HandlerManager().handlers
    for v in handlers.values():
        # u = plugin.url_for(choose_handler)
        u = plugin.url_for(show_programs, handler_id=v.handler_id, args='_first_run')
        item = ListItem(v.title, iconImage="DefaultFolder.png", thumbnailImage=v.image)
        item.addAvailableArtwork(url=v.image, art_type="thumb")
        items.append((u, item, True))
    status = xbmcplugin.addDirectoryItems(handle=plugin.handle, items=items, totalItems=len(handlers))
    xbmcplugin.endOfDirectory(plugin.handle)

    xbmcplugin.setContent(plugin.handle, 'episodes')
    xbmc.executebuiltin("Container.SetViewMode(504)")
    return status


@plugin.route('/show_programs/<handler_id>/<args>')
def show_programs(handler_id, args):
    if args == '_first_run':
        args = ''
    handlers = HandlerManager().handlers
    handler = handlers[int(handler_id)]
    xbmc.log('Showing programs for handler {i} and ids: {ids}'.format(i=handler.handler_id, ids=args))
    if len(args) > 0:
        xbmc.log(str([int(x) for x in args.split(separator)[1:]]))
        show_list = handler.main_module.get_show_object(*(int(x) for x in args.split(separator)[1:]))
    else:
        show_list = handler.main_module.get_show_object(*())
    items = []
    for x in show_list.sub_objects:
        u = plugin.url_for(play_episode if x.is_final_object is True else show_programs,
                           handler_id=handler.handler_id, args=args + separator + str(x.id))
        item = ListItem(x.title, iconImage="DefaultFolder.png", thumbnailImage=x.image_link)
        item.setInfo(type="Video", infoLabels={"Title": x.title, "Plot": x.subtitle})
        item.setProperty('IsPlayable', 'true' if x.is_final_object is True else 'false')
        item.addAvailableArtwork(url=x.image_link, art_type="thumb")
        items.append((u, item, True))
    status = xbmcplugin.addDirectoryItems(handle=plugin.handle, items=items, totalItems=len(show_list.sub_objects))
    xbmcplugin.endOfDirectory(plugin.handle)

    xbmcplugin.setContent(plugin.handle, 'episodes')
    xbmc.executebuiltin("Container.SetViewMode(504)")
    return status


@plugin.route('/play_episode/<handler_id>/<args>')
def play_episode(handler_id, args):
    handlers = HandlerManager().handlers
    handler = handlers[int(handler_id)]
    xbmc.log('Playing videos for handler {i} and ids: {ids}'.format(i=handler.handler_id, ids=args))
    episode = handler.main_module.get_show_object(*(int(x) for x in args.split(separator)[1:]))
    xbmc.log('Site video links {0}.'.format(episode.url))
    # import web_pdb
    # web_pdb.set_trace()
    video_links = handler.main_module.get_video_links_from_video_data(episode.url)
    xbmc.log('Video page links {0}.'.format(video_links[0]))

    fetched_cookies = handler.main_module.session.cookies
    fetched_cookies_str = ';'.join(['{0}={1}'.format(urllib.quote_plus(k), urllib.quote_plus(v))
                                    for k, v in fetched_cookies.items()])
    fetched_user_agent = handler.main_module.user_agent
    video_url = '{0}|User-Agent={1}&Cookie={2}' \
                ''.format(video_links[0][0].encode('utf-8'), fetched_user_agent, fetched_cookies_str)
    play_item = ListItem(path=video_url)
    xbmc.log('Video link {0}.'.format(video_url))

    xbmcplugin.setResolvedUrl(handle=plugin.handle, succeeded=True, listitem=play_item)


def run():
    plugin.run()
