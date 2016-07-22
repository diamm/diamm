from rest_framework.renderers import TemplateHTMLRenderer

class SinglePageAppRenderer(TemplateHTMLRenderer):
    template_name = 'single_page_app.jinja2'

    def resolve_context(self, data, request, response):
        view_data = super().resolve_context(data, request, response)

        return { 'view_data': view_data }
