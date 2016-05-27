from rest_framework import renderers
from rest_framework import views
from diamm.models.site.aboutpages import AboutPages
from diamm.renderers.html_renderer import HTMLRenderer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status



class AboutPagesDetail(views.APIView):
    template_name = "aboutpages_detail.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def get(self, request, *args, **kwargs):
        current_url = request.path
        aboutpages = get_object_or_404(AboutPages, url=current_url)
        return Response({
            'aboutpages': aboutpages
        })
       # return Response({}, status=status.HTTP_404_NOT_FOUND)


