import jinja2
from django_jinja import library
from wagtail.models import Page, Site


@library.global_function
@jinja2.pass_context
def get_site_root(context):
    return Site.find_for_request(context["request"]).root_page


@library.global_function
@library.render_with("website/blocks/dropdown_menu.jinja2")
@jinja2.pass_context
def get_menu(context):
    request = context["request"]
    site = Site.find_for_request(request)
    root = site.root_page
    pages = (
        Page.objects.live()
        .in_menu()
        .filter(
            path__startswith=root.path,
            depth__in=(root.depth + 1, root.depth + 2),
        )
        .order_by("path")
    )

    menu_items = []
    parents = {}
    for page in pages:
        item = {
            "title": page.title,
            "url": page.get_url(request=request),
            "children": [],
        }
        if page.depth == root.depth + 1:
            menu_items.append(item)
            parents[page.path] = item
        else:
            parent = parents.get(page.path[:-4])
            if parent:
                parent["children"].append(item)

    return {"menu_items": menu_items}
