from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db import models
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from pagedown.widgets import AdminPagedownWidget
from reversion.admin import VersionAdmin

from diamm.admin.forms.merge_people import MergePeopleForm
from diamm.admin.helpers.html import admin_change_link
from diamm.admin.helpers.optimized_raw_id import RawIdWidgetAdminMixin
from diamm.admin.merge_models import MergeConflictError, merge
from diamm.models import ItemComposer
from diamm.models.data.composition_composer import CompositionComposer
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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("person")


class PersonIdentifierInline(admin.TabularInline):
    verbose_name = "Identifier"
    model = PersonIdentifier
    extra = 0
    readonly_fields = ("get_external_url",)

    @admin.display(description="URL")
    def get_external_url(self, instance) -> str:
        if not instance.identifier_type:
            return ""
        return admin_change_link(instance.identifier_url, instance.identifier_url)


class PersonRoleInline(admin.TabularInline):
    verbose_name = "Role"
    verbose_name_plural = "Roles"
    model = PersonRole
    extra = 0
    raw_id_fields = ("role",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("person", "role")


class CopiedSourcesInline(GenericTabularInline):
    verbose_name = "Source Copied"
    verbose_name_plural = "Sources Copied"
    model = SourceCopyist
    extra = 0
    raw_id_fields = ("source",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("source__archive", "content_type")
        )


class RelatedSourcesInline(GenericTabularInline):
    model = SourceRelationship
    extra = 0
    raw_id_fields = ("source",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("source__archive", "content_type")
        )


class ProvenanceSourcesInline(GenericTabularInline):
    model = SourceProvenance
    extra = 0
    raw_id_fields = ("source", "city", "country", "region", "protectorate")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("source__archive", "content_type")
        )


class PersonBiography(admin.SimpleListFilter):
    title = _("Has Biography")
    parameter_name = "biography"

    def lookups(self, request, model_admin):
        return ("yes", _("Has biography")), ("no", _("Does not have biography"))

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        if self.value() == "yes":
            return queryset.filter(notes__type=1).distinct()
        if self.value() == "no":
            return queryset.exclude(notes__type=1)
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
        return super().get_queryset(request)

    @admin.action(description="Merge People")
    def merge_people_action(self, request, queryset):
        if "do_action" in request.POST:
            form = MergePeopleForm(request.POST, queryset=queryset)

            if form.is_valid():
                keep_old = form.cleaned_data["keep_old"]
                target = form.cleaned_data["target"]
                remainder = list(queryset.exclude(pk=target.pk))
                try:
                    merged = merge(target, remainder, keep_old=keep_old)
                except MergeConflictError as exc:
                    messages.error(request, str(exc))
                    merged = None

                # Trigger a save for all the records to update it in solr.
                if merged is not None:
                    for composition in merged.compositions.all():
                        composition.composition.save()

                    for scopied in merged.sources_copied.all():
                        scopied.save()

                    for srelated in merged.sources_related.all():
                        srelated.save()

                    for sprovenance in merged.sources_provenance.all():
                        sprovenance.save()

                    messages.success(request, "Objects successfully merged.")
                    return None
            else:
                messages.error(request, "There was an error")
        else:
            form = MergePeopleForm(queryset=queryset)

        return render(
            request,
            "admin/person/merge_people.html",
            {
                **self.admin_site.each_context(request),
                "objects": queryset,
                "form": form,
                "opts": self.model._meta,
                "title": "Merge people",
            },
        )
