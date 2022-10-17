from django.contrib import admin
from diamm.models.site.commentary import Commentary
from rest_framework.reverse import reverse
from django.utils.safestring import mark_safe
from diamm.models.data.source import Source
from diamm.models.data.page import Page


@admin.register(Commentary)
class CommentaryAdmin(admin.ModelAdmin):
    list_display = ('author', 'get_author_name', 'created', 'comment_type', 'content_type')
    list_filter = ('comment_type', 'content_type')

    fields = (
        'comment',
        'author',
        'comment_type',
        'get_entity'
    )

    readonly_fields = ('content_type', 'object_id', 'get_entity',)

    def get_author_name(self, obj):
        return obj.author.full_name
    get_author_name.short_description = "Author Name"

    def get_entity(self, obj):
        if isinstance(obj.attachment, Source):
            url: str = reverse('source-detail', kwargs={"pk": obj.attachment.pk})
            return mark_safe(f'<a href="{url}">{obj.attachment.display_name} (source)</a>')
        elif isinstance(obj.attachment, Page):
            return "Page (not implemented)"
        else:
            return "Unknown (error?)"
    get_entity.short_description = "Commentary On"

