from django.core.management import BaseCommand
from diamm.serializers.iiif.manifest import SourceManifestSerializer


class Command(BaseCommand):
    def handle(self, *args, **options):
        # test serializer
        import pysolr
        from django.conf import settings
        from django.test.client import RequestFactory

        fact = RequestFactory()
        req = fact.get("/sources/202/manifest")

        conn = pysolr.Solr(settings.SOLR['SERVER'])
        res = conn.search("*:*", fq=["type:source", "pk:202"])
        d = res.docs[0]
        m = SourceManifestSerializer(d, context={'request': req})
        print(m.data)
