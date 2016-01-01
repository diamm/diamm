from diamm.models.migrate.legacy_bibliography_source import LegacyBibliographySource
from diamm.models.data.bibliography import Bibliography
from diamm.models.data.source import Source
from diamm.models.data.source_bibliography import SourceBibliography
from blessings import Terminal

term = Terminal()


def empty_source_bibliography():
    print(term.magenta("\tDeleting Source Bibliography"))
    SourceBibliography.objects.all().delete()


def migrate_source_bibliography(entry):
    print(term.green("\tMigrating source bibliography entry {0}".format(entry.pk)))
    source_pk = entry.sourcekey
    source = Source.objects.get(pk=source_pk)
    bibliography_pk = entry.bibliographykey
    bibliography = Bibliography.objects.get(pk=bibliography_pk)
    notes = entry.notes if entry.notes != 'none' else None  # enter None if the text value is 'none'

    d = {
        'source': source,
        'bibliography': bibliography,
        'notes': notes,
        'pages': entry.page
    }

    sb = SourceBibliography(**d)
    sb.save()


def migrate():
    print(term.blue('Migrating Source Bibliographies'))
    for entry in LegacyBibliographySource.objects.all():
        migrate_source_bibliography(entry)
    print(term.blue('Done migrating Source Bibliographies'))
