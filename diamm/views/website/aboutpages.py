from rest_framework import renderers
from rest_framework import generics
from django.shortcuts import get_object_or_404
from diamm.models.site.aboutpages import AboutPages
from diamm.renderers.html_renderer import HTMLRenderer

from diamm.serializers.website.aboutpages import AboutPagesSerializer


class AboutPagesDetail(generics.RetrieveAPIView):
    template_name = "website/aboutpages/aboutpages_detail.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
    serializer_class = AboutPagesSerializer
    lookup_field = 'url'
    lookup_url_kwarg = 'url'

    def get_queryset(self):
        queryset = AboutPages.objects.filter(url=self.request.path)
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        filter = {}
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter)
        return obj



