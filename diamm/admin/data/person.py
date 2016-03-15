from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from diamm.models.data.person import Person
from diamm.models.data.item import Item
from diamm.models.data.person_note import PersonNote
from diamm.models.data.person_role import PersonRole
from diamm.models.data.source_copyist import SourceCopyist
from diamm.models.data.source_relationship import SourceRelationship
from diamm.models.data.source_provenance import SourceProvenance
from diamm.models.data.organization import Organization
from reversion.admin import VersionAdmin


class PersonNoteInline(admin.TabularInline):
    model = PersonNote
    extra = 0


class PersonRoleInline(admin.TabularInline):
    model = PersonRole
    extra = 0
    raw_id_fields = ('role',)


class CopiedSourcesInline(GenericTabularInline):
    model = SourceCopyist
    extra = 0
    raw_id_fields = ('source',)


class RelatedSourcesInline(GenericTabularInline):
    model = SourceRelationship
    extra = 0
    raw_id_fields = ('source',)


class ProvenanceSourcesInline(GenericTabularInline):
    model = SourceProvenance
    extra = 0
    raw_id_fields = ('source', 'city', 'country', 'region', 'protectorate')


def migrate_to_organization(modeladmin, request, queryset):
    """
        Migrates a person to an organzation. Also migrates any relationships
        that may point to that person.
    """
    for entity in queryset:
        d = {
            'legacy_id': entity.legacy_id,
            'name': entity.last_name
        }

        o = Organization(**d)
        o.save()

        # Check the original entry's relationships and migrate them.
        source_relationships = entity.sources_related.all()
        for rel in source_relationships:
            rel.related_entity = o
            rel.save()

        source_copyist = entity.sources_copied.all()
        for rel in source_copyist:
            rel.copyist = o
            rel.save()

        source_provenance = entity.sources_provenance.all()
        for rel in source_provenance:
            rel.entity = o
            rel.save()

        # delete the original entity.
        entity.delete()

migrate_to_organization.short_description = "Migrate Person to Organization"


@admin.register(Person)
class PersonAdmin(VersionAdmin):
    list_display = ('last_name', 'first_name', 'earliest_year', 'latest_year')
    search_fields = ('last_name', 'first_name')
    inlines = (PersonNoteInline, PersonRoleInline,
               CopiedSourcesInline, RelatedSourcesInline, ProvenanceSourcesInline)
    actions = (migrate_to_organization,)
    filter_horizontal = ('roles',)

    def get_queryset(self, request):
        qset = super(PersonAdmin, self).get_queryset(request)
        qset = qset.prefetch_related('roles')
        return qset
