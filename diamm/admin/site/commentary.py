from django.contrib import admin
from diamm.models.site.commentary import Commentary


@admin.register(Commentary)
class CommentaryAdmin(admin.ModelAdmin):
    list_display = ('author', 'created', 'comment_type', 'content_type')
    list_filter = ('comment_type', 'content_type')
