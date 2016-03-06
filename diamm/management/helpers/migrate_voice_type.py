from diamm.models.migrate.legacy_voice import LegacyVoice
from diamm.models.data.voice_type import VoiceType
from blessings import Terminal

term = Terminal()

def empty_table():
    print(term.red("\tEmptying Voice Type table"))
    VoiceType.objects.all().delete()


def migrate_voice_type(entry):
    print(term.green("\tMigrating voice entry pk {0}".format(entry.pk)))

    d = {
        'name': entry.voice,
        'legacy_id': "voice_{0}".format(int(entry.pk))
    }

    v = VoiceType(**d)
    v.save()


def migrate():
    print(term.green("Migrating voice types"))
    empty_table()

    for entry in LegacyVoice.objects.all():
        migrate_voice_type(entry)
