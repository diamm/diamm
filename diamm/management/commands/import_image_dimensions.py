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

                img.width = csvinfo["width"]
                img.height = csvinfo["height"]
                img.save()

            # Image.objects.bulk_update(all_images, ["width", "height"])
