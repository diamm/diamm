from django.contrib import admin
from django.db.models import Count

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
