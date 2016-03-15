import psycopg2 as psql
from django.conf import settings
from diamm.models.migrate.legacy_composition_cycle import LegacyCompositionCycle
from diamm.models.migrate.legacy_composition_cycle_composition import LegacyCompositionCycleComposition
from diamm.models.migrate.legacy_cycle_type import LegacyCycleType
from diamm.models.data.cycle_type import CycleType
from diamm.models.data.cycle import Cycle
from diamm.models.data.composition_cycle import CompositionCycle
from diamm.models.data.person import Person
from diamm.models.data.composition import Composition

from blessings import Terminal

term = Terminal()

def empty_tables():
    print(term.red("\tEmptying tables"))
    CompositionCycle.objects.all().delete()
    Cycle.objects.all().delete()
    CycleType.objects.all().delete()

def migrate_cycle_type(entry):
    print(term.green("\tMigrating Cycle Type pk {0}".format(entry.pk)))
    d = {
        'id': entry.pk,
        'name': entry.cycletype
    }
    ct = CycleType(**d)
    ct.save()


def migrate_cycle(entry):
    print(term.green("\tMigrating cycle PK {0}".format(entry.pk)))
    ctype = CycleType.objects.get(pk=int(entry.alcycletypekey))
    composer = None
    if entry.composerkey != 0:
        composer = Person.objects.get(legacy_id="legacy_composer.{0}".format(int(entry.composerkey)))

    d = {
        'id': entry.pk,
        'title': entry.title,
        'composer': composer,
        'type': ctype
    }
    c = Cycle(**d)
    c.save()

def migrate_composition_cycle(entry):
    print(term.green("\tMigrating composition cycle relationship pk {0}".format(entry.pk)))
    composition = Composition.objects.get(pk=int(entry.compositionkey))
    cycle = Cycle.objects.get(pk=int(entry.compositioncyclekey))

    d = {
        'composition': composition,
        'cycle': cycle,
        'order': int(entry.orderno)
    }
    cc = CompositionCycle(**d)
    cc.save()


def update_tables():
    print(term.yellow("\tUpdating the ID sequences for the Django Composition Cycle Tables"))
    sql_max = "SELECT MAX(id) AS maxid FROM diamm_data_cycletype;"
    sql_alt = "ALTER SEQUENCE diamm_data_cycletype_id_seq RESTART WITH %s"
    sql_max2 = "SELECT MAX(id) AS maxid FROM diamm_data_cycle;"
    sql_alt2 = "ALTER SEQUENCE diamm_data_cycle_id_seq RESTART WITH %s"

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

    curs.execute(sql_max2)
    maxid = curs.fetchone()['maxid']
    nextid = maxid + 1
    curs.execute(sql_alt2, (nextid,))


def migrate():
    print(term.blue("Migrating Cycle Data"))
    empty_tables()

    for entry in LegacyCycleType.objects.all():
        migrate_cycle_type(entry)

    for entry in LegacyCompositionCycle.objects.all():
        migrate_cycle(entry)

    for entry in LegacyCompositionCycleComposition.objects.all():
        migrate_composition_cycle(entry)

    update_tables()

    print(term.blue("Done migrating cycle data"))
