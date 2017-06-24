from django.contrib import admin, messages
from django.db import models
from django.shortcuts import render
from django.contrib.contenttypes.admin import GenericTabularInline
from pagedown.widgets import AdminPagedownWidget
from diamm.models.data.person import Person
from diamm.models.data.composition_composer import CompositionComposer
from diamm.models.data.person_note import PersonNote
from diamm.models.data.person_role import PersonRole
from diamm.models.data.source_copyist import SourceCopyist
from diamm.models.data.source_relationship import SourceRelationship
from diamm.models.data.source_provenance import SourceProvenance
from diamm.models.data.organization import Organization
from diamm.admin.forms.merge_people import MergePeopleForm
from diamm.admin.merge_models import merge
from reversion.admin import VersionAdmin
from salmonella.admin import SalmonellaMixin


class CompositionsInline(SalmonellaMixin, admin.TabularInline):
    verbose_name = "Composition"
    verbose_name_plural = "Compositions"
    model = CompositionComposer
    extra = 0
    salmonella_fields = ('composition',)


class PersonNoteInline(admin.TabularInline):
    verbose_name = "Note"
    verbose_name_plural = "Notes"
    model = PersonNote
    extra = 0

    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget}
    }


class PersonRoleInline(SalmonellaMixin, admin.TabularInline):
    verbose_name = "Role"
    verbose_name_plural = "Roles"
    model = PersonRole
    extra = 0
    salmonella_fields = ('role',)


class CopiedSourcesInline(SalmonellaMixin, GenericTabularInline):
    verbose_name = "Source Copied"
    verbose_name_plural = "Sources Copied"
    model = SourceCopyist
    extra = 0
    salmonella_fields = ('source',)


class RelatedSourcesInline(SalmonellaMixin, GenericTabularInline):
    model = SourceRelationship
    extra = 0
    salmonella_fields = ('source',)


class ProvenanceSourcesInline(SalmonellaMixin, GenericTabularInline):
    model = SourceProvenance
    extra = 0
    salmonella_fields = ('source', 'city', 'country', 'region', 'protectorate')


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
    list_display = ('last_name', 'first_name', 'earliest_year', 'latest_year', 'legacy_id')
    search_fields = ('last_name', 'first_name')
    inlines = (PersonNoteInline, PersonRoleInline,
               CopiedSourcesInline, RelatedSourcesInline, ProvenanceSourcesInline,
               CompositionsInline)
    actions = ['merge_people_action']
    # filter_horizontal = ('roles',)
    list_filter = []

    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget}
    }

    def get_queryset(self, request):
        qset = super(PersonAdmin, self).get_queryset(request)
        # qset = qset.prefetch_related('roles')
        return qset

    def merge_people_action(self, request, queryset):
        print('merging people')

        if 'do_action' in request.POST:
            print('do action called')
            form = MergePeopleForm(request.POST)

            if form.is_valid():
                print('form is valid')
                keep_old = form.cleaned_data['keep_old']
                target = queryset.first()
                remainder = list(queryset[1:])
                merged = merge(target, remainder, keep_old=keep_old)

                # Trigger a save for all the records to update it in solr.
                for composition in merged.compositions.all():
                    composition.composition.save()

                for scopied in merged.sources_copied.all():
                    scopied.save()

                for srelated in merged.sources_related.all():
                    srelated.save()

                for sprovenance in merged.sources_provenance.all():
                    sprovenance.save()

                messages.success(request, "Objects successfully merged.")
                print('returning in form is valid.')
                return
            else:
                messages.error(request, "There was an error")
                print('form is not valid')

        else:
            print('not in post')
            form = MergePeopleForm()

        print('returning render')
        return render(request,
                      'admin/person/merge_people.html', {
                          'objects': queryset,
                          'form': form
                      })

    merge_people_action.short_description = "Merge People"
