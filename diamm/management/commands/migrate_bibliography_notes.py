import csv

from django.core.management.base import BaseCommand

from diamm.models.data.bibliography import Bibliography
from diamm.models.data.bibliography_publication import BibliographyPublication


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("csvfile")

    def handle(self, *args, **options):
        csvfile = options["csvfile"]
        f1 = open(csvfile)
        datareader = csv.DictReader(f1)

        for row in datareader:
            if not row["notes_old"]:
                print("no note. Skipping.")
                continue

            print(f"Updating {row['bibliographyKey']}")
            try:
                brec = Bibliography.objects.get(pk=row["bibliographyKey"])
            except Bibliography.DoesNotExist:
                print(f"Bibliography {row['bibliographyKey']} does not exist")
                continue

            b = {
                "entry": row["notes_old"],
                "type": BibliographyPublication.B_NOTE,
                "bibliography": brec,
            }
            rec = BibliographyPublication(**b)
            rec.save()

        f1.close()
