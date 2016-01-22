from django.conf import settings
import psycopg2 as psql
from diamm.models.data.source import Source
from diamm.models.data.person import Person
from diamm.models.data.source_relationship_type import SourceRelationshipType
from diamm.models.data.source_relationship import SourceRelationship
from diamm.models.migrate.legacy_relationship_type import LegacyRelationshipType
from diamm.models.migrate.legacy_source_person import LegacySourcePerson
from diamm.management.helpers.utilities import convert_yn_to_boolean
from blessings import Terminal

term = Terminal()


def empty_source_relationship():
    print(term.magenta('\tEmptying source relationships'))
    SourceRelationship.objects.all().delete()
    SourceRelationshipType.objects.all().delete()


def migrate_relationship_type(entry):
    print(term.green("\tMigrating relationship type {0}".format(entry.pk)))
    d = {
        'id': entry.pk,  # maintain the same pk for relationship types so we don't have to store the legacy ID
        'name': entry.relationshiptype
    }
    sr = SourceRelationshipType(**d)
    sr.save()


def migrate_source_relationship(entry):
    print(term.green("\tMigrating Source Relationship ID {0}".format(entry.pk)))
    source_pk = entry.sourcekey
    source = Source.objects.get(pk=source_pk)
    person_pk = entry.alpersonkey
    person_lookup = "legacy_person.{0}".format(int(person_pk))
    person = Person.objects.get(legacy_id=person_lookup)
    rtype_pk = entry.alpersonrelationshipkey
    rtype = SourceRelationshipType.objects.get(pk=rtype_pk)
    uncertain = convert_yn_to_boolean(entry.attribution_uncertain)

    d = {
        'source': source,
        'related_entity': person,
        'relationship_type': rtype,
        'uncertain': uncertain
    }
    sp = SourceRelationship(**d)
    sp.save()


def update_table():
    print(term.yellow("\tUpdating the ID sequences for the Django Source Relationship Table"))
    sql_max = "SELECT MAX(id) AS maxid FROM diamm_data_sourcerelationshiptype;"
    sql_alt = "ALTER SEQUENCE diamm_data_sourcerelationshiptype_id_seq RESTART WITH %s"
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
    print(term.blue("Migrating Source Relationships"))
    empty_source_relationship()

    for entry in LegacyRelationshipType.objects.all():
        migrate_relationship_type(entry)

    for entry in LegacySourcePerson.objects.all():
        migrate_source_relationship(entry)

    update_table()
    print(term.blue("Done Migrating Source Relationships"))
