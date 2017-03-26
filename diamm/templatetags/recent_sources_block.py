from diamm.models.data.source import Source
from django_jinja import library


@library.global_function
@library.render_with("website/blocks/recently_added_sources.jinja2")
def recently_added_sources():
    return {
        "recently_added_sources": Source.objects.order_by('-id')[:5]
    }


@library.global_function
@library.render_with("website/blocks/recently_updated_sources.jinja2")
def recently_updated_sources():
    # To avoid having the same sources in both 'recently created' and 'recently updated' we
    # exclude the recently added sources from the recently updated sources.
    recent_sources = Source.objects.order_by('-id')[:5]
    return {
        "recently_updated_sources": Source.objects.exclude(id__in=recent_sources.values_list('id')).order_by('-updated')[:5]
    }


