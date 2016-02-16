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
    print(term.red("\tEmptying Bibliography Tables"))
    Bibliography.objects.all().delete()
    BibliographyAuthor.objects.all().delete()
    BibliographyType.objects.all().delete()
    BibliographyAuthorRole.objects.all().delete()
    print(term.red("\tDone Emptying tables"))


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
        'last_name': legacy.lastname.strip(),
        'first_name': legacy.firstname.strip() if legacy.firstname else None
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

    if type.pk == BibliographyType.JOURNAL_ARTICLE and legacy.journal:
        __create_new_publication_entry(legacy.journal, BibliographyPublication.B_PARENT_TITLE, b)
    elif type.pk == BibliographyType.CHAPTER_IN_BOOK:
        __create_new_publication_entry(legacy.booktitle, BibliographyPublication.B_PARENT_TITLE, b)

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
    if legacy.novolumes:
        __create_new_publication_entry(legacy.novolumes, BibliographyPublication.B_NUMBER_OF_VOLUMES, b)

    # If the series title was chosen as the main title, skip it.
    if legacy.seriestitle and title != legacy.seriestitle:
        __create_new_publication_entry(legacy.seriestitle, BibliographyPublication.B_SERIES, b)

    # Add any authors we may not know about. Here there be dragons.
    __get_or_create_people(legacy.author1surname, legacy.author1firstname, b, BibliographyAuthorRole.R_AUTHOR, 1)
    __get_or_create_people(legacy.author2surname, legacy.author2firstname, b, BibliographyAuthorRole.R_AUTHOR, 2)
    __get_or_create_people(legacy.author3surname, legacy.author3firstname, b, BibliographyAuthorRole.R_AUTHOR, 3)
    __get_or_create_people(legacy.author4surname, legacy.author4firstname, b, BibliographyAuthorRole.R_AUTHOR, 4)
    __get_or_create_people(legacy.editor1surname, legacy.editor1firstname, b, BibliographyAuthorRole.R_EDITOR, 1)
    __get_or_create_people(legacy.editor2surname, legacy.editor2firstname, b, BibliographyAuthorRole.R_EDITOR, 2)
    __get_or_create_people(legacy.editor3surname, legacy.editor3firstname, b, BibliographyAuthorRole.R_EDITOR, 3)
    __get_or_create_people(legacy.editor4surname, legacy.editor4firstname, b, BibliographyAuthorRole.R_EDITOR, 4)


def __get_or_create_people(surname, firstname, bibliography, role, position):
    if surname and firstname:
        # clean up any trailing spaces to reduce false positives
        surname = surname.strip()
        firstname = firstname.strip()

        # weed out anything that already exists and bail if it does.
        if BibliographyAuthor.objects.filter(last_name=surname, first_name=firstname).exists():
            return None

        print(term.red("\t\tCreating a possibly spurious record for {0} {1}".format(firstname, surname)))
        person, created = BibliographyAuthor.objects.get_or_create(last_name=surname, first_name=firstname)
        if created:
            __light_attach_author(bibliography, person, role, position)


def __light_attach_author(bibliography, author, role, position):
    d = {
        'bibliography_author': author,
        'bibliography_entry': bibliography,
        'role': role,
        'position': position
    }
    bar = BibliographyAuthorRole(**d)
    bar.save()


def attach_author_to_bibliography(entry):
    print(term.green("\tAttaching author {0} to bibliography {1}".format(entry.alauthorkey, entry.bibliographykey)))
    author = BibliographyAuthor.objects.get(pk=entry.alauthorkey)
    bibliography = Bibliography.objects.get(pk=entry.bibliographykey)
    role = __determine_person_role(entry)

    exists = BibliographyAuthorRole.objects.filter(bibliography_author=author, bibliography_entry=bibliography, role=role).exists()
    if exists:
        # Don't re-attach this record if it already exists.
        print(term.red("\t\tThis author relationship already exists. Bailing."))
        return None

    d = {
        'bibliography_author': author,
        'bibliography_entry': bibliography,
        'role': role,
        'position': 1   #  Authors listed here are assumed to be in first position...
    }
    bar = BibliographyAuthorRole(**d)
    bar.save()

def update_author_table():
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
    print(term.yellow("\t\tUpdating Bibliography Table Sequence"))
    sql_max_bibl = "SELECT MAX(id) AS maxid FROM diamm_data_bibliography;"
    sql_alt_bibl = "ALTER SEQUENCE diamm_data_bibliography_id_seq RESTART WITH %s"
    curs.execute(sql_max_bibl)
    maxid = curs.fetchone()['maxid']
    nextid = maxid + 1
    curs.execute(sql_alt_bibl, (nextid,))

def migrate():
    print(term.blue("Migrating Bibliography Entries"))
    empty_bibliography()
    populate_btypes()

    authors = LegacyAuthor.objects.all()
    for author in authors:
        migrate_author(author)

    update_author_table()

    entries = LegacyBibliography.objects.all()
    for entry in entries:
        migrate_bibliography(entry)

    # Since we may have added new authors to the author table in the bibliography
    # migration, we will update the keys again.
    update_author_table()
    update_table()

    biblauthors = LegacyAuthorBibliography.objects.all()
    for entry in biblauthors:
        attach_author_to_bibliography(entry)

    print(term.blue("Done migrating Bibliography Entries"))



