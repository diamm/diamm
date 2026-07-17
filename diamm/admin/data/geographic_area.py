from django.contrib import admin, messages
from django.shortcuts import render
from reversion.admin import VersionAdmin

from diamm.admin.forms.merge_areas import MergeAreasForm
from diamm.admin.merge_models import MergeConflictError, merge
from diamm.models.data.geographic_area import GeographicArea


@admin.register(GeographicArea)
class GeographicAreaAdmin(VersionAdmin):
    list_display = ("name", "area_type", "get_parent", "created", "updated")
    search_fields = ("name",)
    list_filter = ("type",)
    actions = ["merge_areas_action"]
    raw_id_fields = ("parent",)

    @admin.display(description="Parent", ordering="parent")
    def get_parent(self, obj):
        if obj.parent:
            return f"{obj.parent.name}"
        return None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("parent__parent")

    @admin.action(description="Merge Areas")
    def merge_areas_action(self, request, queryset):
        if "do_action" in request.POST:
            form = MergeAreasForm(request.POST, queryset=queryset)

            if form.is_valid():
                keep_old = form.cleaned_data["keep_old"]
                target = form.cleaned_data["target"]
                remainder = list(queryset.exclude(pk=target.pk))
                try:
                    merged = merge(target, remainder, keep_old=keep_old)
                except MergeConflictError as exc:
                    messages.error(request, str(exc))
                    merged = None

                if merged is not None:
                    for archive in merged.archives.all():
                        archive.save()

                    for source in merged.protectorate_sources.all():
                        source.save()

                    for source in merged.city_sources.all():
                        source.save()

                    for source in merged.country_sources.all():
                        source.save()

                    for source in merged.region_sources.all():
                        source.save()

                    for org in merged.organizations.all():
                        org.save()

                    messages.success(request, "Objects successfully merged")
                    return None
            else:
                messages.error(
                    request, "There was an error merging these organizations"
                )
        else:
            form = MergeAreasForm(queryset=queryset)

        return render(
            request,
            "admin/geographic_area/merge_areas.html",
            {
                **self.admin_site.each_context(request),
                "objects": queryset,
                "form": form,
                "opts": self.model._meta,
                "title": "Merge geographic areas",
            },
        )
