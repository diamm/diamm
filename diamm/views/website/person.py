from rest_framework import generics
from rest_framework import renderers
from diamm.models.data.person import Person
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.serializers.website.person import PersonListSerializer, PersonDetailSerializer


class PersonList(generics.ListAPIView):
    template_name = "website/person/person_list.html"
    queryset = Person.objects.all()
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
    serializer_class = PersonListSerializer


class PersonDetail(generics.RetrieveAPIView):
    template_name = "website/person/person_detail.html"
    queryset = Person.objects.all()
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
    serializer_class = PersonDetailSerializer
