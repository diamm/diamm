from rest_framework import views
from rest_framework.response import Response
from diamm.models.data.source import Source
from diamm.models.data.archive import Archive
from diamm.models.data.image import Image
from diamm.models.data.composition import Composition
from diamm.models.data.person import Person
from diamm.models.data.organization import Organization


class HomeView(views.APIView):
    template_name = "index.jinja2"

    def _counts(self):
        num_sources = Source.objects.count()
        num_archives = Archive.objects.count()
        num_images = Image.objects.count()
        num_compositions = Composition.objects.count()
        num_people = Person.objects.count()
        num_organizations = Organization.objects.count()

        return {
            'num_sources': num_sources,
            'num_archives': num_archives,
            'num_images': num_images,
            'num_compositions': num_compositions,
            'num_people': num_people,
            'num_organizations': num_organizations
        }

    def get(self, request, *args, **kwargs):
        return Response({
            'counts': self._counts()
        })
