import csv
import re

from django.core.management import BaseCommand

from diamm.helpers.identifiers import ExternalIdentifiers
from diamm.models.data.archive import Archive
from diamm.models.data.archive_identifier import ArchiveIdentifier


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("csvfile")

    def handle(self, *args, **options):
        csvfile = options["csvfile"]

        with open(csvfile) as aligned:
            csvreader = csv.DictReader(aligned)

            for row in csvreader:
                diamm_id = re.sub(r"diamm_archive_", "", row["diamm_id"])
                rism_id = re.sub(r"institution_", "", row["rism_id"])

                archive_record = Archive.objects.get(id=diamm_id)

                rism_ident = ArchiveIdentifier(
                    identifier=f"institutions/{rism_id}",
                    identifier_type=ExternalIdentifiers.RISM,
                    archive=archive_record,
                ).save()
