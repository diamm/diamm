import pysolr
from django.conf import settings
from django.core.management.base import BaseCommand
from diamm.models.data.image import Image


class Command(BaseCommand):
    def handle(self, *args, **options):
        images = Image.objects.all()

        for im in images:
            if not im.location:
                continue
            loc = im.location
            im.location = "/".join(loc.split("/")[-2:])

        Image.objects.bulk_update(images, ["location"], batch_size=1000)
