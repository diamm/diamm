from diamm.helpers.solr_helpers import solr_delete, solr_index
from diamm.serializers.search.source_provenance import SourceProvenanceSearchSerializer


# @receiver(post_save, sender=SourceProvenance)
def index_source_provenance(sender, instance, created, **kwargs):
    solr_index(SourceProvenanceSearchSerializer, instance)


# @receiver(post_delete, sender=SourceProvenance)
def delete_source_provenance(sender, instance, **kwargs):
    solr_delete(instance)
