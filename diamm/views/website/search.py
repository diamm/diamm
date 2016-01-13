from rest_framework import generics
from rest_framework import renderers
from rest_framework import response
from diamm.renderers.html_renderer import HTMLRenderer


class SearchView(generics.GenericAPIView):
    template_name = "website/search/search.html"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def get(self, request, *args, **kwargs):
        return response.Response({})
