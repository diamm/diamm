from django.core.management.base import BaseCommand
import csv
from diamm.models.data.bibliography import Bibliography
from diamm.models.data.bibliography_publication import BibliographyPublication


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csvfile')

    def handle(self, *args, **options):
        csvfile = options['csvfile']
        f1 = open(csvfile, 'r')
        datareader = csv.DictReader(f1)

        for row in datareader:
            if not row['notes_old']:
                print("no note. Skipping.")
                continue

            print("Updating {0}".format(row['bibliographyKey']))
            brec = Bibliography.objects.get(pk=row['bibliographyKey'])
            b = {
                'entry': row['notes_old'],
                'type': BibliographyPublication.B_NOTE,
                'bibliography': brec
            }
            rec = BibliographyPublication(**b)
            rec.save()

        f1.close()
