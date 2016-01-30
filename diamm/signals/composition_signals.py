from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from diamm.models.data.composition import Composition
from diamm.serializers.search.composition import CompositionSearchSerializer
from diamm.helpers.solr_helpers import solr_delete, solr_index


@receiver(post_save, sender=Composition)
def index_composition(sender, instance, created, **kwargs):
    solr_index(CompositionSearchSerializer, instance)


@receiver(post_delete, sender=Composition)
def delete_composition(sender, instance, **kwargs):
    solr_delete(CompositionSearchSerializer, instance)
