# -*- coding: utf-8 -*-
# import sys
from os import path

from ..hidden.PornSites.ahme import AhMe, SunPorno
from ..hidden.PornSites.analpornvideosxxx import AnalPornVideosXXX
from ..hidden.PornSites.anyporn import AnyPorn, PervertSluts, Fapster, HellPorno, AlphaPorno, XBabe, \
    BravoPorn, HellMoms, MadThumbs, Sex3, CrocoTube, \
    PornFd, PornBimbo, BoundHub, AdultCartoons, MoviesAnd
from ..hidden.PornSites.anyporn.watchmygfme import WatchMyGfMe
from ..hidden.PornSites.anyporn.pornodep import PornoDep
from ..hidden.PornSites.anyporn.watchmyexgf import WatchMyExGf
from ..hidden.PornSites.anyporn.watchmygftv import WatchMyGfTv
from ..hidden.PornSites.anyporn.anysex import AnySex
from ..hidden.PornSites.anyporn.slutload import SlutLoad
from ..hidden.PornSites.anyporn.xozilla import Xozilla
from ..hidden.PornSites.anyporn.vqtube import VQTube
from ..hidden.PornSites.anyporn.bravoteens import BravoTeens
from ..hidden.PornSites.anyporn.punishbang import PunishBang
from ..hidden.PornSites.anyporn.deviants import Deviants
from ..hidden.PornSites.anyporn.interracial import Interracial
from ..hidden.PornSites.anyporn.porn7 import Porn7
from ..hidden.PornSites.anyporn.camuploads import CamUploads
from ..hidden.PornSites.anyporn.ebony8 import Ebony8
from ..hidden.PornSites.anyporn.mrdeepfake import MrDeepFake
from ..hidden.PornSites.anyporn.anonv import AnonV
from ..hidden.PornSites.anyporn.camvideostv import CamVideosTv
from ..hidden.PornSites.anyporn.eroclips import EroClips
from ..hidden.PornSites.anyporn.zerodaysporn import ZeroDaysPorn
from ..hidden.PornSites.anyporn.zedporn import ZedPorn
from ..hidden.PornSites.anyporn.tropictube import TropicTube
from ..hidden.PornSites.anyporn.pornplus import PornPlus
from ..hidden.PornSites.anyporn.xcum import XCum
from ..hidden.PornSites.anyporn.tubewolf import TubeWolf
from ..hidden.PornSites.anyporn.magatubexxx import MegaTubeXXX
from ..hidden.PornSites.anyporn.pornrewind import PornRewind
from ..hidden.PornSites.anyporn.analdin import Analdin
from ..hidden.PornSites.asspoint import LesbianPornVideos
from ..hidden.PornSites.asspoint.xjizz import XJizz
from ..hidden.PornSites.asspoint.movietitan import MovieTitan
from ..hidden.PornSites.asspoint.movieshark import MovieShark
from ..hidden.PornSites.asspoint.mobilepornvideos import MobilePornMovies
from ..hidden.PornSites.asspoint.suzisporn import SuzisPorn
from ..hidden.PornSites.asspoint.youngporno import YoungPorno
from ..hidden.PornSites.asspoint.porntitan import PornTitan
from ..hidden.PornSites.asspoint.hoodtube import HoodTube
from ..hidden.PornSites.asspoint.teenieporn import TeeniePorn
from ..hidden.PornSites.asspoint.sexoasis import SexOasis
from ..hidden.PornSites.asspoint.cartoonpornvideos import CartoonPornVideos
from ..hidden.PornSites.asspoint.youngpornvideos import YoungPornVideos
from ..hidden.PornSites.asspoint.porntv import PornTV
from ..hidden.PornSites.asspoint.ghettotube import GhettoTube
from ..hidden.PornSites.asspoint.analpornvideos import AnalPornVideos
from ..hidden.PornSites.asspoint.asianpornvideos import AsianPornVideos
from ..hidden.PornSites.asspoint.asspoint import AssPoint
from ..hidden.PornSites.beeg import Beeg
from ..hidden.PornSites.cliphunter import ClipHunter
from ..hidden.PornSites.collectionofbestporn import CollectionOfBestPorn
from ..hidden.PornSites.cumlouder import CumLouder
from ..hidden.PornSites.cumngo import CumNGo
from ..hidden.PornSites.dachix import DaChix, DeviantClip
from ..hidden.PornSites.dachix.dagay import DaGay
from ..hidden.PornSites.draftsex import DraftSex
from ..hidden.PornSites.drtuber import DrTuber
from ..hidden.PornSites.eporner import EPorner
from ..hidden.PornSites.extremetube import SpankWire
from ..hidden.PornSites.extremetube.extremetube import ExtremeTube
from ..hidden.PornSites.faapy import Faapy
from ..hidden.PornSites.fapbraze import FapBraze
from ..hidden.PornSites.fapbraze.freehdinterracialporn import FreeHDInterracialPorn
from ..hidden.PornSites.fakings import FakingsTV
from ..hidden.PornSites.fetishpapa import AShemaleTube
from ..hidden.PornSites.fetishpapa.boyfriendtv import BoyfriendTV
from ..hidden.PornSites.fetishpapa.pornoxo import Pornoxo
from ..hidden.PornSites.fetishpapa.fetishpapa import FetishPapa
from ..hidden.PornSites.freeones import FreeOnes
from ..hidden.PornSites.goforporn import GoForPorn
from ..hidden.PornSites.gotporn import PornHD
from ..hidden.PornSites.gotporn.pornrox import PornRox
from ..hidden.PornSites.gotporn.pinflix import PinFlix
from ..hidden.PornSites.gotporn.gotporn import GotPorn
from ..hidden.PornSites.hdtubeporn import HDTubePorn, ZBPorn
from ..hidden.PornSites.hdtubeporn.pornid import PornID
from ..hidden.PornSites.hdtubeporn.sexvid import SexVid
from ..hidden.PornSites.homemoviestube import HomeMoviesTube
from ..hidden.PornSites.hotgirlclub import HotGirlClub
from ..hidden.PornSites.hqporner import HQPorner
from ..hidden.PornSites.jizzbunker import JizzBunker, XXXDan
from ..hidden.PornSites.joysporn import JoysPorn
from ..hidden.PornSites.katestube import KatesTube, PornWhite, WankOz
from ..hidden.PornSites.katestube.sheshaft import SheShaft
from ..hidden.PornSites.katestube.fetishshrine import FetishShrine
from ..hidden.PornSites.katestube.pornicom import PorniCom
from ..hidden.PornSites.katestube.vikiporn import VikiPorn
from ..hidden.PornSites.katestube.sleazyneasy import SleazyNEasy
from ..hidden.PornSites.katestube.pervclips import PervClips
from ..hidden.PornSites.laidhub import PornXio
from ..hidden.PornSites.laidhub.eroxia import Eroxia
from ..hidden.PornSites.laidhub.stileproject import StileProject
from ..hidden.PornSites.laidhub.pornwatchers import PornWatchers
from ..hidden.PornSites.laidhub.pornrabbit import PornRabbit
from ..hidden.PornSites.laidhub.handjobhub import HandJobHub
from ..hidden.PornSites.laidhub.hypnotube import HypnoTube
from ..hidden.PornSites.laidhub.nudez import Nudez
from ..hidden.PornSites.laidhub.laidhub import LaidHub
from ..hidden.PornSites.letsjerk import LetsJerk
from ..hidden.PornSites.likuoo import Likuoo
from ..hidden.PornSites.lovehomeporn import LoveHomePorn
from ..hidden.PornSites.luxuretv import LuxureTV
from ..hidden.PornSites.motherless import MotherLess
from ..hidden.PornSites.netfapx import Netfapx
from ..hidden.PornSites.nubilefilmxxx import NubileFilmXXX
from ..hidden.PornSites.nubilefilmxxx.plusone8 import PlusOne8
from ..hidden.PornSites.okxxx import OkXXX
from ..hidden.PornSites.palmtube import PalmTube
from ..hidden.PornSites.perfectgirls import PerfectGirls
from ..hidden.PornSites.porn00 import Porn00
from ..hidden.PornSites.porn300 import Porn300
from ..hidden.PornSites.porndig import PornDig
from ..hidden.PornSites.porndoe import PornDoe
from ..hidden.PornSites.porngo import PornGo
from ..hidden.PornSites.porngo.xxxfiles import XXXFiles
from ..hidden.PornSites.pornhd8k import PornHDEightK
from ..hidden.PornSites.pornhub import PornHub
from ..hidden.PornSites.pornhub.tube8 import TubeEight
from ..hidden.PornSites.pornhub.youporn import YouPorn
from ..hidden.PornSites.pornhub.porndotcom import PornDotCom
from ..hidden.PornSites.pornktube import PornKy, PornKTube, RushPorn, TubeXXPorn
from ..hidden.PornSites.pornomovies import PornoMovies
from ..hidden.PornSites.porntrex import PornTrex, JAVBangers, CamWhoresBay
from ..hidden.PornSites.porntube import PornTube, PornerBros, Fux, FourTube
from ..hidden.PornSites.realgfporn import RealGfPorn
from ..hidden.PornSites.red_wap import RedWap
from ..hidden.PornSites.redtube import RedTube
from ..hidden.PornSites.sextvx import SexTvX
from ..hidden.PornSites.sexu import SexU
from ..hidden.PornSites.shesfreaky import ShesFreaky
from ..hidden.PornSites.spankbang import SpankBang
from ..hidden.PornSites.sxyprn import SexyPorn
from ..hidden.PornSites.taxi69 import Taxi69
from ..hidden.PornSites.three_movs import ThreeMovs
from ..hidden.PornSites.tnaflix import TnaFlix, MovieFap, EmpFlix
from ..hidden.PornSites.tubev import TubeV
from ..hidden.PornSites.txxx import Txxx, HClips, UPornia, HDZog, HotMovs, VoyeurHit, TubePornClassic, VJav, TheGay, \
    Shemalez
from ..hidden.PornSites.ultrahorny import UltraHorny
from ..hidden.PornSites.veporns import VePorns
from ..hidden.PornSites.vintagetube import VintageTube
from ..hidden.PornSites.vporn import VPorn
from ..hidden.PornSites.wankgalore import WankGalore
from ..hidden.PornSites.xfantazy import XFantazy
from ..hidden.PornSites.xhamster import XHamster
from ..hidden.PornSites.xnxx import Xnxx, XVideos
from ..hidden.PornSites.yes_porn_please import YesPornPleaseX, SayPornPlease
from ..hidden.PornSites.youjizz import YouJizz


class PornHandlerIndicator(object):
    def __init__(self):
        self.best = False
        self.second_best = False
        self.third_best = False
        self.gay = False
        self.shemale = False
        self.cartoon = False
        self.amateur = False
        self.lesbian = False
        self.interracial = False
        self.black = False
        self.asian = False
        self.teens = False
        self.mature = False
        self.vintage = False
        self.fetish = False
        self.deep_fake = False
        self.search = False
        self.database = False


class SourceHandler(object):
    def __init__(self, source_id, logo_dir):
        unsupported_dir = path.join(logo_dir, 'Unsupported')
        self.is_active = True
        self.flags = PornHandlerIndicator()
        if source_id == -1:
            self.title = 'PornHub'
            self.main_module = PornHub
            self.image = path.join(logo_dir, 'pornhub.png')
        elif source_id == -2:
            self.title = 'XVideos'
            self.main_module = XVideos
            self.image = path.join(logo_dir, 'xvideos.png')
        elif source_id == -3:
            self.title = 'XHamster'
            self.main_module = XHamster
            self.image = path.join(logo_dir, 'xhamster.png')
        elif source_id == -4:
            self.title = 'XNXX'
            self.main_module = Xnxx
            self.image = path.join(logo_dir, 'xnxx.png')
        elif source_id == -5:
            self.title = 'Beeg'
            self.main_module = Beeg
            self.image = path.join(logo_dir, 'beeg.png')
        elif source_id == -6:
            self.title = 'PornHD'
            self.main_module = PornHD
            self.image = path.join(logo_dir, 'pornhd.png')
        elif source_id == -7:
            self.title = 'HQPorner'
            self.main_module = HQPorner
            self.image = path.join(logo_dir, 'hqporner.png')
        elif source_id == -8:
            self.title = 'EPorner'
            self.main_module = EPorner
            self.image = path.join(logo_dir, 'eporner.png')
        elif source_id == -9:
            self.title = 'YourPorn'
            self.main_module = SexyPorn
            self.image = path.join(logo_dir, 'sexyporn.png')
        elif source_id == -10:
            self.title = 'SpankBang'
            self.main_module = SpankBang
            self.image = path.join(logo_dir, 'spankbang.png')
        elif source_id == -11:
            self.title = 'PornTrex'
            self.main_module = PornTrex
            self.image = path.join(logo_dir, 'porntrex.png')
        elif source_id == -12:
            self.title = 'YesPornPlease'
            self.main_module = YesPornPleaseX
            self.image = path.join(logo_dir, 'yespornplease.png')
        elif source_id == -13:
            self.title = 'DraftSex'
            self.main_module = DraftSex
            self.image = path.join(logo_dir, 'draftsex.png')
        elif source_id == -14:
            self.title = 'YouJizz'
            self.main_module = YouJizz
            self.image = path.join(logo_dir, 'youjizz.png')
        elif source_id == -15:
            self.title = 'MotherLess'
            self.main_module = MotherLess
            self.image = path.join(logo_dir, 'motherless.png')
        elif source_id == -16:
            self.title = 'RedTube'
            self.main_module = RedTube
            self.image = path.join(logo_dir, 'redtube.png')
        elif source_id == -17:
            self.title = 'YouPorn'
            self.main_module = YouPorn
            self.image = path.join(logo_dir, 'youporn.png')
        elif source_id == -18:
            self.title = 'vPorn'
            self.main_module = VPorn
            self.image = path.join(logo_dir, 'vporn.png')
        elif source_id == -19:
            self.title = 'Porn.com'
            self.main_module = PornDotCom
            self.image = path.join(logo_dir, 'porn_com.png')
            self.is_active = False
            self.flags.search = True
        elif source_id == -20:
            self.title = 'VePorns'
            self.main_module = VePorns
            self.image = path.join(logo_dir, 'veporn.png')
        elif source_id == -21:
            self.title = 'PornKTube'
            self.main_module = PornKTube
            self.image = path.join(logo_dir, 'pornktube.png')
        elif source_id == -22:
            self.title = 'GotPorn'
            self.main_module = GotPorn
            self.image = path.join(logo_dir, 'gotporn.png')
        elif source_id == -23:
            self.title = '4Tube'
            self.main_module = FourTube
            self.image = path.join(logo_dir, '4tube.png')
        elif source_id == -24:
            self.title = 'PornTube'
            self.main_module = PornTube
            self.image = path.join(logo_dir, 'PornTube.png')
        elif source_id == -25:
            self.title = '3Movs'
            self.main_module = ThreeMovs
            self.image = path.join(logo_dir, '3movs.png')
        elif source_id == -26:
            self.title = 'PornGo'
            self.main_module = PornGo
            self.image = path.join(logo_dir, 'porngo.png')
        elif source_id == -27:
            self.title = 'Tube8'
            self.main_module = TubeEight
            self.image = path.join(logo_dir, 'tube8.png')
        elif source_id == -28:
            self.title = 'CumLouder'
            self.main_module = CumLouder
            self.image = path.join(logo_dir, 'cumlouder.png')
        elif source_id == -29:
            self.title = 'Txxx'
            self.main_module = Txxx
            self.image = path.join(logo_dir, 'txxx.png')
        elif source_id == -30:
            self.title = 'TubXPorn'
            self.main_module = TubeXXPorn
            self.image = path.join(logo_dir, 'tubxporn.png')
        elif source_id == -31:
            self.title = 'PornDoe'
            self.main_module = PornDoe
            self.image = path.join(logo_dir, 'porndoe.png')
        elif source_id == -32:
            self.title = 'XXXFiles'
            self.main_module = XXXFiles
            self.image = path.join(logo_dir, 'xxxfiles.png')
        elif source_id == -33:
            self.title = 'TNAFlix'
            self.main_module = TnaFlix
            self.image = path.join(logo_dir, 'tnaflix.png')
        elif source_id == -34:
            self.title = 'PornDig'
            self.main_module = PornDig
            self.image = path.join(logo_dir, 'porndig.png')
        elif source_id == -35:
            # Not supported site, thus we return fake inactive result
            self.title = 'PornDish'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'porndish.png')
        elif source_id == -36:
            # Not supported site, thus we return fake inactive result
            self.title = 'Porn4Days'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'porn4days.png')
        elif source_id == -37:
            self.title = 'LaidHub'
            self.main_module = LaidHub
            self.image = path.join(logo_dir, 'laidhub.png')
        elif source_id == -38:
            # Not supported site, thus we return fake inactive result
            self.title = 'VePorn'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'paradisehill.png')
        elif source_id == -39:
            # Not supported site, thus we return fake inactive result
            self.title = 'ParadiseHill'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'veporn.png')
        elif source_id == -40:
            self.title = 'PornHD8K'
            self.main_module = PornHDEightK
            self.image = path.join(logo_dir, 'pornhd8k.png')
        elif source_id == -41:
            self.title = 'LuxureTV'
            self.main_module = LuxureTV
            self.image = path.join(logo_dir, 'luxuretv.png')
        elif source_id == -42:
            self.title = 'PerfectGirls'
            self.main_module = PerfectGirls
            self.image = path.join(logo_dir, 'perfectgirls.png')
        elif source_id == -43:
            self.title = 'Porn300'
            self.main_module = Porn300
            self.image = path.join(logo_dir, 'porn300.png')
        elif source_id == -44:
            self.title = 'AnySex'
            self.main_module = AnySex
            self.image = path.join(logo_dir, 'anysex.png')
        elif source_id == -45:
            self.title = 'DrTuber'
            self.main_module = DrTuber
            self.image = path.join(logo_dir, 'drtuber.png')
        elif source_id == -46:
            self.title = 'Netfapx'
            self.main_module = Netfapx
            self.image = path.join(logo_dir, 'netfapx.png')
        elif source_id == -47:
            # Not supported site, thus we return fake inactive result
            self.title = 'XMovieswForYou'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'xmoviesforyou.png')
        elif source_id == -48:
            self.title = 'LetsJerk'
            self.main_module = LetsJerk
            self.image = path.join(logo_dir, 'letsjerk.png')
        elif source_id == -49:
            self.title = 'Likuoo'
            self.main_module = Likuoo
            self.image = path.join(logo_dir, 'likuoo.png')
        elif source_id == -50:
            # Not supported site, thus we return fake inactive result
            self.title = 'PornoBae'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'pornobae.png')
        elif source_id == -51:
            self.title = 'XXXStreams'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'xxxstreams.png')
        elif source_id == -52:
            self.title = 'Porn00'
            self.main_module = Porn00
            self.image = path.join(logo_dir, 'porn00.png')
        elif source_id == -53:
            self.title = 'RushPorn'
            self.main_module = RushPorn
            self.image = path.join(logo_dir, 'rushporn.png')
        elif source_id == -54:
            self.title = 'PornKy'
            self.main_module = PornKy
            self.image = path.join(logo_dir, 'pornky.png')
        elif source_id == -55:
            self.title = 'JoysPorn'
            self.main_module = JoysPorn
            self.image = path.join(logo_dir, 'joysporn.png')
        elif source_id == -56:
            self.title = 'UltraHorny'
            self.main_module = UltraHorny
            self.image = path.join(logo_dir, 'ultrahorny.png')
        elif source_id == -57:
            self.title = 'WatchXXXFree'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'watchxxxfree.png')
        elif source_id == -58:
            self.title = 'PlusOne8'
            self.main_module = PlusOne8
            self.image = path.join(logo_dir, 'plusone8.png')
        elif source_id == -59:
            self.title = 'FreeoMovie'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'freeomovie.png')
        elif source_id == -60:
            self.title = 'AnyPorn'
            self.main_module = AnyPorn
            self.image = path.join(logo_dir, 'anyporn.png')
        elif source_id == -61:
            self.title = 'ClipHunter'
            self.main_module = ClipHunter
            self.image = path.join(logo_dir, 'cliphunter.png')
        elif source_id == -62:
            self.title = 'PornRewindpornr'
            self.main_module = PornRewind
            self.image = path.join(logo_dir, 'pornrewind.png')
        elif source_id == -63:
            self.title = 'VQTube'
            self.main_module = VQTube
            self.image = path.join(logo_dir, 'vqtube.png')
        elif source_id == -64:
            self.title = 'CollectionOfBestPorn'
            self.main_module = CollectionOfBestPorn
            self.image = path.join(logo_dir, 'collectionofbestporn.png')
        elif source_id == -65:
            self.title = 'PornHD6K'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'pornhd6k.png')
        elif source_id == -66:
            self.title = 'XTapes'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'xtapes.png')
        elif source_id == -67:
            self.title = 'Sweext'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'sweext.png')
        elif source_id == -68:
            self.title = 'PervertSluts'
            self.main_module = PervertSluts
            self.image = path.join(logo_dir, 'pervertslut.png')
        elif source_id == -69:
            self.title = 'XkeezMovies'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'xkeezmovies.png')
        elif source_id == -70:
            self.title = 'SexGalaxy'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'sexgalaxy.png')
        elif source_id == -71:
            self.title = 'NetPornSex'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'netpornsex.png')
        elif source_id == -72:
            self.title = 'Palimas'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'palimas.png')
        elif source_id == -73:
            self.title = 'SexTvX'
            self.main_module = SexTvX
            self.image = path.join(logo_dir, 'sextvx.png')
        elif source_id == -74:
            self.title = 'HotGirlClub'
            self.main_module = HotGirlClub
            self.image = path.join(logo_dir, 'hotgirlclub.png')
        elif source_id == -75:
            self.title = 'SexU'
            self.main_module = SexU
            self.image = path.join(logo_dir, 'sexu.png')
        elif source_id == -76:
            self.title = 'YourDailyPornVideos'
            self.main_module = None
            self.image = None
        elif source_id == -77:
            self.title = 'PornoVideoHub'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'pornovideohub.png')
        elif source_id == -78:
            self.title = 'YoungPornVideos'
            self.main_module = YoungPornVideos
            self.image = path.join(logo_dir, 'youngpornvideos.png')
        elif source_id == -79:
            self.title = 'PandaMovies'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'pandamovies.png')
        elif source_id == -80:
            self.title = 'StramingPorn'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'streamingporn.png')
        elif source_id == -81:
            self.title = 'XXXstreams.eu'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'xxxstreams.eu.png')
        elif source_id == -82:
            self.title = 'FullXXXMovies'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'fullxxxmovies.png')
        elif source_id == -83:
            self.title = 'Pornxbit'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'pornxbit.png')
        elif source_id == -84:
            self.title = 'PussySpace'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'pussyspace.png')
        elif source_id == -85:
            self.title = 'GameOfPorn'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'gameofporn.jpg')
        elif source_id == -86:
            self.title = 'PornStreams'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'pornstreams.png')
        elif source_id == -87:
            self.title = 'PornVibe'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'pornvibe.png')
        elif source_id == -88:
            self.title = 'HD-EasyPorn'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'hdeasyporn.png')
        elif source_id == -89:
            self.title = 'PalmTube'
            self.main_module = PalmTube
            self.image = path.join(logo_dir, 'palmtube.png')
        elif source_id == -90:
            self.title = 'FakingsTV'
            self.main_module = FakingsTV
            self.image = path.join(logo_dir, 'fakingstv.png')
        elif source_id == -91:
            self.title = 'VRPorn'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'vrporn.png')
        elif source_id == -92:
            self.title = 'DVDTrailerTube'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'dvdtrailertube.png')
        elif source_id == -93:
            self.title = 'EmpFlix'
            self.main_module = EmpFlix
            self.image = path.join(logo_dir, 'empflix.jpg')
        elif source_id == -94:
            self.title = 'Taxi69'
            self.main_module = Taxi69
            self.image = path.join(logo_dir, 'taxi69.png')
        elif source_id == -95:
            self.title = 'SlutLoad'
            self.main_module = SlutLoad
            self.image = path.join(logo_dir, 'slutload.png')
        elif source_id == -96:
            self.title = 'Fux'
            self.main_module = Fux
            self.image = path.join(logo_dir, 'fux.png')
        elif source_id == -97:
            self.title = 'MangoPorn'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'mangoporn.png')
        elif source_id == -98:
            self.title = 'StreamPorn'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'streamingporn.png')
        elif source_id == -99:
            self.title = 'JustSwallows'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'justswallows.png')
        elif source_id == -100:
            self.title = '0DaysPorn'
            self.main_module = ZeroDaysPorn
            self.image = path.join(logo_dir, '0dayporn.png')
        elif source_id == -101:
            self.title = 'YourDailyPornMovies'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'yourdailypornmovies.png')
        elif source_id == -102:
            self.title = 'CastingPornoTube'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'Casting-porno-tube-logo.png')
        elif source_id == -103:
            self.title = 'SwingersPornFun'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'swingerspornfun.png')
        elif source_id == -104:
            self.title = 'CumNGo'
            self.main_module = CumNGo
            self.image = path.join(logo_dir, 'cumngo.png')
        elif source_id == -105:
            self.title = 'PornoDep'
            self.main_module = PornoDep
            self.image = path.join(logo_dir, 'pornodep.png')
        elif source_id == -106:
            self.title = 'SayPornPlease'
            self.main_module = SayPornPlease
            self.image = path.join(logo_dir, 'saypornplease.png')
        # from here and on we use the rating of hall-of-fame page
        elif source_id == -201:
            self.title = 'SpankWire'
            self.main_module = SpankWire
            self.image = path.join(logo_dir, 'spankwire.png')
        elif source_id == -202:
            self.title = 'FreeHDInterracialPorn'
            self.main_module = FreeHDInterracialPorn
            self.image = path.join(logo_dir, 'freehdinterracialporn.png')
            self.flags.interracial = True
        elif source_id == -203:
            self.title = 'RedWap'
            self.main_module = RedWap
            self.image = path.join(logo_dir, 'redwap.jpg')
        elif source_id == -204:
            self.title = 'XXXBunker'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'xxxbunker.png')
        elif source_id == -205:
            self.title = 'MadThumbs'
            self.main_module = MadThumbs
            self.image = path.join(logo_dir, 'madthumbs.png')
        elif source_id == -206:
            self.title = 'ZBPorn'
            self.main_module = ZBPorn
            self.image = path.join(logo_dir, 'zbporn.png')
        elif source_id == -207:
            self.title = 'Analdin'
            self.main_module = Analdin
            self.image = path.join(logo_dir, 'analdin.png')
        elif source_id == -208:
            self.title = 'SunPorno'
            self.main_module = SunPorno
            self.image = path.join(logo_dir, 'sunporno.png')
        elif source_id == -220:
            self.title = 'Pornoxo'
            self.main_module = Pornoxo
            self.image = path.join(logo_dir, 'pornoxo.jpg')
        elif source_id == -240:
            self.title = 'ExtremeTube'
            self.main_module = ExtremeTube
            self.image = path.join(logo_dir, 'extremetube.png')
        elif source_id == -250:
            self.title = 'UPornia'
            self.main_module = UPornia
            self.image = path.join(logo_dir, 'upornia.png')
        elif source_id == -270:
            self.title = 'Faapy'
            self.main_module = Faapy
            self.image = path.join(logo_dir, 'faapy.png')
        elif source_id == -280:
            self.title = 'HDZog'
            self.main_module = HDZog
            self.image = path.join(logo_dir, 'hdzog.png')
        elif source_id == -285:
            self.title = 'Xozilla'
            self.main_module = Xozilla
            self.image = path.join(logo_dir, 'xozilla.png')
        elif source_id == -290:
            self.title = 'PinFlix'
            self.main_module = PinFlix
            self.image = path.join(logo_dir, 'pinflix.png')
        elif source_id == -295:
            self.title = 'HandJobHub'
            self.main_module = HandJobHub
            self.image = path.join(logo_dir, 'handjobhub.png')
        elif source_id == -297:
            self.title = 'AnonV'
            self.main_module = AnonV
            self.image = path.join(logo_dir, 'anonv.png')
        # from here and on we use the rest (not cataloged) general sites
        elif source_id == -401:
            self.title = 'PornerBros'
            self.main_module = PornerBros
            self.image = path.join(logo_dir, 'pornerbros.png')
        elif source_id == -402:
            self.title = 'JizzBunker'
            self.main_module = JizzBunker
            self.image = path.join(logo_dir, 'jizzbunker.png')
        elif source_id == -403:
            self.title = 'WankGalore'
            self.main_module = WankGalore
            self.image = path.join(logo_dir, 'wankgalore.png')
        elif source_id == -404:
            self.title = 'PornoMovies'
            self.main_module = PornoMovies
            self.image = path.join(logo_dir, 'pornomovies.png')
        elif source_id == -405:
            self.title = 'NubileFilmXXX'
            self.main_module = NubileFilmXXX
            self.image = path.join(logo_dir, 'nubilefilmxxx.png')
        elif source_id == -406:
            self.title = 'HDTubePorn'
            self.main_module = HDTubePorn
            self.image = path.join(logo_dir, 'hdtubeporn.png')
        elif source_id == -407:
            self.title = 'GoForPorn'
            self.main_module = GoForPorn
            self.image = path.join(logo_dir, 'goforporn.png')
        elif source_id == -408:
            self.title = 'DaChix'
            self.main_module = DaChix
            self.image = path.join(logo_dir, 'dachix.png')
        elif source_id == -409:
            self.title = 'DeviantClip'
            self.main_module = DeviantClip
            self.image = path.join(logo_dir, 'deviantclip.png')
            self.flags.fetish = True
        elif source_id == -410:
            self.title = 'TubeV'
            self.main_module = TubeV
            self.image = path.join(logo_dir, 'tubev.png')
        elif source_id == -411:
            self.title = 'OkXXX'
            self.main_module = OkXXX
            self.image = path.join(logo_dir, 'okxxx.png')
        elif source_id == -412:
            self.title = 'SexyPorn'
            self.main_module = SexyPorn
            self.image = path.join(logo_dir, 'sexyporn.png')
        elif source_id == -413:
            self.title = 'XXXDan'
            self.main_module = XXXDan
            self.image = path.join(logo_dir, 'xxxdan.png')
        elif source_id == -414:
            self.title = 'AhMe'
            self.main_module = AhMe
            self.image = path.join(logo_dir, 'ahme.jpg')
        elif source_id == -415:
            self.title = 'Nudez'
            self.main_module = Nudez
            self.image = path.join(logo_dir, 'nudez.png')
        elif source_id == -416:
            self.title = 'FapBraze'
            self.main_module = FapBraze
            self.image = path.join(logo_dir, 'fapbraze.png')
        elif source_id == -417:
            self.title = 'PornXio'
            self.main_module = PornXio
            self.image = path.join(logo_dir, 'pornxio.png')
        elif source_id == -418:
            self.title = 'PornRabbit'
            self.main_module = PornRabbit
            self.image = path.join(logo_dir, 'pornrabbit.png')
        elif source_id == -419:
            self.title = 'SexVid'
            self.main_module = SexVid
            self.image = path.join(logo_dir, 'sexvid.png')
        elif source_id == -420:
            self.title = 'PornWatchers'
            self.main_module = PornWatchers
            self.image = path.join(logo_dir, 'pornwatchers.png')
        elif source_id == -421:
            self.title = 'StileProject'
            self.main_module = StileProject
            self.image = path.join(logo_dir, 'stileproject.png')
        elif source_id == -422:
            self.title = 'Eroxia'
            self.main_module = Eroxia
            self.image = path.join(logo_dir, 'eroxia.png')
        elif source_id == -423:
            self.title = 'PornTV'
            self.main_module = PornTV
            self.image = path.join(logo_dir, 'porntv.png')
        elif source_id == -424:
            self.title = 'SexOasis'
            self.main_module = SexOasis
            self.image = path.join(logo_dir, 'sexoasis.png')
        elif source_id == -425:
            self.title = 'PornTitan'
            self.main_module = PornTitan
            self.image = path.join(logo_dir, 'porntitan.png')
        elif source_id == -426:
            self.title = 'SuzisPorn'
            self.main_module = SuzisPorn
            self.image = path.join(logo_dir, 'suzisporn.png')
        elif source_id == -427:
            self.title = 'MobilePornMovies'
            self.main_module = MobilePornMovies
            self.image = path.join(logo_dir, 'mobilepornmovies.png')
        elif source_id == -428:
            self.title = 'MovieShark'
            self.main_module = MovieShark
            self.image = path.join(logo_dir, 'movieshark.png')
        elif source_id == -429:
            self.title = 'MovieTitan'
            self.main_module = MovieTitan
            self.image = path.join(logo_dir, 'movietitan.png')
        elif source_id == -430:
            self.title = 'XJizz'
            self.main_module = XJizz
            self.image = path.join(logo_dir, 'xjizz.png')
        elif source_id == -431:
            self.title = 'Fapster'
            self.main_module = Fapster
            self.image = path.join(logo_dir, 'fapster.png')
        elif source_id == -432:
            self.title = 'HellPorno'
            self.main_module = HellPorno
            self.image = path.join(logo_dir, 'hellporno.png')
        elif source_id == -433:
            self.title = 'AlphaPorno'
            self.main_module = AlphaPorno
            self.image = path.join(logo_dir, 'alphaporno.png')
        elif source_id == -434:
            self.title = 'TubeWolf'
            self.main_module = TubeWolf
            self.image = path.join(logo_dir, 'tubewolf.png')
        elif source_id == -435:
            self.title = 'XBabe'
            self.main_module = XBabe
            self.image = path.join(logo_dir, 'xbabe.png')
        elif source_id == -436:
            self.title = 'BravoPorn'
            self.main_module = BravoPorn
            self.image = path.join(logo_dir, 'bravoporn.png')
        elif source_id == -437:
            self.title = 'XCum'
            self.main_module = XCum
            self.image = path.join(logo_dir, 'xcum.png')
        elif source_id == -438:
            self.title = 'PornPlus'
            self.main_module = PornPlus
            self.image = path.join(logo_dir, 'pornplus.png')
        elif source_id == -439:
            self.title = 'MegaTubeXXX'
            self.main_module = MegaTubeXXX
            self.image = path.join(logo_dir, 'megatube.png')
        elif source_id == -440:
            self.title = 'Sex3'
            self.main_module = Sex3
            self.image = path.join(logo_dir, 'sex3.png')
        elif source_id == -441:
            self.title = 'CrocoTube'
            self.main_module = CrocoTube
            self.image = path.join(logo_dir, 'crocotube.png')
        elif source_id == -442:
            self.title = 'TropicTube'
            self.main_module = TropicTube
            self.image = path.join(logo_dir, 'tropictube.png')
        elif source_id == -443:
            self.title = 'EroClips'
            self.main_module = EroClips
            self.image = path.join(logo_dir, 'eroclips.png')
        elif source_id == -444:
            self.title = 'ZedPorn'
            self.main_module = ZedPorn
            self.image = path.join(logo_dir, 'zedporn.png')
        elif source_id == -445:
            self.title = 'Porn7'
            self.main_module = Porn7
            self.image = path.join(logo_dir, 'porn7.png')
        elif source_id == -446:
            self.title = 'MoviesAnd'
            self.main_module = MoviesAnd
            self.image = path.join(logo_dir, 'moviesand.png')
        elif source_id == -447:
            self.title = 'KatesTube'
            self.main_module = KatesTube
            self.image = path.join(logo_dir, 'katestube.png')
        elif source_id == -448:
            self.title = 'PervClips'
            self.main_module = PervClips
            self.image = path.join(logo_dir, 'pervclips.png')
        elif source_id == -449:
            self.title = 'PornWhite'
            self.main_module = PornWhite
            self.image = path.join(logo_dir, 'pornwhite.png')
        elif source_id == -450:
            self.title = 'SleazyNEasy'
            self.main_module = SleazyNEasy
            self.image = path.join(logo_dir, 'sleazyneasy.png')
        elif source_id == -451:
            self.title = 'VikiPorn'
            self.main_module = VikiPorn
            self.image = path.join(logo_dir, 'vikiporn.png')
        elif source_id == -452:
            self.title = 'WankOz'
            self.main_module = WankOz
            self.image = path.join(logo_dir, 'wankoz.png')
        elif source_id == -453:
            self.title = 'PorniCom'
            self.main_module = PorniCom
            self.image = path.join(logo_dir, 'pornicom.png')
        elif source_id == -454:
            self.title = 'MovieFap'
            self.main_module = MovieFap
            self.image = path.join(logo_dir, 'moviefap.png')
        elif source_id == -460:
            self.title = 'PornID'
            self.main_module = PornID
            self.image = path.join(logo_dir, 'pornid.png')
        elif source_id == -461:
            self.title = 'HotMovs'
            self.main_module = HotMovs
            self.image = path.join(logo_dir, 'hotmovs.png')
        elif source_id == -462:
            self.title = 'PornRox'
            self.main_module = PornRox
            self.image = path.join(logo_dir, 'pornrox.png')
        # Amateur sites
        elif source_id == -501:
            self.title = 'HomeMoviesTube'
            self.main_module = HomeMoviesTube
            self.image = path.join(logo_dir, 'homemoviestube.png')
        elif source_id == -502:
            self.title = 'EroProfile'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'eroprofile.png')
        elif source_id == -503:
            self.title = 'HClips'
            self.main_module = HClips
            self.image = path.join(logo_dir, 'hclips.png')
        elif source_id == -504:
            self.title = 'XTube'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'xtube.png')
        elif source_id == -505:
            self.title = 'CamWhores'
            self.main_module = None
            self.image = path.join(unsupported_dir, 'camwhores.png')
        elif source_id == -506:
            self.title = 'VoyuerHit'
            self.main_module = VoyeurHit
            self.image = path.join(logo_dir, 'voyeurhit.png')
        elif source_id == -511:
            self.title = 'CamWhoresBay'
            self.main_module = CamWhoresBay
            self.image = path.join(logo_dir, 'camwhorebay.png')
        elif source_id == -512:
            self.title = 'RealGfPorn'
            self.main_module = RealGfPorn
            self.image = path.join(logo_dir, 'realgfporn.png')
        elif source_id == -513:
            self.title = 'LoveHomePorn'
            self.main_module = LoveHomePorn
            self.image = path.join(logo_dir, 'lovehomeporn.png')
        elif source_id == -514:
            self.title = 'WatchMyGfMe'
            self.main_module = WatchMyGfMe
            self.image = path.join(logo_dir, 'watchmygfme.png')
        elif source_id == -515:
            self.title = 'WatchMyGfTv'
            self.main_module = WatchMyGfTv
            self.image = path.join(logo_dir, 'watchmygftv.png')
        elif source_id == -516:
            self.title = 'WatchMyExGf'
            self.main_module = WatchMyExGf
            self.image = path.join(logo_dir, 'watchmyexgf.png')
        elif source_id == -517:
            self.title = 'CamVideosTv'
            self.main_module = CamVideosTv
            self.image = path.join(logo_dir, 'camvideostv.png')
        elif source_id == -518:
            self.title = 'CamUploads'
            self.main_module = CamUploads
            self.image = path.join(logo_dir, 'camuploads.png')
        # Anal
        elif source_id == -620:
            self.title = 'AssPoint'
            self.main_module = AssPoint
            self.image = path.join(logo_dir, 'asspoint.png')
        elif source_id == -621:
            self.title = 'AnalPornVideos'
            self.main_module = AnalPornVideos
            self.image = path.join(logo_dir, 'analpornvideos.png')
        elif source_id == -622:
            self.title = 'AnalPornVideosXXX'
            self.main_module = AnalPornVideosXXX
            self.image = path.join(logo_dir, 'analpornvideosxxx.png')
        # Teens
        elif source_id == -720:
            self.title = 'TeeniePorn'
            self.main_module = TeeniePorn
            self.image = path.join(logo_dir, 'teenieporn.png')
        elif source_id == -721:
            self.title = 'YoungPorno'
            self.main_module = YoungPorno
            self.image = path.join(logo_dir, 'youngporno.png')
        elif source_id == -721:
            self.title = 'BravoTeens'
            self.main_module = BravoTeens
            self.image = path.join(logo_dir, 'bravoteens.png')
        # Mature
        elif source_id == -820:
            self.title = 'HellMoms'
            self.main_module = HellMoms
            self.image = path.join(logo_dir, 'hellmoms.png')
        # DeepFake sites
        elif source_id == -904:
            self.title = 'MrDeepFake'
            self.main_module = MrDeepFake
            self.image = path.join(logo_dir, 'mrdeepfake.png')
        # Interracial sites
        elif source_id == -1030:
            self.title = 'Interracial'
            self.main_module = Interracial
            self.image = path.join(logo_dir, 'interracial.png')
        # Black sites
        elif source_id == -1101:
            self.title = 'ShesFreaky'
            self.main_module = ShesFreaky
            self.image = path.join(logo_dir, 'shesfreaky.png')
        elif source_id == -1108:
            self.title = 'GhettoTube'
            self.main_module = GhettoTube
            self.image = path.join(logo_dir, 'ghettotube.png')
        elif source_id == -1150:
            self.title = 'HoodTube'
            self.main_module = HoodTube
            self.image = path.join(logo_dir, 'hoodtube.png')
        elif source_id == -1151:
            self.title = 'Ebony8'
            self.main_module = Ebony8
            self.image = path.join(logo_dir, 'ebony8.png')
        # Asian sites
        elif source_id == -1203:
            self.title = 'VJav'
            self.main_module = VJav
            self.image = path.join(logo_dir, 'vjav.png')
        elif source_id == -1205:
            self.title = 'JAVBangers'
            self.main_module = JAVBangers
            self.image = path.join(logo_dir, 'javbangers.png')
        elif source_id == -1250:
            self.title = 'AsianPornVideos'
            self.main_module = AsianPornVideos
            self.image = path.join(logo_dir, 'asianpornmovies.png')
        # Vintage sites
        elif source_id == -1301:
            self.title = 'TubePornClassic'
            self.main_module = TubePornClassic
            self.image = path.join(logo_dir, 'tubepornclassic.png')
        elif source_id == -1320:
            self.title = 'VintageTube'
            self.main_module = VintageTube
            self.image = path.join(logo_dir, 'vintagetube.png')
        # Lesbian sites
        elif source_id == -1430:
            self.title = 'LesbianPornVideos'
            self.main_module = LesbianPornVideos
            self.image = path.join(logo_dir, 'lesbianpornvideos.png')
        # Gay sites
        elif source_id == -1520:
            self.title = 'DaGay'
            self.main_module = DaGay
            self.image = path.join(logo_dir, 'dagay.png')
        elif source_id == -1550:
            self.title = 'TheGay'
            self.main_module = TheGay
            self.image = path.join(logo_dir, 'thegay.png')
        elif source_id == -1551:
            self.title = 'BoyfriendTV'
            self.main_module = BoyfriendTV
            self.image = path.join(logo_dir, 'boyfriendtv.png')
        # Shemale sites
        elif source_id == -1600:
            self.title = 'AShemaleTube'
            self.main_module = AShemaleTube
            self.image = path.join(logo_dir, 'ashemaletube.png')
        elif source_id == -1608:
            self.title = 'Shemalez'
            self.main_module = Shemalez
            self.image = path.join(logo_dir, 'shemalez.png')
        elif source_id == -1650:
            self.title = 'SheShaft'
            self.main_module = SheShaft
            self.image = path.join(logo_dir, 'sheshaft.png')
        # Cartoon sites
        elif source_id == -1730:
            self.title = 'CartoonPornVideos'
            self.main_module = CartoonPornVideos
            self.image = path.join(logo_dir, 'cartoonpornvideos.png')
        elif source_id == -1731:
            self.title = 'AdultCartoons'
            self.main_module = AdultCartoons
            self.image = path.join(logo_dir, 'adultcartoons.png')
        # Fetish sites
        elif source_id == -1802:
            self.title = 'BoundHub'
            self.main_module = BoundHub
            self.image = path.join(logo_dir, 'boundhub.png')
        elif source_id == -1807:
            self.title = 'HypnoTube'
            self.main_module = HypnoTube
            self.image = path.join(logo_dir, 'hypnotube.png')
        elif source_id == -1814:
            self.title = 'PunishBang'
            self.main_module = PunishBang
            self.image = path.join(logo_dir, 'punishbang.png')
        elif source_id == -1816:
            self.title = 'PornBimbo'
            self.main_module = PornBimbo
            self.image = path.join(logo_dir, 'pornbimbo.png')
        elif source_id == -1818:
            self.title = 'PornFd'
            self.main_module = PornFd
            self.image = path.join(logo_dir, 'pornfd.png')
        elif source_id == -1850:
            self.title = 'FetishPapa'
            self.main_module = FetishPapa
            self.image = path.join(logo_dir, 'fetishpapa.png')
        elif source_id == -1851:
            self.title = 'Deviants'
            self.main_module = Deviants
            self.image = path.join(logo_dir, 'deviants.png')
        elif source_id == -1852:
            self.title = 'FetishShrine'
            self.main_module = FetishShrine
            self.image = path.join(logo_dir, 'fetishshrine.png')
        # Search sites
        elif source_id == -1920:
            self.title = 'XFantazy'
            self.main_module = XFantazy
            self.image = path.join(logo_dir, 'xfantazy.png')
        # Databases sites
        elif source_id == -2001:
            self.title = 'FreeOnes'
            self.main_module = FreeOnes
            self.image = path.join(logo_dir, 'freeones.png')
        else:
            raise ValueError('Wrong source type {s}'.format(s=source_id))
        if self.main_module is None:
            # Every not implemented module is inactive, but not visa-versa...
            self.is_active = False
        positive_source_id = -source_id
        if positive_source_id in range(1, 201):
            self.flags.best = True
        elif positive_source_id in range(201, 401):
            self.flags.second_best = True
        elif positive_source_id in range(401, 501):
            self.flags.third_best = True
        elif positive_source_id in range(501, 601):
            self.flags.amateur = True
        elif positive_source_id in range(601, 701):
            self.flags.teens = True
        elif positive_source_id in range(701, 801):
            self.flags.mature = True
        elif positive_source_id in range(801, 901):
            self.flags.deep_fake = True
        elif positive_source_id in range(901, 1001):
            self.flags.interracial = True
        elif positive_source_id in range(1001, 1101):
            self.flags.black = True
        elif positive_source_id in range(1101, 1201):
            self.flags.asian = True
        elif positive_source_id in range(1201, 1301):
            self.flags.vintage = True
        elif positive_source_id in range(1301, 1401):
            self.flags.lesbian = True
        elif positive_source_id in range(1401, 1501):
            self.flags.gay = True
        elif positive_source_id in range(1501, 1601):
            self.flags.shemale = True
        elif positive_source_id in range(1601, 1701):
            self.flags.cartoon = True
        elif positive_source_id in range(1701, 1801):
            self.flags.fetish = True
        elif positive_source_id in range(1801, 1901):
            self.flags.search = True
        elif positive_source_id in range(1901, 2001):
            self.flags.database = True
        self.handler_id = source_id
        self.initialized_module = None


class HandlerManager(object):
    def __init__(self, logo_dir, user_data_dir, session_id):
        self.handlers = {}
        self.logo_dir = logo_dir
        self.user_data_dir = user_data_dir
        self.session_id = session_id
        source_ids = range(-1, -2100, -1)
        # xbmc.log('Preparing handlers for source ids {s}'.format(s=source_ids))
        for _x in source_ids:
            try:
                _h = SourceHandler(_x, logo_dir)
                if _h.main_module is None:
                    continue
                self.handlers[_h.handler_id] = _h
            except ValueError:
                continue

    def get_handler(self, handler_id, use_web_server=True):
        handler = self.handlers[handler_id]
        if handler.initialized_module is None:
            handler.initialized_module = handler.main_module(source_id=handler_id, data_dir=self.user_data_dir,
                                                             session_id=self.session_id, use_web_server=use_web_server,
                                                             )
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
