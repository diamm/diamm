from diamm.helpers.solr_helpers import solr_delete, solr_index
from diamm.serializers.search_old.organization import OrganizationSearchSerializer


# @receiver(post_save, sender=Organization)
def index_organization(sender, instance, created, **kwargs):
    solr_index(OrganizationSearchSerializer, instance)


# @receiver(post_delete, sender=Organization)
def delete_organization(sender, instance, **kwargs):
    solr_delete(instance)
