from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from diamm.helpers.solr_helpers import solr_index, solr_delete
from diamm.models.data.source_provenance import SourceProvenance
from diamm.serializers.search.source_provenance import SourceProvenanceSearchSerializer


@receiver(post_save, sender=SourceProvenance)
def index_source_provenance(sender, instance, created, **kwargs):
    solr_index(SourceProvenanceSearchSerializer, instance)


@receiver(post_delete, sender=SourceProvenance)
def delete_source_provenance(sender, instance, **kwargs):
    solr_delete(instance)


