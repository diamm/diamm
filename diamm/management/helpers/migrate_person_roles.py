import psycopg2 as psql
from django.conf import settings
from diamm.models.data.person import Person
from diamm.models.data.person_role import PersonRole
from diamm.models.data.role import Role
from diamm.models.migrate.legacy_affiliation import LegacyAffiliation
from diamm.models.migrate.legacy_person import LegacyPerson
from diamm.models.migrate.legacy_copyist import LegacyCopyist
from blessings import Terminal

term = Terminal()


# NB: This must be run after all the people have been migrated!
def empty_roles():
    print(term.magenta("\tEmptying role table"))
    Role.objects.all().delete()
    PersonRole.objects.all().delete()


def migrate_role(entry):
    if entry.pk == 0:
        return

    print(term.green("\tMigrating role ID {0}".format(entry.pk)))
    d = {
        'id': entry.pk,
        'name': entry.affiliation
    }

    r = Role(**d)
    r.save()


def attach_person_to_role(entry):
    print(term.green("\tAttaching roles to person with legacy ID {0}".format(entry.pk)))
    new_person = Person.objects.get(legacy_id="legacy_person.{0}".format(int(entry.pk)))

    role = Role.objects.get(pk=int(entry.alaffiliationkey))

    d = {
        "person": new_person,
        "role": role
    }
    pr = PersonRole(**d)
    pr.save()


def attach_copyist_to_role(entry):
    print(term.green("\tAttaching roles to copyist with legacy ID {0}".format(entry.pk)))
    new_person = Person.objects.get(legacy_id="legacy_copyist.{0}".format(int(entry.pk)))
    role = Role.objects.get(pk=int(entry.alaffiliationkey))

    d = {
        "person": new_person,
        "role": role
    }
    pr = PersonRole(**d)
    pr.save()


def update_table():
    print(term.yellow("\tUpdating the ID sequences for the Django Role Table"))
    sql_max = "SELECT MAX(id) AS maxid FROM diamm_data_role;"
    sql_alt = "ALTER SEQUENCE diamm_data_role_id_seq RESTART WITH %s"
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
    print(term.blue("Creating and attaching people to roles"))
    empty_roles()

    for entry in LegacyAffiliation.objects.all():
        migrate_role(entry)

    # we update this now, not at the end. Because we can.
    update_table()

    # NB: Don't try to migrate the organizations.
    for entry in LegacyPerson.objects.exclude(alaffiliationkey=0).exclude(type='institution').exclude(alaffiliationkey=None):
        attach_person_to_role(entry)

    for entry in LegacyCopyist.objects.exclude(alaffiliationkey=0).exclude(alaffiliationkey=None):
        attach_copyist_to_role(entry)

    print(term.blue("Done creating and attaching people to roles"))

