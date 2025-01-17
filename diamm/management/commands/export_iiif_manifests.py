from django.core.management import BaseCommand

from diamm.models.data.source import Source

IIIF_BASE_URL = "https://{0}/sources/{1}/manifest/"


class Command(BaseCommand):
    def handle(self, *args, **options):
        sources = Source.objects.filter(public_images=True).only("pk").order_by("pk")
        f = open("iiif_manifests.txt", "w")
        for source in sources:
            manifest_url = IIIF_BASE_URL.format("beta.diamm.ac.uk", source.pk)
            print(manifest_url)
            print(manifest_url, file=f)
        f.close()
