from django.contrib import admin, messages
from django.shortcuts import render
from django.contrib.contenttypes.admin import GenericTabularInline
from diamm.admin.forms.update_organization_type import UpdateOrganizationTypeForm
from diamm.models.data.organization import Organization
from diamm.models.data.source_copyist import SourceCopyist
from diamm.models.data.source_relationship import SourceRelationship
from diamm.models.data.source_provenance import SourceProvenance
from diamm.admin.forms.merge_organizations import MergeOrganizationsForm
from diamm.admin.merge_models import merge
from reversion.admin import VersionAdmin
from dynamic_raw_id.admin import DynamicRawIDMixin


class CopiedSourcesInline(DynamicRawIDMixin, GenericTabularInline):
    verbose_name = "Source Copied"
    verbose_name_plural = "Sources Copied"
    model = SourceCopyist
    extra = 0
    dynamic_raw_id_fields = ('source',)


class RelatedSourcesInline(DynamicRawIDMixin, GenericTabularInline):
    model = SourceRelationship
    extra = 0
    dynamic_raw_id_fields = ('source',)


class ProvenanceSourcesInline(DynamicRawIDMixin, GenericTabularInline):
    model = SourceProvenance
    extra = 0
    dynamic_raw_id_fields = ('source', 'city', 'country', 'region', 'protectorate')


@admin.register(Organization)
class OrganizationAdmin(DynamicRawIDMixin, VersionAdmin):
    save_on_top = True
    list_display = ('name', 'location', 'type', 'legacy_id')
    list_filter = ('type',)
    search_fields = ('name', 'location__name')
    inlines = (CopiedSourcesInline, ProvenanceSourcesInline, RelatedSourcesInline)
    actions = ['update_organization_action', 'merge_organizations_action']

    dynamic_raw_id_fields = ('location', 'archive')

    def update_organization_action(self, request, queryset):
        if 'do_action' in request.POST:
            form = UpdateOrganizationTypeForm(request.POST)

            if form.is_valid():
                org_type = form.cleaned_data['org_type']
                updated = queryset.update(type=org_type)
                messages.success(request, "{0} organizations were updated.".format(updated))
                return
            else:
                messages.error(request, "There was an error.")
        else:
            form = UpdateOrganizationTypeForm()

        return render(request,
                      'admin/organization/update_organization_type.html', {
                          'objects': queryset,
                          'form': form
                      })

    update_organization_action.short_description = "Update organization type"

    def merge_organizations_action(self, request, queryset):
        if 'do_action' in request.POST:
            form = MergeOrganizationsForm(request.POST)

            if form.is_valid():
                keep_old = form.cleaned_data['keep_old']
                target = queryset.first()
                remainder = list(queryset[1:])
                merged = merge(target, remainder, keep_old=keep_old)

                # Trigger saves for Solr
                for relationship in merged.sources_related.all():
                    relationship.source.save()

                for provenance in merged.sources_provenance.all():
                    provenance.source.save()

                for copied in merged.sources_copied.all():
                    copied.source.save()

                messages.success(request, "Objects successfully merged")
                return
            else:
                messages.error(request, "There was an error merging these organizations")
        else:
            form = MergeOrganizationsForm()

        return render(request,
                      'admin/organization/merge_organization.html', {
                        'objects': queryset,
                        'form': form
                      })
    merge_organizations_action.short_description = "Merge Organizations"

