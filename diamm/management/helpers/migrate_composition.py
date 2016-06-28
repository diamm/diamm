import psycopg2 as psql
from django.conf import settings
from diamm.models.migrate.legacy_composition import LegacyComposition
from diamm.models.migrate.legacy_composition_composer import LegacyCompositionComposer
from diamm.models.data.composition import Composition
from diamm.models.data.person import Person
from diamm.models.data.genre import Genre
from diamm.models.data.composition_composer import CompositionComposer
from diamm.management.helpers.utilities import convert_yn_to_boolean
from blessings import Terminal

term = Terminal()


def empty_composition():
    print(term.magenta("\tEmptying composition composer tables"))
    CompositionComposer.objects.all().delete()
    print(term.magenta("\tEmptying composition tables"))
    Composition.objects.all().delete()


def attempt_genre_matching(legacy_genre):
    genres = legacy_genre.split(',')
    newgenres = []
    for g in genres:
        g = g.strip()
        ng = Genre.objects.filter(name=g)
        if len(ng) > 0:
            # only take the first one...
            newgenres.append(ng[0])
    return newgenres


def migrate_composition(entry):
    print(term.green("\tMigrating composition ID {0}".format(entry.pk)))

    if entry.genre:
        genres = attempt_genre_matching(entry.genre)
    else:
        genres = []

    title = None
    if entry.composition_name:
        title = entry.composition_name.strip()

    d = {
        'id': entry.pk,
        'title': title,
        'legacy_genre': entry.genre,
    }

    c = Composition(**d)
    c.save()
    # expands the list of genres
    c.genres.add(*genres)


def attach_composers_to_composition(entry):
    print(term.green("\tAttaching composer {0} to composition {1} with PK {2}".format(entry.composerkey, entry.compositionkey, entry.pk)))
    composition_pk = entry.compositionkey
    composition = Composition.objects.get(pk=composition_pk)

    # Set the composition to anonymous if the composer is anonymous.
    if entry.composerkey == 0:
        composition.anonymous = True
        composition.save()
        return None

    composer_pk = entry.composerkey
    composer_lookup = "legacy_composer.{0}".format(int(composer_pk))
    composer = Person.objects.get(legacy_id=composer_lookup)

    uncertain = convert_yn_to_boolean(entry.attribution_uncertain)
    notes = entry.notes_attribution

    d = {
        'composer': composer,
        'composition': composition,
        'uncertain': uncertain,
        'notes': notes
    }

    cc = CompositionComposer(**d)
    cc.save()


def update_table():
    print(term.yellow("\tUpdating the ID sequences for the Django Composition Table"))
    sql_max = "SELECT MAX(id) AS maxid FROM diamm_data_composition;"
    sql_alt = "ALTER SEQUENCE diamm_data_composition_id_seq RESTART WITH %s"
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
    print(term.blue("Migrating Compositions"))
    empty_composition()
    COMPOSITIONS_TO_SKIP = (0, 69332, 888888, 999999, 69558, 79920, 54681, 87464)
    for entry in LegacyComposition.objects.exclude(pk__in=COMPOSITIONS_TO_SKIP):
        # Skip the "this source has not been inventoried" composition.
        # 69332 = "See description for inventory"
        migrate_composition(entry)

    for entry in LegacyCompositionComposer.objects.exclude(compositionkey__in=COMPOSITIONS_TO_SKIP):
        attach_composers_to_composition(entry)

    update_table()
    print(term.blue("Done migrating compositions"))
