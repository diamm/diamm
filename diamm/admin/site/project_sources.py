from django.contrib import admin
from django.db.models import Count

from diamm.admin.helpers.source_picker import source_picker_label
from diamm.models import ProjectSources


@admin.register(ProjectSources)
class ProjectSourcesAdmin(admin.ModelAdmin):
    filter_horizontal = ["sources"]
    prepopulated_fields = {"slug": ["project"]}
    list_display = ("project", "source_count")

    @admin.display(description="Number of sources")
    def source_count(self, obj) -> str:
        return f"{obj.source_count}"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(source_count=Count("sources"))

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)

        if field is not None and db_field.name == "sources":
            queryset = field.queryset
            if queryset is not None:
                field.queryset = queryset.select_related("archive")

            field.label_from_instance = source_picker_label

        return field
