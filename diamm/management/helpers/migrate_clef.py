import psycopg2 as psql
from django.conf import settings

from diamm.models.migrate.legacy_clef import LegacyClef
from diamm.models.data.clef import Clef
from blessings import Terminal

term = Terminal()


def emtpy_clef():
    print(term.red("\tEmptying clef database"))
    Clef.objects.all().delete()


def migrate_clef(entry):
    print(term.green("\tMigrating clef PK {0}".format(entry.pk)))

    d = {
        'id': entry.pk,
        'name': entry.clef
    }

    c = Clef(**d)
    c.save()


def update_table():
    print(term.yellow("\tUpdating the ID sequences for the Django Genre Table"))
    sql_max = "SELECT MAX(id) AS maxid FROM diamm_data_clef;"
    sql_alt = "ALTER SEQUENCE diamm_data_clef_id_seq RESTART WITH %s"
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
    print(term.blue("Migrating clefs"))
    emtpy_clef()
    for entry in LegacyClef.objects.all():
        if entry.pk == 0:
            continue

        migrate_clef(entry)

    update_table()


