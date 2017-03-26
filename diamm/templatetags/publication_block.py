from diamm.models.site.publication_page import PublicationPage
from django_jinja import library

@library.global_function
@library.render_with("website/blocks/publications_front_page.jinja2")
def publication_block():
    return {
        "publications": PublicationPage.objects.filter(show_on_front=True)[:5]
    }