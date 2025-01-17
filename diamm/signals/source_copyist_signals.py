from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from diamm.helpers.solr_helpers import solr_delete, solr_index
from diamm.models.data.source_copyist import SourceCopyist
from diamm.serializers.search.source_copyist import SourceCopyistSearchSerializer


@receiver(post_save, sender=SourceCopyist)
def index_source_copyist(sender, instance, created, **kwargs):
    solr_index(SourceCopyistSearchSerializer, instance)


@receiver(post_delete, sender=SourceCopyist)
def delete_source_copyist(sender, instance, **kwargs):
    solr_delete(instance)
