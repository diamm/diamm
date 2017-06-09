from django.dispatch import receiver
from django.db.models.signals import post_save
from diamm.models.data.geographic_area import GeographicArea
from diamm.serializers.search.archive import ArchiveSearchSerializer
from diamm.serializers.search.organization import OrganizationSearchSerializer
from diamm.serializers.search.source import SourceSearchSerializer
from diamm.helpers.solr_helpers import solr_index, solr_index_many


# A geographic area has relationships with a lot of different models. This will ensure that
# saving a geographic area will update the related objects. Since we don't store Geographic Areas
# in Solr, we don't need to have a delete method.
@receiver(post_save, sender=GeographicArea)
def index_geo_area(sender, instance, created, **kwargs):
    print('reindexing stuff')
    solr_index_many(ArchiveSearchSerializer, instance.archives.all())
    solr_index_many(OrganizationSearchSerializer, instance.organizations.all())
    # This iterates through the SourceProvenance records, so we need to grab the source from each of them
    # and index that.
    for sourceprov in instance.city_sources.all():
        solr_index(SourceSearchSerializer, sourceprov.source)

    for sourceprov in instance.region_sources.all():
        solr_index(SourceSearchSerializer, sourceprov.source)

    for sourceprov in instance.country_sources.all():
        solr_index(SourceSearchSerializer, sourceprov.source)

    for sourceprov in instance.protectorate_sources.all():
        solr_index(SourceSearchSerializer, sourceprov.source)