from .base_catalog import *


class PornCategoryTypes(Enum):
    GENERAL_CATEGORY = 0
    MAIN_CATEGORY = 1
    SECONDARY_CATEGORY = 2
    VIDEO_CATEGORY = 3
    LIVE_VIDEO_CATEGORY = 4


# Main page categories
class PornCategories(CategoryEnum):
    # Copy from PornCategories :(
    PAGE = (PornCategoryTypes.GENERAL_CATEGORY, 0)
    VIDEO = (PornCategoryTypes.GENERAL_CATEGORY, 1)
    VIDEO_PAGE = (PornCategoryTypes.GENERAL_CATEGORY, 2)
    SEARCH_MAIN = (PornCategoryTypes.GENERAL_CATEGORY, 3)
    SEARCH_PAGE = (PornCategoryTypes.GENERAL_CATEGORY, 4)
    GENERAL_MAIN = (PornCategoryTypes.GENERAL_CATEGORY, 5)
    LIVE_VIDEO = (PornCategoryTypes.GENERAL_CATEGORY, 6)
    LIVE_SCHEDULE = (PornCategoryTypes.GENERAL_CATEGORY, 7)

    CATEGORY_MAIN = (PornCategoryTypes.MAIN_CATEGORY, 0)
    PORN_STAR_MAIN = (PornCategoryTypes.MAIN_CATEGORY, 1)
    CHANNEL_MAIN = (PornCategoryTypes.MAIN_CATEGORY, 2)
    TAG_MAIN = (PornCategoryTypes.MAIN_CATEGORY, 3)
    ACTRESS_MAIN = (PornCategoryTypes.MAIN_CATEGORY, 4)

    # Personal page categories
    CATEGORY = (PornCategoryTypes.SECONDARY_CATEGORY, 0)
    PORN_STAR = (PornCategoryTypes.SECONDARY_CATEGORY, 1)
    CHANNEL = (PornCategoryTypes.SECONDARY_CATEGORY, 2)
    TAG = (PornCategoryTypes.SECONDARY_CATEGORY, 3)
    ACTRESS = (PornCategoryTypes.SECONDARY_CATEGORY, 4)

    # General video categories
    LATEST_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 0)
    MOST_VIEWED_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 1)
    TOP_RATED_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 2)
    POPULAR_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 3)
    LONGEST_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 4)
    HD_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 5)
    ALL_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 6)
    MOST_DISCUSSED_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 7)
    # LIVE_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 8)
    RECOMMENDED_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 9)
    HOTTEST_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 10)
    RANDOM_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 11)
    INTERESTING_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 12)
    TRENDING_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 13)
    UPCOMING_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 14)
    ORGASMIC_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 15)
    USER_UPLOADED_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 16)
    FAVORITE_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 17)
    VERIFIED_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 18)
    BEING_WATCHED_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 19)
    MOST_DOWNLOADED_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 20)
    MOST_WATCHED_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 21)
    FULL_MOVIE_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 22)
    SHORTEST_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 23)
    RELEVANT_VIDEO = (PornCategoryTypes.VIDEO_CATEGORY, 24)
    # Live modes
    JUST_LOGGED_IN_VIDEO = (PornCategoryTypes.LIVE_VIDEO_CATEGORY, 0)
    NEW_MODEL_VIDEO = (PornCategoryTypes.LIVE_VIDEO_CATEGORY, 1)


PORN_VIDEO_CATEGORIES = (PornCategories.LATEST_VIDEO, PornCategories.MOST_VIEWED_VIDEO, PornCategories.TOP_RATED_VIDEO,
                         PornCategories.POPULAR_VIDEO, PornCategories.LONGEST_VIDEO, PornCategories.HD_VIDEO,
                         PornCategories.ALL_VIDEO, PornCategories.MOST_DISCUSSED_VIDEO, PornCategories.LIVE_VIDEO,
                         PornCategories.RECOMMENDED_VIDEO, PornCategories.HOTTEST_VIDEO, PornCategories.RANDOM_VIDEO,
                         PornCategories.INTERESTING_VIDEO, PornCategories.TRENDING_VIDEO,
                         PornCategories.UPCOMING_VIDEO, PornCategories.ORGASMIC_VIDEO,
                         PornCategories.USER_UPLOADED_VIDEO, PornCategories.FAVORITE_VIDEO,
                         PornCategories.VERIFIED_VIDEO, PornCategories.BEING_WATCHED_VIDEO,
                         PornCategories.MOST_DOWNLOADED_VIDEO, PornCategories.MOST_WATCHED_VIDEO,
                         PornCategories.FULL_MOVIE_VIDEO, PornCategories.SHORTEST_VIDEO,
                         PornCategories.JUST_LOGGED_IN_VIDEO, PornCategories.NEW_MODEL_VIDEO,
                         )


# Types
class PornFilterTypes(CategoryEnum):
    # Copy from PornCategories :(
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
    FourteenType = (FilterTypes.GENERAL_TYPE, 14)
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
    SevenDate = (FilterTypes.DATE_TYPE, 7)
    EightDate = (FilterTypes.DATE_TYPE, 8)
    NineDate = (FilterTypes.DATE_TYPE, 9)
    # Quality filters
    AllQuality = (FilterTypes.QUALITY_TYPE, 0)
    SDQuality = (FilterTypes.QUALITY_TYPE, 1)
    HDQuality = (FilterTypes.QUALITY_TYPE, 2)
    UHDQuality = (FilterTypes.QUALITY_TYPE, 3)
    VRQuality = (FilterTypes.QUALITY_TYPE, 4)
    R270Quality = (FilterTypes.QUALITY_TYPE, 5)
    R360Quality = (FilterTypes.QUALITY_TYPE, 6)
    R540Quality = (FilterTypes.QUALITY_TYPE, 7)
    R720Quality = (FilterTypes.QUALITY_TYPE, 8)
    R1080Quality = (FilterTypes.QUALITY_TYPE, 9)
    R2160Quality = (FilterTypes.QUALITY_TYPE, 10)
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
    RatingOrder2 = (FilterTypes.SORT_ORDER_TYPE, 4)
    ViewsOrder = (FilterTypes.SORT_ORDER_TYPE, 5)
    PopularityOrder = (FilterTypes.SORT_ORDER_TYPE, 6)
    PopularityOrder2 = (FilterTypes.SORT_ORDER_TYPE, 7)
    CommentsOrder = (FilterTypes.SORT_ORDER_TYPE, 8)
    RelevanceOrder = (FilterTypes.SORT_ORDER_TYPE, 9)
    AlphabeticOrder = (FilterTypes.SORT_ORDER_TYPE, 10)
    AlphabeticOrder2 = (FilterTypes.SORT_ORDER_TYPE, 11)
    NumberOfVideosOrder = (FilterTypes.SORT_ORDER_TYPE, 12)
    NumberOfGalleriesOrder = (FilterTypes.SORT_ORDER_TYPE, 13)
    DownloadsOrder = (FilterTypes.SORT_ORDER_TYPE, 14)
    QualityOrder = (FilterTypes.SORT_ORDER_TYPE, 15)
    FavorOrder = (FilterTypes.SORT_ORDER_TYPE, 16)
    VideosPopularityOrder = (FilterTypes.SORT_ORDER_TYPE, 17)
    VideosRatingOrder = (FilterTypes.SORT_ORDER_TYPE, 18)
    RecommendedOrder = (FilterTypes.SORT_ORDER_TYPE, 19)
    BestOrder = (FilterTypes.SORT_ORDER_TYPE, 20)
    TrendingOrder = (FilterTypes.SORT_ORDER_TYPE, 21)
    SubscribersOrder = (FilterTypes.SORT_ORDER_TYPE, 22)
    RandomOrder = (FilterTypes.SORT_ORDER_TYPE, 23)
    FeaturedOrder = (FilterTypes.SORT_ORDER_TYPE, 24)
    BeingWatchedOrder = (FilterTypes.SORT_ORDER_TYPE, 25)
    HottestOrder = (FilterTypes.SORT_ORDER_TYPE, 26)
    VotesOrder = (FilterTypes.SORT_ORDER_TYPE, 27)
    ClicksOrder = (FilterTypes.SORT_ORDER_TYPE, 28)
    TwitterFollowersOrder = (FilterTypes.SORT_ORDER_TYPE, 29)
    InterestOrder = (FilterTypes.SORT_ORDER_TYPE, 30)
    UpcomingOrder = (FilterTypes.SORT_ORDER_TYPE, 31)
    OrgasmicOrder = (FilterTypes.SORT_ORDER_TYPE, 32)
    UserVideosOrder = (FilterTypes.SORT_ORDER_TYPE, 33)
    DateAddedOrder = (FilterTypes.SORT_ORDER_TYPE, 34)
    ChannelViewsOrder = (FilterTypes.SORT_ORDER_TYPE, 35)
    HDOrder = (FilterTypes.SORT_ORDER_TYPE, 36)
    LiveOrder = (FilterTypes.SORT_ORDER_TYPE, 37)
    LoginOrder = (FilterTypes.SORT_ORDER_TYPE, 38)
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

    StraightType = OneType
    GayType = TwoType
    ShemaleType = ThreeType
    LesbianType = FourType
    CartoonType = FiveType
    MemberType = SixType
    GirlType = SevenType
    GuyType = EightType
    OtherType = NineType
    FunnyType = TenType
    ExtremeType = ElevenType
    AmateurType = TwelveType
    CoupleType = ThirteenType
    NewType = FourteenType

    # Professions
    PornStarProfession = OneProfession
    ActorProfession = TwoProfession
    AdultModelProfession = ThreeProfession
    CenterfoldProfession = FourProfession
    MusicianProfession = FiveProfession
    SportsmenProfession = SixProfession
    SupermodelProfession = SevenProfession
    TVHostProfession = EightProfession


class PornCatalogNode(CatalogNode):
    @property
    def _false_object_types(self):
        return PornCategories.PAGE, PornCategories.VIDEO_PAGE, PornCategories.SEARCH_PAGE


class PornCatalogPageNode(PornCatalogNode):
    pass


class PornCatalogVideoPageNode(PornCatalogNode):
    def __init__(self, catalog_manager, obj_id, title, number=None, page_number=None, url=None, image_link=None,
                 poster_link=None, related_objects=None, sub_objects=None, super_object=None,
                 subtitle=None, description=None, duration=None, date=None,
                 object_type=None, additional_data=None, raw_data=None,
                 flip_images_link=None, preview_video_link=None, is_hd=None, resolution=None,
                 pos_rating=None, neg_rating=None, rating=None, number_of_views=None, number_of_likes=None,
                 number_of_comments=None, added_before=None, is_vr=None
                 ):
        """
        C'tor
        :param catalog_manager:
        :param obj_id:
        :param title:
        :param number:
        :param page_number:
        :param url:
        :param image_link:
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
        :param flip_images_link:
        :param preview_video_link:
        :param is_hd:
        :param resolution:
        :param pos_rating:
        :param neg_rating:
        :param rating:
        :param number_of_views:
        :param number_of_likes:
        :param number_of_comments:
        :param added_before:
        :param is_vr:
        """
        super(PornCatalogVideoPageNode, self).__init__(catalog_manager, obj_id, title, number, page_number, url,
                                                       image_link, poster_link, related_objects,
                                                       sub_objects, super_object,
                                                       subtitle, description, duration, date,
                                                       object_type, additional_data, raw_data)
        self.flip_images_link = flip_images_link
        self.preview_video_link = preview_video_link
        self.is_hd = is_hd
        self.resolution = resolution
        self.pos_rating = pos_rating
        self.neg_rating = neg_rating
        self.rating = rating
        self.number_of_views = number_of_views
        self.number_of_likes = number_of_likes
        self.number_of_comments = number_of_comments
        self.added_before = added_before
        self.is_vr = is_vr


class PornCatalogMainCategoryNode(PornCatalogNode):
    def __init__(self, catalog_manager, obj_id, title, number=None, page_number=None, url=None, image_link=None,
                 poster_link=None, related_objects=None, sub_objects=None, super_object=None,
                 subtitle=None, description=None, duration=None, date=None,
                 object_type=None, additional_data=None, raw_data=None,
                 number_of_videos=None, number_of_photos=None, number_of_views=None, number_of_subscribers=None,
                 rating=None, preview_video_link=None,
                 ):
        """
        C'tor
        :param catalog_manager:
        :param obj_id:
        :param title:
        :param number:
        :param page_number:
        :param url:
        :param image_link:
        :param poster_link:
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
        :param number_of_videos:
        :param number_of_photos:
        :param number_of_views:
        :param number_of_subscribers:
        :param rating:
        :param preview_video_link:
        """
        super(PornCatalogMainCategoryNode, self).__init__(catalog_manager, obj_id, title, number, page_number, url,
                                                          image_link, poster_link, related_objects,
                                                          sub_objects, super_object,
                                                          subtitle, description, duration,
                                                          date, object_type, additional_data, raw_data)
        self.number_of_videos = number_of_videos
        self.number_of_photos = number_of_photos
        self.number_of_views = number_of_views
        self.number_of_subscribers = number_of_subscribers
        self.rating = rating
        self.preview_video_link = preview_video_link


class PornCatalogCategoryNode(PornCatalogMainCategoryNode):
    pass


class PornFilter(object):
    def __init__(self, data_dir, general_args=None, categories_args=None, tags_args=None, porn_stars_args=None,
                 actresses_args=None, channels_args=None,
                 single_category_args=None, single_tag_args=None, single_porn_star_args=None, single_actress_args=None,
                 single_channel_args=None, video_args=None, search_args=None):
        if general_args is None:
            general_args = {}

        if categories_args is None:
            categories_args = {}

        if tags_args is None:
            tags_args = {}

        if porn_stars_args is None:
            porn_stars_args = {}

        if actresses_args is None:
            actresses_args = {}

        if channels_args is None:
            channels_args = {}

        if single_category_args is None:
            single_category_args = {}

        if single_tag_args is None:
            single_tag_args = {}

        if single_porn_star_args is None:
            single_porn_star_args = {}

        if single_actress_args is None:
            single_actress_args = {}

        if single_channel_args is None:
            single_channel_args = {}

        if video_args is None:
            video_args = {}

        if search_args is None:
            search_args = {}

        self.__filters = {
            PornCategories.GENERAL_MAIN: VideoFilter(data_dir, 'general_filters.dat', **general_args),
            PornCategories.CATEGORY_MAIN: VideoFilter(data_dir, 'categories_filters.dat', **categories_args),
            PornCategories.TAG_MAIN: VideoFilter(data_dir, 'tags_filters.dat', **tags_args),
            PornCategories.PORN_STAR_MAIN: VideoFilter(data_dir, 'porn_stars_filters.dat', **porn_stars_args),
            PornCategories.ACTRESS_MAIN: VideoFilter(data_dir, 'actresses_filters.dat', **actresses_args),
            PornCategories.CHANNEL_MAIN: VideoFilter(data_dir, 'channels_filters.dat', **channels_args),
            PornCategories.CATEGORY: VideoFilter(data_dir, 'single_category_filters.dat', **single_category_args),
            PornCategories.TAG: VideoFilter(data_dir, 'single_tag_filters.dat', **single_tag_args),
            PornCategories.PORN_STAR: VideoFilter(data_dir, 'single_porn_stars_filters.dat', **single_porn_star_args),
            PornCategories.ACTRESS: VideoFilter(data_dir, 'single_actress_filters.dat', **single_actress_args),
            PornCategories.CHANNEL: VideoFilter(data_dir, 'single_channel_filters.dat', **single_channel_args),
            PornCategories.VIDEO_PAGE: VideoFilter(data_dir, 'video_page_filters.dat', **video_args),
            PornCategories.VIDEO: VideoFilter(data_dir, 'video_filters.dat', **{}),
            PornCategories.SEARCH_MAIN: VideoFilter(data_dir, 'search_filters.dat', **search_args),
        }

    def __getitem__(self, item):
        return self.__filters[item]

    def __setitem__(self, key, value):
        self.__filters[key] = value

    def __iter__(self):
        return iter(k for k, v in self.__filters.items() if len([x for x in v]) > 0)

    def __repr__(self):
        return '\n'.join(['{k}: {v}'.format(k=k, v=self.__filters[k]) for k in self])
