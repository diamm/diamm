import psycopg2 as psql
from django.conf import settings
from django.db.models import Q
from diamm.models.migrate.legacy_item import LegacyItem
from diamm.models.migrate.legacy_item_image import LegacyItemImage
from diamm.models.data.item import Item
from diamm.models.data.item_note import ItemNote
from diamm.models.data.item_composer import ItemComposer
from diamm.models.data.source import Source
from diamm.models.data.composition import Composition
from diamm.management.helpers.utilities import remove_leading_zeroes
from diamm.management.helpers.migrate_composition import COMPOSITIONS_TO_SKIP
from blessings import Terminal

term = Terminal()

# Composition keys that don't actually point to compositions, but to composition place-holders.
# BAD_COMPOSITION_KEYS = (0, 69332, 54681, 69558, 79920, 888888, 999999, 87464)
NON_COMPOSITION_KEYS = {1024, 1025,1049,12333,12335,12336,12338,12339,12340,12790,13128,13149,13168,13179,13323,13324,13325,13340,13475,13481,13681,13684,13968,14044,14190,14191,14192,14193,14194,14198,14200,14201,14203,14204,14205,14206,14208,14209,14210,14226,14242,14336,14337,14338,14521,14786,14846,14880,14907,14959,14962,14963,14966,15223,15228,15257,1536,15697,15769,15920,16159,16181,16187,16193,16459,16502,16552,16554,16742,16743,16744,16751,16752,16941,16953,17149,17150,17151,17152,17162,17163,17165,17174,17176,17177,17186,17202,17215,17689,17691,17717,17946,17947,18289,19065,19083,19110,19154,19156,19157,19186,19574,19579,19588,19592,19623,19624,19631,19635,19653,19654,19669,19708,19710,19718,19721,19727,19728,19730,19735,19739,19741,19746,19747,19749,19753,19755,19860,1988,19985,20069,20074,20075,20076,20077,20078,20079,20080,20081,20097,2010,2012,20156,20158,20159,20160,20162,2070,20754,20916,20921,21118,2113,2114,2115,2143,21676,21972,22251,22252,22255,22258,22275,22387,22389,22390,22392,22432,22603,22703,22708,22713,22715,22716,22717,22720,22857,22862,22994,22996,23019,23020,23021,23025,23163,23164,23384,2339,23414,23415,23417,23418,23455,23460,23482,23492,23629,23630,23637,23644,23657,23663,23664,23668,23669,23676,23677,23710,23761,23828,23829,23844,24881,24892,24893,24894,24896,24898,24906,24908,24910,24912,24913,24918,24919,24921,24926,24931,24933,24936,24937,24938,24940,24943,24944,24945,24946,24947,24948,24951,25060,25076,25079,25080,25090,25091,25104,25105,25110,25222,25234,25236,25490,25909,25917,25988,26028,265,26647,2687,27144,27246,27249,27713,27715,27723,27724,27725,27778,27780,27796,27823,27856,27875,27876,27946,27967,28264,28265,28266,28267,28268,28269,28271,28272,28273,28274,28275,28276,28277,28278,28280,28281,28282,28283,28284,28285,28286,28287,28288,28289,28291,28292,28293,28294,28295,28487,28504,28657,28658,28663,29104,29115,29279,29280,29282,29286,29287,29288,29292,29396,29399,29577,30423,30459,30461,30467,30468,30469,30470,30471,30472,30476,30477,30995,31306,31391,31555,31727,31870,32234,32290,32291,32292,32294,32295,32296,32297,32298,32299,32300,32301,32302,32303,32304,32305,32306,32307,32308,32309,32310,32312,32313,32314,32315,32317,32318,32319,32320,32321,32323,32324,32327,32328,32331,32332,32333,32334,32335,32336,32352,32353,32354,32355,32356,32357,32358,32359,32360,32361,32362,32364,32365,32366,32367,32368,32369,32370,32371,32372,32373,32374,32377,32378,32379,32380,32381,32382,32383,32384,32385,32386,32387,32388,32389,32390,32391,32392,32393,32394,32395,32396,32397,32398,32399,32400,32401,32402,32403,32404,32405,32406,32407,32408,32409,32410,32411,32412,32413,32414,32415,32416,32417,32418,32419,32420,32421,32422,32423,32424,32425,32426,32427,32428,32430,32431,32432,32433,32434,32435,32436,32437,32438,32439,32440,32441,32442,32443,32444,32445,32446,32448,32455,32456,32457,32459,32460,32462,32465,32466,32467,32468,32486,32487,32488,32489,32490,32491,32492,32493,32494,3296,33009,33381,33762,33832,34490,35262,35928,35959,36011,36310,36786,36838,36911,36931,36932,37181,37182,37183,37193,37200,37201,37208,37209,37220,37221,37237,37240,37245,37246,37250,37251,37253,37255,37256,37257,37258,37259,37260,37261,37262,37267,37268,37269,37270,37271,37277,37278,37279,37281,37282,37283,37284,37285,37286,37287,37288,37289,37290,37291,37294,37295,37296,37297,37298,37299,37300,37301,37304,37306,37307,37308,37309,37312,37313,37314,37315,37316,37319,37320,37321,37322,37323,37324,37328,37346,37347,37366,37411,37436,37437,37438,37439,37440,37441,37442,37443,37444,37445,37446,37447,37448,37449,37450,37451,37452,37453,37454,37455,37456,37457,37465,37468,37471,37472,37473,37474,37475,37476,37477,37479,37480,37482,37794,37897,37899,37902,37904,37906,37907,37908,37913,37916,37917,37925,37939,37953,37977,37979,37994,37999,38000,38001,38002,38003,38004,38005,38006,38007,38010,38019,38025,38090,38118,38119,38120,38121,38122,38154,38156,38158,38160,38161,38162,38163,38164,38165,38166,38167,38168,38169,38170,38171,38172,38173,38174,38175,38176,38177,38228,38229,38230,38231,38232,38233,38234,38235,38236,38269,38270,38271,38272,38273,38274,38324,38325,38363,38366,38422,38423,38424,38511,38558,38692,38889,38904,38975,38982,39676,40144,40145,40146,40147,40165,40166,40167,40168,40169,40170,40171,40199,40204,40207,40208,40209,40472,40476,40477,40478,40479,40480,40481,40482,40483,40484,40485,40486,40487,40488,40489,40491,40492,40494,40495,40496,40497,40499,40500,40501,40502,40504,40505,40506,40507,40508,40509,40513,40515,40516,40517,40518,40519,40522,40524,40525,40527,40529,40530,40531,40535,40536,40537,40538,40539,40540,40541,40542,40543,40545,40546,40547,40548,40549,40550,40551,40552,40558,40559,40560,40561,40562,40563,40564,40566,40568,40569,40570,40571,40572,40573,40574,40575,40576,40577,40578,40579,40580,40583,40585,40586,40588,40591,40592,40593,40595,40597,40598,40599,40602,40605,40606,40607,40608,40609,40610,40611,40612,40613,40614,40615,40616,40617,40618,40619,40621,40622,40623,40624,40625,40626,40627,40628,40629,40630,40631,40632,40633,40634,40640,40641,40646,40648,40651,40653,40655,40658,40660,40661,40663,40664,40665,40666,40667,40668,40669,40671,40677,40679,40680,40681,40682,40683,40684,40686,40688,40689,40691,40693,40694,40695,40696,40697,40702,40703,40872,40873,40875,40876,40943,40946,42240,42242,42244,42246,42247,42249,42250,42252,42254,42255,42256,42262,42287,42289,42290,42293,42294,42295,42296,42297,42299,42301,42310,42311,43177,5027,5104,5113,5114,5116,5118,5131,5133,5135,5145,5147,5149,5150,5151,5152,5172,5176,5179,5180,52292,5231,52337,52338,53614,53671,53839,53845,53851,53857,53865,53875,54062,54101,54174,54247,54400,54458,54641,54683,54698,54699,54700,54704,54705,54706,54857,54860,54861,54864,54881,54882,54896,54899,54910,55120,55169,55170,55205,55254,55579,55580,55584,55587,55591,55592,55593,55606,55629,55638,55646,55648,55654,55657,55660,55664,55665,55667,55669,55671,5731,61063,61229,61421,61607,61623,61629,62134,66461,66553,6687,67294,67295,67296,67297,67317,67319,67326,67327,67368,67375,67382,67386,67391,67394,67439,67447,67449,67454,68214,68218,68222,68251,68482,68745,68764,69149,69154,69156,69158,69159,69160,69163,69164,69165,69169,69170,69267,69278,69285,69303,69309,69314,69315,69318,69319,69321,69322,69323,69326,69327,69328,69331,69353,69354,69357,69359,69376,69381,69394,69396,69401,69402,69409,69410,69418,69440,69449,69452,69460,69470,69567,69576,69581,69582,69648,69724,69725,69749,69750,69752,69857,69923,69926,69928,69930,69937,69938,69947,69949,69950,69951,69953,71540,73261,73312,73318,73319,775,79927,842,843,844,85452,85713,85755,85755,85763,85763,85764,85764,85958,85959,85960,85965,85971,85972,85973,85979,86048,86050,86093,86096,86263,86264,8634,86343,86357,86366,86368,86381,86621,86664,86673,86676,86677,86678,86681,86685,86861,86908,87024,87029,87042,87191,87192,87193,87194,87195,87197,87200,87202,87203,87204,87205,87213,87214,87217,87223,87229,87231,87234,87236,87330,87331,87343,87353,87365,87367,87378,87394,87396,87398,87402,87404,87405,87410,87496,87497,87498,87499,87500,87502,87503,87504,87505,87506,87507,87508,87510,87514,87515,87522,87524,87528,8770,87735,87736,87737,87823,87943,87959,88044,88045,88047,88098,88099,88170,88251,88428,88429,88431,88433,88435,88454,88467,88468,88473,88476,88477,88478,88524,88538,88594,88608,88700,88701,88725,88737,88773,89027,9265}

aggregate_titles = ("work(s) by",
                    "works by",
                    "1 work",
                    "1 - 3 works",
                    "2 works",
                    "2 + ?1 works",
                    "3 works",
                    "3 work",
                    "4 works",
                    "5 works",
                    "6 work",
                    "6 works",
                    "7 works",
                    "8 works",
                    "9 works",
                    "10 works",
                    "11 works",
                    "11+?1 works",
                    "12 works",
                    "13 works",
                    "14 works",
                    "18 works",
                    "20 works",
                    "21 works",
                    "22 works",
                    "45 works",
                    "30 works",
                    "37 work")


def empty_items():
    print(term.magenta("\tEmptying item and notes tables"))
    ItemComposer.objects.all().delete()
    ItemNote.objects.all().delete()
    Item.objects.all().delete()


def clear_aggregate_compositions():
    print(term.magenta("\tClearing aggregate compositions"))
    Composition.objects.filter(title__in=aggregate_titles).delete()


def migrate_item(entry):
    print(term.green("\tMigrating composition {0} in source {1} with Item ID {2}".format(entry.compositionkey,
                                                                                         entry.sourcekey,
                                                                                         entry.pk)))
    source_pk = entry.sourcekey
    source = Source.objects.get(pk=source_pk)

    # This will stop any composition placeholders from being added to the item table.
    # We'll skip adding this composition to the source
    # and simply set a flag on the source that no inventory has been provided.
    if entry.compositionkey in COMPOSITIONS_TO_SKIP:
        print(term.red('\t\tMarking the inventory as not provided.'))
        source.inventory_provided = False
        source.save()
        # Prevent the migration from creating a new item for this record.
        return None

    layout = None
    if layout == "score":
        layout = Item.L_SCORE
    elif layout == "parts":
        layout = Item.L_PARTS

    d = {
        'id': entry.pk,
        'source': source,
        'folio_start': remove_leading_zeroes(entry.folio_start),
        'folio_end': remove_leading_zeroes(entry.folio_end),
        'source_attribution': entry.composeroriginal,
        'source_incipit': entry.incipittranscription,
        'layout': layout,
        'num_voices': entry.novoices,
        'legacy_position_ms': entry.positionms,
        'page_order': entry.positionpage if entry.positionpage else 0
    }

    it = Item(**d)
    it.save()

    composition = None
    composition_pk = None
    if entry.compositionkey:
        composition_pk = int(entry.compositionkey)
    orig_composition = None

    if Composition.objects.filter(pk=composition_pk).count() > 0:
        orig_composition = Composition.objects.get(pk=composition_pk)

    # print(orig_composition)
    # print(entry.compositionkey in NON_COMPOSITION_KEYS)

    if orig_composition and entry.compositionkey in NON_COMPOSITION_KEYS:
        # This is a non-composition index entry (e.g., an index page, illumination, etc.). It should
        # not be linked to the composition (because that says "index" and is not a real composition) but
        # should be titled.
        # import pdb
        # pdb.set_trace()

        print(term.red("\t\tCreating a non-composition index entry."))
        it.item_title = orig_composition.title
        it.legacy_composition = "legacy_composition.{0}".format(int(orig_composition.pk))
        it.save()

        # we can delete the composition now.
        orig_composition.delete()

    elif orig_composition and orig_composition.title in aggregate_titles:
        # If the composition is a 'filler' one that meant to stand in for one or more
        # listed but un-titled works in the source, we will instead shift the
        # composer to being an 'item composer entry' and not join the original 'composition'
        # to the source.
        print(term.magenta('\tCreating non-work composer entries.'))
        # we have an aggregate entry, and iterate through the CompositionComposer objects.
        for composer in orig_composition.composers.all():
            # store the original title ("4 works") in a note.
            note = orig_composition.title
            if composer.notes:
                note = "{0}\n{1}".format(note, composer.notes)

            icd = {
                'item': it,
                'composer': composer.composer,
                'note': orig_composition.title,
                'uncertain': composer.uncertain
            }
            ic = ItemComposer(**icd)
            ic.save()
    else:
        it.composition = orig_composition
        it.save()

    note_fields = (
        (ItemNote.GENERAL_NOTE, entry.notes),
        (ItemNote.COPYING_STYLE, entry.copyingstyle),
        (ItemNote.CONCORDANCES, entry.concordances),
        (ItemNote.LAYOUT, entry.layout)
    )

    for nt in note_fields:
        if not nt[1]:
            continue
        d = {
            'type': nt[0],
            'note': nt[1],
            'item': it
        }
        itn = ItemNote(**d)
        itn.save()

    # Migrate the position note from the item image table.
    itemimages = LegacyItemImage.objects.filter(pk=entry.pk, positiononpage__isnull=False)
    for entry in itemimages:
        d = {
            'type': ItemNote.POSITION,
            'note': entry.positiononpage,
            'item': it
        }
        itmn = ItemNote(**d)
        itmn.save()


def update_table():
    print(term.yellow("\tUpdating the ID sequences for the Django Item Table"))
    sql_max = "SELECT MAX(id) AS maxid FROM diamm_data_item;"
    sql_alt = "ALTER SEQUENCE diamm_data_item_id_seq RESTART WITH %s"
    db = settings.DATABASES['default']
    conn = psql.connect(database=db['NAME'],
                        user=db['USER'],
                        password=db['PASSWORD'],
                        host=db['HOST'],
                        port=db['PORT'],
                        cursor_factory=psql.extras.DictCursor)
    curs = conn.cursor()
    curs.execute(sql_max)
    maxid = curs.fetchone()['maxid']
    nextid = maxid + 1
    curs.execute(sql_alt, (nextid,))


def migrate():
    print(term.blue("Migrating Items"))
    empty_items()

    for entry in LegacyItem.objects.filter(sourcekey__isnull=False).order_by('itemkey'):
        migrate_item(entry)

    clear_aggregate_compositions()
    update_table()
    print(term.blue("Done migrating items"))


# Only run after a migration if you need to update these things.
def update_item_voices():
    legacy_items = LegacyItem.objects.filter(novoices__isnull=False)
    for v in legacy_items:
        print("Updating item {0}".format(v.pk))
        try:
            item = Item.objects.get(pk=v.pk)
        except Item.DoesNotExist:
            print('This item does not exist')
            continue

        item.num_voices = v.novoices
        item.save()


def update_item_notes():
    # Clear all item notes before re-importing.
    ItemNote.objects.all().delete()

    legacy_items = LegacyItem.objects.filter(Q(notes__isnull=False) | Q(copyingstyle__isnull=False) | \
                                             Q(concordances__isnull=False) | Q(layout__isnull=False))

    for entry in legacy_items:
        print("Updating item {0}".format(entry.pk))
        note_fields = (
            (ItemNote.GENERAL_NOTE, entry.notes),
            (ItemNote.COPYING_STYLE, entry.copyingstyle),
            (ItemNote.CONCORDANCES, entry.concordances),
            (ItemNote.LAYOUT, entry.layout)
        )

        try:
            item = Item.objects.get(pk=entry.pk)
        except Item.DoesNotExist:
            print('This item does not exist')
            continue

        for nt in note_fields:
            if not nt[1]:
                continue
            d = {
                'type': nt[0],
                'note': nt[1],
                'item': item
            }
            itn = ItemNote(**d)
            itn.save()

    for entry in LegacyItemImage.objects.filter(positiononpage__isnull=False):
        print("Updating item {0}".format(entry.pk))
        try:
            item = Item.objects.get(pk=entry.pk)
        except Item.DoesNotExist:
            print('This item does not exist')
            continue

        d = {
            'type': ItemNote.POSITION,
            'note': entry.positiononpage,
            'item': item
        }
        itmn = ItemNote(**d)
        itmn.save()


