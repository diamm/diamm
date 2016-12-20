from blessings import Terminal
from diamm.models.migrate.legacy_note import LegacyNote
from diamm.models.site.commentary import Commentary
from diamm.models.diamm_user import CustomUserModel
from diamm.models.data.source import Source
from diamm.models.data.page import Page
import html2text

term = Terminal()

text_converter = html2text.HTML2Text()
text_converter.unicode_snob = True

def empty_commentary():
    print(term.magenta("\tEmptying commentary"))
    Commentary.objects.all().delete()


def migrate_note(entry):
    print(term.green("\tMigrating note with ID {0}".format(entry.pk)))

    try:
        user = CustomUserModel.objects.get(legacy_id=entry.user)
    except CustomUserModel.DoesNotExist:
        print(term.red("\t\t User with ID {0} does not exist (anymore?)".format(entry.user)))
        return None

    attached = None
    if entry.sourcekey:
        attached = Source.objects.get(pk=entry.sourcekey)
    elif entry.imagekey:
        try:
            attached = Page.objects.get(legacy_id="legacy_image.{0}".format(entry.imagekey))
        except Page.DoesNotExist:
            print(term.red("\tPage with key legacy_image.{0} could not be found".format(entry.imagekey)))
            return None

    # 0 = 1, 1 = 2 for private / public.
    comment_type = 0 if entry.visibility == 1 else 1

    d = {
        "comment_type": comment_type,
        "attachment": attached,
        "author": user,
        "comment": text_converter.handle(entry.notetext)  # converts HTML to Markdown
    }
    c = Commentary(**d)
    c.save()


def migrate():
    print(term.blue("Migrating Notes to commentary"))
    empty_commentary()

    notes = LegacyNote.objects.exclude(sourcekey__isnull=True, imagekey__isnull=True)
    for note in notes:
        migrate_note(note)

    print(term.blue("Done migrating notes!"))
