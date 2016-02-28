from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from diamm.models.data.set import Set
from diamm.serializers.search.set import SetSearchSerializer
from diamm.helpers.solr_helpers import solr_delete, solr_index


@receiver(post_save, sender=Set)
def index_set(sender, instance, created, **kwargs):
    solr_index(SetSearchSerializer, instance)


@receiver(post_delete, sender=Set)
def delete_set(sender, instance, **kwargs):
    solr_delete(SetSearchSerializer, instance)
