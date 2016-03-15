import re
from diamm.management.helpers.utilities import convert_yn_to_boolean
from diamm.models.migrate.legacy_composer import LegacyComposer
from diamm.models.migrate.legacy_copyist import LegacyCopyist
from diamm.models.migrate.legacy_person import LegacyPerson
from diamm.models.migrate.legacy_affiliation import LegacyAffiliation
from diamm.models.data.person_note import PersonNote
from diamm.models.data.person import Person
from diamm.models.data.organization import Organization
from diamm.models.data.organization_type import OrganizationType


from blessings import Terminal
term = Terminal()


def empty_people():
    print(term.magenta("\tEmptying People and Organizations"))
    Person.objects.all().delete()
    Organization.objects.all().delete()


def migrate_copyist_to_people(legacy_copyist):
    print(term.green('Migrating copyist ID {0} name {1}'.format(legacy_copyist.pk, legacy_copyist.copyistname)))
    legacy_id = "legacy_copyist.{0}".format(legacy_copyist.pk)
    name_search = re.compile(r'(?P<copyist_name>[\w0-9\. ]+(\(\?\))?)( (\(|\[)((?P<dates>(b\.|d\.|ca\.|fl\.)?[0-9\?;,\.\-ca ]+)|= (?P<alias>[a-zA-Z ]+)|or (?P<alias2>[a-zA-Z]+)|alias \"(?P<alias3>[a-zA-Z]+)\"|(?P<ctitle>(Scribe|workshop) [a-zA-Z- ]+)(\)|\]))|$)', re.UNICODE)
    name = re.search(name_search, legacy_copyist.copyistname)
    fullname = name.group("copyist_name") if name else legacy_copyist.copyistname
    articles = ['del', 'de', 'von', 'da', 'san']

    last_name = ""
    first_names = ""
    date_stmt = ""
    if len(fullname.split()) > 2 and fullname.split()[-2] in articles:
        last_name = " ".join(fullname.split()[-2:])
    else:
        last_name = fullname.split()[-1]  # choose the last component of the split name

    first_names = " ".join(fullname.split()[:-1])  # choose everything up to the last component

    if name and name.group('dates'):
        date_stmt = name.group('dates')
    else:
        date_stmt = None

    d = {
        'last_name': last_name,
        'first_name': first_names,
        'legacy_id': legacy_id
    }

    p = Person(**d)
    p.save()

    if date_stmt:
        n = {
            'type': PersonNote.DATE_NOTE,
            'note': date_stmt,
            'person': p
        }
        pn = PersonNote(**n)
        pn.save()


def migrate_person_to_people(legacy_person):
    print(term.green('\tMigrating person ID {0}'.format(legacy_person.pk)))
    legacy_id = "legacy_person.{0}".format(legacy_person.pk)

    d = {
        'last_name': legacy_person.surname,
        'first_name': legacy_person.firstname,
        'earliest_year': legacy_person.startdate,
        'earliest_year_approximate': convert_yn_to_boolean(legacy_person.startdate_approx),
        'latest_year': legacy_person.enddate,
        'latest_year_approximate': convert_yn_to_boolean(legacy_person.enddate_approx),
        'legacy_id': legacy_id
    }

    p = Person(**d)
    p.save()

    notes = (
        (PersonNote.VARIANT_NAME_NOTE, legacy_person.aliases),
    )

    for n in notes:
        if not n[1]:
            continue
        d = {
            'note': n[1],
            'type': n[0],
            'person': p
        }
        pn = PersonNote(**d)
        pn.save()


def migrate_composers_to_people(legacy_composer):
    print(term.green("\tMigrating composer ID {0}".format(legacy_composer.pk)))
    if legacy_composer.pk == 0:
        print(term.red('\tSkipping Anonymous Composer!'))
        return None

    earliest = legacy_composer.date_floruit_earliest.strip(' ') if legacy_composer.date_floruit_earliest else None
    latest = legacy_composer.date_floruit_latest.strip(' ') if legacy_composer.date_floruit_latest else None
    earliest_year = int(earliest) if earliest else None
    latest_year = int(latest) if latest else None
    legacy_id = "legacy_composer.{0}".format(legacy_composer.composerkey)

    d = {
        'last_name': legacy_composer.lastname,
        'first_name': legacy_composer.firstname,
        'earliest_year': earliest_year,
        'latest_year': latest_year,
        'legacy_id': legacy_id
    }
    p = Person(**d)
    p.save()

    notes = (
        (PersonNote.VARIANT_NAME_NOTE, legacy_composer.variantspellings),
        (PersonNote.BIOGRAPHY, legacy_composer.tngentry),
        (PersonNote.DATE_NOTE, legacy_composer.dates_public)
    )
    for n in notes:
        if not n[1]:
            continue

        d = {
            'note': n[1],
            'type': n[0],
            'person': p
        }
        pn = PersonNote(**d)
        pn.save()


def migrate_organizations(entry):
    print(term.green("\tMigrating person record {0} to organization".format(entry.pk)))
    affiliation_name = None
    otype = OrganizationType.objects.get(pk=1)
    legacy_id = "legacy_person.{0}".format(int(entry.pk))

    if entry.alaffiliationkey:
        affiliation = LegacyAffiliation.objects.get(pk=entry.alaffiliationkey)
        affiliation_name = affiliation.affiliation

    d = {
        'name': entry.surname,
        'note': affiliation_name,
        'variant_names': entry.aliases,
        'type': otype,
        'legacy_id': legacy_id
    }

    o = Organization(**d)
    o.save()


def migrate():
    print(term.blue("Migrating people"))
    empty_people()

    composers = LegacyComposer.objects.all()
    for composer in composers:
        if composer.pk == 999999:
            continue
        migrate_composers_to_people(composer)

    for copyist in LegacyCopyist.objects.all():
        migrate_copyist_to_people(copyist)

    people = LegacyPerson.objects.filter(type="person")
    for person in people:
        migrate_person_to_people(person)

    organizations = LegacyPerson.objects.filter(type="institution")
    for entry in organizations:
        migrate_organizations(entry)

    print(term.blue("Done migrating people"))
