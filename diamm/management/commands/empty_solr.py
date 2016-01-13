from django.core.management.base import BaseCommand
from django.conf import settings
import scorched


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Emptying Solr")
        connection = scorched.SolrInterface(settings.SOLR_SERVER)
        connection.delete_all()
        connection.commit()
