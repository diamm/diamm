import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextSerializer, ContextDictSerializer

class BibliographySerializer(ContextDictSerializer):
    entry = serpy.MethodField()
    pk = serpy.IntField()

    def get_entry(self, obj):
        return obj['prerendered_sni']


class BibliographyAuthorSerializer(ContextSerializer):
    url = serpy.MethodField()
    last_name = serpy.StrField()
    first_name = serpy.StrField()
    bibliography = serpy.MethodField()

    def get_url(self, obj):
        return reverse('author-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])

    def get_bibliography(self, obj):
        return BibliographySerializer(obj.solr_bibliography,
                                      many=True,
                                      context={'request': self.context['request']}).data
