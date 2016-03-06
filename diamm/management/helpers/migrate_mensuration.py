import psycopg2 as psql
from django.conf import settings
from diamm.models.migrate.legacy_mensuration import LegacyMensuration
from diamm.models.data.mensuration import Mensuration
from blessings import Terminal

term = Terminal()


def empty_table():
    print(term.red("\tDeleting Mensuration table"))
    Mensuration.objects.all().delete()


def update_table():
    print(term.yellow("\tUpdating the ID sequences for the Django Language Table"))
    sql_max = "SELECT MAX(id) AS maxid FROM diamm_data_mensuration;"
    sql_alt = "ALTER SEQUENCE diamm_data_language_id_seq RESTART WITH %s"
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

def migrate_mensuration(entry):
    print(term.green("\tMigrating mensuration sign {0}".format(entry.pk)))

    d = {
        'id': entry.pk,
        'sign': entry.mensurationsign,
        'text': entry.mensurationtext
    }

    m = Mensuration(**d)
    m.save()

def migrate():
    print(term.blue("Migrating mensuration signs"))
    empty_table()
    for entry in LegacyMensuration.objects.all():
        migrate_mensuration(entry)

    update_table()
