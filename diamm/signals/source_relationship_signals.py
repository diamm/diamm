from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from diamm.models.data.source_relationship import SourceRelationship
from diamm.serializers.search.source_relationship import SourceRelationshipSerializer
from diamm.helpers.solr_helpers import solr_index, solr_delete


@receiver(post_save, sender=SourceRelationship)
def index_source_relationship(sender, instance, created, **kwargs):
    solr_index(SourceRelationshipSerializer, instance)


@receiver(post_delete, sender=SourceRelationship)
def delete_source_relationship(sender, instance, **kwargs):
    solr_delete(instance)


