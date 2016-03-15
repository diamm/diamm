from django.core.management import BaseCommand
from diamm.models.data.page import Page
from diamm.models.migrate.legacy_image import LegacyImage


class Command(BaseCommand):
    def handle(self, *args, **options):
        legacy_images = LegacyImage.objects.all()
        for image in legacy_images:
            print("Updating for image {0}".format(image.pk))
            new_page = Page.objects.get(legacy_id="legacy_image.{0}".format(int(image.pk)))
            new_page.sort_order = image.orderno
            new_page.save()
