from diamm.models.migrate.legacy_source_provenance import LegacySourceProvenance
from diamm.models.data.source_provenance import SourceProvenance
from diamm.models.data.source import Source
from diamm.models.data.geographic_area import GeographicArea
from diamm.models.data.organization import Organization
from diamm.models.data.legacy_id import LegacyId
from diamm.management.helpers.utilities import convert_yn_to_boolean
from blessings import Terminal

term = Terminal()


def empty_source_provenance():
    print(term.magenta("\tEmptying Source Provenance Table"))
    SourceProvenance.objects.all().delete()


def migrate_source_provenance(entry):
    print(term.green("\tMigrating Source Provenance ID {0}".format(int(entry.pk))))
    note = "Original: "
    source = Source.objects.get(pk=int(entry.sourcekey))
    legacy_id = "legacy_provenance.{0}".format(int(entry.alprovenancekey))

    country = None
    try:
        country = GeographicArea.objects.get(legacy_id__name=legacy_id)
    except GeographicArea.DoesNotExist:
        raise('Could not determine provenance country with ID {0}. Bailing'.format(int(entry.alprovenancekey)))

    note = "{0} {1} ({2})".format(note, country.name, entry.alprovenancekey)

    city = None
    if entry.city:
        cname = entry.city.rstrip("?")
        lid = "legacy_source_provenance_city.{0}_{1}".format(entry.alprovenancekey, cname.lower())

        try:
            city = GeographicArea.objects.get(legacy_id__name=lid)
        except GeographicArea.DoesNotExist:
            try:
                print(term.red("\tCity may not exist. Checking by name {0}, {1}.".format(cname, country.name)))
                city = GeographicArea.objects.get(name=cname, parent=country)
                lgid = LegacyId(name=lid)
                lgid.save()
                city.legacy_id.add(lgid)
                city.save()
            except GeographicArea.DoesNotExist:
                print(term.red("\tCity {0} does not exist. Attempting to create."))
                d = {
                    'type': GeographicArea.CITY,
                    'name': cname,
                    'parent': country
                }
                city = GeographicArea(**d)
                city.save()
                lgid = LegacyId(name=lid)
                lgid.save()
                city.legacy_id.add(lgid)
                city.save()

        note = note + " " + entry.city

    organization = None
    if entry.institution:
        orgname = entry.institution.strip("?")
        try:
            organization = Organization.objects.get(name=orgname)
        except Organization.DoesNotExist:
            print(term.red("\tOrganization {0} does not exist. Attempting to create.".format(orgname)))
            location = city if city else country
            d = {
                "name": orgname,
                "location": location,
                "legacy_id": "legacy_source_provenance.{0}".format(int(entry.pk))
            }
            organization = Organization(**d)
            organization.save()

        note = note + " " + entry.institution

    region = None
    if entry.region:
        regname = entry.region.strip("?")
        legacy_id = "legacy_source_provenance_region.{0}_{1}".format(entry.alprovenancekey, regname.lower())

        try:
            region = GeographicArea.objects.get(legacy_id__name=legacy_id)
        except GeographicArea.DoesNotExist:
            try:
                region = GeographicArea.objects.get(name=regname)
                lgid = LegacyId(name=legacy_id)
                lgid.save()
                region.legacy_id.add(lgid)
            except GeographicArea.DoesNotExist:
                d = {
                    "name": regname,
                    "type": GeographicArea.REGION,
                    "parent": country
                }
                region = GeographicArea(**d)
                region.save()
                lgid = LegacyId(name=legacy_id)
                lgid.save()
                region.legacy_id.add(lgid)
                region.save()

            note = note + " " + entry.region

    protectorate = None
    if entry.protectorate:
        pname = entry.protectorate.strip("?")
        legacy_id = "legacy_source_provenance_protectorate.{0}_{1}".format(entry.alprovenancekey, pname.lower())

        try:
            protectorate = GeographicArea.objects.get(legacy_id__name=legacy_id)
        except GeographicArea.DoesNotExist:
            try:
                protectorate = GeographicArea.objects.get(name=pname, type=GeographicArea.REGION)
                lgid = LegacyId(name=legacy_id)
                lgid.save()
                protectorate.legacy_id.add(lgid)
                protectorate.save()
            except GeographicArea.DoesNotExist:
                d = {
                    "name": pname,
                    "type": GeographicArea.REGION,
                    "parent": country
                }
                protectorate = GeographicArea(**d)
                protectorate.save()
                lgid = LegacyId(name=legacy_id)
                lgid.save()
                protectorate.legacy_id.add(lgid)
                protectorate.save()

            note = note + " " + entry.protectorate

    sp = {
        'source': source,
        'country': country,
        'city': city,
        'protectorate': protectorate,
        'region': region,
        'organization': organization,
        'uncertain': convert_yn_to_boolean(entry.uncertain),
        'note': note
    }
    spe = SourceProvenance(**sp)
    spe.save()



def migrate():
    print(term.blue("Migrating Source Provenance"))
    for entry in LegacySourceProvenance.objects.all():
        migrate_source_provenance(entry)

    print(term.blue("Done Migrating Source Provenance"))
