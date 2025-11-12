from django.contrib import admin

from diamm.models import ProjectSources


@admin.register(ProjectSources)
class ProjectSourcesAdmin(admin.ModelAdmin):
    filter_horizontal = ["sources"]
    prepopulated_fields = {"slug": ["project"]}
