from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from diamm.models.data.image import
from diamm.serializers.search.
from diamm.helpers.solr_helpers import solr_delete, solr_index


@receiver(post_save, sender=Image)
def index_image(sender, instance, created, **kwargs):
    solr_index(ArchiveSearchSerializer, instance)


@receiver(post_delete, sender=Image)
def delete_archive(sender, instance, **kwargs):
    solr_delete(ArchiveSearchSerializer, instance)
