import csv

from django.core.management import BaseCommand

from diamm.models import Item


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("csvfile")

    def handle(self, *args, **options):
        csvfile = options["csvfile"]

        with open(csvfile) as aligned:
            csvreader = csv.DictReader(aligned)

            for row in csvreader:
                rism_identifier = row.get("item_id")
                if not rism_identifier:
                    continue

                source_incipit = row.get("source_incipit")
                try:
                    i = Item.objects.get(id=rism_identifier)
                except Item.DoesNotExist:
                    print(f"Item {rism_identifier} does not exist!")
                    continue

                if not i.source_incipit:
                    i.source_incipit = source_incipit
                else:
                    print(f"Item {rism_identifier} already has a value for source incipit. Current: {i.source_incipit}, Spreadsheet: {source_incipit}")
                    continue

                i.save()
