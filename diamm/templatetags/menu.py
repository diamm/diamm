from django_jinja import library
import jinja2


@library.global_function
@jinja2.contextfunction
def get_site_root(context):
    return context['request'].site.root_page


@library.global_function
@library.render_with("website/blocks/dropdown_menu.jinja2")
@jinja2.contextfunction
def get_menu(context):
    parent = context['request'].site.root_page
    menu_items = parent.get_children().live().in_menu()
    return {
        "menu_items": menu_items,
        "request": context['request']
    }
