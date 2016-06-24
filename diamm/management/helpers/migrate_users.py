from diamm.models.migrate.legacy_diammuser import LegacyDiammUser
import uuid
# from django.contrib.auth.models import User
from diamm.models.diamm_user import CustomUserModel
import blessings

term = blessings.Terminal()


def empty_users():
    print(term.magenta("\tEmptying user table"))
    # NB: Don't empty PK 1!
    CustomUserModel.objects.all().delete()
    # User.objects.exclude(username="ahankins").all().delete()


def migrate_user(entry):
    print(term.green("\tMigrating user ID {0}".format(entry.pk)))
    nm = entry.displayname.split()

    # Assume last name is the last component, and first name is everything but.
    last_name = nm[-1]
    first_names = " ".join(nm[:-1])
    d = {
        "legacy_username": entry.username,
        "last_name": last_name,
        "first_name": first_names,
        "email": entry.email,
        "affiliation": entry.affiliation,
        "password": str(uuid.uuid4())  # set a random password. This will be changed on first login.
    }
    u = CustomUserModel.objects.create_user(**d)
    u.save()


def migrate():
    print(term.blue("Migrating users"))
    empty_users()
    for entry in LegacyDiammUser.objects.all():
        migrate_user(entry)

    print(term.blue("Done migrating users"))
