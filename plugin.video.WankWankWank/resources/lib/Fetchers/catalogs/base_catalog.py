# ID generator
from ..id_generator import IdGenerator

# OS
from os import path, makedirs

# pickle
import pickle

# Enum
from .. import Enum

# Abstract
from abc import abstractmethod, ABCMeta

# copy
# import copy


class CategoryEnum(Enum):
    def __init__(self, category_type, item_id):
        self._value = (category_type, item_id)
        self.category_type = category_type


# Video types
class VideoTypes(Enum):
    __order__ = 'VIDEO_REGULAR, VIDEO_SEGMENTS, VIDEO_YOUTUBE, VIDEO_DASH'
    VIDEO_REGULAR = 0
    VIDEO_SEGMENTS = 1
    VIDEO_YOUTUBE = 2
    VIDEO_DASH = 3


class FilterTypes(Enum):
    GENERAL_TYPE = 0
    PROFESSION_TYPE = 1
    LENGTH_TYPE = 2
    ADDED_BEFORE_TYPE = 3
    DATE_TYPE = 4
    QUALITY_TYPE = 5
    RATING_TYPE = 6
    COMMENTS_TYPE = 7
    SORT_ORDER_TYPE = 8
    COUNTRY_TYPE = 9


# Filters
class BaseFilterTypes(Enum):
    # Types
    AllType = (FilterTypes.GENERAL_TYPE, 0)
    OneType = (FilterTypes.GENERAL_TYPE, 1)
    TwoType = (FilterTypes.GENERAL_TYPE, 2)
    ThreeType = (FilterTypes.GENERAL_TYPE, 3)
    FourType = (FilterTypes.GENERAL_TYPE, 4)
    FiveType = (FilterTypes.GENERAL_TYPE, 5)
    SixType = (FilterTypes.GENERAL_TYPE, 6)
    SevenType = (FilterTypes.GENERAL_TYPE, 7)
    EightType = (FilterTypes.GENERAL_TYPE, 8)
    NineType = (FilterTypes.GENERAL_TYPE, 9)
    TenType = (FilterTypes.GENERAL_TYPE, 10)
    ElevenType = (FilterTypes.GENERAL_TYPE, 11)
    TwelveType = (FilterTypes.GENERAL_TYPE, 12)
    ThirteenType = (FilterTypes.GENERAL_TYPE, 13)
    # Profession
    AllProfession = (FilterTypes.PROFESSION_TYPE, 0)
    OneProfession = (FilterTypes.PROFESSION_TYPE, 1)
    TwoProfession = (FilterTypes.PROFESSION_TYPE, 2)
    ThreeProfession = (FilterTypes.PROFESSION_TYPE, 3)
    FourProfession = (FilterTypes.PROFESSION_TYPE, 4)
    FiveProfession = (FilterTypes.PROFESSION_TYPE, 5)
    SixProfession = (FilterTypes.PROFESSION_TYPE, 6)
    SevenProfession = (FilterTypes.PROFESSION_TYPE, 7)
    EightProfession = (FilterTypes.PROFESSION_TYPE, 8)
    # Video length filters
    AllLength = (FilterTypes.LENGTH_TYPE, 0)
    OneLength = (FilterTypes.LENGTH_TYPE, 1)
    TwoLength = (FilterTypes.LENGTH_TYPE, 2)
    ThreeLength = (FilterTypes.LENGTH_TYPE, 3)
    FourLength = (FilterTypes.LENGTH_TYPE, 4)
    # Video added before filters
    AllAddedBefore = (FilterTypes.ADDED_BEFORE_TYPE, 0)
    OneAddedBefore = (FilterTypes.ADDED_BEFORE_TYPE, 1)
    TwoAddedBefore = (FilterTypes.ADDED_BEFORE_TYPE, 2)
    ThreeAddedBefore = (FilterTypes.ADDED_BEFORE_TYPE, 3)
    FourAddedBefore = (FilterTypes.ADDED_BEFORE_TYPE, 4)
    FiveAddedBefore = (FilterTypes.ADDED_BEFORE_TYPE, 5)
    SixAddedBefore = (FilterTypes.ADDED_BEFORE_TYPE, 6)
    # Video added before filters
    AllDate = (FilterTypes.DATE_TYPE, 0)
    OneDate = (FilterTypes.DATE_TYPE, 1)
    TwoDate = (FilterTypes.DATE_TYPE, 2)
    ThreeDate = (FilterTypes.DATE_TYPE, 3)
    FourDate = (FilterTypes.DATE_TYPE, 4)
    FiveDate = (FilterTypes.DATE_TYPE, 5)
    SixDate = (FilterTypes.DATE_TYPE, 6)
    # Quality filters
    AllQuality = (FilterTypes.QUALITY_TYPE, 0)
    SDQuality = (FilterTypes.QUALITY_TYPE, 1)
    HDQuality = (FilterTypes.QUALITY_TYPE, 2)
    UHDQuality = (FilterTypes.QUALITY_TYPE, 3)
    VRQuality = (FilterTypes.QUALITY_TYPE, 4)
    # Rating filters
    AllRating = (FilterTypes.RATING_TYPE, 0)
    OneRating = (FilterTypes.RATING_TYPE, 1)
    TwoRating = (FilterTypes.RATING_TYPE, 2)
    ThreeRating = (FilterTypes.RATING_TYPE, 3)
    FourRating = (FilterTypes.RATING_TYPE, 4)
    # Comments filters
    AllComments = (FilterTypes.COMMENTS_TYPE, 0)
    OneComments = (FilterTypes.COMMENTS_TYPE, 1)
    TwoComments = (FilterTypes.COMMENTS_TYPE, 2)
    ThreeComments = (FilterTypes.COMMENTS_TYPE, 3)
    FourComments = (FilterTypes.COMMENTS_TYPE, 4)
    # Sort order filters
    DateOrder = (FilterTypes.SORT_ORDER_TYPE, 0)
    LengthOrder = (FilterTypes.SORT_ORDER_TYPE, 1)
    LengthOrder2 = (FilterTypes.SORT_ORDER_TYPE, 2)
    RatingOrder = (FilterTypes.SORT_ORDER_TYPE, 3)
    ViewsOrder = (FilterTypes.SORT_ORDER_TYPE, 4)
    PopularityOrder = (FilterTypes.SORT_ORDER_TYPE, 5)
    PopularityOrder2 = (FilterTypes.SORT_ORDER_TYPE, 6)
    CommentsOrder = (FilterTypes.SORT_ORDER_TYPE, 7)
    RelevanceOrder = (FilterTypes.SORT_ORDER_TYPE, 8)
    AlphabeticOrder = (FilterTypes.SORT_ORDER_TYPE, 9)
    NumberOfVideosOrder = (FilterTypes.SORT_ORDER_TYPE, 10)
    NumberOfGalleriesOrder = (FilterTypes.SORT_ORDER_TYPE, 11)
    DownloadsOrder = (FilterTypes.SORT_ORDER_TYPE, 12)
    QualityOrder = (FilterTypes.SORT_ORDER_TYPE, 13)
    FavorOrder = (FilterTypes.SORT_ORDER_TYPE, 14)
    VideosPopularityOrder = (FilterTypes.SORT_ORDER_TYPE, 15)
    VideosRatingOrder = (FilterTypes.SORT_ORDER_TYPE, 16)
    RecommendedOrder = (FilterTypes.SORT_ORDER_TYPE, 17)
    BestOrder = (FilterTypes.SORT_ORDER_TYPE, 18)
    TrendingOrder = (FilterTypes.SORT_ORDER_TYPE, 19)
    SubscribersOrder = (FilterTypes.SORT_ORDER_TYPE, 20)
    RandomOrder = (FilterTypes.SORT_ORDER_TYPE, 21)
    FeaturedOrder = (FilterTypes.SORT_ORDER_TYPE, 22)
    # Country filters
    AfghanistanCountry = (FilterTypes.COUNTRY_TYPE, 0)
    AlbaniaCountry = (FilterTypes.COUNTRY_TYPE, 1)
    AlgeriaCountry = (FilterTypes.COUNTRY_TYPE, 2)
    AndorraCountry = (FilterTypes.COUNTRY_TYPE, 3)
    AngolaCountry = (FilterTypes.COUNTRY_TYPE, 4)
    AntiguaAndDepsCountry = (FilterTypes.COUNTRY_TYPE, 5)
    ArgentinaCountry = (FilterTypes.COUNTRY_TYPE, 6)
    ArmeniaCountry = (FilterTypes.COUNTRY_TYPE, 7)
    AustraliaCountry = (FilterTypes.COUNTRY_TYPE, 8)
    AustriaCountry = (FilterTypes.COUNTRY_TYPE, 9)
    AzerbaijanCountry = (FilterTypes.COUNTRY_TYPE, 10)
    BahamasCountry = (FilterTypes.COUNTRY_TYPE, 11)
    BahrainCountry = (FilterTypes.COUNTRY_TYPE, 12)
    BangladeshCountry = (FilterTypes.COUNTRY_TYPE, 13)
    BarbadosCountry = (FilterTypes.COUNTRY_TYPE, 14)
    BelarusCountry = (FilterTypes.COUNTRY_TYPE, 15)
    BelgiumCountry = (FilterTypes.COUNTRY_TYPE, 16)
    BelizeCountry = (FilterTypes.COUNTRY_TYPE, 17)
    BeninCountry = (FilterTypes.COUNTRY_TYPE, 18)
    BhutanCountry = (FilterTypes.COUNTRY_TYPE, 19)
    BoliviaCountry = (FilterTypes.COUNTRY_TYPE, 20)
    BosniaHerzegovinaCountry = (FilterTypes.COUNTRY_TYPE, 21)
    BotswanaCountry = (FilterTypes.COUNTRY_TYPE, 22)
    BrazilCountry = (FilterTypes.COUNTRY_TYPE, 23)
    BruneiCountry = (FilterTypes.COUNTRY_TYPE, 24)
    BulgariaCountry = (FilterTypes.COUNTRY_TYPE, 25)
    BurkinaCountry = (FilterTypes.COUNTRY_TYPE, 26)
    BurundiCountry = (FilterTypes.COUNTRY_TYPE, 27)
    CambodiaCountry = (FilterTypes.COUNTRY_TYPE, 28)
    CameroonCountry = (FilterTypes.COUNTRY_TYPE, 29)
    CanadaCountry = (FilterTypes.COUNTRY_TYPE, 30)
    CapeVerdeCountry = (FilterTypes.COUNTRY_TYPE, 31)
    CentralAfricanRepCountry = (FilterTypes.COUNTRY_TYPE, 32)
    ChadCountry = (FilterTypes.COUNTRY_TYPE, 33)
    ChileCountry = (FilterTypes.COUNTRY_TYPE, 34)
    ChinaCountry = (FilterTypes.COUNTRY_TYPE, 35)
    ColombiaCountry = (FilterTypes.COUNTRY_TYPE, 36)
    ComorosCountry = (FilterTypes.COUNTRY_TYPE, 37)
    CongoCountry = (FilterTypes.COUNTRY_TYPE, 38)
    CongoDemocraticRepCountry = (FilterTypes.COUNTRY_TYPE, 39)
    CostaRicaCountry = (FilterTypes.COUNTRY_TYPE, 40)
    CroatiaCountry = (FilterTypes.COUNTRY_TYPE, 41)
    CubaCountry = (FilterTypes.COUNTRY_TYPE, 42)
    CyprusCountry = (FilterTypes.COUNTRY_TYPE, 43)
    CzechRepublicCountry = (FilterTypes.COUNTRY_TYPE, 44)
    DenmarkCountry = (FilterTypes.COUNTRY_TYPE, 45)
    DjiboutiCountry = (FilterTypes.COUNTRY_TYPE, 46)
    DominicaCountry = (FilterTypes.COUNTRY_TYPE, 47)
    DominicanRepublicCountry = (FilterTypes.COUNTRY_TYPE, 48)
    EastTimorCountry = (FilterTypes.COUNTRY_TYPE, 49)
    EcuadorCountry = (FilterTypes.COUNTRY_TYPE, 50)
    EgyptCountry = (FilterTypes.COUNTRY_TYPE, 51)
    ElSalvadorCountry = (FilterTypes.COUNTRY_TYPE, 52)
    EquatorialGuineaCountry = (FilterTypes.COUNTRY_TYPE, 53)
    EritreaCountry = (FilterTypes.COUNTRY_TYPE, 54)
    EstoniaCountry = (FilterTypes.COUNTRY_TYPE, 55)
    EthiopiaCountry = (FilterTypes.COUNTRY_TYPE, 56)
    FijiCountry = (FilterTypes.COUNTRY_TYPE, 57)
    FinlandCountry = (FilterTypes.COUNTRY_TYPE, 58)
    FranceCountry = (FilterTypes.COUNTRY_TYPE, 59)
    GabonCountry = (FilterTypes.COUNTRY_TYPE, 60)
    GambiaCountry = (FilterTypes.COUNTRY_TYPE, 61)
    GeorgiaCountry = (FilterTypes.COUNTRY_TYPE, 62)
    GermanyCountry = (FilterTypes.COUNTRY_TYPE, 63)
    GhanaCountry = (FilterTypes.COUNTRY_TYPE, 64)
    GreeceCountry = (FilterTypes.COUNTRY_TYPE, 65)
    GrenadaCountry = (FilterTypes.COUNTRY_TYPE, 66)
    GuatemalaCountry = (FilterTypes.COUNTRY_TYPE, 67)
    GuineaCountry = (FilterTypes.COUNTRY_TYPE, 68)
    GuineaBissauCountry = (FilterTypes.COUNTRY_TYPE, 69)
    GuyanaCountry = (FilterTypes.COUNTRY_TYPE, 70)
    HaitiCountry = (FilterTypes.COUNTRY_TYPE, 71)
    HondurasCountry = (FilterTypes.COUNTRY_TYPE, 72)
    HungaryCountry = (FilterTypes.COUNTRY_TYPE, 73)
    IcelandCountry = (FilterTypes.COUNTRY_TYPE, 74)
    IndiaCountry = (FilterTypes.COUNTRY_TYPE, 75)
    IndonesiaCountry = (FilterTypes.COUNTRY_TYPE, 76)
    IranCountry = (FilterTypes.COUNTRY_TYPE, 77)
    IraqCountry = (FilterTypes.COUNTRY_TYPE, 78)
    IrelandRepublicCountry = (FilterTypes.COUNTRY_TYPE, 79)
    IsraelCountry = (FilterTypes.COUNTRY_TYPE, 80)
    ItalyCountry = (FilterTypes.COUNTRY_TYPE, 81)
    IvoryCoastCountry = (FilterTypes.COUNTRY_TYPE, 82)
    JamaicaCountry = (FilterTypes.COUNTRY_TYPE, 83)
    JapanCountry = (FilterTypes.COUNTRY_TYPE, 84)
    JordanCountry = (FilterTypes.COUNTRY_TYPE, 85)
    KazakhstanCountry = (FilterTypes.COUNTRY_TYPE, 86)
    KenyaCountry = (FilterTypes.COUNTRY_TYPE, 87)
    KiribatiCountry = (FilterTypes.COUNTRY_TYPE, 88)
    KoreaNorthCountry = (FilterTypes.COUNTRY_TYPE, 89)
    KoreaSouthCountry = (FilterTypes.COUNTRY_TYPE, 90)
    KosovoCountry = (FilterTypes.COUNTRY_TYPE, 91)
    KuwaitCountry = (FilterTypes.COUNTRY_TYPE, 92)
    KyrgyzstanCountry = (FilterTypes.COUNTRY_TYPE, 93)
    LaosCountry = (FilterTypes.COUNTRY_TYPE, 94)
    LatviaCountry = (FilterTypes.COUNTRY_TYPE, 95)
    LebanonCountry = (FilterTypes.COUNTRY_TYPE, 96)
    LesothoCountry = (FilterTypes.COUNTRY_TYPE, 97)
    LiberiaCountry = (FilterTypes.COUNTRY_TYPE, 98)
    LibyaCountry = (FilterTypes.COUNTRY_TYPE, 99)
    LiechtensteinCountry = (FilterTypes.COUNTRY_TYPE, 100)
    LithuaniaCountry = (FilterTypes.COUNTRY_TYPE, 101)
    LuxembourgCountry = (FilterTypes.COUNTRY_TYPE, 102)
    MacedoniaCountry = (FilterTypes.COUNTRY_TYPE, 103)
    MadagascarCountry = (FilterTypes.COUNTRY_TYPE, 104)
    MalawiCountry = (FilterTypes.COUNTRY_TYPE, 105)
    MalaysiaCountry = (FilterTypes.COUNTRY_TYPE, 106)
    MaldivesCountry = (FilterTypes.COUNTRY_TYPE, 107)
    MaliCountry = (FilterTypes.COUNTRY_TYPE, 108)
    MaltaCountry = (FilterTypes.COUNTRY_TYPE, 109)
    MarshallIslandsCountry = (FilterTypes.COUNTRY_TYPE, 110)
    MauritaniaCountry = (FilterTypes.COUNTRY_TYPE, 111)
    MauritiusCountry = (FilterTypes.COUNTRY_TYPE, 112)
    MexicoCountry = (FilterTypes.COUNTRY_TYPE, 113)
    MicronesiaCountry = (FilterTypes.COUNTRY_TYPE, 114)
    MoldovaCountry = (FilterTypes.COUNTRY_TYPE, 115)
    MonacoCountry = (FilterTypes.COUNTRY_TYPE, 116)
    MongoliaCountry = (FilterTypes.COUNTRY_TYPE, 117)
    MontenegroCountry = (FilterTypes.COUNTRY_TYPE, 118)
    MoroccoCountry = (FilterTypes.COUNTRY_TYPE, 119)
    MozambiqueCountry = (FilterTypes.COUNTRY_TYPE, 120)
    MyanmarBurmaCountry = (FilterTypes.COUNTRY_TYPE, 121)
    NamibiaCountry = (FilterTypes.COUNTRY_TYPE, 122)
    NauruCountry = (FilterTypes.COUNTRY_TYPE, 123)
    NepalCountry = (FilterTypes.COUNTRY_TYPE, 124)
    NetherlandsCountry = (FilterTypes.COUNTRY_TYPE, 125)
    NewZealandCountry = (FilterTypes.COUNTRY_TYPE, 126)
    NicaraguaCountry = (FilterTypes.COUNTRY_TYPE, 127)
    NigerCountry = (FilterTypes.COUNTRY_TYPE, 128)
    NigeriaCountry = (FilterTypes.COUNTRY_TYPE, 129)
    NorwayCountry = (FilterTypes.COUNTRY_TYPE, 130)
    OmanCountry = (FilterTypes.COUNTRY_TYPE, 131)
    PakistanCountry = (FilterTypes.COUNTRY_TYPE, 132)
    PalauCountry = (FilterTypes.COUNTRY_TYPE, 133)
    PanamaCountry = (FilterTypes.COUNTRY_TYPE, 134)
    PapuaNewGuineaCountry = (FilterTypes.COUNTRY_TYPE, 135)
    ParaguayCountry = (FilterTypes.COUNTRY_TYPE, 136)
    PeruCountry = (FilterTypes.COUNTRY_TYPE, 137)
    PhilippinesCountry = (FilterTypes.COUNTRY_TYPE, 138)
    PolandCountry = (FilterTypes.COUNTRY_TYPE, 139)
    PortugalCountry = (FilterTypes.COUNTRY_TYPE, 140)
    QatarCountry = (FilterTypes.COUNTRY_TYPE, 141)
    RomaniaCountry = (FilterTypes.COUNTRY_TYPE, 142)
    RussianFederationCountry = (FilterTypes.COUNTRY_TYPE, 143)
    RwandaCountry = (FilterTypes.COUNTRY_TYPE, 144)
    StKittsAndNevisCountry = (FilterTypes.COUNTRY_TYPE, 145)
    StLuciaCountry = (FilterTypes.COUNTRY_TYPE, 146)
    SaintVincentAndTheGrenadinesCountry = (FilterTypes.COUNTRY_TYPE, 147)
    SamoaCountry = (FilterTypes.COUNTRY_TYPE, 148)
    SanMarinoCountry = (FilterTypes.COUNTRY_TYPE, 149)
    SaoTomeAndPrincipeCountry = (FilterTypes.COUNTRY_TYPE, 150)
    SaudiArabiaCountry = (FilterTypes.COUNTRY_TYPE, 151)
    SenegalCountry = (FilterTypes.COUNTRY_TYPE, 152)
    SerbiaCountry = (FilterTypes.COUNTRY_TYPE, 153)
    SeychellesCountry = (FilterTypes.COUNTRY_TYPE, 154)
    SierraLeoneCountry = (FilterTypes.COUNTRY_TYPE, 155)
    SingaporeCountry = (FilterTypes.COUNTRY_TYPE, 156)
    SlovakiaCountry = (FilterTypes.COUNTRY_TYPE, 157)
    SloveniaCountry = (FilterTypes.COUNTRY_TYPE, 158)
    SolomonIslandsCountry = (FilterTypes.COUNTRY_TYPE, 159)
    SomaliaCountry = (FilterTypes.COUNTRY_TYPE, 160)
    SouthAfricaCountry = (FilterTypes.COUNTRY_TYPE, 161)
    SouthSudanCountry = (FilterTypes.COUNTRY_TYPE, 162)
    SpainCountry = (FilterTypes.COUNTRY_TYPE, 163)
    SriLankaCountry = (FilterTypes.COUNTRY_TYPE, 164)
    SudanCountry = (FilterTypes.COUNTRY_TYPE, 165)
    SurinameCountry = (FilterTypes.COUNTRY_TYPE, 166)
    SwazilandCountry = (FilterTypes.COUNTRY_TYPE, 167)
    SwedenCountry = (FilterTypes.COUNTRY_TYPE, 168)
    SwitzerlandCountry = (FilterTypes.COUNTRY_TYPE, 169)
    SyriaCountry = (FilterTypes.COUNTRY_TYPE, 170)
    TaiwanCountry = (FilterTypes.COUNTRY_TYPE, 171)
    TajikistanCountry = (FilterTypes.COUNTRY_TYPE, 172)
    TanzaniaCountry = (FilterTypes.COUNTRY_TYPE, 173)
    ThailandCountry = (FilterTypes.COUNTRY_TYPE, 174)
    TogoCountry = (FilterTypes.COUNTRY_TYPE, 175)
    TongaCountry = (FilterTypes.COUNTRY_TYPE, 176)
    TrinidadAndTobagoCountry = (FilterTypes.COUNTRY_TYPE, 177)
    TunisiaCountry = (FilterTypes.COUNTRY_TYPE, 178)
    TurkeyCountry = (FilterTypes.COUNTRY_TYPE, 179)
    TurkmenistanCountry = (FilterTypes.COUNTRY_TYPE, 180)
    TuvaluCountry = (FilterTypes.COUNTRY_TYPE, 181)
    UgandaCountry = (FilterTypes.COUNTRY_TYPE, 182)
    UkraineCountry = (FilterTypes.COUNTRY_TYPE, 183)
    UnitedArabEmiratesCountry = (FilterTypes.COUNTRY_TYPE, 184)
    UnitedKingdomCountry = (FilterTypes.COUNTRY_TYPE, 185)
    UnitedStatesCountry = (FilterTypes.COUNTRY_TYPE, 186)
    UruguayCountry = (FilterTypes.COUNTRY_TYPE, 187)
    UzbekistanCountry = (FilterTypes.COUNTRY_TYPE, 188)
    VanuatuCountry = (FilterTypes.COUNTRY_TYPE, 189)
    VaticanCityCountry = (FilterTypes.COUNTRY_TYPE, 190)
    VenezuelaCountry = (FilterTypes.COUNTRY_TYPE, 191)
    VietnamCountry = (FilterTypes.COUNTRY_TYPE, 192)
    YemenCountry = (FilterTypes.COUNTRY_TYPE, 193)
    ZambiaCountry = (FilterTypes.COUNTRY_TYPE, 194)
    ZimbabweCountry = (FilterTypes.COUNTRY_TYPE, 195)


class CatalogNoValuesError(LookupError):
    def __init__(self, value):
        super(CatalogNoValuesError, self).__init__(value)
        self.value = IdGenerator.id_to_original_str(value)

    def __str__(self):
        return repr('Found no results for the id {id}.'.format(id=self.value))


class CatalogMoreThanOneValueError(LookupError):
    def __init__(self, value):
        super(CatalogMoreThanOneValueError, self).__init__(value)
        self.value = IdGenerator.id_to_original_str(value)

    def __str__(self):
        return repr('Found more than 1 results for the id {id}.'.format(id=self.value))


class CatalogNoSubObjectsError(LookupError):
    def __init__(self, value):
        super(CatalogNoSubObjectsError, self).__init__(value)
        self.value = IdGenerator.id_to_original_str(value)

    def __str__(self):
        return repr('The object {id} has no sub objects!.'.format(id=self.value))


class CatalogNoAdditionalObjectsError(LookupError):
    def __init__(self, value):
        super(CatalogNoAdditionalObjectsError, self).__init__(value)
        self.value = IdGenerator.id_to_original_str(value)

    def __str__(self):
        return repr('The object {id} has no additional objects!.'.format(id=self.value))


class CatalogManager(object):
    def __init__(self, session_id, data_dir):
        """
        C'tor.
        :param session_id: Session id (In case the current session data is stored, it will be loaded at the
        construction).
        :param data_dir: Data dir.
        """
        self.session_id = session_id
        if not path.isdir(data_dir):
            makedirs(data_dir)
        self.store_filename = path.join(data_dir, 'catalog.dat')
        if path.isfile(self.store_filename):
            try:
                with open(self.store_filename, 'rb') as fl:
                    self.store_data = pickle.load(fl)
            except EOFError:
                self.store_data = {}
            if self.session_id in self.store_data:
                self._nodes = self.store_data[self.session_id]
            else:
                self._init_store_data()

        else:
            self._init_store_data()

    def __exit__(self):
        """
        Destructor.
        :return:
        """
        self.save_store_data()

    def _init_store_data(self):
        """
        Initializes the store data
        :return:
        """
        self._nodes = {}
        self.store_data = {self.session_id: self._nodes}
        self.save_store_data()

    def save_store_data(self):
        """
        Saves the store data
        :return:
        """
        with open(self.store_filename, 'wb') as fl:
            pickle.dump(self.store_data, fl)

    def get_node(self, node_id, coded=False):
        """
        Searches for the node in the db and fetches it.
        :param node_id: Node id.
        :param coded: Flag that indicates whether the node_id was already coded or not. False by defaut.
        :return: Node (CatalogNode object).
        """
        if coded is False:
            node_id = IdGenerator.make_id(node_id)
        return self._nodes[node_id]

    def is_node(self, node_id, coded=False):
        """
        Checks whether the given node is found in our db.
        :param node_id: Node id.
        :param coded: Flag that indicates whether the node_id was already coded or not. False by defaut.
        :return: Boolean value.
        """
        if coded is False:
            node_id = IdGenerator.make_id(node_id)
        return node_id in self._nodes

    def add_node(self, node):
        """
        Searches for the node in the db and fetches it.
        :param node: Node (CatalogNode object).
        :return: None
        """
        self._nodes[node.id] = node

    def remove_node(self, node_id, coded=False):
        """
        Removes the given node.
        :param node_id: Remove node id.
        :param coded: Flag that indicates whether the node_id was already coded or not. False by defaut.
        :return: None
        """
        if coded is False:
            node_id = IdGenerator.make_id(node_id)
        self._nodes.pop(node_id)
        # self._save_store_data()


class CatalogNode(object):
    metaclass = ABCMeta
    _additional_page_object_ids = []

    @property
    @abstractmethod
    def _false_object_types(self):
        raise NotImplementedError

    def __init__(self, catalog_manager, obj_id, title, number=None, page_number=None, url=None, image_link=None,
                 poster_link=None, related_objects=None, sub_objects=None, super_object=None,
                 subtitle=None, description=None, duration=None, date=None,
                 object_type=None, additional_data=None, raw_data=None):
        """
        Initializes the main properties.
        :param catalog_manager:
        :param obj_id:
        :param title:
        :param number:
        :param page_number:
        :param url:
        :param image_link:
        :param poster_link :
        :param related_objects:
        :param sub_objects:
        :param super_object:
        :param subtitle:
        :param description:
        :param duration:
        :param date:
        :param object_type:
        :param additional_data:
        :param raw_data:
        """
        self.catalog_manager = catalog_manager
        self.id = IdGenerator.make_id(obj_id)
        self.title = title
        self.number = number
        self.page_number = page_number
        self.url = url
        self.image_link = image_link
        self.poster_link = poster_link
        self.related_objects = related_objects
        self._sub_object_ids = [x.id for x in sub_objects] if sub_objects is not None else None
        self._super_object_id = super_object.id if super_object is not None else None
        self.subtitle = subtitle
        self.description = description
        self.duration = duration
        self.date = date
        self.object_type = object_type
        self.additional_data = additional_data
        self.raw_data = raw_data

        # Adds the node to the manager after the initialization
        self.catalog_manager.add_node(self)

    @property
    def super_object(self):
        return self.catalog_manager.get_node(self._super_object_id, True) \
            if self._super_object_id is not None else None

    @property
    def true_object(self):
        true_object = self
        while true_object.object_type in self._false_object_types:
            true_object = true_object.super_object
            if true_object is None:
                raise RuntimeError('Cannot fetch true object type!')
        return true_object

    @property
    def sub_objects(self):
        if self._sub_object_ids is None:
            return None
        return [self.catalog_manager.get_node(x, True) for x in self._sub_object_ids]

    def add_sub_objects(self, sub_objects):
        """
        Adds additional objects to the current object.
        :param sub_objects: list of CatalogNode.
        :return:
        """
        if len(sub_objects) == 0:
            return None
        if self._sub_object_ids is None:
            self._sub_object_ids = []
        self._sub_object_ids.extend((x.id for x in sub_objects if x.id not in self._sub_object_ids))

    def clear_sub_objects(self):
        """
        Removes all the sub objects.
        :return:
        """
        self._sub_object_ids = None

    def add_additional_objects(self, additional_objects):
        """
        Adds additional objects to the current object.
        Note that the fields Number must be int, since it is used as page indicator.
        :param additional_objects: list of CatalogNode.
        :return:
        """
        if len(additional_objects) == 0:
            return None
        if self._additional_page_object_ids is None:
            self._additional_page_object_ids = []
        if self.page_number is None:
            self.page_number = 1

        for additional_object in additional_objects:
            additional_object._additional_page_object_ids = \
                [self.id] + self._additional_page_object_ids + \
                [x.id for x in additional_objects if x.id != additional_object.id]
            if (
                    self.super_object.sub_objects is None or
                    additional_object.id not in (x.id for x in self.super_object.sub_objects)
            ):
                self.super_object.add_sub_objects([additional_object])
        self._additional_page_object_ids.extend([x.id for x in additional_objects])

    def clear_additional_objects(self):
        """
        Removes all the additional objects.
        :return:
        """
        self._additional_page_object_ids = None

    def search_sub_object(self, sub_object_id):
        """
        Searches with the sub ojbect with the given ID. In case no such object was found, proper error will be thrown.
        :param sub_object_id: Search object id.
        :return: Search sub-object.
        """
        if self.sub_objects is None:
            raise CatalogNoSubObjectsError(self.id)
        fit_objects = [x for x in self._sub_object_ids if sub_object_id == x]
        if len(fit_objects) == 0:
            raise CatalogNoValuesError(sub_object_id)
        elif len(fit_objects) > 1:
            raise CatalogMoreThanOneValueError(sub_object_id)
        return self.catalog_manager.get_node(fit_objects[0], True)

    def set_super_object(self, super_object):
        """
        Sets a new super object
        :param super_object: VideoNode object or None
        :return:
        """
        if super_object is None:
            self._super_object_id = None
        else:
            self._super_object_id = super_object.id
            if self.catalog_manager.is_node(super_object.id, True) is False:
                # todo: to take care of updating the catalog manager (could be different ones)...
                self.catalog_manager.add_node(super_object)

    def get_full_id_path(self):
        """
        Returns the ids of all the nodes in the tree (including the current object's).
        :return: List of ids.
        """
        ids = [self.id]
        tmp_super_object = self.super_object
        while tmp_super_object is not None:
            ids.append(tmp_super_object.id)
            tmp_super_object = tmp_super_object.super_object
        ids = ids[::-1]
        return ids[1:]
        # return ids

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if self.__dict__.keys() != other.__dict__.keys():
            return False
        return all(v == other.__dict__[k] for k, v in self.__dict__.items())

    def __hash__(self):
        return hash(self.id)

    # def __repr__(self):
    #     return '\n'.join('{k}: {v}'.format(k=k, v=v) for k, v in self.__dict__.items())


class VideoSource(object):
    __video_types = list(VideoTypes)

    def __init__(self, link, video_type=VideoTypes.VIDEO_REGULAR, quality=None, resolution=None, fps=None, codec=None,
                 size=None):
        self.link = link
        if video_type not in self.__video_types:
            raise TypeError('Video type must be one of the {s}.'.format(s=self.__video_types))
        self.video_type = video_type
        self.quality = int(quality) if quality is not None else None
        self.resolution = int(resolution) if resolution is not None else None
        self.fps = int(fps) if fps is not None else None
        self.codec = codec
        self.size = size

    def __repr__(self):
        return ', '.join(['{k}: {v}'.format(k=k, v=v) for (k, v) in self.__dict__.items()])

    __str__ = __repr__


class VideoNode(object):
    def __init__(self, video_sources, raw_data=None, cookies=None, headers=None, params=None, json=None,
                 query_data=None, subtitles=None, verify=True):
        """
        C'tor.
        :param video_sources:
        :param raw_data:
        :param cookies:
        :param headers:
        :param params:
        :param json:
        :param query_data:
        :param subtitles:
        """
        if any(type(x) is not VideoSource for x in video_sources):
            raise TypeError('All video_link objects must be VideoSource objects.')
        self.video_sources = video_sources
        self.raw_data = raw_data
        self.cookies = cookies
        self.headers = headers
        self.params = params
        self.json = json
        self.query_data = query_data
        self.subtitles = subtitles
        self.verify = verify


class VideoFilterObject(object):
    def __init__(self, filter_id, filter_title, filter_value):
        self.filter_id = filter_id
        self.title = filter_title
        self.value = filter_value


# class VideoFilterCondition(object):
#     def __init__(self, filter_type, filter_possible_ids):
#         self.filter_type = filter_type
#         self.filter_possible_ids = filter_possible_ids


class FilterStructure(object):
    _filter_order = ('general_filters', 'length_filters', 'added_before_filters', 'period_filters',
                     'quality_filters', 'rating_filters', 'comments_filters', 'profession_filters', 'sort_order')

    @property
    def general(self):
        return self.__filter_mapping[FilterTypes.GENERAL_TYPE]

    @property
    def profession(self):
        return self.__filter_mapping[FilterTypes.PROFESSION_TYPE]

    @property
    def length(self):
        return self.__filter_mapping[FilterTypes.LENGTH_TYPE]

    @property
    def added_before(self):
        return self.__filter_mapping[FilterTypes.ADDED_BEFORE_TYPE]

    @property
    def period(self):
        return self.__filter_mapping[FilterTypes.DATE_TYPE]

    @property
    def quality(self):
        return self.__filter_mapping[FilterTypes.QUALITY_TYPE]

    @property
    def rating(self):
        return self.__filter_mapping[FilterTypes.RATING_TYPE]

    @property
    def comments(self):
        return self.__filter_mapping[FilterTypes.COMMENTS_TYPE]

    @property
    def sort_order(self):
        return self.__filter_mapping[FilterTypes.SORT_ORDER_TYPE]

    def __init__(self, general_filters=None, length_filters=None, added_before_filters=None, period_filters=None,
                 quality_filters=None, rating_filters=None, profession_filters=None, comments_filters=None,
                 sort_order=None):
        self.__filter_mapping = {
            FilterTypes.GENERAL_TYPE: general_filters,
            FilterTypes.PROFESSION_TYPE: profession_filters,
            FilterTypes.LENGTH_TYPE: length_filters,
            FilterTypes.ADDED_BEFORE_TYPE: added_before_filters,
            FilterTypes.DATE_TYPE: period_filters,
            FilterTypes.QUALITY_TYPE: quality_filters,
            FilterTypes.RATING_TYPE: rating_filters,
            FilterTypes.COMMENTS_TYPE: comments_filters,
            FilterTypes.SORT_ORDER_TYPE: sort_order,
            # FilterTypes.COUNTRY_TYPE: 9,
        }

    def __getitem__(self, item):
        return self.__filter_mapping[item]

    def __setitem__(self, key, value):
        self.__filter_mapping[key] = value

    def __repr__(self):
        return ', '.join(('{k}: {v}'.format(k=x, v=self[x].filter_id)
                          for x in sorted(self, key=lambda x: x.value)))

    def __iter__(self):
        return self.__filter_mapping.__iter__()


class VideoFilter(object):
    # _filter_order = ('general_filters', 'length_filters', 'added_before_filters', 'period_filters',
    #                  'quality_filters', 'rating_filters', 'comments_filters', 'profession_filters', 'sort_order')

    def __init__(self, data_dir, filename=None, general_filters=None, length_filters=None, added_before_filters=None,
                 period_filters=None, quality_filters=None, rating_filters=None, comments_filters=None,
                 profession_filters=None, sort_order=None):
        """
        C'tor.
        :param data_dir: Store directory.
        :param filename: Store filename. None by default, in this case the name filters.dat will be used.
        :param general_filters: Type filter. List of tuples of (filter_id, filter_title, filter_value).
        :param length_filters: List of tuples of (filter_id, filter_title, filter_value).
        :param added_before_filters: List of tuples of (filter_id, filter_title, filter_value).
        :param period_filters: List of tuples of (filter_id, filter_title, filter_value).
        :param quality_filters: List of tuples of (filter_id, filter_title, filter_value).
        :param rating_filters: List of tuples of (filter_id, filter_title, filter_value).
        :param comments_filters: List of tuples of (filter_id, filter_title, filter_value).
        :param profession_filters: List of tuples of (filter_id, filter_title, filter_value).
        :param sort_order: List of tuples of (filter_id, filter_title, filter_value).
        """
        if filename is None:
            filename = 'filters.dat'
        self.store_filename = path.join(data_dir, filename)
        init_data = True
        try:
            if path.isfile(self.store_filename):
                with open(self.store_filename, 'rb') as fl:
                    self._filters, self._current_filter_values, self._conditions = pickle.load(fl)
                init_data = False
        except EOFError:
            init_data = True
        if init_data is True:
            raw_data = self._prepare_input(general_filters, length_filters, added_before_filters,
                                           period_filters, quality_filters, rating_filters, comments_filters,
                                           profession_filters, sort_order)
            self._filters = \
                FilterStructure(**{x: {v[0]: VideoFilterObject(*v) for v in y[0]} for x, y in raw_data.items()})
            self._current_filter_values = \
                FilterStructure(**{x: VideoFilterObject(*y[0][0]) for x, y in raw_data.items()})
            self._conditions = \
                FilterStructure(**{x: FilterStructure(**{v[0]: v[1] for v in y[1]}) for x, y in raw_data.items()})

            with open(self.store_filename, 'wb') as fl:
                pickle.dump((self._filters, self._current_filter_values, self._conditions), fl)

    def _prepare_input(self, general_filters=None, length_filters=None, added_before_filters=None,
                       period_filters=None, quality_filters=None, rating_filters=None, comments_filters=None,
                       profession_filters=None, sort_order=None):
        raw_data = {'general_filters': self._initialize_filter_input(general_filters)
                    if general_filters is not None
                    else ([(BaseFilterTypes.AllType, 'Any types', None)], tuple()),
                    'length_filters': self._initialize_filter_input(length_filters)
                    if length_filters is not None
                    else ([(BaseFilterTypes.AllLength, 'Any duration', None)], tuple()),
                    'added_before_filters': self._initialize_filter_input(added_before_filters)
                    if added_before_filters is not None
                    else ([(BaseFilterTypes.AllAddedBefore, 'Any added before periods', None)], tuple()),
                    'period_filters': self._initialize_filter_input(period_filters)
                    if period_filters is not None
                    else ([(BaseFilterTypes.AllDate, 'Any date', None)], tuple()),
                    'quality_filters': self._initialize_filter_input(quality_filters)
                    if quality_filters is not None
                    else ([(BaseFilterTypes.AllQuality, 'Any qualities', None)], tuple()),
                    'rating_filters': self._initialize_filter_input(rating_filters)
                    if rating_filters is not None
                    else ([(BaseFilterTypes.AllRating, 'Any ratings', None)], tuple()),
                    'comments_filters': self._initialize_filter_input(comments_filters)
                    if comments_filters is not None
                    else ([(BaseFilterTypes.AllComments, 'Any comments', None)], tuple()),
                    'profession_filters': self._initialize_filter_input(profession_filters)
                    if profession_filters is not None
                    else ([(BaseFilterTypes.AllProfession, 'Any profession', None)], tuple()),
                    'sort_order': self._initialize_filter_input(sort_order)
                    if sort_order is not None
                    else ([(BaseFilterTypes.DateOrder, 'Sort by date', None)], tuple()),
                    }
        return raw_data

    @property
    def filters(self):
        return self._filters

    @property
    def conditions(self):
        return self._conditions

    @property
    def current_filters(self):
        return self._current_filter_values

    def set_current_filter(self, filter_obj, filter_type):
        """
        Sets new filter value and saves the data file.
        :param filter_obj: Filter object we want to update (ont of FilterStructure attributes).
        :param filter_type: Type of the new filter. Must be within the indices of available filters.
        :return:
        """
        self._current_filter_values[filter_obj] = self._filters[filter_obj][filter_type]
        with open(self.store_filename, 'wb') as fl:
            pickle.dump((self._filters, self._current_filter_values, self._conditions), fl)

    @staticmethod
    def _initialize_filter_input(filter_input):
        """
        Receives filter input and prepares it in the right output to fit the filters and conditions structures
        :param filter_input: Can be either tuple of
        (tuple of (filter_id, filter_title, filter_value), tuple of (filter_type, list of possible filter_ids))
        or just tuple of (filter_id, filter_title, filter_value).
        :return: (tuple of (filter_id, filter_title, filter_value), tuple of (filter_type, list of possible filter_ids))
        """
        if (
                len(filter_input) == 2 and
                all(type(x) in (list, tuple) and len(x) == 3 for x in filter_input[0]) and
                all(type(x) in (list, tuple) and len(x) == 2 for x in filter_input[1])
        ):
            return filter_input
        elif all(len(x) == 3 for x in filter_input):
            return filter_input, tuple()
        else:
            raise ValueError('Wrong structure of filter input!')

    def __repr__(self):
        return repr(self._current_filter_values)

    def current_filters_text(self):
        return ', '.join(('{k}: {v}'.format(k=x, v=self._current_filter_values[x].filter_id)
                          for x in sorted(self._current_filter_values, key=lambda x: x.value)
                          if len(self._filters[x]) > 1))

    def __iter__(self):
        return iter((x for x in self._filters if len(self._filters[x]) > 1))
