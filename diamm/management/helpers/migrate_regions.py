from diamm.models.migrate.legacy_city import LegacyCity
from diamm.models.migrate.legacy_country import LegacyCountry
from diamm.models.migrate.legacy_provenance import LegacyProvenance
from diamm.models.data.geographic_area import GeographicArea
from diamm.models.data.legacy_id import LegacyId
from blessings import Terminal

term = Terminal()


def empty_geoarea():
    print(term.magenta("\tEmptying Geographic Area"))
    GeographicArea.objects.all().delete()


def migrate_city_to_geoarea(legacy_city):
    print(term.green('\tMigrating City: {0}'.format(legacy_city.city)))

    country_legacy_id = 'legacy_country.{0}'.format(int(legacy_city.country.pk))
    country = GeographicArea.objects.get(legacy_id__name=country_legacy_id)
    this_legacy_id = "legacy_city.{0}".format(int(legacy_city.pk))

    d = {
        'type': GeographicArea.CITY,
        'name': legacy_city.city,
        'parent': country
    }
    c = GeographicArea(**d)
    c.save()

    lid = LegacyId(name=this_legacy_id)
    lid.save()
    c.legacy_id.add(lid)
    c.save()

    print(term.green('\tMigrated {0} to new Geo Area ID {1}'.format(legacy_city.city, c.pk)))


def migrate_country_to_geoarea(legacy_country):
    print(term.green('\tMigrating Country: {0}'.format(legacy_country.country)))
    if legacy_country.pk == 27:
        # duplicate for Slovenia / Yugoslavia that is not to be migrated.
        return None
    this_legacy_id = "legacy_country.{0}".format(int(legacy_country.pk))
    d = {
        'type': GeographicArea.COUNTRY,
        'name': legacy_country.country,
        'parent': None
    }

    c = GeographicArea(**d)
    c.save()
    lid = LegacyId(name=this_legacy_id)
    lid.save()
    c.legacy_id.add(lid)
    c.save()

    print(term.green('\tMigrated {0} to new Geo Area ID {1}'.format(legacy_country.country, c.pk)))


def migrate_provenance_to_geoarea(entry):
    print(term.green("\tMigrating provenance ID {0} to geo area {1}".format(entry.pk, entry.country)))
    # This should ensure that we can look up countries by name or by ID later.
    this_legacy_id = "legacy_provenance.{0}".format(int(entry.pk))
    try:
        area = GeographicArea.objects.get(name=entry.country)
        # area.legacy_id = "{0}, legacy_provenance.{1}".format(area.legacy_id, int(entry.pk))
        lid = LegacyId(name=this_legacy_id)
        lid.save()
        area.legacy_id.add(lid)
        area.save()
    except GeographicArea.DoesNotExist:
        print(term.red("\tArea {0} does not exist...".format(entry.country)))
        d = {
            'type': GeographicArea.REGION,
            'name': entry.country
        }
        ga = GeographicArea(**d)
        ga.save()

        lid = LegacyId(name=this_legacy_id)
        lid.save()
        ga.legacy_id.add(lid)
        ga.save()


def migrate():
    print(term.blue("Migrating regions"))
    empty_geoarea()

    legacy_countries = LegacyCountry.objects.all()
    for lcountry in legacy_countries:
        migrate_country_to_geoarea(lcountry)

    legacy_cities = LegacyCity.objects.all()
    for lcity in legacy_cities:
        migrate_city_to_geoarea(lcity)

    for entry in LegacyProvenance.objects.all():
        migrate_provenance_to_geoarea(entry)

    print(term.blue("Done migrating regions"))
