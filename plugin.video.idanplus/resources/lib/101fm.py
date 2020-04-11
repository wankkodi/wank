# -*- coding: utf-8 -*-
import xbmc, xbmcaddon
import sys, json, re
import resources.lib.common as common

handle = int(sys.argv[1])
AddonID = 'plugin.video.idanplus'
Addon = xbmcaddon.Addon(AddonID)
module = '101fm'
userAgent = common.GetUserAgent()
headers = {"User-Agent": userAgent}

def WatchLive(url, name='', iconimage='', quality='best'):
	try:
		url = 'http://live1.co.il/jrs101fm/'
		text = common.OpenURL(url, headers=headers)
		match = re.compile('<iframe.*?player/(.*?)/').findall(text)
		url = 'http://opml.tunein.com/Tune.ashx?render=json&id={0}'.format(match[0])
		text = common.OpenURL(url, headers=headers)
		data = json.loads(text)
		link = data['body']['url']
	except Exception as ex:
		xbmc.log(str(ex), 3)
		link = 'http://101.cdnwz.net/101fm'
	final = '{0}|User-Agent={1}'.format(link, userAgent)
	common.PlayStream(final, quality, name, iconimage)

def Run(name, url, mode, iconimage='', moreData=''):
	if mode == 11:
		WatchLive(url, name, iconimage, moreData)
		
	common.SetViewMode('episodes')