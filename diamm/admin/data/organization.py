from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.shortcuts import render
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from diamm.admin.forms.merge_organizations import MergeOrganizationsForm
from diamm.admin.forms.update_organization_type import UpdateOrganizationTypeForm
from diamm.admin.merge_models import merge
from diamm.models import OrganizationIdentifier
from diamm.models.data.organization import Organization
from diamm.models.data.source_copyist import SourceCopyist
from diamm.models.data.source_provenance import SourceProvenance
from diamm.models.data.source_relationship import SourceRelationship


class CopiedSourcesInline(GenericTabularInline):
    verbose_name = "Source Copied"
    verbose_name_plural = "Sources Copied"
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
    raw_id_fields = ('source',
                     'city',
                     'country',
                     'region',
                     'protectorate')


class OrganizationIdentifierInline(admin.TabularInline):
    verbose_name = "Identifier"
    model = OrganizationIdentifier
    extra = 0
    readonly_fields = ("get_external_url",)

    @admin.display(description="URL")
    def get_external_url(self, instance) -> str:
        if not instance.identifier_type:
            return ""
        return mark_safe(f'<a href="{instance.identifier_url}">{instance.identifier_url}</a>')



@admin.register(Organization)
class OrganizationAdmin(VersionAdmin):
    save_on_top = True
    list_display = ('name', 'location', 'type', 'updated')
    list_filter = ('type',)
    search_fields = ('name', 'location__name', 'variant_names')
    inlines = (CopiedSourcesInline,
               ProvenanceSourcesInline,
               RelatedSourcesInline,
               OrganizationIdentifierInline)
    actions = ['update_organization_action', 'merge_organizations_action']
    view_on_site = True
    readonly_fields = ('created', 'updated')
    raw_id_fields = ('location', 'archive')

    def update_organization_action(self, request, queryset):
        if 'do_action' in request.POST:
            form = UpdateOrganizationTypeForm(request.POST)

            if form.is_valid():
                org_type = form.cleaned_data['org_type']
                updated = queryset.update(type=org_type)
                messages.success(request, f"{updated} organizations were updated.")
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

