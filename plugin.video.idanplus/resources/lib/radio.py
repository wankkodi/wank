# -*- coding: utf-8 -*-
import xbmcaddon, xbmc
import sys, re
import resources.lib.common as common

handle = int(sys.argv[1])
AddonID = 'plugin.video.idanplus'
Addon = xbmcaddon.Addon(AddonID)
module = 'radio'
userAgent = common.GetUserAgent()
headers={"User-Agent": userAgent}

def WatchLive(url, name='', iconimage='', quality='best'):
	channels = {
		'90fm': { 'link': 'http://live1.co.il/90fm/', 'regex': 'mp3:\s*"(.*?)"'},
		'91fm': { 'link': 'https://91fm.co.il/wp-content/themes/bootstrap-basic/js/beetle_video.js?ver=1.0.0', 'regex': "loadStream\('(.*?)'\);",},
		'97fm': { 'link': 'https://www.ytn.co.il/radiodarom/97fm/', 'regex': '<video.*src="(.*?)"'},
		'891fm': { 'link': 'http://www.891fm.co.il/', 'regex': 'data-mp3="(.*?)"'},
		'100fm': { 'link': 'http://www.100fm.co.il/Player_new/ind.html', 'regex': 'm4a:\s*"(.*?)"'},
		'1015fm': { 'link': 'https://www.ytn.co.il/radiodarom/1015fm/', 'regex': '<video.*src="(.*?)"'},
		'102fm': { 'link': 'https://102fm.co.il/', 'regex': "src:\s*'(.*?)'"},
		'102fmEilat': { 'link': 'https://www.fm102.co.il/LiveBroadcast', 'regex': 'mp3:\s*"(.*?)"'},
		'103fm': { 'link': 'http://103fm.maariv.co.il/include/OnLineView.aspx', 'regex': 'data-file="(.*?)"'},
		'1045fm': { 'link': 'https://1045fm.maariv.co.il/include/OnLineView.aspx', 'regex': 'data-file="(.*?)"'},
		'1075fm': { 'link': 'http://www.1075.fm/%d7%a0%d7%92%d7%9f/', 'regex': 'mp3:\s*"(.*?)"'},
		'mizrahit': { 'link': 'http://www.mizrahit.fm/', 'regex': '<aside id="sidebar">.*?src\s*=\s*".*?play=(.+?)"', 'flags': re.S}
	}
	text = common.OpenURL(channels[url]['link'], headers=headers)
	link = re.compile(channels[url]['regex'], channels[url].get('flags', 0)).findall(text)[0]
	if link.find('://') < 0:
		link = 'http://' + link
	final = '{0}|User-Agent={1}&verifypeer=false'.format(link, userAgent)
	common.PlayStream(final, quality, name, iconimage)
def Run(name, url, mode, iconimage='', moreData=''):
	if mode == 11:
		WatchLive(url, name, iconimage, moreData)
		
	common.SetViewMode('episodes')