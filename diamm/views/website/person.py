from django.db.models import Prefetch
from rest_framework import generics
from diamm.models.data.person import Person
from diamm.models.data.composition import Composition
from diamm.serializers.website.person import PersonListSerializer, PersonDetailSerializer


class PersonList(generics.ListAPIView):
    template_name = "website/person/person_list.html"
    queryset = Person.objects.all()
    serializer_class = PersonListSerializer


class PersonDetail(generics.RetrieveAPIView):
    template_name = "website/person/person_detail.html"
    serializer_class = PersonDetailSerializer

    def get_queryset(self):
        cc_queryset = Composition.objects.all()
        queryset = Person.objects.prefetch_related(
            Prefetch('compositions__composition__sources__source__archive__city', queryset=cc_queryset),
        )
        return queryset
