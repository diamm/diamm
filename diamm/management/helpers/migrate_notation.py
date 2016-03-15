from diamm.models.migrate.legacy_notation import LegacyNotation
from diamm.models.data.notation import Notation
from django.conf import settings
import psycopg2 as psql
from blessings import Terminal


term = Terminal()

def empty_table():
    print(term.red('\tEmptying notation table'))
    Notation.objects.all().delete()


def migrate_notation(entry):
    print(term.green("\tMigrating notation type {0}".format(entry.pk)))

    d = {
        'id': entry.pk,
        'name': entry.notation_type
    }

    n = Notation(**d)
    n.save()


def update_table():
    print(term.yellow("\tUpdating the ID sequences for the Django Notation Table"))
    sql_max = "SELECT MAX(id) AS maxid FROM diamm_data_notation;"
    sql_alt = "ALTER SEQUENCE diamm_data_notation_id_seq RESTART WITH %s"
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
    print(term.green("Migrating notation types"))
    empty_table()
    for entry in LegacyNotation.objects.all():
        migrate_notation(entry)

    update_table()
