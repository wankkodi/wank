# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys, re, json
import resources.lib.common as common

handle = int(sys.argv[1])
AddonID = 'plugin.video.idanplus'
Addon = xbmcaddon.Addon(AddonID)
sortBy = int(Addon.getSetting("twentySortBy"))
module = 'twenty'
baseUrl = 'https://www.20il.co.il'
userAgent = common.GetUserAgent()
headers = {"User-Agent": userAgent}

def GetCategoriesList(iconimage):
	sortString = common.GetLocaleString(30002) if sortBy == 0 else common.GetLocaleString(30003)
	name = "{0}: {1}".format(common.GetLocaleString(30001), sortString)
	common.addDir(name, "toggleSortingMethod", 4, iconimage, {"Title": name, "Plot": "{0}[CR]{1}[CR]{2} / {3}".format(name, common.GetLocaleString(30004), common.GetLocaleString(30002), common.GetLocaleString(30003))}, module=module, isFolder=False)
	name = common.GetLabelColor("כל התכניות", bold=True, color="none")
	common.addDir(name, '', 0, iconimage, infos={"Title": name, "Plot": "צפיה בתכניות ערוץ מורשת 20"}, module=module)

def GetSeriesList(iconimage):
	text = common.OpenURL('https://www.20il.co.il/tochniot_haarutz/%d7%97%d7%93%d7%a9%d7%95%d7%aa-20/')
	match = re.compile('tochniot-in-use-images(.*?)</div>', re.S).findall(text)
	match = re.compile('<a href="(.*?)".*?<img src="(.*?)"', re.S).findall(match[0])
	grids_arr = []
	for link, iconimage in match:
		name = iconimage[iconimage.rfind('/')+1:iconimage.rfind(".")]
		i = name.find('-סופי')
		if i > 0:
			name = name[:i]
		name = common.GetLabelColor(common.UnEscapeXML(name.replace('-', ' ')), keyColor="prColor", bold=True)
		if iconimage.startswith('http') == False:
			iconimage = '{0}{1}'.format(baseUrl, iconimage)
		grids_arr.append((name, '{0}{1}'.format(baseUrl, link), iconimage, {"Title": name}))
	grids_sorted = grids_arr if sortBy == 0 else sorted(grids_arr,key=lambda grids_arr: grids_arr[0])
	for name, link, image, infos in grids_sorted:
		common.addDir(name, link, 1, common.encode(image, 'utf-8'), infos=infos, module=module)

def GetEpisodesList(url, image):
	bitrate = Addon.getSetting('twenty_res')
	if bitrate == '':
		bitrate = 'best'
	text = common.OpenURL(url)
	episodes = re.compile('<div class="katan-unit(.*?)</div>\s*</div>\s*</div>', re.S).findall(text)
	for episode in episodes:
		match = re.compile('data-videoid="(.*?)".*?src="(.*?)".*?<div class="the-title">(.*?)</div>', re.S).findall(episode)
		for videoid, iconimage, name in match:
			name = common.GetLabelColor(common.UnEscapeXML(name.strip()), keyColor="chColor")
			iconimage = common.encode(iconimage, 'utf-8')
			link = 'https://cdn.ch20-cdnwiz.com/ch20/player.php?clipid={0}&autoplay=true&automute=false'.format(videoid)
			common.addDir(name, link, 2, iconimage, infos={"Title": name}, contextMenu=[(common.GetLocaleString(30005), 'RunPlugin({0}?url={1}&name={2}&mode=2&iconimage={3}&moredata=choose&module={4})'.format(sys.argv[0], common.quote_plus(link), name, common.quote_plus(iconimage), module)), (common.GetLocaleString(30023), 'RunPlugin({0}?url={1}&name={2}&mode=2&iconimage={3}&moredata=set_twenty_res&module={4})'.format(sys.argv[0], common.quote_plus(link), name, common.quote_plus(iconimage), module))], module=module, moreData=bitrate, isFolder=False, isPlayable=True)

def Play(name, url, iconimage, quality='best', live=None):
	text = common.OpenURL(url, headers=headers)
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

def Watch(name, iconimage, quality='best'):
	url = 'https://www.20il.co.il/tochniot_meleot/%D7%A9%D7%99%D7%93%D7%95%D7%A8-%D7%97%D7%99/'
	text = common.OpenURL(url, headers=headers)
	match = re.compile('<div id="cdnwizPlayerWrapper.*?<iframe.*?src="(.*?)"', re.S).findall(text)
	Play(name, match[0], iconimage, quality, live='https://dvr.ch20-cdnwiz.com/mobilehls/dvr.m3u8')

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
		Watch(name, iconimage, moreData)
		
	common.SetViewMode('episodes')
