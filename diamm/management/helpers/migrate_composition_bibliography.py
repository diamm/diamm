from diamm.models.migrate.legacy_bibliography_composition import LegacyBibliographyComposition
from diamm.models.data.bibliography import Bibliography
from diamm.models.data.composition import Composition
from diamm.models.data.composition_bibliography import CompositionBibliography
from blessings import Terminal

term = Terminal()


def empty_composition_bibliography():
    print(term.magenta("\tEmptying Composition Bibliography"))
    CompositionBibliography.objects.all().delete()


def migrate_composition_bibliography(entry):
    print(term.green("\tMigrating Composition {0} bibliography {1} with ID {2}".format(entry.compositionkey,
                                                                                       entry.bibliographykey,
                                                                                       entry.pk)))
    composition = Composition.objects.get(pk=entry.compositionkey)
    bibliography = Bibliography.objects.get(pk=entry.bibliographykey)
    # in this table, the pages are kept in the 'notes' field. We'll migrate them to the pages field.
    pages = entry.notes if entry.notes != "none" else None
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
