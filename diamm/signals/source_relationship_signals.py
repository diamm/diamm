from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from diamm.helpers.solr_helpers import solr_delete, solr_index
from diamm.models.data.source_relationship import SourceRelationship
from diamm.serializers.search_old.source_relationship import (
    SourceRelationshipSerializer,
)


@receiver(post_save, sender=SourceRelationship)
def index_source_relationship(sender, instance, created, **kwargs):
    solr_index(SourceRelationshipSerializer, instance)


@receiver(post_delete, sender=SourceRelationship)
def delete_source_relationship(sender, instance, **kwargs):
    solr_delete(instance)
