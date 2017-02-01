from blessings import Terminal
from django.db.models import Q
from diamm.models.data.source_note import SourceNote
from diamm.models.site.problem_report import ProblemReport

term = Terminal()


def empty_problem_report():
    print(term.magenta("\tEmptying problem reports"))
    ProblemReport.objects.all().delete()


def migrate_contributor(note):
    print(term.green("\tMigrating note with pk {0}".format(note.pk)))
    source = note.source

    credit = note.author

    if note.author == "James Burke, 2016":
        credit = "DIAMM, 2016"

    d = {
        'object_id': source.pk,
        'content_type_id': 34,
        'accepted': True,
        'note': 'Migrated from Filemaker.',
        'credit': credit,
    }

    c = ProblemReport.objects.get_or_create(**d)[0]
    c.record = source

    if c.summary:
        n = c.summary + "; " + note.note_type
    else:
        n = "NB: Migrated from old site. Credit for notes may not be completely accurate. " + note.note_type

    c.summary = n
    c.save()


def migrate():
    print(term.blue("Migrating contributors"))
    empty_problem_report()

    notes = SourceNote.objects.exclude(Q(author__isnull=True) | Q(author="") | Q(type=SourceNote.PRIVATE_NOTE))

    for note in notes:
        migrate_contributor(note)
