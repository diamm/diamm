from diamm.models.migrate.legacy_text import LegacyText
from diamm.models.data.text import Text
from diamm.models.data.voice_type import VoiceType
from diamm.models.data.voice import Voice
from diamm.models.data.item import Item
from diamm.models.data.mensuration import Mensuration
from diamm.models.data.language import Language
from diamm.models.migrate.legacy_text_language import LegacyTextLanguage
from diamm.models.data.clef import Clef
from blessings import Terminal

term = Terminal()


def empty_table():
    print(term.red("\tEmptying Text and Voice table"))
    Text.objects.all().delete()
    Voice.objects.all().delete()


def migrate_text_and_voice(entry):
    print(term.green("\tMigrating text entry {0}".format(entry.pk)))
    voice_type = VoiceType.objects.get(legacy_id="voice.{0}".format(int(entry.alvoicekey)))
    item = Item.objects.get(pk=int(entry.itemkey))
    mensuration = None
    # Skip the 'no designation' mensuration key and favour null for mensuration.
    if entry.almensurationkey not in (None, 0):
        mensuration = Mensuration.objects.get(pk=int(entry.almensurationkey))

    clef = None
    if int(entry.alclefkey) != 0:
        clef = Clef.objects.get(pk=int(entry.alclefkey))

    text_language_obj = LegacyTextLanguage.objects.filter(textkey=int(entry.pk)).values_list('allanguagekey', flat=True)
    languages = Language.objects.filter(pk__in=[int(x) for x in text_language_obj])

    if entry.textincipit_copy in ('untexted', 'Untexted', '[untexted', 'untexted [fragment]',
                                  'untexted line of music', 'untexted notations in f4 clef',
                                  '[untexted piece]', '[untexted work]', '(Untexted)', '[untexted]',
                                  'no text', '(no text)', '[no text]'):
        text = None
    else:
        text = entry.textincipit_copy

    vd = {
        'type': voice_type,
        'item': item,
        'mensuration': mensuration,
        'clef': clef,
        'voice_text': text,
        'legacy_id': 'text.{0}'.format(int(entry.pk)),
        'label': entry.voicepart,
        'position': entry.positiononpage
    }

    v = Voice(**vd)
    v.save()

    v.languages.add(*languages)

    if entry.standardspellingfulltext_copy:
        print(term.green("\t\tCreating or attaching a standardized text entry."))
        text, created = Text.objects.get_or_create(text=entry.standardspellingfulltext_copy)

        if created and entry.standardspellingincipit_copy:
            text.incipit = entry.standardspellingincipit_copy
            text.save()

        v.standard_text = text
        v.save()


def migrate():
    # empty_table()
    for entry in LegacyText.objects.all():
        if entry.pk in (82138, 111695):
            # bad record attached to an empty item.
            continue
        # Skip any previously migrated entries
        if Voice.objects.filter(legacy_id="text.{0}".format(int(entry.pk))).exists():
            print("Skipping {0}".format(entry.pk))
            continue

        migrate_text_and_voice(entry)
