from diamm.models.migrate.legacy_source_copyist import LegacySourceCopyist
from diamm.models.data.source_copyist import SourceCopyist
from diamm.models.data.source import Source
from diamm.models.data.person import Person
from diamm.management.helpers.utilities import convert_yn_to_boolean
from blessings import Terminal

term = Terminal()


def empty_source_copyist():
    print(term.magenta("\tEmptying Source Copyist"))
    SourceCopyist.objects.all().delete()


def migrate_source_copyists(legacy_source_copyist):
    print(term.green("\tMigrating Copyist {0} for Source {1}".format(legacy_source_copyist.alcopyistkey, legacy_source_copyist.sourcekey)))
    source = Source.objects.get(pk=int(legacy_source_copyist.sourcekey))
    copyist_id = "legacy_copyist.{0}".format(int(legacy_source_copyist.alcopyistkey))
    copyist = Person.objects.get(legacy_id=copyist_id)
    uncertain = convert_yn_to_boolean(legacy_source_copyist.attribution_uncertain)

    d = {
        'source': source,
        'copyist': copyist,
        'uncertain': uncertain,
        'type': legacy_source_copyist.alcopyisttypekey
    }

    sc = SourceCopyist(**d)
    sc.save()


def migrate():
    print(term.blue("Migrating Source Copyists"))
    empty_source_copyist()

    sourcecopyists = LegacySourceCopyist.objects.all()

    for copyist in sourcecopyists:
        migrate_source_copyists(copyist)

    print(term.blue("Done Migrating Source Copyists"))
