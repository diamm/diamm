from django.core.management.base import BaseCommand
from django.core.management import call_command
from diamm.management.helpers import migrate_regions
from diamm.management.helpers import migrate_archive
from diamm.management.helpers import migrate_source
from diamm.management.helpers import migrate_people
from diamm.management.helpers import migrate_language
from diamm.management.helpers import migrate_person_roles
from diamm.management.helpers import migrate_source_copyists
from diamm.management.helpers import migrate_bibliography
from diamm.management.helpers import migrate_source_bibliography
from diamm.management.helpers import migrate_source_relationship
from diamm.management.helpers import migrate_genre
from diamm.management.helpers import migrate_composition
from diamm.management.helpers import migrate_composition_bibliography
from diamm.management.helpers import migrate_item
from diamm.management.helpers import migrate_image
from diamm.management.helpers import migrate_source_provenance
from diamm.management.helpers import migrate_users

from diamm.models.data.image_page_condition import ImagePageCondition
from diamm.models.data.image_type import ImageType
from diamm.models.data.organization_type import OrganizationType


class Command(BaseCommand):
    def handle(self, *args, **options):
        # print("Emptying Fixture tables")
        # ImagePageCondition.objects.all().delete()
        # ImageType.objects.all().delete()
        # OrganizationType.objects.all().delete()
        # print("Loading Fixtures")
        # call_command('loaddata', 'image_file_types')
        # call_command('loaddata', 'image_page_conditions')
        # call_command('loaddata', 'organization_types')
        # migrate_regions.migrate()
        # migrate_archive.migrate()
        # migrate_source.migrate()
        # migrate_people.migrate()
        # migrate_language.migrate()
        # migrate_genre.migrate()
        # migrate_person_roles.migrate()
        # migrate_source_copyists.migrate()
        # migrate_source_provenance.migrate()
        # migrate_source_relationship.migrate()
        # migrate_composition.migrate()
        # migrate_bibliography.migrate()
        # migrate_source_bibliography.migrate()
        # migrate_composition_bibliography.migrate()
        # migrate_item.migrate()
        # migrate_image.migrate()
        migrate_users.migrate()
