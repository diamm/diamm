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
                diamm_id = re.sub(r"diamm_person_", "", row['diamm_id'])
                rism_id = re.sub(r"person_", "", row["rism_id"])
                person_record = Person.objects.get(id=diamm_id)

                rism_ident = PersonIdentifier(
                    identifier=f"people/{rism_id}",
                    identifier_type=ExternalIdentifiers.RISM,
                    person=person_record
                ).save()

                if other_identifiers := row["other_identifiers"]:
                    external_idents = other_identifiers.split(",")
                    external_idents_split = [tuple(s.split(":")) for s in external_idents]
                    for ident in external_idents_split:
                        (pfx, idno) = ident
                        ident_type = pfx_lookup.get(pfx, None)
                        if not ident_type:
                            print(f"Unknown prefix {pfx}")
                            continue

                        this_ident = PersonIdentifier(
                            identifier=idno,
                            identifier_type=ident_type,
                            person=person_record
                        ).save()




