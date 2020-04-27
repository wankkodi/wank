# -*- coding: utf-8 -*-
# import sys
from os import path

from ..channels.mako import Mako, Bip, Channel24
from ..channels.reshet import Reshet
from ..channels.sport5 import Sport5
from ..channels.sport1 import Sport1
from ..channels.one import One
from ..channels.kan import Kan, KanEducation, Makan
from ..channels.hot import Hot, HotBidur, HotEight, HotThree, HotYoung, HotZoom
from ..channels.walla import Walla
from ..channels.channel20 import Channel20
from ..channels.channel9 import Channel9
# from ..channels.channel10_obsolete import Channel10
from ..channels.iba_archive import IBA
from ..channels.knesset import Knesset


class SourceHandler(object):
    def __init__(self, source_id, logo_dir):
        if source_id == -1:
            self.title = 'mako'
            self.main_module = Mako
            self.image = path.join(logo_dir, 'makoTV_200X200.jpg')
        elif source_id == -2:
            self.title = 'bip'
            self.main_module = Bip
            self.image = path.join(logo_dir, 'Bip_Logo1.jpg')
        elif source_id == -3:
            self.title = 'reshet'
            self.main_module = Reshet
            self.image = path.join(logo_dir, 'reshet.png')
        elif source_id == -4:
            self.title = 'kan'
            self.main_module = Kan
            self.image = path.join(logo_dir, 'logo_kan.png')
        elif source_id == -5:
            self.title = 'kan_education'
            self.main_module = KanEducation
            self.image = path.join(logo_dir, 'lan1084_img.jpg')
        elif source_id == -6:
            self.title = 'hot'
            self.main_module = Hot
            self.image = path.join(logo_dir, '1200px-HotNewLogo.svg.png')
        elif source_id == -7:
            self.title = 'hot_three'
            self.main_module = HotThree
            self.image = path.join(logo_dir, '250px-HOT3_logo_2010.svg.png')
        elif source_id == -8:
            self.title = 'hot_bidur'
            self.main_module = HotBidur
            self.image = path.join(logo_dir, 'hot-bidur.png')
        elif source_id == -9:
            self.title = 'hot_eight'
            self.main_module = HotEight
            self.image = path.join(logo_dir, 'hot8.jpg')
        elif source_id == -10:
            self.title = 'hot_young'
            self.main_module = HotYoung
            self.image = path.join(logo_dir, 'unnamed.jpg')
        elif source_id == -11:
            self.title = 'hot_zoom'
            self.main_module = HotZoom
            self.image = path.join(logo_dir, 'H69111167_logos_510X1478.jpg')
        elif source_id == -12:
            self.title = 'walla'
            self.main_module = Walla
            self.image = path.join(logo_dir, 'logo_vod.png')
        elif source_id == -13:
            self.title = 'sport5'
            self.main_module = Sport5
            self.image = path.join(logo_dir, '424px-Sport5ch.svg.png')
        elif source_id == -14:
            self.title = 'One'
            self.main_module = One
            self.image = path.join(logo_dir, 'One.png')
        elif source_id == -15:
            self.title = 'sport1'
            self.main_module = Sport1
            self.image = path.join(logo_dir, 'sport1logo.png')
        elif source_id == -16:
            self.title = 'channel20'
            self.main_module = Channel20
            self.image = path.join(logo_dir, 'ch20.png')
        elif source_id == -17:
            self.title = 'channel9'
            self.main_module = Channel9
            self.image = path.join(logo_dir, 'logo_ch9.png')
        elif source_id == -18:
            self.title = 'IBA (Archive)'
            self.main_module = IBA
            self.image = path.join(logo_dir, 'Channel_1_(Israel)_Logo_SVG.svg.png')
        elif source_id == -19:
            self.title = 'Makan'
            self.main_module = Makan
            self.image = path.join(logo_dir, 'logo_makan.png')
        elif source_id == -20:
            self.title = 'channel24'
            self.main_module = Channel24
            self.image = path.join(logo_dir, '24logocleannew.jpg')
        elif source_id == -31:
            self.title = 'Knesset'
            self.main_module = Knesset
            self.image = path.join(logo_dir, 'knesset_channel_logo2.png')
        else:
            raise ValueError('Wrong source type {s}'.format(s=source_id))
        self.handler_id = source_id
        self.initialized_module = None


class HandlerManager(object):
    def __init__(self, logo_dir, user_data_dir, session_id):
        self.handlers = {}
        self.logo_dir = logo_dir
        self.user_data_dir = user_data_dir
        self.session_id = session_id
        source_ids = range(-1, -21, -1)
        # xbmc.log('Preparing handlers for source ids {s}'.format(s=source_ids))
        for _x in source_ids:
            _h = SourceHandler(_x, logo_dir)
            self.handlers[_h.handler_id] = _h

    def get_handler(self, handler_id):
        handler = self.handlers[handler_id]
        if handler.initialized_module is None:
            handler.initialized_module = handler.main_module(vod_id=handler_id, data_dir=self.user_data_dir,
                                                             session_id=self.session_id)
        return handler.initialized_module

    def store_data_for_all_handlers(self):
        """
        Saves tthe data for all handlers.
        :return:
        """
        for handler_id in self.handlers:
            self.store_data_for_handler(handler_id)

    def store_data_for_handler(self, handler_id):
        """
        Saves the data for all handlers.
        :param handler_id: Handler id.
        :return:
        """
        handler = self.handlers[handler_id]
        if handler.initialized_module is not None:
            handler.initialized_module.catalog_manager.save_store_data()
