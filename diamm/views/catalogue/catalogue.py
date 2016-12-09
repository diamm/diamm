from django.views.generic import TemplateView


class CatalogueView(TemplateView):
    template_name = "catalogue/catalogue-index.jinja2"
