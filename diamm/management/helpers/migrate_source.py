import re
from diamm.models.migrate.legacy_source import LegacySource
from diamm.models.data.source import Source
from diamm.models.data.source import PARCHMENT, PAPER, VELLUM, WOOD, SLATE, MIXED, OTHER
from diamm.management.helpers.utilities import convert_yn_to_boolean
from diamm.models.data.archive import Archive
from diamm.models.data.source_identifier import SourceIdentifier
from diamm.models.data.source_identifier import SHELFMARK, RISM, CCM, EARP, OLIM
from diamm.models.data.source_note import SourceNote
from diamm.models.data.source_note import GENERAL_NOTE, RISM_NOTE, CCM_NOTE, EXTENT_NOTE, PHYSICAL_NOTE
from diamm.models.data.source_note import BINDING_NOTE, OWNERSHIP_NOTE, WATERMARK_NOTE, LIMINARY_NOTE
from diamm.models.data.source_note import NOTATION_NOTE, DATE_NOTE, DEDICATION_NOTE, RULING_NOTE, FOLIATION_NOTE, PRIVATE_NOTE
from diamm.models.data.source_url import SourceURL
from diamm.models.data.source_url import HOST, ANCILLARY
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
        return PARCHMENT
    elif legacy_surface.lower() == 'paper':
        return PAPER
    elif legacy_surface.lower() in ('vellum', 'calfskin'):
        return VELLUM
    elif legacy_surface.lower() in ('wood',):
        return WOOD
    elif legacy_surface.lower() in ('slate',):
        return SLATE
    else:
        return OTHER


def migrate_source_to_source(legacy_source):
    print(term.green("\tMigrating Source {0} with ID {1}".format(legacy_source.shelfmark, legacy_source.pk)))
    archive_pk = legacy_source.archivekey.pk
    archive = Archive.objects.get(pk=archive_pk)
    surface = __migrate_surface(legacy_source.surface)
    print(term.magenta("Converting surface {0} to type {1}".format(legacy_source.surface, surface)))

    start_date = __migrate_centuries_to_years(legacy_source.startdate, 1)
    end_date = __migrate_centuries_to_years(legacy_source.enddate)
    units = legacy_source.measurementunits if legacy_source.measurementunits else "mm"
    measurements = "{0} {1}".format(legacy_source.pagemeasurements, units) if legacy_source.pagemeasurements else None

    d = {
        'id': legacy_source.pk,
        'archive': archive,
        'name': legacy_source.sourcename,
        'type': legacy_source.sourcetype,
        'surface': surface,
        'start_date': start_date,
        'end_date': end_date,
        'format': legacy_source.format,
        'measurements': measurements,
        'public': convert_yn_to_boolean(legacy_source.webpermission)
    }

    s = Source(**d)
    s.save()

    sm = {
        'identifier': legacy_source.shelfmark,
        'type': SHELFMARK,
        'source': s
    }
    shelfmark = SourceIdentifier(**sm)
    shelfmark.save()

    other_identifiers = [
        (CCM, legacy_source.ccmabbrev),
        (RISM, legacy_source.rismabbrev),
        (RISM, legacy_source.altrismabbrev),
        (EARP, legacy_source.earpdesignation),
        (OLIM, legacy_source.olim_text_only)
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
                'type': ANCILLARY,
                'link_text': url_list.group('title'),
                'link': url_list.group('url'),
                'source': s
            }
            surl = SourceURL(**d)
            surl.save()

    notes = [
        (DATE_NOTE, legacy_source.dateofsource),
        (DATE_NOTE, legacy_source.datecomments),
        (RISM_NOTE, legacy_source.description_rism),
        (PRIVATE_NOTE, legacy_source.notes),
        (LIMINARY_NOTE, legacy_source.liminarytext),
        (RULING_NOTE, legacy_source.stavegauge),
        (GENERAL_NOTE, legacy_source.description_diamm),
        (CCM_NOTE, legacy_source.description_ccm),
        (DEDICATION_NOTE, legacy_source.dedicationtext)
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


def migrate():
    print(term.blue('Migrating Sources'))
    empty_source()
    legacy_sources = LegacySource.objects.all()
    for lsource in legacy_sources:
        migrate_source_to_source(lsource)

    print(term.blue('Done migrating Sources'))
