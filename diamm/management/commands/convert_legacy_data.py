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
from diamm.management.helpers import migrate_images_and_pages
from diamm.management.helpers import migrate_source_provenance
from diamm.management.helpers import migrate_users
from diamm.management.helpers import migrate_sets
from diamm.management.helpers import migrate_clef
from diamm.management.helpers import migrate_mensuration
from diamm.management.helpers import migrate_text_and_voice
from diamm.management.helpers import migrate_voice_type
from diamm.management.helpers import migrate_notation

from diamm.models.data.page_condition import PageCondition
from diamm.models.data.image_type import ImageType
from diamm.models.data.organization_type import OrganizationType

from django.db.models import signals
from diamm.models.data.source import Source
from diamm.models.data.person import Person
from diamm.models.data.composition import Composition
from diamm.models.data.archive import Archive
from diamm.models.data.organization import Organization
from diamm.signals.source_signals import index_source, delete_source
from diamm.signals.person_signals import index_person, delete_person
from diamm.signals.archive_signals import index_archive, delete_archive
from diamm.signals.composition_signals import index_composition, delete_composition
from diamm.signals.organization_signals import index_organization, delete_organization


class Command(BaseCommand):
    def handle(self, *args, **options):
        signals.post_save.disconnect(index_source, sender=Source)
        signals.post_save.disconnect(index_person, sender=Person)
        signals.post_save.disconnect(index_archive, sender=Archive)
        signals.post_save.disconnect(index_composition, sender=Composition)
        signals.post_save.disconnect(index_organization, sender=Organization)
        signals.post_delete.disconnect(delete_source, sender=Source)
        signals.post_delete.disconnect(delete_person, sender=Person)
        signals.post_delete.disconnect(delete_archive, sender=Archive)
        signals.post_delete.disconnect(delete_composition, sender=Composition)
        signals.post_delete.disconnect(delete_organization, sender=Organization)

        # print("Emptying Fixture tables")
        # PageCondition.objects.all().delete()
        # ImageType.objects.all().delete()
        # OrganizationType.objects.all().delete()
        # print("Loading Fixtures")
        # call_command('loaddata', 'image_file_types')
        # call_command('loaddata', 'page_conditions')
        # call_command('loaddata', 'organization_types')
        # migrate_regions.migrate()
        # migrate_archive.migrate()
        migrate_notation.migrate()
        migrate_source.migrate()
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
        # migrate_images_and_pages.migrate()
        # migrate_voice_type.migrate()
        # migrate_mensuration.migrate()
        # migrate_clef.migrate()
        # migrate_text_and_voice.migrate()
        # migrate_users.migrate()
        # migrate_sets.migrate()

        # call_command('testing_image_locations')

        # print('reindexing')
        # call_command('reindex_all')
