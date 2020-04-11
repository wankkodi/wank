# -*- coding: utf-8 -*-
import xbmc, xbmcaddon
import sys, re, json
import resources.lib.common as common

handle = int(sys.argv[1])
AddonID = 'plugin.video.idanplus'
Addon = xbmcaddon.Addon(AddonID)
module = 'sport1'
sortBy = int(Addon.getSetting('{0}SortBy'.format(module)))
baseUrl = 'https://sport1.maariv.co.il'
userAgent = common.GetUserAgent()
api = 'https://edge.api.brightcove.com/playback/v1/accounts/1521649299001/videos/'
pk = "application/json;pk=BCpkADawqM319AyjUas_YGcHPFVSaW6GS1X-LxgBt4Ewri5A2Aivr5pFT_zrLyeKoN3g3GjW6d7KQ_vw549kMGwMx6WbqNGT9LV98n_wUIJhSwl1noHoyLbcGqeyVSrqxMNhFMo8qJwhgj0L"
bitrate = Addon.getSetting('{0}_res'.format(module))
if bitrate == '':
	bitrate = 'best'

def GetMainList(iconimage):
	sortString = common.GetLocaleString(30002) if sortBy == 0 else common.GetLocaleString(30003)
	name = "{0}: {1}".format(common.GetLocaleString(30001), sortString)
	common.addDir(name, "toggleSortingMethod", 6, iconimage, {"Title": name, "Plot": "{0}[CR]{1}[CR]{2} / {3}".format(name, common.GetLocaleString(30004), common.GetLocaleString(30002), common.GetLocaleString(30003))}, module=module, isFolder=False)
	name = common.GetLabelColor("כל התכניות", bold=True, color="none")
	common.addDir(name, '', 0, iconimage, infos={"Title": name, "Plot": "צפיה בתכניות מאתר ספורט 1"}, module=module)

def GetCategoriesList(iconimage):
	url = '{0}/VOD'.format(baseUrl)
	text = common.OpenURL(url)
	match = re.compile(u'<div class="row category-menu">(.*?)</div>', re.S).findall(text)
	categories = re.compile(u'<a.*?href="(.*?)".*?>(.*?)</a>', re.S).findall(match[0])
	grids_arr = []
	for link, name in categories:
		name = common.GetLabelColor(name, keyColor="prColor", bold=True)
		grids_arr.append((name, link))
	grids_sorted = grids_arr if sortBy == 0 else sorted(grids_arr,key=lambda grids_arr: grids_arr[0])
	for name, link in grids_sorted:
		common.addDir(name, '{0}{1}'.format(baseUrl, link), 1, iconimage, infos={"Title": name}, module=module)
	GetEpisodes(text)

def GetEpisodes(text):
	match = re.compile(u'position-div-2-in-page(.*?)position-div-3-in-page', re.S).findall(text)
	match = re.compile(u"video-item(.*?)</div>\s*<div", re.S).findall(match[0])
	for item in match:
		icon, name, d = re.compile('img src="(.*?)".*?<div>(.*?)</div>.*?<div>(.*?)</div>', re.S).findall(item)[0]
		name = common.GetLabelColor(common.UnEscapeXML(name), keyColor="chColor", bold=True)
		id = icon[icon.rfind('_')+1:icon.rfind('-')]
		common.addDir(name, id, 4, icon, infos={"Title": name, "Aired": d}, contextMenu=[(common.GetLocaleString(30005), 'RunPlugin({0}?url={1}&name={2}&mode=4&iconimage={3}&moredata=choose&module={4})'.format(sys.argv[0], common.quote_plus(id), name, common.quote_plus(icon), module)), (common.GetLocaleString(30023), 'RunPlugin({0}?url={1}&name={2}&mode=4&iconimage={3}&moredata=set_{4}_res&module={4})'.format(sys.argv[0], common.quote_plus(id), name, common.quote_plus(icon), module))], module=module, moreData=bitrate, isFolder=False, isPlayable=True)
			
def GetEpisodesList(url, iconimage):
	text = common.OpenURL(url)
	GetEpisodes(text)

def Play(url, name='', iconimage='', quality='best'):
	try:
		result = common.OpenURL('{0}{1}'.format(api, url), headers={"Accept": pk, "User-Agent": userAgent})
		if result is None:
			link = 'https://c.brightcove.com/services/mobile/streaming/index/master.m3u8?videoId={0}'.format(url)
			link = common.GetStreams(link, headers={"User-Agent": userAgent}, quality=quality)
		else:
			sources = json.loads(result)['sources']
			link = ''
			avg_bitrate = 0
			for source in sources:
				if 'src' in source:
					if source['container'] == 'M2TS':
						link = common.GetStreams(source['src'], headers={"User-Agent": userAgent}, quality=quality)
						break
					if source['avg_bitrate'] > avg_bitrate:
						link = source['src']
						avg_bitrate = source['avg_bitrate']
		final = '{0}|User-Agent={1}'.format(link, userAgent)
		common.PlayStream(final, quality, name, iconimage)
	except Exception as ex:
		xbmc.log(str(ex), 3)

def Run(name, url, mode, iconimage='', moreData=''):
	if mode == -1:
		GetMainList(iconimage)
	elif mode == 0:		
		GetCategoriesList(iconimage)
	elif mode == 1:
		GetEpisodesList(url, iconimage)					
	elif mode == 4:
		Play(url, name, iconimage, moreData)
	elif mode == 6:
		common.ToggleSortMethod('{0}SortBy'.format(module), sortBy)
		
	common.SetViewMode('episodes')
