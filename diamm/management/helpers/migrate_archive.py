from django.conf import settings
import psycopg2 as psql
from django.core.files import File
from diamm.models.migrate.legacy_archive import LegacyArchive
from diamm.models.data.archive import Archive
from diamm.models.data.archive_note import ArchiveNote
from diamm.models.data.geographic_area import GeographicArea
import re
import os

from blessings import Terminal

term = Terminal()
email_regex = r"(?P<address>[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"


def empty_archive():
    print(term.magenta("\tEmptying Archive"))
    Archive.objects.all().delete()


def migrate_archive_to_archive(entry):
    print(term.green("\tMigrating Archive: {0} ID {1}".format(entry.archivenameoriginal, entry.pk)))

    legacy_city_id = "legacy_city.{0}".format(int(entry.alcitykey))
    print(legacy_city_id)
    city = GeographicArea.objects.get(legacy_id__name=legacy_city_id)
    # clean up the addresses from the FM database
    email = None
    if entry.email:
        msearch = re.search(email_regex, entry.email)
        if msearch:
            email = msearch.group('address')

    d = {
        'id': entry.archivekey,
        'name': entry.archivenameoriginal,
        'siglum': entry.siglum,
        'librarian': entry.librariana,
        'secondary_contact': entry.librarianb,
        'fax': entry.fax,
        'telephone': entry.telephone,
        'website': entry.url_original,
        'email': email,
        'copyright_statement': entry.copyrightholder,
        'city': city,
        'address_1': entry.address1,
        'address_2': entry.address2,
        'address_3': entry.address3,
        'address_4': entry.address4,
        'address_5': entry.address5,
        'address_6': entry.address6,
        'address_7': entry.address7,
        'address_8': entry.address8,
    }
    a = Archive(**d)
    a.save()

    private_notes = (
        (ArchiveNote.PRIVATE, entry.notes),
        (ArchiveNote.PRIVATE, entry.specialcase)
    )

    for pn in private_notes:
        if not pn[1]:
            continue
        n = {
            'type': pn[0],  # private note
            'note': pn[1],
            'archive': a
        }
        note = ArchiveNote(**n)
        note.save()

    print(term.green("\tDone Migrating Archive {0}".format(entry.archivenameoriginal)))


def update_table():
    print(term.yellow("\tUpdating the ID sequences for the Django Archive Table"))
    sql_max = "SELECT MAX(id) AS maxid FROM diamm_data_archive;"
    sql_alt = "ALTER SEQUENCE diamm_data_archive_id_seq RESTART WITH %s"
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


def attach_archive_logos():
    print(term.green("\tAttaching Archive Logos"))
    archives = Archive.objects.all()

    for archive in archives:
        print(term.green('\tAttaching logo to {0}'.format(archive.pk)))
        logofile = "{0}.png".format(archive.pk)
        logopath = os.path.join(settings.MEDIA_ROOT, 'archives', logofile)
        logopath_relative = os.path.join('archives', logofile)
        if os.path.exists(logopath):
            archive.logo.name = logopath_relative
            archive.save()


def migrate():
    print(term.blue('Migrating archives'))
    empty_archive()
    for entry in LegacyArchive.objects.all():
        migrate_archive_to_archive(entry)

    attach_archive_logos()

    update_table()
    print(term.blue('Done Migrating Archives'))
