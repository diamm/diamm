import os
import csv
from urllib.parse import urljoin
from django.core.management import BaseCommand
from diamm.models.data.image import Image
from diamm.models.data.image_type import ImageType

IIP_SERVER_BASE = "http://alpha.diamm.ac.uk/iiif/image/D-ERu_MS473_2/"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv', type=str)

    def handle(self, *args, **options):
        imgtype = ImageType.objects.get(pk=ImageType.PRIMARY)
        with open(options['csv'], 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                original_filename, ext = os.path.splitext(row['original'])
                new_location = urljoin(IIP_SERVER_BASE, row['transformed'])
                print("{0} ====> {1}".format(original_filename, new_location))
                try:
                    img = Image.objects.get(legacy_filename=original_filename)
                    img.location = new_location
                    img.save()

                    print(img.location)
                except Image.DoesNotExist:
                    print('Creating a record for image {0}'.format(original_filename))
                    # If the image does not exist, create it. NB: This will not have a page or a
                    # source attached, so it will be an orphan.
                    img = Image.objects.create(legacy_filename=original_filename,
                                               location=new_location,
                                               type=imgtype)
                    img.save()
