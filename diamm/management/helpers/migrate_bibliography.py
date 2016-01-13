import psycopg2 as psql
from django.conf import settings
from diamm.models.migrate.legacy_bibliography import LegacyBibliography
from diamm.models.migrate.legacy_author import LegacyAuthor
from diamm.models.migrate.legacy_author_bibliography import LegacyAuthorBibliography

from diamm.models.data.bibliography import Bibliography
from diamm.models.data.bibliography_author import BibliographyAuthor
from diamm.models.data.bibliography_type import BibliographyType
from diamm.models.data.bibliography_author_role import BibliographyAuthorRole
from diamm.models.data.bibliography_publication import BibliographyPublication
from blessings import Terminal

term = Terminal()


def empty_bibliography():
    Bibliography.objects.all().delete()
    BibliographyAuthor.objects.all().delete()
    BibliographyType.objects.all().delete()
    BibliographyAuthorRole.objects.all().delete()


def populate_btypes():
    print(term.green("\tPopulating Bibliography Type table"))
    btype_arr = [
        {
            "id": BibliographyType.JOURNAL_ARTICLE,
            "name": "Journal Article"
        },
        {
            "id": BibliographyType.BOOK,
            "name": "Book"
        },
        {
            "id": BibliographyType.CHAPTER_IN_BOOK,
            "name": "Chapter in Book"
        },
        {
            "id": BibliographyType.DISSERTATION,
            "name": "Dissertation"
        },
        {
            "id": BibliographyType.FESTSCHRIFT,
            "name": "Festschrift"
        },
        {
            "id": BibliographyType.JOURNAL,
            "name": "Journal"
        }
    ]

    for btype in btype_arr:
        bt = BibliographyType(**btype)
        bt.save()


def __determine_type(entry):
    if entry.journal is not None and entry.articletitle is None:
        return BibliographyType.JOURNAL
    elif entry.articletitle is not None:
        return BibliographyType.JOURNAL_ARTICLE
    elif entry.booktitle is not None and entry.festschrift is not None:
        return BibliographyType.FESTSCHRIFT
    elif entry.booktitle is not None and entry.chapter is not None:
        return BibliographyType.CHAPTER_IN_BOOK
    elif entry.booktitle is not None and entry.chapter is None:
        return BibliographyType.BOOK
    elif entry.seriestitle is not None:
        return BibliographyType.BOOK
    elif entry.dissertation is not None:
        return BibliographyType.DISSERTATION
    else:
        return BibliographyType.BOOK


def __create_new_publication_entry(pubinfo, bptype, bibliography):
    print(term.green('\t\tCreating pub info {0}'.format(pubinfo)))
    entry = {
        'type': bptype,
        'entry': pubinfo,
        'bibliography': bibliography
    }
    bp = BibliographyPublication(**entry)
    bp.save()
    return bp


def __determine_title(entry, btype):
    if btype == BibliographyType.JOURNAL:
        return entry.journal
    elif btype == BibliographyType.JOURNAL_ARTICLE:
        return entry.articletitle
    elif btype == BibliographyType.BOOK:
        if entry.booktitle is not None:
            return entry.booktitle
        elif entry.seriestitle is not None:
            return entry.seriestitle
        else:
            return "{0} ?".format(entry.author1surname)
    elif btype == BibliographyType.CHAPTER_IN_BOOK:
        return entry.chapter
    elif btype == BibliographyType.FESTSCHRIFT:
        return entry.festschrift
    elif btype == BibliographyType.DISSERTATION:
        return entry.dissertation
    else:
        print(term.red('\tCould not determine title for ID {0}'.format(entry.pk)))


def __determine_person_role(entry):
    role = entry.author_editor
    if role == 'author':
        return BibliographyAuthorRole.R_AUTHOR
    elif role == 'editor':
        return BibliographyAuthorRole.R_EDITOR
    elif role == 'indexer':
        return BibliographyAuthorRole.R_INDEXER
    elif role == 'compiler' or role == 'mpiler':  # sic
        return BibliographyAuthorRole.R_COMPILER
    elif role == 'translator':
        return BibliographyAuthorRole.R_TRANSLATOR
    elif role == 'reviser':
        return BibliographyAuthorRole.R_REVISER
    elif role == 'reviewer':
        return BibliographyAuthorRole.R_REVIEWER
    elif role == 'later editor':
        return BibliographyAuthorRole.R_LATER_EDITOR
    elif role == 'collaborator':
        return BibliographyAuthorRole.R_COLLABORATOR
    elif role == 'Festschrift dedicatee':
        return BibliographyAuthorRole.R_FESTSCHRIFT
    elif role == 'supervisor':
        return BibliographyAuthorRole.R_SUPERVISOR
    elif role == 'publisher':
        return BibliographyAuthorRole.R_PUBLISHER
    elif role == 'copyist':
        return BibliographyAuthorRole.R_COPYIST
    else:
        print(term.red("\tCould not determine role for {0}. Assigning as author".format(role)))
        return BibliographyAuthorRole.R_AUTHOR


def migrate_author(legacy):
    print(term.green('\tMigrating Author ID {0}'.format(legacy.pk)))
    d = {
        'id': legacy.pk,
        'last_name': legacy.lastname,
        'first_name': legacy.firstname
    }
    ba = BibliographyAuthor(**d)
    ba.save()


def migrate_bibliography(legacy):
    print(term.green('\tMigrating Bibliography ID {0}'.format(legacy.pk)))
    btype = __determine_type(legacy)
    type = BibliographyType.objects.get(pk=btype)
    title = __determine_title(legacy, btype)
    year = legacy.year

    d = {
        'id': legacy.pk,
        'type': type,
        'title': title,
        'year': year,
        'abbreviation': legacy.biblabbrev
    }

    b = Bibliography(**d)
    b.save()

    if legacy.url:
        __create_new_publication_entry(legacy.url, BibliographyPublication.B_URL, b)
    if legacy.publisher:
        __create_new_publication_entry(legacy.publisher, BibliographyPublication.B_PUBLISHER, b)
    if legacy.university:
        __create_new_publication_entry(legacy.university, BibliographyPublication.B_UNIVERSITY, b)
    if legacy.degree:
        __create_new_publication_entry(legacy.degree, BibliographyPublication.B_DEGREE, b)
    if legacy.festschrift:
        __create_new_publication_entry(legacy.festschrift, BibliographyPublication.B_FESTSCHRIFT_FOR, b)
    if legacy.volno:
        __create_new_publication_entry(legacy.volno, BibliographyPublication.B_VOLUME_NO, b)
    if legacy.vol:
        __create_new_publication_entry(legacy.vol, BibliographyPublication.B_VOLUME_NO, b)
    if legacy.page:
        __create_new_publication_entry(legacy.page, BibliographyPublication.B_PAGES, b)
    if legacy.placepublication:
        __create_new_publication_entry(legacy.placepublication, BibliographyPublication.B_PLACE_PUBLICATION, b)


def attach_author_to_bibliography(entry):
    author = BibliographyAuthor.objects.get(pk=entry.alauthorkey)
    bibliography = Bibliography.objects.get(pk=entry.bibliographykey)
    role = __determine_person_role(entry)

    d = {
        'bibliography_author': author,
        'bibliography': bibliography,
        'role': role
    }
    bar = BibliographyAuthorRole(**d)
    bar.save()


def update_table():
    print(term.yellow("\tUpdating the ID sequences for the Django Bibliography Tables"))
    db = settings.DATABASES['default']
    conn = psql.connect(database=db['NAME'],
                        user=db['USER'],
                        password=db['PASSWORD'],
                        host=db['HOST'],
                        port=db['PORT'],
                        cursor_factory=psql.extras.DictCursor)
    curs = conn.cursor()
    print(term.yellow("\t\tUpdating Author Table Sequence"))
    sql_max_auth = "SELECT MAX(id) AS maxid FROM diamm_data_bibliographyauthor;"
    sql_alt_auth = "ALTER SEQUENCE diamm_data_bibliographyauthor_id_seq RESTART WITH %s"
    curs.execute(sql_max_auth)
    maxid = curs.fetchone()['maxid']
    nextid = maxid + 1
    curs.execute(sql_alt_auth, (nextid,))

    print(term.yellow("\t\tUpdating Bibliography Table Sequence"))
    sql_max_bibl = "SELECT MAX(id) AS maxid FROM diamm_data_bibliography;"
    sql_alt_bibl = "ALTER SEQUENCE diamm_data_bibliography_id_seq RESTART WITH %s"
    curs.execute(sql_max_bibl)
    maxid = curs.fetchone()['maxid']
    nextid = maxid + 1
    curs.execute(sql_alt_auth, (nextid,))


def migrate():
    print(term.blue("Migrating Bibliography Entries"))
    empty_bibliography()
    populate_btypes()

    authors = LegacyAuthor.objects.all()
    for author in authors:
        migrate_author(author)

    entries = LegacyBibliography.objects.all()
    for entry in entries:
        migrate_bibliography(entry)

    biblauthors = LegacyAuthorBibliography.objects.all()
    for entry in biblauthors:
        attach_author_to_bibliography(entry)

    update_table()

    print(term.blue("Done migrating Bibliography Entries"))



