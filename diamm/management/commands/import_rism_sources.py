import csv
import re

from django.core.management import BaseCommand

from diamm.models.data.source import Source
from diamm.models.data.source_authority import SourceAuthority
from diamm.helpers.identifiers import TYPE_PREFIX, ExternalIdentifiers

# inverts the lookups to find the identifier type number from the prefix
pfx_lookup = {t[0]: k for k, t in TYPE_PREFIX.items()}


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csvfile')

    def handle(self, *args, **options):
        csvfile = options['csvfile']

        with open(csvfile, 'r') as aligned:
            csvreader = csv.DictReader(aligned)

            for row in csvreader:
                rism_identifier = row.get("rism_id")
                if not rism_identifier:
                    continue

                diamm_id = row.get("id")
                source_record = Source.objects.get(id=diamm_id)

                rism_ident = SourceAuthority(
                    identifier=f"{rism_identifier}",
                    identifier_type=ExternalIdentifiers.RISM,
                    source=source_record
                ).save()


