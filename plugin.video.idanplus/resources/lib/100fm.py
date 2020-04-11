# -*- coding: utf-8 -*-
import xbmc, xbmcaddon
import sys, re, json
import resources.lib.common as common

handle = int(sys.argv[1])
AddonID = 'plugin.video.idanplus'
Addon = xbmcaddon.Addon(AddonID)
module = '100fm'
userAgent = common.GetUserAgent()
headers = {"User-Agent": userAgent}

def GetCategories(iconimage):
	categories = [
		{'name': 'ערוצים פופולרים', 'cat': 'popular'},
		{'name': 'ערוצים דיגיטלים', 'cat': 'digital'},
		{'name': 'ערוצי תוכן', 'cat': 'content'}
	]
	for category in categories:
		name = common.GetLabelColor(category['name'], keyColor="prColor", bold=True)
		common.addDir(name, category['cat'], 1, iconimage, infos={"Title": name}, module=module)

def GetPlaylists(cat):
	text = common.OpenURL('http://digital.100fm.co.il/app/', headers=headers)
	playlist = json.loads(text)
	for item in playlist['stations']:
		if cat != 'content':
			if item.get('tag', '') == 'content':
				continue
			if cat == 'popular':
				if item.get('popular', '') != 'true':
					continue
			else:
				if item.get('popular', '') == 'true':
					continue
		else:
			if item.get('tag', '') != 'content':
				continue
		name = common.GetLabelColor(item['name'], keyColor="chColor") 
		common.addDir(name, item['audio'], 2, item['cover'], infos={"Title": name, "Plot": item['description']}, module=module, isFolder=False, isPlayable=True)

def Play(name, url, iconimage, quality='best'):
	final = '{0}|User-Agent={1}'.format(url, userAgent)
	common.PlayStream(final, quality, name, iconimage)

def Run(name, url, mode, iconimage='', moreData=''):
	if mode == 0:		#------------- Series: ---------------
		GetCategories(iconimage)
	elif mode == 1:		#------------- Episodes: -----------------
		GetPlaylists(url)
	elif mode == 2:		#------------- Playing episode  ----------
		Play(name, url, iconimage, moreData)
		
	common.SetViewMode('episodes')