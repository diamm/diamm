from django.contrib import admin
from django.urls import reverse

from diamm.admin.helpers.html import admin_change_link
from diamm.models.data.page import Page
from diamm.models.data.source import Source
from diamm.models.site.commentary import Commentary


@admin.register(Commentary)
class CommentaryAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "get_author_name",
        "created",
        "comment_type",
        "content_type",
    )
    list_filter = ("comment_type", "content_type")
    autocomplete_fields = ("author",)

    fields = ("comment", "author", "comment_type", "get_entity")

    readonly_fields = (
        "content_type",
        "object_id",
        "get_entity",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("author", "content_type")

    @admin.display(description="Author Name")
    def get_author_name(self, obj):
        return obj.author.full_name

    @admin.display(description="Commentary On")
    def get_entity(self, obj):
        if isinstance(obj.attachment, Source):
            url: str = reverse("source-detail", kwargs={"pk": obj.attachment.pk})
            return admin_change_link(url, f"{obj.attachment.display_name} (source)")
        elif isinstance(obj.attachment, Page):
            return "Page (not implemented)"
        else:
            return "Unknown (error?)"
