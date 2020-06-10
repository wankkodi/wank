# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys, os, re, time, datetime, json
import resources.lib.common as common

handle = int(sys.argv[1])
AddonID = 'plugin.video.idanplus'
Addon = xbmcaddon.Addon(AddonID)
icon = Addon.getAddonInfo('icon')
imagesDir = common.decode(xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), 'resources', 'images')), "utf-8")
sortBy = int(Addon.getSetting("kanSortBy"))
youtubePlugin = 'plugin://plugin.video.youtube' if Addon.getSetting("youtubePlugin") == "0" else 'plugin://plugin.video.MyYoutube'
module = 'kan'
baseUrl = 'https://www.kan.org.il'
userAgent = common.GetUserAgent()
headers={"User-Agent": userAgent}

def GetCategoriesList(iconimage):
	sortString = common.GetLocaleString(30002) if sortBy == 0 else common.GetLocaleString(30003)
	name = "{0}: {1}".format(common.GetLocaleString(30001), sortString)
	common.addDir(name, "toggleSortingMethod", 4, iconimage, {"Title": name, "Plot": "{0}[CR]{1}[CR]{2} / {3}".format(name, common.GetLocaleString(30004), common.GetLocaleString(30002), common.GetLocaleString(30003))}, module=module, isFolder=False)
	name = common.GetLabelColor("כל התוכניות", bold=True, color="none")
	common.addDir(name, '{0}/page.aspx?landingpageId=1039'.format(baseUrl), 1, iconimage, infos={"Title": name}, module=module, moreData=common.GetLocaleString(30602))
	name = common.GetLabelColor("תוכניות אקטואליה", bold=True, color="none")
	common.addDir(name, '{0}/page.aspx?landingPageId=1037'.format(baseUrl), 1, iconimage, infos={"Title": name}, module=module, moreData=common.GetLocaleString(30602))
	name = common.GetLabelColor("דיגיטל", bold=True, color="none")
	common.addDir(name, '{0}/page.aspx?landingPageId=1041'.format(baseUrl), 1, iconimage, infos={"Title": name}, module=module, moreData=common.GetLocaleString(30602))
	name = common.GetLabelColor("כאן חינוכית 23", bold=True, color="none")
	common.addDir(name, '{0}/page.aspx?landingPageId=1083'.format(baseUrl), 1, iconimage, infos={"Title": name}, module=module, moreData=common.GetLocaleString(30607))
	name = common.GetLabelColor("תכניות רדיו", bold=True, color="none")
	common.addDir(name, '', 21, iconimage, infos={"Title": name}, module=module)
	name = common.GetLabelColor("פודקאסטים", bold=True, color="none")
	common.addDir(name, '', 31, iconimage, infos={"Title": name}, module=module)

def GetSeriesList(url, catName):
	text = common.OpenURL(url)
	matches = re.compile('class="component_sm_item news w-clearfix.+?href=\'.+?\?list=(.+?)\'.+?url\(\'(.+?)\'.+?<h3.+?>(.*?)</h3>.+?<p.+?>(.*?)</p>', re.S|re.I).findall(text)
	for id, iconimage, name, description in matches:
		name = common.GetLabelColor(name.strip(), keyColor="prColor", bold=True)
		common.addDir(name, id, 2, iconimage, infos={"Title": name, "Plot": description}, module=module, moreData='youtube|||{0}'.format(catName), isFolder=False, urlParamsData={'catName': catName})
	matches = re.compile('<div class="component_sm_item news">\s*?<a.*?href="(.+?)".+?"background-image: url\(\'(.+?)\'\);.*?" title="(.*?)">.*?"news_up_txt">(.*?)</div>', re.S|re.I).findall(text)
	AddSeries(matches, catName)
	matches = re.compile('<a class="magazine_info_link w-inline-block.+?href=\'(.+?)\'.+?"background-image: url\(\'(.+?)\'\);.+?"magazine_info_title">(.*?)</h2>.*?"magazine_info_txt">(.*?)</div>', re.S|re.I).findall(text)
	AddSeries(matches, catName)
	matches = re.compile('<div class="it_small_pictgroup.+?"background-image: url\(\'(.+?)\'\);.+?href=".+?/Program/\?catId=(.+?)".+?class="it_small_title">(.*?)</div>.+?class="it_small_txt">(.*?)</div>', re.S).findall(text)
	for iconimage, id, name, description in matches:
		name = common.GetLabelColor(name.strip(), keyColor="prColor", bold=True)
		common.addDir(name, id, 2, iconimage, infos={"Title": name, "Plot": description.strip()}, module=module, moreData='kan|||{0}'.format(catName), urlParamsData={'catName': catName})

def AddSeries(matches, catName):
	for link, iconimage, name, description in matches:
		i = link.lower().find('catid=')
		if i > 0:
			link = link[i+6:]
		elif 'page.aspx' in link.lower():
			try:
				t = common.OpenURL(link)
				m = re.compile('magazine_info_link w-inline-block\s*"\s*href=\'.*?catid=(.*?)&').findall(t)
				link = m[0]
			except:
				pass
		name = common.GetLabelColor(name.strip(), keyColor="prColor", bold=True)
		common.addDir(name, link, 2, iconimage, infos={"Title": name, "Plot": description}, module=module, moreData='kan|||{0}'.format(catName), urlParamsData={'catName': catName})

def GetEpisodesList(catId, moreData=''):
	md = moreData.split('|||')
	site = md[0]
	catName = '' if len(md) < 2 else md[1]
	if site == 'youtube':
		xbmc.executebuiltin('container.Update({0}/playlist/{1}/)'.format(youtubePlugin, catId))
		return
	bitrate = Addon.getSetting('kan_res')
	if bitrate == '':
		bitrate = 'best'
	i = 0
	while True:
		i += 1
		url = '{0}/Program/getMoreProgram.aspx?count={1}&catId={2}'.format(baseUrl, i, catId)
		text = common.OpenURL(url)
		if 'ol' not in text:
			break
		matches = re.compile('w-clearfix">.*?url\(\'(.+?)\'.+?onclick="playVideo\(\'.*?\',\'.*?\',\'(\d*)\'.+?<iframe.+?src="(.+?)".+?"content_title">(.+?)</.+?<p>(.+?)</p>', re.S).findall(text)
		for iconimage, id, url, name, description in matches:
			name = common.GetLabelColor(name.strip(), keyColor="chColor")
			common.addDir(name, '{0}|||{1}'.format(url, id), 3, iconimage, infos={"Title": name, "Plot": description.replace('&nbsp;', '').strip()}, module=module, moreData=bitrate, isFolder=False, isPlayable=True, urlParamsData={'catName': catName})

def GetRadioCategoriesList(iconimage):
	name = common.GetLabelColor("כאן ב", bold=True, color="none")
	common.addDir(name, '{0}/live/radio.aspx?stationid=3'.format(baseUrl), 22, os.path.join(imagesDir, "bet.png"), infos={"Title": name}, module=module)
	name = common.GetLabelColor("כאן גימל", bold=True, color="none")
	common.addDir(name, '{0}/live/radio.aspx?stationid=9'.format(baseUrl), 22, os.path.join(imagesDir, "gimel.png"), infos={"Title": name}, module=module)
	name = common.GetLabelColor("כאן 88", bold=True, color="none")
	common.addDir(name, '{0}/live/radio.aspx?stationid=4'.format(baseUrl), 22, os.path.join(imagesDir, "88.png"), infos={"Title": name}, module=module)
	name = common.GetLabelColor("כאן תרבות", bold=True, color="none")
	common.addDir(name, '{0}/live/radio.aspx?stationid=5'.format(baseUrl), 22, os.path.join(imagesDir, "culture.png"), infos={"Title": name}, module=module)
	name = common.GetLabelColor("כאן קול המוסיקה", bold=True, color="none")
	common.addDir(name, '{0}/live/radio.aspx?stationid=7'.format(baseUrl), 22, os.path.join(imagesDir, "music.png"), infos={"Title": name}, module=module)
	name = common.GetLabelColor("כאן מורשת", bold=True, color="none")
	common.addDir(name, '{0}/live/radio.aspx?stationid=6'.format(baseUrl), 22, os.path.join(imagesDir, "moreshet.png"), infos={"Title": name}, module=module)
	name = common.GetLabelColor("כאן Reka", bold=True, color="none")
	common.addDir(name, '{0}/live/radio.aspx?stationid=10'.format(baseUrl), 22, os.path.join(imagesDir, "reka.png"), infos={"Title": name}, module=module)

def GetRadioSeriesList(url, catName):
	text = common.OpenURL(url)
	match = re.compile('radio_online_group(.*?)footer_section_1', re.S).findall(text)
	matches = re.compile('class="radio_online_block.*?<a href=".*?progId=(.+?)" class="radio_online_pict.*?url\(\'(.*?)\'\);".*?title=["\'](.*?)["\']>.*?station_future_name.*?">(.*?)</div>', re.S).findall(match[0])
	for id, iconimage, name, description in matches:
		name = common.GetLabelColor(name.strip(), keyColor="prColor", bold=True)
		common.addDir(name, id, 23, iconimage, infos={"Title": name, "Plot": description}, module=module, moreData=catName, urlParamsData={'catName': catName})

def GetRadioEpisodesList(progId, iconimage, catName):
	i = 0
	while True:
		url = '{0}/Radio/getMoreItems.aspx?index={1}&progId={2}&subcatid=0&isEng=False'.format(baseUrl, i, progId)
		text = common.OpenURL(url)
		matches = re.compile('class="radio_program_partgroup">.*?class="radio_program_toggle top_plus.*?<div>(.*?)</div>.*?onclick="playItem\(\'(.*?)\'\)"', re.S).findall(text)
		for name, itemId in matches:
			name = common.GetLabelColor(name.strip(), keyColor="chColor")
			common.addDir(name, '{0}/radio/player.aspx?ItemId={1}'.format(baseUrl, itemId), 12, iconimage, infos={"Title": name}, module=module, moreData='best', isFolder=False, isPlayable=True, urlParamsData={'catName': catName})
		if len(matches) < 10:
			break
		i += 1

def PlayRadioProgram(url, name='', iconimage='', quality='best'):
	text = common.OpenURL(url, headers=headers)
	match = re.compile('iframe src="(.*?)"').findall(text)
	match = re.compile('(.+)embed').findall(match[0])
	Play(match[0], name, iconimage, quality)

def Play(url, name='', iconimage='', quality='best'):
	u = url.split('|||')
	url = u[0]
	if (Addon.getSetting("kanPreferYoutube") != "true") and (len(u) > 1) and ('youtube' in url or 'youtu.be' in url):
		text = common.OpenURL('{0}/Item/?itemId={1}'.format(baseUrl, u[1]))
		match = re.compile('<script class="w-json" type="application/json">(.*?)</script>').findall(text)
		match = re.compile('src=\\\\"(.*?)\\\\"').findall(match[0])
		if len(match) == 1:
			url = match[0]
	if 'youtube' in url or 'youtu.be' in url:
		if url.endswith('/'):
			url = url[:-1]
		video_id = url[url.rfind('/')+1:]
		if '?' in video_id:
			video_id = video_id[:video_id.find('?')]
		final = '{0}/play/?video_id={1}'.format(youtubePlugin, video_id)
	elif 'omny.fm' in url:
		#text = common.OpenURL(url)
		#matches = re.compile('AudioUrl":"(.+?)"').findall(text)
		#if len(matches) == 0:
		#	return
		#final = 'https://omny.fm{1}'.format(matches[-1])
		final = '{0}{1}'.format(url[:-1], '.mp3')
	else:
		final = GetPlayerKanUrl(url, headers=headers, quality=quality)
	
	listitem = xbmcgui.ListItem(path=final)
	listitem.setInfo(type="Video", infoLabels={"Title": name})
	xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=listitem)

def GetPlayerKanUrl(url, headers={}, quality='best'):
	url = url.replace('https', 'http')
	i = url.rfind('http://')
	if i > 0:
		url = url[i:]
	url = url.replace('HLS/HLS', 'HLS')
	text = common.OpenURL(url, headers=headers)
	if 'ByPlayer' in url:
		match = re.compile('bynetURL:\s*"(.*?)"').findall(text)
		if len(match) == 0:
			match = re.compile('"UrlRedirector":"(.*?)"').findall(text)
		link = match[0].replace('https', 'http').replace('\u0026', '&')
	elif len(re.compile('media\.(ma)?kan\.org\.il').findall(url)) > 0:
		match = re.compile('hls:\s*?"(.*?)"').findall(text)
		link = match[0]
	else:
		match = re.compile("var\s*metadataURL\s*?=\s*?'(.+?)'").findall(text)
		text = common.OpenURL(match[0].replace('https_streaming=true', 'https_streaming=false'), headers=headers)
		match = re.compile("<SmilURL.*>(.+)</SmilURL>").findall(text)
		smil = match[0].replace('amp;', '')
		match = re.compile("<Server priority=['\"]1['\"]>(.+)</Server>").findall(text)
		server = match[0]
		link = common.urlunparse(common.url_parse(smil)._replace(netloc=server))
	if 'api.bynetcdn.com/Redirector' not in link:
		link = common.GetStreams(link, headers=headers, quality=quality)
	return '{0}|User-Agent={1}'.format(link, userAgent)

def WatchLive(url, name='', iconimage='', quality='best', type='video'):
	channels = {
		'11': '{0}/live/tv.aspx?stationid=2'.format(baseUrl),
		'23': '{0}/live/tv.aspx?stationid=20'.format(baseUrl),
		'33': 'https://www.makan.org.il/live/tv.aspx?stationid=3',
		'kan4K': '{0}/live/tv.aspx?stationid=18'.format(baseUrl),
		'wfb2019': '{0}/Item/?itemId=53195'.format(baseUrl),
		'yfb2019': '{0}/Item/?itemId=52450'.format(baseUrl),
		'bet': '{0}/radio/player.aspx?stationId=3'.format(baseUrl),
		'gimel': '{0}/radio/player.aspx?stationid=9'.format(baseUrl),
		'culture': '{0}/radio/player.aspx?stationid=5'.format(baseUrl),
		'88': '{0}/radio/player.aspx?stationid=4'.format(baseUrl),
		'moreshet':'{0}/radio/player.aspx?stationid=6'.format(baseUrl),
		'music': '{0}/radio/player.aspx?stationid=7'.format(baseUrl),
		'reka': '{0}/radio/player.aspx?stationid=10'.format(baseUrl),
		'makan': '{0}/radio/player.aspx?stationId=13'.format(baseUrl),
		'persian': 'http://farsi.kan.org.il/',
		'nos': '{0}/radio/radio-nos.aspx'.format(baseUrl),
		'oriental': '{0}/radio/oriental.aspx'.format(baseUrl),
		'international': '{0}/radio/radio-international.aspx'.format(baseUrl)
	}
	channelUrl = channels[url]
	text = common.OpenURL(channelUrl, headers=headers)
	if text is None:
		return
	if url == 'persian':
		match = re.compile('id="playerFrame".*?src="(.*?)"', re.S).findall(text)
	elif '?itemId=' in channelUrl:
		match = re.compile('<div class=\'videoWrapper\'><iframe.*?src="(.*?)"').findall(text)
	elif type == 'video':
		match = re.compile('<iframe.*class="embedly-embed".*src="(.+?)"').findall(text)
	else:
		match = re.compile('<div class="player_content">.*?iframe src="(.*?)"', re.S).findall(text)
		if len(match) == 0:
			match = re.compile('iframeLink\s*?=\s*?"(.*?)"').findall(text)
	link = GetPlayerKanUrl(match[0], headers=headers, quality=quality)
	common.PlayStream(link, quality, name, iconimage)

def GetPodcastsList():
	i = -1
	while True:
		i += 1
		url = '{0}/podcast/morePrograms.aspx?index={1}'.format(baseUrl, i)
		text = common.OpenURL(url)
		matches = re.compile('title="(.+?)".+?url\(\'(.+?)\'.+?href=".+?\?progId=(.+?)".+?<p.+?>(.*?)</p>', re.S).findall(text)
		if len(matches) == 0:
			break
		for name, iconimage, id, description in matches:
			name = common.GetLabelColor(name.strip(), keyColor="prColor", bold=True)
			common.addDir(name, id, 32, iconimage, infos={"Title": name, "Plot": description.replace('&nbsp;', '').strip()}, module=module, urlParamsData={'catName': 'כאן פודקאסטים'})

def GetPodcastEpisodesList(progId, iconimage):
	i = -1
	while True:
		i += 1
		url = '{0}/Podcast/getMorePodcasts.aspx?index={1}&leftToRight=0&progId={2}'.format(baseUrl, i, progId)
		text = common.OpenURL(url)
		matches = re.compile('<iframe src="(.+?)embed.+?<h2.+?>(.+?)</h2>.+?<p.+?>(.*?)</p>', re.S).findall(text)
		if len(matches) == 0:
			break
		for link, name, description in matches:
			name = common.GetLabelColor(name.strip(), keyColor="chColor")
			common.addDir(name, link, 3, iconimage, infos={"Title": name, "Plot": description.replace('&nbsp;', '').strip()}, module=module, isFolder=False, isPlayable=True, urlParamsData={'catName': 'כאן פודקאסטים'})


def Run(name, url, mode, iconimage='', moreData=''):
	if mode == 0:	#------------- Categories: ----------------------
		GetCategoriesList(iconimage)
	elif mode == 1:	#------------- Series: --------------------------
		GetSeriesList(url, moreData)
	elif mode == 2:	#------------- Episodes: ------------------------
		GetEpisodesList(url, moreData)
	elif mode == 3:	#------------- Playing episode  -----------------
		Play(url, name, iconimage, moreData)
	elif mode == 4:	#------------- Toggle Lists' sorting method -----
		common.ToggleSortMethod('kanSortBy', sortBy)
	elif mode == 21: #------------- Radio Categories: ---------------
		GetRadioCategoriesList(iconimage)
	elif mode == 22: #------------- Radio Series: -------------------
		GetRadioSeriesList(url, common.GetUnColor(name))
	elif mode == 23: #------------- Radio Episodes: -----------------
		GetRadioEpisodesList(url, iconimage, moreData)
	elif mode == 31: #------------- Podcast Series: -----------------
		GetPodcastsList()
	elif mode == 32: #------------- Podcast Episodes: ---------------
		GetPodcastEpisodesList(url, iconimage)
	elif mode == 10:
		WatchLive(url, name, iconimage, moreData, type='video')
	elif mode == 11:
		WatchLive(url, name, iconimage, moreData, type='radio')
	elif mode == 12:
		PlayRadioProgram(url, name, iconimage, moreData)
		
	if mode != 0:
		common.SetViewMode('episodes')
	if sortBy == 1 and mode == 1:
		xbmcplugin.addSortMethod(handle, 1)