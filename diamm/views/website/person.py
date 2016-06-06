from django.db.models import Prefetch
from django.shortcuts import redirect
from rest_framework import generics
from diamm.models.data.person import Person
from diamm.models.data.composition import Composition
from diamm.serializers.website.person import PersonDetailSerializer


# class PersonList(generics.ListAPIView):
#     template_name = "website/person/person_list.jinja2"
#     queryset = Person.objects.all()
#     serializer_class = PersonListSerializer
#

class PersonDetail(generics.RetrieveAPIView):
    template_name = "website/person/person_detail.jinja2"
    serializer_class = PersonDetailSerializer

    def get_queryset(self):
        cc_queryset = Composition.objects.all()
        # This lets us prefetch on Generic Foreign Relations.
        queryset = Person.objects.prefetch_related(
            Prefetch('compositions__composition__sources__source__archive__city', queryset=cc_queryset),
        )
        return queryset


def legacy_composer_redirect(request, legacy_id):
    legacy_lookup = "legacy_composer.{0}".format(legacy_id)
    person = Person.objects.get(legacy_id=legacy_lookup)
    return redirect('person-detail', pk=person.pk)
