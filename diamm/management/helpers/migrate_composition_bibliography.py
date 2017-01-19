from diamm.models.migrate.legacy_bibliography_composition import LegacyBibliographyComposition
from diamm.models.data.bibliography import Bibliography
from diamm.models.data.composition import Composition
from diamm.models.data.item import Item
from diamm.models.data.composition_bibliography import CompositionBibliography
from diamm.models.data.item_bibliography import ItemBibliography
from blessings import Terminal

term = Terminal()


def empty_composition_bibliography():
    print(term.magenta("\tEmptying Composition Bibliography"))
    CompositionBibliography.objects.all().delete()


def migrate_composition_bibliography(entry):
    print(term.green("\tMigrating Composition {0} bibliography {1} with ID {2}".format(entry.compositionkey,
                                                                                       entry.bibliographykey,
                                                                                       entry.pk)))

    bibliography = Bibliography.objects.get(pk=entry.bibliographykey)
    # in this table, the pages are kept in the 'notes' field. We'll migrate them to the pages field.
    pages = entry.notes if entry.notes != "none" else None

    try:
        composition = Composition.objects.get(pk=entry.compositionkey)
    except Composition.DoesNotExist:
        # This composition has been converted to an item.
        print(term.yellow("\t\tConverting record to an item bibliography entry"))
        i = Item.objects.get(legacy_composition="legacy_composition.{0}".format(int(entry.compositionkey)))
        d = {
            'item': i,
            'bibliography': bibliography,
            'pages': pages
        }
        en = ItemBibliography(**d)
        en.save()
        return

    d = {
        "composition": composition,
        "bibliography": bibliography,
        "pages": pages
    }
    c = CompositionBibliography(**d)
    c.save()


def migrate():
    print(term.blue("Migrating Composition Bibliographies"))
    empty_composition_bibliography()

    for entry in LegacyBibliographyComposition.objects.all():
        migrate_composition_bibliography(entry)

    print(term.blue("Done migrating composition bibliographies"))
