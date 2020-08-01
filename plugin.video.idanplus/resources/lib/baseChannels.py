# -*- coding: utf-8 -*-
import xbmcaddon

AddonID = 'plugin.video.idanplus'
Addon = xbmcaddon.Addon(AddonID)
module = 'baseChannels'
icon = Addon.getAddonInfo('icon')

TvChannels = [
	{'ch':'ch_11', 'index': 1, 'nameID': 30602, 'channelID':'11', 'mode': 10, 'image':'kan.jpg', 'module':'kan', 'resKey':'ch_11_res', 'tvgID':'11', 'type':'tv'}, 
	#{'ch':'ch_11b', 'index': 1, 'nameID': 30633, 'channelID':'11b', 'mode': 10, 'image':'kan.jpg', 'module':'tv', 'resKey':'', 'tvgID':'11', 'type':'tv'}, 
	{'ch':'ch_12', 'index': 2, 'nameID': 30603, 'channelID':'12', 'mode': 10, 'image':'keshet.jpg', 'module':'keshet', 'resKey':'ch_12_res', 'tvgID':'12', 'type':'tv'}, 
	{'ch':'ch_12c', 'index': 2, 'nameID': 30626, 'channelID':'12c', 'mode': 10, 'image':'keshet.jpg', 'module':'keshet', 'resKey':'ch_12c_res', 'tvgID':'12', 'type':'tv'}, 
	{'ch':'ch_13', 'index': 3, 'nameID': 30604, 'channelID':'13', 'mode': 4, 'image':'13.png', 'module':'reshet', 'resKey':'ch_13_res', 'tvgID':'13', 'type':'tv'}, 
	{'ch':'ch_13b', 'index': 3, 'nameID': 30634, 'channelID':'13b', 'mode': 10, 'image':'13.png', 'module':'tv', 'resKey':'', 'tvgID':'13', 'type':'tv'}, 
	{'ch':'ch_13c', 'index': 3, 'nameID': 30631, 'channelID':'13c', 'mode': 4, 'image':'13.png', 'module':'reshet', 'resKey':'ch_13c_res', 'tvgID':'13', 'type':'tv'}, 
	{'ch':'ch_20', 'index': 4, 'nameID': 30606, 'channelID':'20', 'mode': 10, 'image':'20.png', 'module':'twenty', 'resKey':'ch_20_res', 'tvgID':'20', 'type':'tv'}, 
	{'ch':'ch_21', 'index': 5, 'nameID': 30619, 'channelID':'21', 'mode': 10, 'image':'21.jpg', 'module':'21tv', 'resKey':'ch_21_res', 'tvgID':'21', 'type':'tv'}, 
	{'ch':'ch_23', 'index': 6, 'nameID': 30607, 'channelID':'23', 'mode': 10, 'image':'23tv.jpg', 'module':'kan', 'resKey':'ch_23_res', 'tvgID':'23', 'type':'tv'}, 
	{'ch':'ch_24', 'index': 7, 'nameID': 30608, 'channelID':'24', 'mode': 10, 'image':'24telad.png', 'module':'keshet', 'resKey':'ch_24_res', 'tvgID':'24', 'type':'tv'}, 
	{'ch':'ch_bb', 'index': 8, 'nameID': 30621, 'channelID':'bb', 'mode': 4, 'image':'bb.jpg', 'module':'reshet', 'resKey':'ch_bb_res', 'tvgID':'', 'type':'tv'}, 
	{'ch':'ch_bbb', 'index': 8, 'nameID': 30625, 'channelID':'bbb', 'mode': 10, 'image':'bb.jpg', 'module':'tv', 'resKey':'', 'tvgID':'', 'type':'tv'}, 
	{'ch':'ch_33', 'index': 9, 'nameID': 30609, 'channelID':'33', 'mode': 10, 'image':'makan.png', 'module':'kan', 'resKey':'ch_33_res', 'tvgID':'33', 'type':'tv'}, 
	{'ch':'ch_66', 'index': 10, 'nameID': 30610, 'channelID':'17', 'mode': 10, 'image':'kabbalah.jpg', 'module':'kabbalah', 'resKey':'ch_66_res', 'tvgID':'66', 'type':'tv'}, 
	{'ch':'ch_97', 'index': 11, 'nameID': 30612, 'channelID':'97', 'mode': 10, 'image':'hidabroot.jpg', 'module':'hidabroot', 'resKey':'ch_97_res', 'tvgID':'97', 'type':'tv'}, 
	{'ch':'ch_99', 'index': 12, 'nameID': 30613, 'channelID':'99', 'mode': 10, 'image':'knesset.png', 'module':'knesset', 'resKey':'ch_99_res', 'tvgID':'99', 'type':'tv'}, 
	#{'ch':'ch_n12', 'index': 13, 'nameID': 30636, 'channelID':'n12', 'mode': 10, 'image':'n12.png', 'module':'tv', 'resKey':'', 'tvgID':'', 'type':'tv'}, 
	{'ch':'ch_ynet', 'index': 13, 'nameID': 30622, 'channelID':'live', 'mode': 10, 'image':'ynet.jpg', 'module':'ynet', 'resKey':'ch_ynet_res', 'tvgID':'', 'type':'tv'}, 
	#{'ch':'ch_walla', 'index': 14, 'nameID': 30624, 'channelID':'live', 'mode': 10, 'image':'wallanews.png', 'module':'walla', 'resKey':'ch_walla_res', 'tvgID':'', 'type':'tv'}, 
	{'ch':'ch_sport5', 'index': 15, 'nameID': 30632, 'channelID':'5studio', 'mode': 10, 'image':'Sport5.png', 'module':'sport5','resKey':'','tvgID':'5radio','type':'tv'},
	{'ch':'ch_100', 'index': 16, 'nameID': 30726, 'channelID':'100fm', 'mode': 10, 'image':'100fm.jpg', 'module':'tv', 'resKey':'', 'tvgID':'100fm', 'type':'tv'},
	{'ch':'ch_891', 'index': 17, 'nameID': 30734, 'channelID':'891fm', 'mode': 10, 'image':'891fm.png', 'module':'tv', 'resKey':'', 'tvgID':'891fm', 'type':'tv'},
	{'ch':'ch_kabru', 'index': 18, 'nameID': 30629, 'channelID':'18', 'mode': 10, 'image':'kabbalah.jpg', 'module':'kabbalah', 'resKey':'ch_kabru_res', 'tvgID':'', 'type':'tv'},
	{'ch':'ch_musayof', 'index': 19, 'nameID': 30635, 'channelID':'musayof', 'mode': 10, 'image':'musayof.jpg', 'module':'tv', 'resKey':'ch_musayof', 'tvgID':'', 'type':'tv'},
	{'ch':'ch_refresh', 'index': 100, 'nameID': 30618, 'channelID':'refresh', 'mode': 6, 'image': icon, 'module':'', 'resKey':'', 'tvgID':'', 'type':'refresh'}
]

RadioChannels = [
	{'ch':'rd_glglz', 'index': 1, 'nameID': 30702, 'channelID':'glglz', 'mode': 11, 'image':'glglz.jpg', 'module':'glz', 'tvgID':'glglz', 'type':'radio'}, 
	{'ch':'rd_88', 'index': 2, 'nameID': 30703, 'channelID':'88', 'mode': 11, 'image':'88.png', 'module':'kan', 'tvgID':'88', 'type':'radio'}, 
	{'ch':'rd_90', 'index': 3, 'nameID': 30724, 'channelID':'90fm', 'mode': 11, 'image':'90fm.jpg', 'module':'radio', 'tvgID':'90fm', 'type':'radio'}, 
	{'ch':'rd_91', 'index': 3, 'nameID': 30736, 'channelID':'91fm', 'mode': 11, 'image':'91fm.jpg', 'module':'radio', 'tvgID':'91fm', 'type':'radio'}, 
	{'ch':'rd_97', 'index': 4, 'nameID': 30725, 'channelID':'97fm', 'mode': 11, 'image':'97fm.jpg', 'module':'radio', 'tvgID':'97fm', 'type':'radio'}, 
	{'ch':'rd_99', 'index': 5, 'nameID': 30704, 'channelID':'99fm', 'mode': 11, 'image':'99fm.png', 'module':'99fm', 'tvgID':'99fm', 'type':'radio'}, 
	{'ch':'rd_100', 'index': 6, 'nameID': 30726, 'channelID':'100fm', 'mode': 11, 'image':'100fm.jpg', 'module':'radio', 'tvgID':'100fm', 'type':'radio'}, 
	{'ch':'rd_101', 'index': 7, 'nameID': 30727, 'channelID':'101fm', 'mode': 11, 'image':'101fm.png', 'module':'101fm', 'tvgID':'101fm', 'type':'radio'}, 
	{'ch':'rd_1015', 'index': 8, 'nameID': 30728, 'channelID':'1015fm', 'mode': 11, 'image':'1015fm.jpg', 'module':'radio', 'tvgID':'1015fm', 'type':'radio'}, 
	{'ch':'rd_102', 'index': 9, 'nameID': 30705, 'channelID':'102fm', 'mode': 11, 'image':'102fm.jpg', 'module':'radio', 'tvgID':'102fm', 'type':'radio'}, 
	{'ch':'rd_102Eilat', 'index': 10, 'nameID': 30729, 'channelID':'102fmEilat', 'mode': 11, 'image':'102fmEilat.jpg', 'module':'radio', 'tvgID':'102fmEilat', 'type':'radio'}, 
	{'ch':'rd_103', 'index': 11, 'nameID': 30706, 'channelID':'103fm', 'mode': 11, 'image':'103fm.png', 'module':'radio', 'tvgID':'103fm', 'type':'radio'}, 
	{'ch':'rd_1045', 'index': 12, 'nameID': 30730, 'channelID':'1045fm', 'mode': 11, 'image':'1045fm.jpg', 'module':'radio', 'tvgID':'1045fm', 'type':'radio'}, 
	{'ch':'rd_1075', 'index': 13, 'nameID': 30731, 'channelID':'1075fm', 'mode': 11, 'image':'1075fm.jpg', 'module':'radio', 'tvgID':'1075fm', 'type':'radio'}, 
	{'ch':'rd_glz', 'index': 14, 'nameID': 30707, 'channelID':'glz', 'mode': 11, 'image':'glz.jpg', 'module':'glz', 'tvgID':'glz', 'type':'radio'}, 
	{'ch':'rd_bet', 'index': 15, 'nameID': 30708, 'channelID':'bet', 'mode': 11, 'image':'bet.png', 'module':'kan', 'tvgID':'bet', 'type':'radio'}, 
	{'ch':'rd_gimel', 'index': 16, 'nameID': 30709, 'channelID':'gimel', 'mode': 11, 'image':'gimel.png', 'module':'kan', 'tvgID':'gimel', 'type':'radio'}, 
	{'ch':'rd_culture', 'index': 17, 'nameID': 30710, 'channelID':'culture', 'mode': 11, 'image':'culture.png', 'module':'kan', 'tvgID':'culture', 'type':'radio'}, 
	{'ch':'rd_music', 'index': 18, 'nameID': 30711, 'channelID':'music', 'mode': 11, 'image':'music.png', 'module':'kan', 'tvgID':'music', 'type':'radio'}, 
	{'ch':'rd_moreshet', 'index': 19, 'nameID': 30712, 'channelID':'moreshet', 'mode': 11, 'image':'moreshet.png', 'module':'kan', 'tvgID':'moreshet', 'type':'radio'}, 
	{'ch':'rd_sport5', 'index': 20, 'nameID': 30632, 'channelID':'5live', 'mode': 10, 'image':'Sport5.png', 'module':'sport5', 'tvgID':'5radio', 'type':'radio'}, 
	{'ch':'rd_reka', 'index': 21, 'nameID': 30713, 'channelID':'reka', 'mode': 11, 'image':'reka.png', 'module':'kan', 'tvgID':'reka', 'type':'radio'}, 
	{'ch':'rd_891', 'index': 22, 'nameID': 30734, 'channelID':'891fm', 'mode': 11, 'image':'891fm.png', 'module':'radio', 'tvgID':'891fm', 'type':'radio'}, 
	{'ch':'rd_makan', 'index': 23, 'nameID': 30714, 'channelID':'makan', 'mode': 11, 'image':'makan.png', 'module':'kan', 'tvgID':'makan', 'type':'radio'}, 
	#{'ch':'rd_persian', 'index': 24, 'nameID': 30715, 'channelID':'persian', 'mode': 11, 'image':'persian.png', 'module':'kan', 'tvgID':'persian', 'type':'radio'}, 
	{'ch':'rd_nos', 'index': 25, 'nameID': 30720, 'channelID':'nos', 'mode': 11, 'image':'nos.png', 'module':'kan', 'tvgID':'', 'type':'radio'}, 
	{'ch':'rd_oriental', 'index': 26, 'nameID': 30722, 'channelID':'oriental', 'mode': 11, 'image':'oriental.png', 'module':'kan', 'tvgID':'', 'type':'radio'}, 
	{'ch':'rd_international', 'index': 27, 'nameID': 30716, 'channelID':'international', 'mode': 11, 'image':'kan-international.jpg', 'module':'kan', 'tvgID':'', 'type':'radio'}, 
	{'ch':'rd_mizrahit', 'index': 28, 'nameID': 30733, 'channelID':'mizrahit', 'mode': 11, 'image':'mizrahit.png', 'module':'radio', 'tvgID':'', 'type':'radio'}, 
	{'ch':'rd_refresh', 'index': 100, 'nameID': 30723, 'channelID':'refresh', 'mode': 6, 'image': icon, 'module':'', 'tvgID':'', 'type':'refresh'}
]