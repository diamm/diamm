from django.core.management.base import BaseCommand
from diamm.models.data.source_bibliography import SourceBibliography
from diamm.models.data.source import Source
from diamm.models.data.bibliography import Bibliography
import csv


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Importing Bibliographies")
        with open('bibliography_split.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Skip this for now.
                if row['set'] == "288":
                    continue
                master = row['master']
                keys = row['keys'].split("\t")
                master_bibliography = SourceBibliography.objects.filter(source=master)
                for k in keys:
                    print("Source: {0}".format(k))
                    source = Source.objects.get(id=k)
                    # If re-running this, clean up the existing entries for this key.
                    # SourceBibliography.objects.filter(source=source).delete()

                    for bibl in master_bibliography:
                        d = {
                            "source": source,
                            "bibliography": Bibliography.objects.get(id=bibl.bibliography_id),
                            "primary_study": bibl.primary_study,
                            "notes": bibl.notes,
                            "pages": bibl.pages
                        }
                        s = SourceBibliography(**d)
                        s.save()
