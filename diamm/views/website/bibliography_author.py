from rest_framework import generics

from diamm.models.data.bibliography_author import BibliographyAuthor
from diamm.serializers.website.bibliography_author import BibliographyAuthorSerializer


class BibliographyAuthorDetail(generics.RetrieveAPIView):
    template_name = "website/bibliography_author/bibliography_author_detail.jinja2"
    serializer_class = BibliographyAuthorSerializer
    queryset = BibliographyAuthor.objects.all()
