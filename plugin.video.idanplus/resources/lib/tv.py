# -*- coding: utf-8 -*-
import xbmc, xbmcaddon
import sys, re
import resources.lib.common as common

handle = int(sys.argv[1])
AddonID = 'plugin.video.idanplus'
Addon = xbmcaddon.Addon(AddonID)
module = 'tv'
userAgent = common.GetUserAgent()

def WatchLive(url, name='', iconimage='', quality='best'):
	channels = {
		'891fm': { 'link': 'https://www.oles.tv/891fm/player/', 'regex': "streamSource\s*=\s*'(.*?)'"},
		'100fm': { 'link': 'https://100fm.multix.co.il/', 'regex': "hls:\s*'(.*?)'", 'direct': 'https://video_cdn.streamgates.net/radios100fm/feed720/playlist.m3u8'},
		'11b': { 'link': 'https://kanlivep2event-i.akamaihd.net/hls/live/747610/747610/source1_4k/chunklist.m3u8', 'final': True},
		'n12': { 'link': 'https://keshethlslive-lh.akamaihd.net/i/c2n_1@195269/index_3100_av-p.m3u8', 'final': True},
		'13b': { 'link': 'http://reshet-live-net.ctedgecdn.net/13tv-desktop/dvr/r13.m3u8', 'referer': 'http://13tv.co.il/live/'},
		'bbb': { 'link': 'http://reshet-live-net.ctedgecdn.net/13tv-premium/bb/r13.m3u8', 'referer': 'http://13tv.co.il/home/bb-livestream/'},
		'musayof': { 'link': 'http://wowza.media-line.co.il/Musayof-Live/livestream.sdp/playlist.m3u8', 'referer': 'http://media-line.co.il/Media-Line-Player/musayof/livePlayer.aspx'}
	}
	headers={"User-Agent": userAgent}
	regex = channels[url].get('regex')
	if regex:
		text = common.OpenURL(channels[url]['link'], headers=headers)
		link = re.compile(regex).findall(text)
		if len(link) > 0:
			link = link[0]
		else:
			link = channels[url]['direct']
	else:
		link = channels[url]['link']
	if link.startswith('//'):
		link = 'http:{0}'.format(link)
	referer = channels[url].get('referer')
	if referer:
		headers['referer'] = referer
	if not channels[url].get('final') == True:
		link = common.GetStreams(link, headers=headers, quality=quality)
	if referer:
		common.PlayStream('{0}|User-Agent={1}&Referer={2}'.format(link, userAgent, referer), quality, name, iconimage)
	else:
		common.PlayStream('{0}|User-Agent={1}'.format(link, userAgent), quality, name, iconimage)

def Run(name, url, mode, iconimage='', moreData=''):
	if mode == 10:
		WatchLive(url, name, iconimage, moreData)
		
	common.SetViewMode('episodes')