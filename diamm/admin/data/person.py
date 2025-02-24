from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db import models
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from pagedown.widgets import AdminPagedownWidget
from reversion.admin import VersionAdmin

from diamm.admin.forms.merge_people import MergePeopleForm
from diamm.admin.helpers.optimized_raw_id import RawIdWidgetAdminMixin
from diamm.admin.merge_models import merge
from diamm.models import ItemComposer
from diamm.models.data.composition_composer import CompositionComposer
from diamm.models.data.organization import Organization
from diamm.models.data.person import Person
from diamm.models.data.person_identifier import PersonIdentifier
from diamm.models.data.person_note import PersonNote
from diamm.models.data.person_role import PersonRole
from diamm.models.data.source_copyist import SourceCopyist
from diamm.models.data.source_provenance import SourceProvenance
from diamm.models.data.source_relationship import SourceRelationship


class CompositionsInline(RawIdWidgetAdminMixin, admin.TabularInline):
    verbose_name = "Composition"
    verbose_name_plural = "Compositions"
    model = CompositionComposer
    extra = 0
    raw_id_fields = ("composition",)
    classes = ("collapse",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


class PersonNoteInline(admin.TabularInline):
    verbose_name = "Note"
    verbose_name_plural = "Notes"
    model = PersonNote
    extra = 0

    formfield_overrides = {models.TextField: {"widget": AdminPagedownWidget}}


class PersonIdentifierInline(admin.TabularInline):
    verbose_name = "Identifier"
    model = PersonIdentifier
    extra = 0
    readonly_fields = ("get_external_url",)

    @admin.display(description="URL")
    def get_external_url(self, instance) -> str:
        if not instance.identifier_type:
            return ""
        return mark_safe(  # noqa: S308
            f'<a href="{instance.identifier_url}">{instance.identifier_url}</a>'
        )


class PersonRoleInline(admin.TabularInline):
    verbose_name = "Role"
    verbose_name_plural = "Roles"
    model = PersonRole
    extra = 0
    raw_id_fields = ("role",)


class CopiedSourcesInline(GenericTabularInline):
    verbose_name = "Source Copied"
    verbose_name_plural = "Sources Copied"
    model = SourceCopyist
    extra = 0
    raw_id_fields = ("source",)


class RelatedSourcesInline(GenericTabularInline):
    model = SourceRelationship
    extra = 0
    raw_id_fields = ("source",)


class ProvenanceSourcesInline(GenericTabularInline):
    model = SourceProvenance
    extra = 0
    raw_id_fields = ("source", "city", "country", "region", "protectorate")


def migrate_to_organization(modeladmin, request, queryset):
    """
    Migrates a person to an organzation. Also migrates any relationships
    that may point to that person.
    """
    for entity in queryset:
        d = {"legacy_id": entity.legacy_id, "name": entity.last_name}

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


class PersonBiography(admin.SimpleListFilter):
    title = _("Has Biography")
    parameter_name = "biography"

    def lookups(self, request, model_admin):
        return (("yes", _("Has biography")), ("no", _("Does not have biography")))

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        if self.value() == "yes":
            return queryset.filter(notes__type=1)
        elif self.value() == "no":
            return queryset


class PersonUnattributedInline(RawIdWidgetAdminMixin, admin.TabularInline):
    verbose_name = "Unattributed Item"
    verbose_name_plural = "Unattributed Items"
    model = ItemComposer
    extra = 0
    raw_id_fields = ("item",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(Person)
class PersonAdmin(VersionAdmin):
    save_on_top = True
    list_display = (
        "last_name",
        "first_name",
        "title",
        "earliest_year",
        "latest_year",
        "floruit",
        "updated",
    )
    search_fields = ("last_name", "first_name", "title")
    inlines = (
        PersonNoteInline,
        PersonRoleInline,
        PersonIdentifierInline,
        CopiedSourcesInline,
        RelatedSourcesInline,
        ProvenanceSourcesInline,
        CompositionsInline,
        PersonUnattributedInline,
    )
    actions = ["merge_people_action"]
    # filter_horizontal = ('roles',)
    list_filter = [PersonBiography]
    view_on_site = True
    readonly_fields = ("created", "updated")

    formfield_overrides = {models.TextField: {"widget": AdminPagedownWidget}}

    def get_queryset(self, request):
        qset = (
            super()
            .get_queryset(request)
            .prefetch_related("compositions", "unattributed_works__item__source")
        )
        return qset

    def merge_people_action(self, request, queryset):
        if "do_action" in request.POST:
            form = MergePeopleForm(request.POST)

            if form.is_valid():
                keep_old = form.cleaned_data["keep_old"]
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
                return
            else:
                messages.error(request, "There was an error")
        else:
            form = MergePeopleForm()

        return render(
            request,
            "admin/person/merge_people.html",
            {"objects": queryset, "form": form},
        )

    merge_people_action.short_description = "Merge People"
