import psycopg2 as psql
from django.conf import settings
from diamm.models.data.set import Set
from diamm.models.data.source import Source
from diamm.models.migrate.legacy_set import LegacySet
from diamm.models.migrate.legacy_source_set import LegacySourceSet
from blessings import Terminal

term = Terminal()


def empty_set():
    print(term.magenta("\tEmptying Sets"))
    Set.objects.all().delete()


def migrate_set(entry):
    print(term.green("\tMigrating Set ID {0}".format(entry.pk)))

    description = "{0}\n{1}".format(entry.description, entry.bibliography)

    d = {
        'id': entry.pk,
        'cluster_shelfmark': entry.clustershelfmark,
        'description': description,
        'type': int(entry.settypekey)
    }
    s = Set(**d)
    s.save()


def update_table():
    print(term.yellow("\tUpdating the ID sequences for the Django Set Table"))
    sql_max = "SELECT MAX(id) AS maxid FROM diamm_data_set;"
    sql_alt = "ALTER SEQUENCE diamm_data_genre_id_seq RESTART WITH %s"
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


def attach_source_to_set(entry):
    print(term.green("\tAttaching Source {0} to Set {1}".format(entry.sourcekey, entry.setkey)))

    source = Source.objects.get(pk=int(entry.sourcekey))
    sourceset = Set.objects.get(pk=int(entry.setkey))

    sourceset.sources.add(source)
    sourceset.save()

def migrate():
    empty_set()

    for entry in LegacySet.objects.all():
        migrate_set(entry)

    for entry in LegacySourceSet.objects.all():
        attach_source_to_set(entry)

    update_table()
