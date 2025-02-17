from django.contrib import admin
from django.utils.safestring import mark_safe
from rest_framework.reverse import reverse
from reversion.admin import VersionAdmin

from diamm.models.data.composition import Composition
from diamm.models.data.organization import Organization
from diamm.models.data.person import Person
from diamm.models.data.source import Source
from diamm.models.site.problem_report import ProblemReport


@admin.register(ProblemReport)
class ProblemReportAdmin(VersionAdmin):
    list_display = ("get_contributor", "get_entity", "created", "accepted")
    search_fields = (
        "contributor__last_name",
        "contributor__first_name",
        "contributor__email",
        "credit",
        "=object_id",
    )
    list_filter = ("accepted", "content_type")

    raw_id_fields = ("contributor",)

    fields = (
        "content_type",
        "object_id",
        # "get_entity",
        "note",
        "internal_note",
        "accepted",
        "summary",
        "credit",
        "contributor",
    )
    # readonly_fields = (
    #     "content_type",
    #     "object_id",
    #     "get_entity",
    # )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("contributor", "content_type").prefetch_related(
            "record__archive__city", "record"
        )

    def view_on_site(self, obj) -> str | None:
        if not isinstance(obj.record, Source):
            return None

        return reverse("source-detail", kwargs={"pk": obj.record.pk})

    def get_contributor(self, obj):
        if obj.contributor and obj.contributor.last_name and obj.contributor.first_name:
            return f"{obj.contributor.first_name} {obj.contributor.last_name}"
        elif obj.contributor:
            return f"{obj.contributor.get_username()}"
        else:
            return f"{obj.credit}"

    get_contributor.short_description = "contributor"

    def get_entity(self, obj):
        obj_pk = obj.record.id
        if isinstance(obj.record, Source):
            url = reverse("admin:diamm_data_source_change", args=[obj_pk])
            return mark_safe(f"<a href='{url}'>{obj.record.display_name} (source)</a>")  # noqa: S308
        elif isinstance(obj.record, Organization):
            url = reverse("admin:diamm_data_organization_change", args=[obj_pk])
            return mark_safe(f"<a href='{url}'>{obj.record.name} (organization)</a>")  # noqa: S308
        elif isinstance(obj.record, Person):
            url = reverse("admin:diamm_data_person_change", args=[obj_pk])
            return mark_safe(f"<a href='{url}'>{obj.record.full_name} (person)</a>")  # noqa: S308
        elif isinstance(obj.record, Composition):
            url = reverse("admin:diamm_data_composition_change", args=[obj_pk])
            return mark_safe(f"<a href='{url}'>{obj.record.title} (composition)</a>")  # noqa: S308

    get_entity.short_description = "entity"
