from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from diamm.helpers.solr_helpers import solr_delete, solr_index
from diamm.models.data.archive import Archive
from diamm.serializers.search_old.archive import ArchiveSearchSerializer


@receiver(post_save, sender=Archive)
def index_archive(sender, instance, created, **kwargs):
    solr_index(ArchiveSearchSerializer, instance)


@receiver(post_delete, sender=Archive)
def delete_archive(sender, instance, **kwargs):
    solr_delete(instance)
