from rest_framework import views
from rest_framework import renderers
from rest_framework.response import Response
from diamm.renderers.html_renderer import HTMLRenderer


class HomeView(views.APIView):
    template_name = "index.html"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def get(self, request, *args, **kwargs):
        return Response({})
