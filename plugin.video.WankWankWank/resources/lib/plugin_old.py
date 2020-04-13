# -*- coding: utf-8 -*-

import routing
import xbmcaddon
from resources.lib import kodilogging
from xbmcgui import ListItem
import xbmcplugin
import xbmc

from mako import Mako
import urllib
from urlparse import urljoin

import sys
from os import path

__url__ = sys.argv[0]
__handle__ = int(sys.argv[1])
ADDON = xbmcaddon.Addon()
kodilogging.config()
plugin = routing.Plugin()



addon_dir = xbmc.translatePath(ADDON.getAddonInfo('path'))
addon_save_dir = xbmc.translatePath(ADDON.getAddonInfo('profile'))

xbmc.log(addon_dir)
mako = Mako(save_dir=path.join(addon_dir, 'resources', 'lib', 'Mako'), 
            data_dir=path.join(addon_dir, 'resources', 'lib', 'Data'))


@plugin.route('/')
def show_programs():
    xbmc.log('My programs.')
    show_list = mako.get_available_shows()
    items = []
    for x in show_list:
        u = plugin.url_for(show_seasons, program_guid=x['guid'].encode('utf-8'))
        item = ListItem(x['title'], iconImage="DefaultFolder.png", thumbnailImage=x['pic'])
        item.setInfo(type="Video", infoLabels={"Title": x['title'], "Plot": x['brief']})
        item.addAvailableArtwork(url=x['pic'], art_type="thumb")
        items.append([u, item, True])
    status = xbmcplugin.addDirectoryItems(handle=plugin.handle, items=items, totalItems=len(show_list))
    xbmcplugin.endOfDirectory(plugin.handle)

    xbmcplugin.setContent(plugin.handle, 'episodes')
    xbmc.executebuiltin("Container.SetViewMode(504)")
    return status


@plugin.route('/show_seasons/<program_guid>')
def show_seasons(program_guid):
    xbmc.log('My season for program guid {0}.'.format(program_guid))
    show_list = mako.get_available_shows()
    our_show_data = [x for x in show_list if x['guid'].encode('utf-8') == program_guid]
    assert len(our_show_data) == 1
    our_show_data = our_show_data[0]
    seasons = mako.get_show_season_data(our_show_data['title'].encode('utf-8'))
    items = []
    for x in seasons:
        u = plugin.url_for(show_episodes, program_guid=program_guid, season_guid=x['id'].encode('utf-8'))
        item = ListItem(x['name'], iconImage="DefaultFolder.png", thumbnailImage=our_show_data['pic'])
        item.setInfo(type="Video", infoLabels={"Title": x['name'], "Plot": x['brief']})
        item.addAvailableArtwork(url=our_show_data['pic'], art_type="thumb")
        items.append([u, item, True])
    status = xbmcplugin.addDirectoryItems(handle=plugin.handle, items=items, totalItems=len(seasons))
    xbmcplugin.endOfDirectory(plugin.handle)

    xbmcplugin.setContent(plugin.handle, 'episodes')
    xbmc.executebuiltin("Container.SetViewMode(504)")
    return status


@plugin.route('/show_episodes/<program_guid>/<season_guid>')
def show_episodes(program_guid, season_guid):
    xbmc.log('My episodes for program guid {0} for season guid {1}.'.format(program_guid, season_guid))
    show_list = mako.get_available_shows()
    our_show_data = [x for x in show_list if x['guid'].encode('utf-8') == program_guid][0]
    seasons = mako.get_show_season_data(our_show_data['title'].encode('utf-8'))
    our_season_data = [x for x in seasons if x['id'].encode('utf-8') == season_guid][0]

    episodes = mako.get_season_videos_data(our_show_data['title'].encode('utf-8'), 
                                           our_season_data['name'].encode('utf-8'))
    items = []
    for x in episodes:
        u = plugin.url_for(play_episode, program_guid=program_guid, season_guid=season_guid,
                           episode_guid=x['guid'].encode('utf-8'))
        item = ListItem(x['title'], iconImage="DefaultFolder.png", thumbnailImage=x['picUrl'])
        item.setInfo(type="Video", infoLabels={"Title": x['title'], "Plot": x['subtitle']})
        item.setProperty('IsPlayable', 'true')
        items.append([u, item, False])
    status = xbmcplugin.addDirectoryItems(handle=plugin.handle, items=items, totalItems=len(episodes))
    xbmcplugin.endOfDirectory(plugin.handle)

    xbmcplugin.setContent(plugin.handle, 'episodes')
    xbmc.executebuiltin("Container.SetViewMode(504)")
    return status


@plugin.route('/play_episode/<program_guid>/<season_guid>/<episode_guid>')
def play_episode(program_guid, season_guid, episode_guid):
    xbmc.log('Plays episode {0} for program {1} for season {2}.'.format(program_guid, season_guid, 
                                                                        episode_guid))
    show_list = mako.get_available_shows()
    our_show_data = [x for x in show_list if x['guid'].encode('utf-8') == program_guid][0]
    seasons = mako.get_show_season_data(our_show_data['title'].encode('utf-8'))
    our_season_data = [x for x in seasons if x['id'].encode('utf-8') == season_guid][0]
    episodes = mako.get_season_videos_data(our_show_data['title'].encode('utf-8'), 
                                           our_season_data['name'].encode('utf-8'))
    episode = [x for x in episodes if episode_guid == x['guid'].encode('utf-8')]
    if len(episode) > 1:
        raise RuntimeError('Found more than one possible episode!'
                           '{0} {1}'.format(season_episode, [x['title'].encode('utf-8') for x in episodes]))
    elif len(episode) == 0:
        raise RuntimeError('No episode found!'
                           '{0} {1}'.format(season_episode, [x['title'].encode('utf-8') for x in episodes]))
    episode = episode[0]
    episode_url = urljoin(mako.base_url, episode['link'])
    xbmc.log('Site video links {0}.'.format(episode_url))
    video = mako.fetch_video_from_episode_url(episode_url)
    xbmc.log('Video links {0}.'.format(video))

    # save_dir = path.join(addon_save_dir, 'data')
    # if not xbmcvfs.exists(save_dir):
        # xbmcvfs.mkdirs(save_dir)
    # save_filename = path.join(save_dir, '{0}.m3u'.format(x['guid'].encode('utf-8')))
    # video.dump(save_filename)
    # # with xbmcvfs.File(save_filename, 'w') as fl:
    # #     fl.write(video.dumps())

    fetched_cookies = mako.get_cookies()
    fetched_cookies_str = ';'.join(['{0}={1}'.format(urllib.quote_plus(k), urllib.quote_plus(v)) 
                                    for k, v in fetched_cookies.items()])
    fetched_user_agent = mako.get_user_agent()
    play_item = ListItem(path='{0}|User-Agent={1}&Cookie={2}'
                              ''.format(video.encode('utf-8'), mako.get_user_agent(), fetched_cookies_str))
    xbmcplugin.setResolvedUrl(plugin.handle, True, listitem=play_item)



def run():
    plugin.run()
