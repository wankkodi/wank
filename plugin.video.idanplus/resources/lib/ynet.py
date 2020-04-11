# -*- coding: utf-8 -*-
import xbmc, xbmcaddon
import sys, re
import resources.lib.common as common

handle = int(sys.argv[1])
AddonID = 'plugin.video.idanplus'
Addon = xbmcaddon.Addon(AddonID)
module = 'ynet'
userAgent = common.GetUserAgent()

def WatchLive(url, name='', iconimage='', quality='best'):
	headers={"User-Agent": userAgent}
	channels = {
		'live': {'ch': 'https://www.ynet.co.il/video/live/0,20658,1-5259927,00.html', 'link': 'http://ynet-lh.akamaihd.net/i/ynet_1@123290/master.m3u8'},
	}
	link = channels[url]['link']
	text = common.OpenURL(channels[url]['ch'], headers=headers)
	if text is not None:
		match = re.compile("progresivePath: function.*?return replacePath\(decodeURIComponent\('(.*?)'\).*?}", re.S).findall(text)
		if match[0] != '':
			link = match[0]
	link = common.GetStreams(link, headers=headers, quality=quality)
	final = '{0}|User-Agent={1}'.format(link, userAgent)
	common.PlayStream(final, quality, name, iconimage)

def Run(name, url, mode, iconimage='', moreData=''):
	if mode == 10:
		WatchLive(url, name, iconimage, moreData)
		
	common.SetViewMode('episodes')