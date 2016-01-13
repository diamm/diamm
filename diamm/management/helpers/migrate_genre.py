import psycopg2 as psql
from django.conf import settings
from diamm.models.data.genre import Genre
from diamm.models.migrate.legacy_genre import LegacyGenre
from blessings import Terminal

term = Terminal()


def empty_genre():
    print(term.magenta('\tEmptying Genre'))
    Genre.objects.all().delete()


def migrate_genre(entry):
    print(term.green("\tMigrating Genre ID {0}".format(entry.pk)))
    d = {
        "id": entry.pk,
        'name': entry.genre
    }
    g = Genre(**d)
    g.save()


def update_table():
    print(term.yellow("\tUpdating the ID sequences for the Django Genre Table"))
    sql_max = "SELECT MAX(id) AS maxid FROM diamm_data_genre;"
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


def migrate():
    print(term.blue("Migrating Genre"))
    empty_genre()
    for entry in LegacyGenre.objects.all():
        migrate_genre(entry)

    update_table()
    print(term.blue("Done Migrating Genre"))
