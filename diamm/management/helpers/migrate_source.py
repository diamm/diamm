import re
import os
import psycopg2 as psql
from django.conf import settings
from django.db.models import Q
from django.core.files import File
from diamm.models.migrate.legacy_source import LegacySource
from diamm.models.migrate.legacy_source_notation import LegacySourceNotation
from diamm.models.data.source import Source
from diamm.models.data.source_catalogue_entry import SourceCatalogueEntry
from diamm.models.data.notation import Notation
from diamm.management.helpers.utilities import convert_yn_to_boolean
from diamm.models.data.archive import Archive
from diamm.models.data.source_identifier import SourceIdentifier
from diamm.models.data.source_note import SourceNote
from diamm.models.data.source_url import SourceURL
from blessings import Terminal

term = Terminal()


def empty_source():
    print(term.magenta('\tEmptying Source'))
    Source.objects.all().delete()


# the end parameter controls the conversion to a span. Passing '1' to this
# will subtract 100 years from the output.
def __migrate_centuries_to_years(legacy_century, end=0):
    try:
        cent = int(legacy_century)
        return (cent - end) * 100
    except:
        return None


def __migrate_surface(legacy_surface):
    if not legacy_surface:
        return None

    if legacy_surface.lower() == 'parchment':
        return Source.PARCHMENT
    elif legacy_surface.lower() == 'paper':
        return Source.PAPER
    elif legacy_surface.lower() in ('vellum', 'calfskin'):
        return Source.VELLUM
    elif legacy_surface.lower() in ('wood',):
        return Source.WOOD
    elif legacy_surface.lower() in ('slate',):
        return Source.SLATE
    else:
        return Source.OTHER


def format_measurements(page_measurements, units):
    if not page_measurements:
        return None
    if page_measurements and not units:
        return "{0}".format(page_measurements.strip())

    if units and page_measurements.strip().endswith(units):
        return "{0}".format(page_measurements.strip())
    else:
        return "{0} {1}".format(page_measurements.strip(), units)


def migrate_source_to_source(legacy_source):
    print(term.green("\tMigrating Source {0} with ID {1}".format(legacy_source.shelfmark, legacy_source.pk)))
    archive_pk = legacy_source.archivekey.pk
    archive = Archive.objects.get(pk=archive_pk)
    surface = __migrate_surface(legacy_source.surface)
    print(term.magenta("Converting surface {0} to type {1}".format(legacy_source.surface, surface)))

    start_date = __migrate_centuries_to_years(legacy_source.startdate, 1)
    end_date = __migrate_centuries_to_years(legacy_source.enddate)
    units = legacy_source.measurementunits if legacy_source.measurementunits else "mm"
    measurements = format_measurements(legacy_source.pagemeasurements, units)

    # Quite a few of these entries have trailing spaces
    source_type = None
    if legacy_source.sourcetype:
        source_type = legacy_source.sourcetype.strip()

    d = {
        'id': legacy_source.pk,
        'archive': archive,
        'name': legacy_source.sourcename,
        'shelfmark': legacy_source.shelfmark,
        'type': source_type,
        'surface': surface,
        'start_date': start_date,
        'end_date': end_date,
        'date_statement': legacy_source.dateofsource,
        'format': legacy_source.format,
        'measurements': measurements,
        'public': True,
        'public_images': convert_yn_to_boolean(legacy_source.webpermission),
        'inventory_provided': True  # set this as true at this stage of the import; will be switched later when the inventory is actually imported.
    }

    s = Source(**d)
    s.save()

    other_identifiers = [
        (SourceIdentifier.CCM, legacy_source.ccmabbrev),
        (SourceIdentifier.RISM, legacy_source.rismabbrev),
        (SourceIdentifier.RISM, legacy_source.altrismabbrev),
        (SourceIdentifier.EARP, legacy_source.earpdesignation),
        (SourceIdentifier.OLIM, legacy_source.olim_text_only)
    ]

    for i in other_identifiers:
        if i[1]:
            d = {
                'identifier': i[1],
                'type': i[0],
                'source': s
            }
            sid = SourceIdentifier(**d)
            sid.save()

    if legacy_source.external_urls:
        split_list = legacy_source.external_urls.split('\r')
        finder = r'<a href="(?P<url>.*)"target="_blank">(?P<title>.*)</a>'
        for link in split_list:
            url_list = re.search(finder, link)
            if not url_list:
                continue

            d = {
                'type': SourceURL.ANCILLARY,
                'link_text': url_list.group('title'),
                'link': url_list.group('url'),
                'source': s
            }
            surl = SourceURL(**d)
            surl.save()

    notes = [
        (SourceNote.DATE_NOTE, legacy_source.datecomments),
        (SourceNote.RISM_NOTE, legacy_source.description_rism),
        (SourceNote.PRIVATE_NOTE, legacy_source.notes),
        (SourceNote.LIMINARY_NOTE, legacy_source.liminarytext),
        (SourceNote.RULING_NOTE, legacy_source.stavegauge),
        (SourceNote.GENERAL_NOTE, legacy_source.description_diamm),
        (SourceNote.CCM_NOTE, legacy_source.description_ccm),
        (SourceNote.DEDICATION_NOTE, legacy_source.dedicationtext)
    ]

    for n in notes:
        if n[1]:
            d = {
                'note': n[1],
                'type': n[0],
                'source': s
            }
            note = SourceNote(**d)
            note.save()


def attach_notation_to_source(entry):
    print(term.green("\tAttaching notation type {0} to source {1}, entry {2}".format(
        entry.alnotationtypekey,
        entry.sourcekey,
        entry.pk
    )))

    source = Source.objects.get(pk=int(entry.sourcekey))
    notation = Notation.objects.get(pk=int(entry.alnotationtypekey))
    source.notations.add(notation)
    source.save()


def update_table():
    print(term.yellow("\tUpdating the ID sequences for the Django Source Table"))
    sql_max = "SELECT MAX(id) AS maxid FROM diamm_data_source;"
    sql_alt = "ALTER SEQUENCE diamm_data_source_id_seq RESTART WITH %s"
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
    print(term.blue('Migrating Sources'))
    empty_source()

    for entry in LegacySource.objects.all():
        migrate_source_to_source(entry)

    update_table()

    for entry in LegacySourceNotation.objects.all():
        attach_notation_to_source(entry)

    print(term.blue('Done migrating Sources'))


def update_rism_images():
    SourceCatalogueEntry.objects.all().delete()

    print(term.blue("Updating sources with RISM images"))

    fpath = os.path.join(settings.BASE_DIR, 'rism_images')

    for entry in LegacySource.objects.filter(Q(rismimagefilename1__isnull=False) | Q(rismimagefilename2__isnull=False) | Q(rismimagefilename3__isnull=False)):
        print("Updating rism attachments for source {0}".format(entry.pk))
        source = Source.objects.get(pk=entry.pk)

        if entry.rismimagefilename1:
            fn1 = entry.rismimagefilename1.rstrip()
            fobj = "{0}.png".format(fn1)
            d = {
                'order': 1,
                'entry': fobj,
                'source': source
            }
            sce = SourceCatalogueEntry(**d)
            sce.save()

        if entry.rismimagefilename2:
            fn2 = entry.rismimagefilename2.rstrip()
            fobj = "{0}.png".format(fn2)
            d = {
                'order': 2,
                'entry': fobj,
                'source': source
            }
            sce = SourceCatalogueEntry(**d)
            sce.save()

        if entry.rismimagefilename3:
            fn3 = entry.rismimagefilename3.rstrip()
            fobj = "{0}.png".format(fn3)
            d = {
                'order': 3,
                'entry': fobj,
                'source': source
            }
            sce = SourceCatalogueEntry(**d)
            sce.save()
