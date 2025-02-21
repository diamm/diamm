import csv
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand

from diamm.models import Item


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("csvfile")

    def handle(self, *args, **options):
        csvfile = options["csvfile"]

        with open(csvfile) as incipits:
            csvreader = csv.DictReader(incipits)
            not_found = 0
            images_not_found = 0
            images_found = 0
            images_total = 0
            for rn, row in enumerate(csvreader):
                try:
                    itm = Item.objects.get(pk=int(row["item"]))
                except Item.DoesNotExist:
                    not_found += 1
                    self.stdout.write(f"Item {row['item']} not found")
                    continue

                image_path = Path(
                    settings.MEDIA_ROOT, "rism", "incipits", f"{row['incipit']}.png"
                )
                images_total += 1

                if not image_path.exists():
                    images_not_found += 1
                    continue
                images_found += 1

                # At this point we should have both an item record and an image that exists.
                itm.incipit = f"rism/incipits/{row['incipit']}.png"
                itm.save()

            print(f"Items Total: {rn}, not found: {not_found}")
            print(
                f"Images Total: {images_total}, found: {images_found}, not found: {images_not_found}"
            )
