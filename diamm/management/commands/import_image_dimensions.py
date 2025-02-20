import csv

from django.core.management import BaseCommand

from diamm.models import Image


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("csvfile")

    def handle(self, *args, **options):
        csvfile = options["csvfile"]

        with open(csvfile) as imageinfo:
            csvreader = csv.DictReader(imageinfo)

            lookup_table = {}
            for row in csvreader:
                lookup_table[row["filename"]] = row

            all_images = Image.objects.all()
            for img in all_images:
                loc = img.location
                csvinfo = lookup_table.get(loc)
                if not csvinfo:
                    self.stdout.write(
                        f"No image info for {loc}, Image {img.pk}. Skipping."
                    )
                    continue

                if img.width != 0 and img.height != 0:
                    self.stdout.write(
                        f"Skipping {img.pk} becuase it seems to already have a width and height"
                    )
                    continue

                img.width = csvinfo["width"]
                img.height = csvinfo["height"]
                self.stdout.write(f"Saving image {img.pk}")
                img.save()

            # Image.objects.bulk_update(all_images, ["width", "height"])
