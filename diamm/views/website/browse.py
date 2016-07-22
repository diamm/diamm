from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import generics

from diamm.renderers.single_page_renderer import SinglePageAppRenderer

class BrowseView(generics.GenericAPIView):
    renderer_classes = (SinglePageAppRenderer, JSONRenderer)

    def get(self, request, *args, **kwargs):
        return Response()
