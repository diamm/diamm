from django_jinja import library

from diamm.models.data.source import Source


@library.global_function
@library.render_with("website/blocks/recent_sources.jinja2")
def recently_added_sources():
    return {"sources": Source.objects.filter(public=True).order_by("-id")[:5]}


@library.global_function
@library.render_with("website/blocks/recent_sources.jinja2")
def recently_updated_sources():
    # To avoid having the same sources in both 'recently created' and 'recently updated' we
    # exclude the recently added sources from the recently updated sources.
    recent_sources = Source.objects.order_by("-id")[:5]
    return {
        "sources": Source.objects.filter(public=True).exclude(
            id__in=recent_sources.values_list("id")
        ).order_by("-updated")[:5]
    }
