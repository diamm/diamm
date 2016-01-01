from diamm.models.migrate.legacy_city import LegacyCity
from diamm.models.migrate.legacy_country import LegacyCountry

from diamm.models.data.geographic_area import CITY, COUNTRY, REGION, STATE, FICTIONAL
from diamm.models.data.geographic_area import GeographicArea
from blessings import Terminal

term = Terminal()


def empty_geoarea():
    print(term.magenta("\tEmptying Geographic Area"))
    GeographicArea.objects.all().delete()


def migrate_city_to_geoarea(legacy_city):
    print(term.green('\tMigrating City: {0}'.format(legacy_city.city)))

    country_legacy_id = 'legacy_country.{0}'.format(legacy_city.country.pk)
    country = GeographicArea.objects.get(legacy_id=country_legacy_id)
    this_legacy_id = "legacy_city.{0}".format(legacy_city.pk)

    d = {
        'type': CITY,
        'name': legacy_city.city,
        'parent': country,
        'legacy_id': this_legacy_id
    }
    c = GeographicArea(**d)
    c.save()
    print(term.green('\tMigrated {0} to new Geo Area ID {1}'.format(legacy_city.city, c.pk)))


def migrate_country_to_geoarea(legacy_country):
    print(term.green('\tMigrating Country: {0}'.format(legacy_country.country)))

    this_legacy_id = "legacy_country.{0}".format(legacy_country.pk)
    d = {
        'type': COUNTRY,
        'name': legacy_country.country,
        'parent': None,
        'legacy_id': this_legacy_id
    }

    c = GeographicArea(**d)
    c.save()

    print(term.green('\tMigrated {0} to new Geo Area ID {1}'.format(legacy_country.country, c.pk)))


def migrate():

    print(term.blue("Migrating regions"))
    empty_geoarea()

    legacy_countries = LegacyCountry.objects.all()
    for lcountry in legacy_countries:
        migrate_country_to_geoarea(lcountry)

    legacy_cities = LegacyCity.objects.all()
    for lcity in legacy_cities:
        migrate_city_to_geoarea(lcity)

    print(term.blue("Done migrating regions"))
