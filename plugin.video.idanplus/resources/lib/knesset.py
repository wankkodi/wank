# -*- coding: utf-8 -*-
import xbmc, xbmcaddon
import sys, re
import resources.lib.common as common

handle = int(sys.argv[1])
AddonID = 'plugin.video.idanplus'
Addon = xbmcaddon.Addon(AddonID)
module = 'knesset'
userAgent = common.GetUserAgent()

def WatchLive(name='', iconimage='', quality='best'):
	try:
		headers={"User-Agent": userAgent}
		#url = 'https://main.knesset.gov.il/News/Broadcast/Pages/default.aspx?pos=tv'
		#url = 'https://main.knesset.gov.il/_layouts/15/1037/CustomScripts/KnessetBroadcastLobby.js'
		url = 'https://main.knesset.gov.il/_layouts/15/1037/CustomScripts/KnessetMainScripts.js?v=9'
		text = common.OpenURL(url, headers=headers)
		#match = re.compile('pathChannelVideo = ko\.observable\("(.*?)"\);').findall(text)
		match = re.compile("playerPlenumLiveMediaElement\.setSrc\('(.*?)'\);").findall(text)
		#url = common.GetRedirect(match[0], headers=headers)
		url = match[0]
	except Exception as ex:
		xbmc.log(str(ex), 3)
	if url is None or len(url) < 10:
		url = '	https://contact.gostreaming.tv/Knesset/myStream/playlist.m3u8'
	link = common.GetStreams(url, headers=headers, quality=quality)
	final = '{0}|User-Agent={1}'.format(link, userAgent)
	common.PlayStream(final, quality, name, iconimage)

def Run(name, url, mode, iconimage='', moreData=''):
	if mode == 10:
		WatchLive(name, iconimage, moreData)
		
	common.SetViewMode('episodes')
