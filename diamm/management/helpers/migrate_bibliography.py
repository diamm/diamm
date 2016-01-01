from diamm.models.migrate.legacy_bibliography import LegacyBibliography
from diamm.models.migrate.legacy_author import LegacyAuthor
from diamm.models.migrate.legacy_author_bibliography import LegacyAuthorBibliography

from diamm.models.data.bibliography import Bibliography
from diamm.models.data.bibliography_author import BibliographyAuthor
from diamm.models.data.bibliography_type import BibliographyType
from diamm.models.data.bibliography_author_role import BibliographyAuthorRole
from diamm.models.data.bibliography_author_role import R_AUTHOR, R_COLLABORATOR, R_COMPILER, R_EDITOR, R_FESTSCHRIFT, R_INDEXER, R_LATER_EDITOR, R_PUBLISHER, R_REVIEWER, R_REVISER, R_SUPERVISOR, R_TRANSLATOR, R_COPYIST
from diamm.models.data.bibliography_publication import BibliographyPublication
from diamm.models.data.bibliography_publication import B_TRANSLATOR, B_CHAPTER, B_PUBLISHER, B_PARENT_TITLE
from diamm.models.data.bibliography_publication import B_DEGREE, B_FESTSCHRIFT_FOR, B_PAGES, B_SERIES
from diamm.models.data.bibliography_publication import B_UNIVERSITY, B_URL_ACCESSED, B_URL, B_VOLUME_NO, B_PLACE_PUBLICATION
from blessings import Terminal

term = Terminal()

JOURNAL_ARTICLE = 1
BOOK = 2
CHAPTER_IN_BOOK = 3
DISSERTATION = 4
FESTSCHRIFT = 5
JOURNAL = 6

def empty_bibliography():
    Bibliography.objects.all().delete()
    BibliographyAuthor.objects.all().delete()
    BibliographyType.objects.all().delete()
    BibliographyAuthorRole.objects.all().delete()


def populate_btypes():
    print(term.green("\tPopulating Bibliography Type table"))
    btype_arr = [
        {
            "id": JOURNAL_ARTICLE,
            "name": "Journal Article"
        },
        {
            "id": BOOK,
            "name": "Book"
        },
        {
            "id": CHAPTER_IN_BOOK,
            "name": "Chapter in Book"
        },
        {
            "id": DISSERTATION,
            "name": "Dissertation"
        },
        {
            "id": FESTSCHRIFT,
            "name": "Festschrift"
        },
        {
            "id": JOURNAL,
            "name": "Journal"
        }
    ]

    for btype in btype_arr:
        bt = BibliographyType(**btype)
        bt.save()


def __determine_type(entry):
    if entry.journal is not None and entry.articletitle is None:
        return JOURNAL
    elif entry.articletitle is not None:
        return JOURNAL_ARTICLE
    elif entry.booktitle is not None and entry.festschrift is not None:
        return FESTSCHRIFT
    elif entry.booktitle is not None and entry.chapter is not None:
        return CHAPTER_IN_BOOK
    elif entry.booktitle is not None and entry.chapter is None:
        return BOOK
    elif entry.seriestitle is not None:
        return BOOK
    elif entry.dissertation is not None:
        return DISSERTATION
    else:
        return BOOK


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
    if btype == JOURNAL:
        return entry.journal
    elif btype == JOURNAL_ARTICLE:
        return entry.articletitle
    elif btype == BOOK:
        if entry.booktitle is not None:
            return entry.booktitle
        elif entry.seriestitle is not None:
            return entry.seriestitle
        else:
            return "{0} ?".format(entry.author1surname)
    elif btype == CHAPTER_IN_BOOK:
        return entry.chapter
    elif btype == FESTSCHRIFT:
        return entry.festschrift
    elif btype == DISSERTATION:
        return entry.dissertation
    else:
        print(term.red('\tCould not determine title for ID {0}'.format(entry.pk)))


def __determine_person_role(entry):
    role = entry.author_editor
    if role == 'author':
        return R_AUTHOR
    elif role == 'editor':
        return R_EDITOR
    elif role == 'indexer':
        return R_INDEXER
    elif role == 'compiler' or role == 'mpiler':  # sic
        return R_COMPILER
    elif role == 'translator':
        return R_TRANSLATOR
    elif role == 'reviser':
        return R_REVISER
    elif role == 'reviewer':
        return R_REVIEWER
    elif role == 'later editor':
        return R_LATER_EDITOR
    elif role == 'collaborator':
        return R_COLLABORATOR
    elif role == 'Festschrift dedicatee':
        return R_FESTSCHRIFT
    elif role == 'supervisor':
        return R_SUPERVISOR
    elif role == 'publisher':
        return R_PUBLISHER
    elif role == 'copyist':
        return R_COPYIST
    else:
        print(term.red("\tCould not determine role for {0}. Assigning as author".format(role)))
        return R_AUTHOR


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
        __create_new_publication_entry(legacy.url, B_URL, b)
    if legacy.publisher:
        __create_new_publication_entry(legacy.publisher, B_PUBLISHER, b)
    if legacy.university:
        __create_new_publication_entry(legacy.university, B_UNIVERSITY, b)
    if legacy.degree:
        __create_new_publication_entry(legacy.degree, B_DEGREE, b)
    if legacy.festschrift:
        __create_new_publication_entry(legacy.festschrift, B_FESTSCHRIFT_FOR, b)
    if legacy.volno:
        __create_new_publication_entry(legacy.volno, B_VOLUME_NO, b)
    if legacy.vol:
        __create_new_publication_entry(legacy.vol, B_VOLUME_NO, b)
    if legacy.page:
        __create_new_publication_entry(legacy.page, B_PAGES, b)
    if legacy.placepublication:
        __create_new_publication_entry(legacy.placepublication, B_PLACE_PUBLICATION, b)


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

    print(term.blue("Done migrating Bibliography Entries"))



