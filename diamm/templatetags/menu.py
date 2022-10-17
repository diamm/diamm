
from django_jinja import library
import jinja2
from wagtail.models import Site


@library.global_function
@jinja2.pass_context
def get_site_root(context):
    return Site.find_for_request(context['request']).root_page


@library.global_function
@library.render_with("website/blocks/dropdown_menu.jinja2")
@jinja2.pass_context
def get_menu(context):
    parent = Site.find_for_request(context['request']).root_page
    menu_items = parent.get_children().live().in_menu()
    return {
        "menu_items": menu_items,
        "request": context['request']
    }
