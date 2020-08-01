# -*- coding: utf-8 -*-
import xbmc, xbmcaddon
import sys, re, json, collections
import resources.lib.common as common

handle = int(sys.argv[1])
AddonID = 'plugin.video.idanplus'
Addon = xbmcaddon.Addon(AddonID)
sortBy = int(Addon.getSetting("reshetSortBy"))
module = 'reshet'
bitrate = Addon.getSetting('reshet_res')
if bitrate == '':
	bitrate = 'best'
baseUrl = 'https://13tv.co.il'
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
api = 'https://edge.api.brightcove.com/playback/v1/accounts/1551111274001/videos/'
pk = "application/json;pk=BCpkADawqM30eqkItS5d08jYUtMkbTKu99oEBllbfUaFKeknXu4iYsh75cRm2huJ_b1-pXEPuvItI-733TqJN1zENi-DcHlt7b4Dv6gCT8T3BS-ampD0XMnORQLoLvjvxD14AseHxvk0esW3"

def GetCategoriesList(iconimage):
	name = "{0}: {1}".format(common.GetLocaleString(30001), common.GetLocaleString(30002) if sortBy == 0 else common.GetLocaleString(30003))
	common.addDir(name, "toggleSortingMethod", 5, iconimage, {"Title": name, "Plot": "{0}[CR]{1}[CR]{2} / {3}".format(name, common.GetLocaleString(30004), common.GetLocaleString(30002), common.GetLocaleString(30003))}, module=module, isFolder=False)
	result = GetUrlJson('{0}/vod/'.format(baseUrl))
	if len(result) > 0:
		name = common.GetLabelColor("כל התכניות", bold=True, color="none")
		common.addDir(name, '', 0, iconimage, infos={"Title": name, "Plot": "צפיה בתכניות רשת 13"}, module=module)
		grids = result.get('Content', {}).get('PageGrid', {})
		for grid in grids:
			gridType = grid.get('GridType')
			if gridType is not None and gridType == 'grid_content_4col' or gridType == 'carousel_grid_content':
				gridTitle = common.encode(grid.get('GridTitle').get('title').strip(), 'utf-8')
				name = common.GetLabelColor(gridTitle, bold=True, color="none")
				common.addDir(name, str(grid.get('grid_id')), 6, iconimage, infos={"Title": name}, module=module)
	name = common.GetLabelColor("החדשות 13", bold=True, color="none")
	common.addDir(name, '', 10, iconimage, infos={"Title": name, "Plot": "צפיה בתכניות חדשות 13"}, module=module)

def GetUrlJson(url):
	result = {}
	try:
		html = common.OpenURL(url, headers={"User-Agent": userAgent})
		data_query = re.compile('data_query = (.*?)\.data_query;', re.S).findall(html)
		result = json.loads(data_query[0])['data_query'] if len(data_query) > 0 else {}
	except Exception as ex:
		xbmc.log(str(ex), 3)
	return result

def GetGridList(iconimage, grid_id):
	url = '{0}/vod/'.format(baseUrl)
	result = GetUrlJson(url)
	if len(result) < 1:
		return
	episodes = []
	series = []
	postsIDs = []
	posts = {}
	grids = result.get('Content', {}).get('PageGrid', {})
	for grid in grids:
		if grid.get('grid_id') != int(grid_id):
			continue
		gridType = grid.get('GridType')
		if gridType is None or 'grid_content' not in gridType:
			continue
		title = grid.get('GridTitle')
		gridTitle = '' if title is None else common.encode(title.get('title', '').strip(), 'utf-8')
		titleLink = '' if title is None else title.get('link', '')
		gridLink = '' if titleLink is None else common.encode(str(titleLink).strip(), 'utf-8')
		if gridLink != '' and gridTitle != '' and gridLink != url:
			series.append((gridTitle, gridLink, iconimage, '', ''))
		for postsID in grid.get('Posts', {}):
			try:
				if postsID in postsIDs:
					continue
				post = result.get('ItemStore', {}).get(str(postsID), {})
				link = post.get('link')
				title = common.encode(post['title'], 'utf-8')
				subtitle = common.encode(post['subtitle'], 'utf-8')
				icon = common.encode(post['images']['app_16x9'], 'utf-8')
				publishDate = post.get('publishDate')
				postType = post.get('postType', '')
				if postType == 'item':
					mode = 3
					video = post.get('video')
					if video is None or video.get('videoID') is None:
						continue
					link = video['videoID']
				elif postType != 'page':
					continue
				else:
					mode = 1
				if link == '' or link in posts:
					continue
				posts[link] = title
				postsIDs.append(postsID)
				
				if mode == 1:
					series.append((title, link, icon, subtitle, publishDate))
				else:
					episodes.append((title, gridTitle, link, icon, subtitle, publishDate))
			except Exception as ex:
				xbmc.log(str(ex), 3)
		break
	if sortBy == 1:
		series = sorted(series,key=lambda series: series[0])
		#episodes = sorted(episodes,key=lambda episodes: episodes[0])
	for title, link, icon, subtitle, publishDate in series:
		name = common.GetLabelColor(title, keyColor="prColor", bold=True)
		link = str(link)
		infos= {"Title": name, "Plot": subtitle, "Aired": publishDate}
		common.addDir(name, link, 1, icon, infos=infos, module=module)
	programNameFormat = int(Addon.getSetting("programNameFormat"))
	for title, gridTitle, link, icon, subtitle, publishDate in episodes:
		name = common.GetLabelColor(title, keyColor="chColor") if gridTitle is None or gridTitle == '' else common.getDisplayName(gridTitle, title, programNameFormat)
		link = str(link)
		infos= {"Title": name, "Plot": subtitle, "Aired": publishDate}
		common.addDir(name, link, 3, icon, infos=infos, contextMenu=[(common.GetLocaleString(30005), 'RunPlugin({0}?url={1}&name={2}&mode=3&iconimage={3}&moredata=choose&module=reshet)'.format(sys.argv[0], common.quote_plus(link), common.quote_plus(name), common.quote_plus(icon))), (common.GetLocaleString(30023), 'RunPlugin({0}?url={1}&name={2}&mode=3&iconimage={3}&moredata=set_reshet_res&module=reshet)'.format(sys.argv[0], common.quote_plus(link), common.quote_plus(name), common.quote_plus(icon)))], moreData=bitrate, module=module, isFolder=False, isPlayable=True)

def GetSeriesList(iconimage):
	url = '{0}/vod/'.format(baseUrl)
	result = GetUrlJson(url)
	if len(result) < 1:
		return
	grids_arr = []
	seriesIDs = []
	series = {}
	grids = result.get('Content', {}).get('PageGrid', {})
	for grid in grids:
		for seriesID in grid.get('Posts', {}):
			try:
				if seriesID in seriesIDs or seriesID == 170768:
					continue
				serie = result.get('ItemStore', {}).get(str(seriesID), {})
				link = serie.get('link')
				postType = serie.get('postType', '')
				if postType == 'item':
					if '/movies/' in link:
						link = link[:link.find('/movies/') +8].replace('/item', '')
					else:
						link = link[:link.find('/season') +1].replace('/item', '')
					page_2_level_heb = serie['coolaData'].get('page_2_level_heb')
					name = '' if page_2_level_heb is None else common.encode(page_2_level_heb, 'utf-8')
				elif postType != 'page':
					continue
				else:
					if len(common.url_parse(link).path.split('/')) > 4 and 'channel2-news' not in link:
						continue
					name = common.encode(serie['title'], 'utf-8')
				name = common.GetLabelColor(name, keyColor="prColor", bold=True)
				if link == '' or link in series and postType != 'page':
					continue
				series[link] = name
				seriesIDs.append(seriesID)
				pageTitle = serie.get('pageTitle', {})
				description = '' if pageTitle is None else common.encode(pageTitle.get('description', ''), 'utf-8')
				matches = [grids_arr.index(x) for x in grids_arr if link == x[1]]
				if len(matches) == 1:
					grids_arr[matches[0]] = (name, link, common.encode(serie['images']['app_16x9'], 'utf-8'), {"Title": name, "Plot": description})
				else:
					grids_arr.append((name, link, common.encode(serie['images']['app_16x9'], 'utf-8'), {"Title": name, "Plot": description}))
			except Exception as ex:
				xbmc.log(str(ex), 3)
	grids_sorted = grids_arr if sortBy == 0 else sorted(grids_arr,key=lambda grids_arr: grids_arr[0])
	for name, link, icon, infos in grids_sorted:
		common.addDir(name, link, 1, icon, infos=infos, module=module)
	
def GetSeasonList(url, iconimage):
	result = GetUrlJson(url)
	seasons, episodes = GetLinks(url, result, iconimage)
	if len(seasons) > 0:
		for link, title in common.items(seasons):
			name = common.GetLabelColor(title, keyColor="timesColor", bold=True)
			common.addDir(name, link, 2, iconimage, infos={"Title": name}, module=module)
		if len(episodes) < 1:
			return
	ShowEpisodes(episodes, iconimage)

def GetEpisodesList(url, iconimage):
	result = GetUrlJson(url)
	seasons, episodes = GetLinks(url, result, iconimage)
	for link, title in common.items(seasons):
		if 'reshet.tv/news/tonight/' in link:
			name = 'אין פרקים מלאים'
			common.addDir(name, '', 99, iconimage, infos={"Title": name}, module=module, isFolder=False)
			return
	ShowEpisodes(episodes, iconimage)
	ShowPaging(result.get('Content', {}).get('PageGrid', {}), result.get('PageMeta', {}).get('page_url', ''), iconimage, 2)
	
def GetLinks(url, result, iconimage):
	seasons = collections.OrderedDict() if common.NewerThanPyVer('2.6.99') else {}
	episodes = []
	subMenus = result.get('Header', {}).get('subMenu', {})
	if subMenus:
		for subMenu in subMenus:
			try:
				title = subMenu.get('title')
				link = subMenu.get('url')
				ending = link[link.rfind('/', 0, len(link)-1):]
				if 'episodes' in ending or 'season' in ending and (link not in seasons or seasons[link] == ''):
					seasons[link] = common.encode(title.strip(), 'utf-8')
			except Exception as ex:
				xbmc.log(str(ex), 3)
	grids = result.get('Content', {}).get('PageGrid', {})
	for grid in grids:
		title = grid.get('GridTitle')
		gridTitle = '' if title is None else common.encode(title.get('title', '').strip(), 'utf-8')
		titleLink = '' if title is None else title.get('link', '')
		gridLink = '' if titleLink is None else common.encode(str(titleLink).strip(), 'utf-8')
		if 'episodes' in gridLink and (gridLink not in seasons or seasons[gridLink] == ''):
			seasons[gridLink] = gridTitle if gridTitle != '' else common.encode(result.get('PageMeta', {}).get('title', '').strip(), 'utf-8')
		elif gridLink != '' and gridTitle != '' and gridLink != url:
			seasons[gridLink] = gridTitle
		for pid in grid.get('Posts', {}):
			try:
				post = result.get('ItemStore', {}).get(str(pid), {})
				link = post['link'].replace('vod-2', 'vod').replace('/channel2/', '/channel2-news/')
				if 'episodes' not in link and '/movies/' not in link:
					ending = link[link.rfind('/', 0, len(link)-1):]
					if 'season' in ending and (link not in seasons or seasons[link] == ''):
						seasons[link] = common.encode(post.get('title', '').strip(), 'utf-8')
					if post['postType'] != 'item':
						continue
				if 'links' in post['postType'] and link not in seasons:
					seasons[link] = common.encode(post.get('title', '').strip(), 'utf-8')
				else:
					if '/episodes/' in link:
						seasonsLink = link[:link.find('/episodes/') + 10].replace('/item', '')
						match = re.compile('/season-(\d+)(.*?)/').findall(seasonsLink)
						if len(match) > 0 and match[0][1] != '':
							seasonsLink = seasonsLink.replace(match[0][1], '')
						if seasonsLink not in seasons and '/movies/' not in link:
							page_2_level_heb = post['coolaData'].get('page_2_level_heb')
							page_2_level_heb = '' if page_2_level_heb is None else common.encode(page_2_level_heb, 'utf-8')
							page_3_level_heb = post['coolaData'].get('page_3_level_heb')
							page_3_level_heb = '' if page_3_level_heb is None else common.encode(page_3_level_heb, 'utf-8')
							page_4_level_heb = post['coolaData'].get('page_4_level_heb')
							page_4_level_heb = '' if page_4_level_heb is None else common.encode(page_4_level_heb, 'utf-8')
							seasons[seasonsLink] = '{0} {1} {2}'.format(page_2_level_heb, page_3_level_heb, page_4_level_heb)
					video = post.get('video')
					if video is None or video.get('videoID') is None:
						continue
					videoID = video['videoID']
					if videoID == '-1':
						videoID = video.get('videoRef', videoID)
					icon =  common.encode(post['images'].get('app_16x9', iconimage), 'utf-8')
					episodes.append((gridTitle, videoID, icon, common.encode(post.get('title', '').strip(), 'utf-8'), common.encode(post.get('subtitle', '').strip(), 'utf-8'), post.get('publishDate')))
			except Exception as ex:
				xbmc.log(str(ex), 3)
	return seasons, episodes

def ShowEpisodes(episodes, iconimage):
	if len(episodes) < 1:
		name = 'אין פרקים מלאים'
		common.addDir(name, '', 99, iconimage, infos={"Title": name}, module=module, isFolder=False)
		return
	programNameFormat = int(Addon.getSetting("programNameFormat"))
	#for gridTitle, link, icon, title, subtitle, publishDate in sorted(episodes,key=lambda episodes: episodes[5]):#reversed(episodes):
	for gridTitle, link, icon, title, subtitle, publishDate in episodes:
		name = common.GetLabelColor(title, keyColor="chColor") if gridTitle is None or gridTitle == '' else common.getDisplayName(gridTitle, title, programNameFormat)
		link = str(link)
		common.addDir(name, link, 3, icon, infos={"Title": name, "Plot": subtitle, "Aired": publishDate}, contextMenu=[(common.GetLocaleString(30005), 'RunPlugin({0}?url={1}&name={2}&mode=3&iconimage={3}&moredata=choose&module=reshet)'.format(sys.argv[0], common.quote_plus(link), common.quote_plus(name), common.quote_plus(icon))), (common.GetLocaleString(30023), 'RunPlugin({0}?url={1}&name={2}&mode=3&iconimage={3}&moredata=set_reshet_res&module=reshet)'.format(sys.argv[0], common.quote_plus(link), common.quote_plus(name), common.quote_plus(icon)))], moreData=bitrate, module=module, isFolder=False, isPlayable=True)

def ShowPaging(grids, page_url, iconimage, mode):
	WpQuery = grids[0].get('WpQuery', None)
	if WpQuery is None:
		paged = 0  
	else: 
		paged = WpQuery.get('paged', 0)
	if paged > 0 and  len(grids) > 0:
		max_page = grids[0].get('max_page', 0)
		if paged > 1:
			prev_page = page_url + 'page/' + str(paged-1) + '/' if paged - 1 > 1 else page_url
			common.addDir(common.GetLabelColor(common.GetLocaleString(30011), color="green"), prev_page, mode, iconimage, module=module)
		if max_page > paged:
			common.addDir(common.GetLabelColor(common.GetLocaleString(30012), color="green"), page_url + 'page/' + str(paged+1) + '/', mode, iconimage, module=module)

def Play(url, name='', iconimage='', quality='best'):
	try:
		headers={"User-Agent": userAgent}
		if common.isnumeric(url):
			result = common.OpenURL('https://13tv-api.oplayer.io/api/getlink/getVideoById?userId=45E4A9FB-FCE8-88BF-93CC-3650C39DDF28&serverType=web&videoId={0}&callback=x'.format(url), headers=headers)
		else:
			result = common.OpenURL('https://13tv-api.oplayer.io/api/getlink/getVideoByFileName?userId=45E4A9FB-FCE8-88BF-93CC-3650C39DDF28&videoName={0}&serverType=web&callback=x'.format(url), headers=headers)
		if result is not None:
			source = json.loads(result)[0]
			link = '{0}{1}{2}{3}{4}.mp4{5}{6}'.format(source['ProtocolType'], source['ServerAddress'], source['MediaRoot'], source['MediaFile'][:source['MediaFile'].find('.mp4')], source['Bitrates'], source['StreamingType'], source['Token'])
			#xbmc.log(link, 5)
			session = common.GetSession()
			link = common.GetStreams(link, headers=headers, session=session, quality=quality)
			final = '{0}|User-Agent={1}'.format(link, userAgent)
			cookies = "&".join(['Cookie={0}'.format(common.quote('{0}={1}'.format(_cookie.name, _cookie.value))) for _cookie in session.cookies])
			if cookies != '':
				final = '{0}&{1}'.format(final, cookies)
		else:
			result = common.OpenURL('{0}{1}'.format(api, url), headers={"Accept": pk, "User-Agent": userAgent})
			if result is None:
				link = 'https://c.brightcove.com/services/mobile/streaming/index/master.m3u8?videoId={0}'.format(url)
				link = common.GetStreams(link, headers=headers, quality=quality)
			else:
				sources = json.loads(result)['sources']
				link = ''
				avg_bitrate = 0
				for source in sources:
					if 'src' in source:
						if source['container'] == 'M2TS':
							link = common.GetStreams(source['src'], headers=headers, quality=quality)
							break
						if source['avg_bitrate'] > avg_bitrate:
							link = source['src']
							avg_bitrate = source['avg_bitrate']
							#xbmc.log('[{0}]  {1}'.format(avg_bitrate, link), 5)
			final = '{0}|User-Agent={1}'.format(link, userAgent)
		common.PlayStream(final, quality, name, iconimage)
	except Exception as ex:
		xbmc.log(str(ex), 3)

def WatchLive(url, name='', iconimage='', quality='best'):
	channels = {
		'13': {'ch': 'videoId', 'casttimeId': '1', 'referer': '{0}/live/'.format(baseUrl), 'link': 'http://reshet-live-il.ctedgecdn.net/13tv-desktop/dvr/r13.m3u8'},
		'13c': {'ch': 'accessibility_ref', 'casttimeId': '27', 'referer': '{0}/live/'.format(baseUrl), 'link': 'https://reshet-live-il.ctedgecdn.net/13tv-desktop/dvrsubs/r13.m3u8'},
		'bb': {'ch': 'videoId', 'casttimeId': '26', 'referer': '{0}/home/bb-livestream/'.format(baseUrl), 'link': 'http://reshet-live-il.ctedgecdn.net/13tv-premium/bb/r13.m3u8'}
	}
	referer = channels[url]['referer']
	try:
		result = GetUrlJson(referer)
		provider = result['Header']['Live']['extras']['live_video_provider']
		if provider == 'cast_time':
			result = common.OpenURL('https://13tv-api.oplayer.io/api/getlink/?userId=45E4A9FB-FCE8-88BF-93CC-3650C39DDF28&serverType=web&cdnName=casttime&ch={0}'.format(channels[url]['casttimeId']), headers={"User-Agent": userAgent})
			link = json.loads(result)[0]['Link']
		else:
			result = common.OpenURL('{0}{1}'.format(api, result['Header']['Live'][channels[url]['ch']]), headers={"Accept": pk, "User-Agent": userAgent})
			link = json.loads(result)['sources'][0]['src']
	except Exception as ex:
		xbmc.log(str(ex), 3)
		link = channels[url]['link']
	link = common.GetStreams(link, headers={"User-Agent": userAgent, 'Referer': referer}, quality=quality)
	final = '{0}|User-Agent={1}&Referer={2}'.format(link, userAgent, referer)
	common.PlayStream(final, quality, name, iconimage)

def GetNewsCategoriesList(iconimage):
	url = 'https://13news.co.il/programs/'
	result = GetUrlJson(url)
	if len(result) < 1:
		return
	grids_arr = []
	mainMenus = result.get('Header', {}).get('mainMenu', [])
	for mainMenu in mainMenus:
		if mainMenu['url'] == url:
			grids = mainMenu['children']
			for grid in grids:
				name = common.GetLabelColor(common.UnEscapeXML(common.encode(grid['title'], 'utf-8')), keyColor="prColor", bold=True)
				link = grid['url']
				grids_arr.append((name, link, iconimage, {"Title": name}))
	grids_sorted = grids_arr if sortBy == 0 else sorted(grids_arr,key=lambda grids_arr: grids_arr[0])
	for name, link, icon, infos in grids_sorted:
		common.addDir(name, link, 1, icon, infos=infos, module=module)

def Run(name, url, mode, iconimage='', moreData=''):
	if mode == -1:
		GetCategoriesList(iconimage)
	elif mode == 0:
		GetSeriesList(iconimage)						# Series
	elif mode == 1:
		GetSeasonList(url, iconimage)					# Seasons
	elif mode == 2:
		GetEpisodesList(url, iconimage)					# Episodes
	elif mode == 3:
		Play(url, name, iconimage, moreData)			# Playing episode
	elif mode == 4:
		WatchLive(url, name, iconimage, moreData)		# Playing Live
	elif mode == 5:	
		common.ToggleSortMethod('reshetSortBy', sortBy)	# Toggle Lists' sorting method
	elif mode == 6:
		GetGridList(iconimage, url)
	elif mode == 10:
		GetNewsCategoriesList(iconimage)					# News Shows
	
	common.SetViewMode('episodes')
