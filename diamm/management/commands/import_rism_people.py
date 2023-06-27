import csv
import re

from django.core.management import BaseCommand

from diamm.models.data.person import Person
from diamm.models.data.person_identifier import PersonIdentifier
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
                person_record = Person.objects.get(id=diamm_id)
                if person_record.identifiers.filter(identifier_type=ExternalIdentifiers.RISM).exists():
                    continue

                _ = PersonIdentifier(
                    identifier=f"{rism_identifier}",
                    identifier_type=ExternalIdentifiers.RISM,
                    person=person_record
                ).save()
