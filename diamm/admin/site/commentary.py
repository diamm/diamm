from django.contrib import admin
from diamm.models.site.commentary import Commentary


@admin.register(Commentary)
class CommentaryAdmin(admin.ModelAdmin):
    list_display = ('author', 'get_author_name', 'created', 'comment_type', 'content_type')
    list_filter = ('comment_type', 'content_type')

    def get_author_name(self, obj):
        return obj.author.full_name
    get_author_name.short_description = "Author Name"
