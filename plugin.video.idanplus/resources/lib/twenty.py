# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys, re, json
import resources.lib.common as common

handle = int(sys.argv[1])
AddonID = 'plugin.video.idanplus'
Addon = xbmcaddon.Addon(AddonID)
sortBy = int(Addon.getSetting("twentySortBy"))
module = 'twenty'
userAgent = common.GetUserAgent()
headers = {"User-Agent": userAgent}

def GetCategoriesList(iconimage):
	sortString = common.GetLocaleString(30002) if sortBy == 0 else common.GetLocaleString(30003)
	name = "{0}: {1}".format(common.GetLocaleString(30001), sortString)
	common.addDir(name, "toggleSortingMethod", 4, iconimage, {"Title": name, "Plot": "{0}[CR]{1}[CR]{2} / {3}".format(name, common.GetLocaleString(30004), common.GetLocaleString(30002), common.GetLocaleString(30003))}, module=module, isFolder=False)
	name = common.GetLabelColor("כל התכניות", bold=True, color="none")
	common.addDir(name, '', 0, iconimage, infos={"Title": name, "Plot": "צפיה בתכניות ערוץ מורשת 20"}, module=module)

def GetSeriesList(iconimage):
	text = common.OpenURL('https://www.20il.co.il/%D7%AA%D7%95%D7%9B%D7%A0%D7%99%D7%95%D7%AA/')
	matches = re.compile('<div class="show-thumb">\s*<a href="(.*?)"><img src="(.*?)".*?title=\'(.*?)\'></a></div>', re.S).findall(text)
	grids_arr = []
	for link, iconimage, name in matches:
		name = common.GetLabelColor(common.UnEscapeXML(name), keyColor="prColor", bold=True)
		grids_arr.append((name, link, iconimage, {"Title": name}))
	grids_sorted = grids_arr if sortBy == 0 else sorted(grids_arr,key=lambda grids_arr: grids_arr[0])
	for name, link, image, infos in grids_sorted:
		common.addDir(name, link, 1, common.encode(image, 'utf-8'), infos=infos, module=module)

def GetEpisodesList(url, image):
	text = common.OpenURL(url)
	i = url.find('/page/')
	if i > 0:
		j = url.find('/', i+6)
		if j < 0:
			j = len(url)
		page = int(url[i+6:j])
		_url = url[:i+1]
	else:
		page = 1
		_url = url if url[len(url)-1] == '/' else '{0}/'.format(url)
	match = re.compile('<div class="pagination">(.*)</div>', re.S).findall(text)
	if len(match) > 0:
		match = re.compile('<a href=".*?/page/(\d*)/".*?</a>').findall(match[0])
	pages = 1 if len(match) < 1 else match[-1]
	parts = text.split('<div id="catabpart"')
	name = common.GetLabelColor("תכניות מלאות", keyColor="prColor") 
	common.addDir(name, '', 99, image, infos={"Title": name, "Plot": name}, module=module, isFolder=False)
	episodes = re.compile('<div class="post-thumbnail">\s+<a href="(.*?)</p>', re.S).findall(parts[0])
	EpisodesToList(episodes)
	if len(parts) < 2:
		return
	name = common.GetLabelColor("קטעים נבחרים", keyColor="prColor") 
	common.addDir(name, '', 99, image, infos={"Title": name, "Plot": name}, module=module, isFolder=False)
	episodes = re.compile('<div class="post-thumbnail">\s+<a href="(.*?)</p>', re.S).findall(parts[1][:parts[1].find("<p id='content_bottom'>")])
	EpisodesToList(episodes)
	if page > 1:
		name = common.GetLabelColor(common.GetLocaleString(30011), color="green")
		_url1 = _url if page == 2 else '{0}page/{1}/'.format(_url, page-1)
		common.addDir(name, _url1, 1, image, infos={"Title": name, "Plot": name}, module=module)
	if pages > page:
		name = common.GetLabelColor(common.GetLocaleString(30012), color="green")
		common.addDir(name, '{0}page/{1}/'.format(_url, page+1), 1, image, infos={"Title": name, "Plot": name}, module=module)
	if pages > 1:
		name = common.GetLabelColor(common.GetLocaleString(30013), color="green")
		common.addDir(name, '{0}?pages={1}'.format(_url, pages), 3, image, infos={"Title": name, "Plot": name}, module=module)

def EpisodesToList(episodes):
	bitrate = Addon.getSetting('twenty_res')
	if bitrate == '':
		bitrate = 'best'
	for episode in episodes:
		ps = re.compile('^(.*?)" rel="bookmark">.*?src="(.*?)".*?</a>.*?<div class="entry">.*?rel="bookmark">(.*?)</a></h2>\s+<p>(.*?)$', re.S).findall(episode)
		for link, iconimage, name, desc in ps:
			name = common.GetLabelColor(common.UnEscapeXML(name), keyColor="chColor")
			desc = common.UnEscapeXML(desc)
			iconimage = common.encode(iconimage, 'utf-8')
			common.addDir(name, link, 2, iconimage, infos={"Title": name, "Plot": desc}, contextMenu=[(common.GetLocaleString(30005), 'RunPlugin({0}?url={1}&name={2}&mode=2&iconimage={3}&moredata=choose&module={4})'.format(sys.argv[0], common.quote_plus(link), name, common.quote_plus(iconimage), module)), (common.GetLocaleString(30023), 'RunPlugin({0}?url={1}&name={2}&mode=2&iconimage={3}&moredata=set_twenty_res&module={4})'.format(sys.argv[0], common.quote_plus(link), name, common.quote_plus(iconimage), module))], module=module, moreData=bitrate, isFolder=False, isPlayable=True)

def Play(name, url, iconimage, quality='best', live=None):
	text = common.OpenURL(url, headers=headers)
	match = re.compile('<div class="content">(.*?)<!-- .content -->', re.S).findall(text)
	match = re.compile('<div id="cdnwizPlayerWrapper.*?<iframe.*?src="(.*?)"', re.S).findall(match[0])
	text = common.OpenURL(match[0], headers=headers)
	#match = re.compile('<iframe src="(.*?)"').findall(text)
	#text = common.OpenURL(match[0], headers=headers)
	match = re.compile('src:\s*"(.*?)"').findall(text)
	if len(match) < 0:
		match = re.compile('source\s*src="(.*?)"').findall(text)
	if len(match) < 0:
		match = re.compile("hls.loadSource\('(.*?)'\)").findall(text)
	if len(match) < 0 and live is not None:
		match = [live]
	link = common.GetStreams(match[0], headers=headers, quality=quality)
	final = '{0}|User-Agent={1}'.format(link, userAgent)
	common.PlayStream(final, quality, name, iconimage)

def Run(name, url, mode, iconimage='', moreData=''):
	if mode == -1:
		GetCategoriesList(iconimage)
	if mode == 0:		#------------- Series: ---------------
		GetSeriesList(iconimage)
	elif mode == 1:		#------------- Episodes: -----------------
		GetEpisodesList(url, iconimage)
	elif mode == 2:		#------------- Playing episode  ----------
		Play(name, url, iconimage, moreData)
	elif mode == 3:		#--- Move to a specific episodes' page  --
		url, pages = url.split('?pages=')
		page = common.GetIndexFromUser(name, pages)
		if page > 1: 
			url = '{0}page/{1}/'.format(url, page)
		GetEpisodesList(url, iconimage)
	elif mode == 4:		#------------- Toggle Lists' sorting method -----
		common.ToggleSortMethod('twentySortBy', sortBy)
	elif mode == 10:	#------------- Watch live channel  -------
		Play(name, 'https://www.20il.co.il/vod/', iconimage, moreData, live='https://dvr.ch20-cdnwiz.com/mobilehls/dvr.m3u8')
		
	common.SetViewMode('episodes')
