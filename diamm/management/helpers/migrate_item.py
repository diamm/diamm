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
from blessings import Terminal

term = Terminal()

aggregate_titles = ("works by",
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

    # This is a special 'composition' that says that it's a post-1550 source.
    # If that's the case, we'll skip adding this composition to the source
    # and simply set a flag on the source that no inventory has been provided.
    if entry.compositionkey in (0, 79920):
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
        'folio_start': entry.folio_start,
        'folio_end': entry.folio_end,
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
    composition_pk = entry.compositionkey
    orig_composition = None

    if composition_pk not in (0, 69332, 54681, 69558, 79920, 888888, 999999):
        orig_composition = Composition.objects.get(pk=composition_pk)

    # If the composition is a 'filler' one that meant to stand in for one or more
    # listed but un-titled works in the source, we will instead shift the
    # composer to being an 'item composer entry' and not join the original 'composition'
    # to the source.
    if orig_composition and orig_composition.title in aggregate_titles:
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
    for entry in LegacyItem.objects.all():
        migrate_item(entry)

    clear_aggregate_compositions()
    update_table()
    print(term.blue("Done migrating items"))


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


