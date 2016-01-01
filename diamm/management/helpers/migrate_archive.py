from diamm.models.migrate.legacy_archive import LegacyArchive
from diamm.models.data.archive import Archive
from diamm.models.data.archive_note import ArchiveNote
from diamm.models.data.geographic_area import GeographicArea
import re

from blessings import Terminal

term = Terminal()
email_regex = r"(?P<address>[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"


def empty_archive():
    print(term.magenta("\tEmptying Archive"))
    Archive.objects.all().delete()


def migrate_archive_to_archive(legacy_archive):
    print(term.green("\tMigrating Archive: {0} ID {1}".format(legacy_archive.archivenameoriginal, legacy_archive.pk)))

    legacy_city_id = "legacy_city.{0}".format(legacy_archive.alcitykey.pk)
    city = GeographicArea.objects.get(legacy_id=legacy_city_id)
    # clean up the addresses from the FM database
    email = None
    if legacy_archive.email:
        msearch = re.search(email_regex, legacy_archive.email)
        if msearch:
            email = msearch.group('address')

    d = {
        'id': legacy_archive.archivekey,
        'name': legacy_archive.archivenameoriginal,
        'siglum': legacy_archive.siglum,
        'librarian': legacy_archive.librariana,
        'secondary_contact': legacy_archive.librarianb,
        'fax': legacy_archive.fax,
        'telephone': legacy_archive.telephone,
        'website': legacy_archive.url_original,
        'email': email,
        'copyright_statement': legacy_archive.copyrightholder,
        'city': city,
        'address_1': legacy_archive.address1,
        'address_2': legacy_archive.address2,
        'address_3': legacy_archive.address3,
        'address_4': legacy_archive.address4,
        'address_5': legacy_archive.address5,
        'address_6': legacy_archive.address6,
        'address_7': legacy_archive.address7,
        'address_8': legacy_archive.address8,
    }
    a = Archive(**d)
    a.save()

    if legacy_archive.notes:
        n = {
            'type': 0,  # private note
            'note': legacy_archive.notes,
            'archive': a
        }
        note = ArchiveNote(**n)
        note.save()

    print(term.green("\tDone Migrating Archive {0}".format(legacy_archive.archivenameoriginal)))


def migrate():
    print(term.blue('Migrating archives'))
    empty_archive()
    legacy_archives = LegacyArchive.objects.all()
    for larchive in legacy_archives:
        migrate_archive_to_archive(larchive)

    print(term.blue('Done Migrating Archives'))
