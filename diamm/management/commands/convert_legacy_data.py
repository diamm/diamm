from django.core.management.base import BaseCommand
from diamm.management.helpers import migrate_regions
from diamm.management.helpers import migrate_archive
from diamm.management.helpers import migrate_source
from diamm.management.helpers import migrate_people
from diamm.management.helpers import migrate_source_copyists
from diamm.management.helpers import migrate_bibliography
from diamm.management.helpers import migrate_source_bibliography


class Command(BaseCommand):
    def handle(self, *args, **options):
        # migrate_regions.migrate()
        # migrate_archive.migrate()
        # migrate_source.migrate()
        # migrate_people.migrate()
        # migrate_source_copyists.migrate()
        migrate_bibliography.migrate()
        migrate_source_bibliography.migrate()
