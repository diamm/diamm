from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from diamm.models.data.bibliography import Bibliography
from diamm.serializers.search.bibliography import BibliographySearchSerializer
from diamm.helpers.solr_helpers import solr_delete, solr_index


@receiver(post_save, sender=Bibliography)
def index_bibliography(sender, instance, created, **kwargs):
    solr_index(BibliographySearchSerializer, instance)


@receiver(post_delete, sender=Bibliography)
def delete_bibliography(sender, instance, **kwargs):
    solr_delete(BibliographySearchSerializer, instance)
