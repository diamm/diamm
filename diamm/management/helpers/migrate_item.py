from diamm.models.migrate.legacy_item import LegacyItem
from diamm.models.data.item import Item
from diamm.models.data.item_note import ItemNote
from diamm.models.data.source import Source
from diamm.models.data.composition import Composition
from blessings import Terminal

term = Terminal()


def empty_items():
    print(term.magenta("\tEmptying item table"))
    Item.objects.all().delete()


def __clear_aggregate_compositions():
    print(term.magenta("\tClearing aggregate compositions"))
    Composition.objects.filter(name="works by").delete()


def migrate_item(entry):
    print(term.green("\tMigrating composition {0} in source {1} with Item ID {2}".format(entry.compositionkey,
                                                                                         entry.sourcekey,
                                                                                         entry.pk)))
    source_pk = entry.sourcekey
    source = Source.objects.get(pk=source_pk)

    # This is a special 'composition' that says that it's a post-1550 source.
    # If that's the case, we'll skip adding this composition to the source
    # and simply set a flag on the source that no inventory has been provided.
    if entry.compositionkey == 0:
        print(term.red('\t\tMarking the inventory as not provided.'))
        source.inventory_provided = False
        source.save()

    composition = None
    aggregate_composer = None
    composition_pk = entry.compositionkey
    orig_composition = None

    if composition_pk not in (0, 69332, 54681, 69558, 79920, 888888, 999999):
        orig_composition = Composition.objects.get(pk=composition_pk)

    if orig_composition and orig_composition.name == "works by":
        print(term.magenta('\tCreating aggregate composer entry.'))
        # we have an aggregate entry. An aggregate composition should only
        # have one composer attached.
        aggregate_composer = orig_composition.composers.all()[0].composer
    else:
        composition = orig_composition

    layout = None
    if layout == "score":
        layout = Item.L_SCORE
    elif layout == "parts":
        layout = Item.L_PARTS

    d = {
        'id': entry.pk,
        'source': source,
        'composition': composition,
        'aggregate_composer': aggregate_composer,
        'folio_start': entry.folio_start,
        'folio_end': entry.folio_end,
        'source_attribution': entry.composeroriginal,
        'source_incipit': entry.incipittranscription,
        'layout': layout,
        # 'num_voices': entry.novoices  # TODO: Fix this in Filemaker to be Integers...
        'legacy_position_ms': entry.positionms,
    }

    it = Item(**d)
    it.save()

    note_fields = (
        (ItemNote.I_GENERAL_NOTE, entry.notes),
        (ItemNote.I_COPYING_STYLE, entry.copyingstyle),
        (ItemNote.I_CONCORDANCES, entry.concordances),
        (ItemNote.I_LEGACY_LAYOUT, entry.layout),
        (ItemNote.I_LEGACY_VOICES, entry.novoices),
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


def migrate():
    print(term.blue("Migrating Items"))
    empty_items()
    for entry in LegacyItem.objects.all():
        migrate_item(entry)

    __clear_aggregate_compositions()
    print(term.blue("Done migrating items"))
