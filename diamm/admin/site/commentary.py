from django.contrib import admin
from diamm.models.site.commentary import Commentary


@admin.register(Commentary)
class CommentaryAdmin(admin.ModelAdmin):
    pass
