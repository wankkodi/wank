﻿# -*- coding: utf-8 -*-
import xbmc, xbmcaddon
import sys, re
import resources.lib.common as common

handle = int(sys.argv[1])
AddonID = 'plugin.video.idanplus'
Addon = xbmcaddon.Addon(AddonID)
module = '21tv'
userAgent = common.GetUserAgent()

def WatchLive(name='', iconimage='', quality='best'):
	headers={"User-Agent": userAgent}
	url = 'https://www.21.tv/pages/video/videoS.htm'
	text = common.OpenURL(url, headers=headers)
	match = re.compile('var videoSrc="(.*?)";').findall(text)
	text = common.OpenURL(match[0], headers=headers)
	match = re.compile("var\s*metadataURL\s*?=\s*?'(.+?)'").findall(text)
	metadataURL = match[0]
	text = common.OpenURL(metadataURL, headers=headers)
	match = re.compile("<SmilURL.*>(.+)</SmilURL>").findall(text)
	smil = match[0].replace('amp;', '')
	match = re.compile("<Server priority='1'>(.+)</Server>").findall(text)
	server = match[0]
	link = common.urlunparse(common.url_parse(smil)._replace(netloc=server))
	headers = {
		'Connection': 'keep-alive',
		'Pragma': 'no-cache',
		'Cache-Control': 'no-cache',
		'Accept': '*/*',
		'User-Agent': userAgent,
		'Sec-Fetch-Site': 'same-site',
		'Sec-Fetch-Mode': 'cors',
		'Referer': metadataURL,
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'en-US,en;q=0.9',
	}
	link = common.GetStreams(link, headers=headers, quality=quality)
	final = '{0}|User-Agent={1}&Referer={2}'.format(link, userAgent, metadataURL)
	common.PlayStream(final, quality, name, iconimage)

def Run(name, url, mode, iconimage='', moreData=''):
	if mode == 10:
		WatchLive(name, iconimage, moreData)
		
	common.SetViewMode('episodes')