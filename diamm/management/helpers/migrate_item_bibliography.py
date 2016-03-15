from diamm.models.migrate.legacy_bibliography_item import LegacyBibliographyItem
from diamm.models.data.item import Item
from diamm.models.data.bibliography import Bibliography
from diamm.models.data.item_bibliography import ItemBibliography
from blessings import Terminal

term = Terminal()


def empty_item_bibliography():
    print(term.red('\tEmptying Item Bibliography table'))
    ItemBibliography.objects.all().delete()


def migrate_item_bibliography(entry):
    print(term.green("\tMigrating item bibliography PK {0}".format(entry.pk)))
    item = Item.objects.get(pk=int(entry.itemkey))
    bibliography = Bibliography.objects.get(pk=int(entry.bibliographykey))
    pages = entry.notes.strip() if entry.notes not in (None, 'none') else None

    d = {
        'item': item,
        'bibliography': bibliography,
        'pages': pages
    }
    ib = ItemBibliography(**d)
    ib.save()


def migrate():
    print(term.blue("Migrating Item Bibliography"))
    empty_item_bibliography()

    for entry in LegacyBibliographyItem.objects.all():
        migrate_item_bibliography(entry)

    print(term.blue("Done migrating item bibliography"))
