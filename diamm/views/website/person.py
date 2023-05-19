from django.db.models import Prefetch
from django.shortcuts import redirect, get_object_or_404
from rest_framework import generics

from diamm.models.data.composition import Composition
from diamm.models.data.person import Person
from diamm.serializers.website.person import PersonDetailSerializer


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


# Since the old DIAMM IDs have been replaced with new ones, this
# call will handle redirections to the new records.
def legacy_composer_redirect(req, legacy_id: str) -> str:
    legacy_lookup = f"legacy_composer.{legacy_id}"
    person = get_object_or_404(Person, legacy_id=legacy_lookup)

    return redirect('person-detail', pk=person.pk)
