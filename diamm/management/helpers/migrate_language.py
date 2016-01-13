import psycopg2 as psql
from django.conf import settings
from diamm.models.migrate.legacy_language import LegacyLanguage
from diamm.models.data.language import Language
from blessings import Terminal

term = Terminal()


def empty_language():
    print(term.magenta("\tEmptying Languages"))
    Language.objects.all().delete()


def migrate_language(entry):
    print(term.green("\tMigrating language ID {0}".format(entry.pk)))
    d = {
        "id": entry.pk,
        "name": entry.language
    }
    l = Language(**d)
    l.save()


def update_table():
    print(term.yellow("\tUpdating the ID sequences for the Django Language Table"))
    sql_max = "SELECT MAX(id) AS maxid FROM diamm_data_language;"
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


def migrate():
    print(term.blue("Migrating languages"))
    for entry in LegacyLanguage.objects.all():
        migrate_language(entry)

    update_table()
    print(term.blue("Done migrating language"))
