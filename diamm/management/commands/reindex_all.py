from django.core.management.base import BaseCommand
from django.conf import settings
import pysolr
from blessings import Terminal
import progressbar

from diamm.models.data.source import Source
from diamm.serializers.search.source import SourceSearchSerializer
from diamm.models.data.archive import Archive
from diamm.serializers.search.archive import ArchiveSearchSerializer
from diamm.models.data.person import Person
from diamm.serializers.search.person import PersonSearchSerializer
from diamm.models.data.composition import Composition
from diamm.serializers.search.composition import CompositionSearchSerializer
from diamm.models.data.organization import Organization
from diamm.serializers.search.organization import OrganizationSearchSerializer
from diamm.models.data.bibliography import Bibliography
from diamm.serializers.search.bibliography import BibliographySearchSerializer
from diamm.models.data.item import Item
from diamm.serializers.search.item import ItemSearchSerializer
from diamm.models.data.page import Page
from diamm.serializers.search.page import PageSearchSerializer
from diamm.models.data.set import Set
from diamm.serializers.search.set import SetSearchSerializer
from diamm.models.data.source_provenance import SourceProvenance
from diamm.serializers.search.source_provenance import SourceProvenanceSearchSerializer
from diamm.models.data.source_relationship import SourceRelationship
from diamm.serializers.search.source_relationship import SourceRelationshipSerializer
from diamm.models.data.source_copyist import SourceCopyist
from diamm.serializers.search.source_copyist import SourceCopyistSearchSerializer
from diamm.models.data.item_bibliography import ItemBibliography
from diamm.serializers.search.item_bibliography import ItemBibliographySearchSerializer
from diamm.models.data.voice import Voice
from diamm.serializers.search.voice import VoiceSearchSerializer

term = Terminal()


class Writer:
    def __init__(self, location):
        self.location = location

    def write(self, string):
        with term.location(*self.location):
            print(string)


class Command(BaseCommand):
    def _index(self, objects, name_field, serializer):
        num_sources = objects.count()
        writer = Writer((1, 1))
        pbar = progressbar.ProgressBar(fd=writer, max_value=num_sources)

        docs = []
        for i, obj in enumerate(objects):
            pbar.update(i)
            if not name_field:
                name = "Object {0}".format(obj.pk)
            else:
                name = getattr(obj, name_field)

            self.stdout.write('{0} {1}: {2} ({3})'.format(term.blue('Indexing'),
                                                    term.green(obj.__class__.__name__),
                                                    term.yellow(name),
                                                    term.yellow(str(obj.pk))))
            data = serializer(obj).data
            docs.append(data)

            # queue up the docs and index them at every 100 records.
            # This saves expensive calls out to Solr so it should make
            # indexing quite quick.
            if i % 100 == 0:
                self.solrconn.add(docs)
                del docs
                docs = []

        # ensure any leftovers are added
        self.solrconn.add(docs)
        pbar.finish()

    def _index_sources(self):
        self.stdout.write(term.blue('Indexing Sources'))
        self.solrconn.delete(q="type:source")
        objs = Source.objects.all().order_by('pk').select_related('archive__city__parent')
        objs = objs.prefetch_related('pages__images', 'sets', 'identifiers', 'copyists', 'inventory__composition', 'provenance')
        self._index(objs, 'shelfmark', SourceSearchSerializer)

    def _index_inventories(self):
        self.stdout.write(term.blue('Indexing Inventories'))
        self.solrconn.delete(q="type:item")
        objs = Item.objects.all()
        self._index(objs, '', ItemSearchSerializer)

    def _index_archives(self):
        self.stdout.write(term.blue('Indexing Archives'))
        self.solrconn.delete(q="type:archive")
        objs = Archive.objects.all()
        self._index(objs, 'name', ArchiveSearchSerializer)

    def _index_people(self):
        self.stdout.write(term.blue("Indexing People"))
        self.solrconn.delete(q="type:person")
        objs = Person.objects.all()
        self._index(objs, 'full_name', PersonSearchSerializer)

    def _index_compositions(self):
        self.stdout.write(term.blue("Indexing Compositions"))
        self.solrconn.delete(q="type:composition")
        objs = Composition.objects.all()
        self._index(objs, 'title', CompositionSearchSerializer)

    def _index_organizations(self):
        self.stdout.write(term.blue("Indexing Organizations"))
        self.solrconn.delete(q="type:organization")
        objs = Organization.objects.all()
        self._index(objs, 'name', OrganizationSearchSerializer)

    def _index_bibliography(self):
        self.stdout.write(term.blue("Indexing Bibliography"))
        self.solrconn.delete(q="type:bibliography")
        objs = Bibliography.objects.all()
        self._index(objs, 'title', BibliographySearchSerializer)

    def _index_pages(self):
        self.stdout.write(term.blue("Indexing Pages"))
        self.solrconn.delete(q="type:page")
        self.solrconn.delete(q="type:image")
        objs = Page.objects.all()
        self._index(objs, 'numeration', PageSearchSerializer)

    def _index_sets(self):
        self.stdout.write(term.blue("Indexing Sets"))
        self.solrconn.delete(q="type:set")
        self.solrconn.delete(q="type:child_source")
        objs = Set.objects.all()
        self._index(objs, 'cluster_shelfmark', SetSearchSerializer)

    def _index_source_provenance(self):
        self.stdout.write(term.blue("Indexing Source Provenance"))
        self.solrconn.delete(q="type:sourceprovenance")
        objs = SourceProvenance.objects.all()
        self._index(objs, '', SourceProvenanceSearchSerializer)

    def _index_source_relationship(self):
        self.stdout.write(term.blue("Indexing Source Relationships"))
        self.solrconn.delete(q="type:sourcerelationship")
        objs = SourceRelationship.objects.all()
        self._index(objs, '', SourceRelationshipSerializer)

    def _index_source_copyists(self):
        self.stdout.write(term.blue("Indexing Source Copyists"))
        self.solrconn.delete(q="type:sourcecopyist")
        objs = SourceCopyist.objects.all()
        self._index(objs, '', SourceCopyistSearchSerializer)

    def _index_item_bibliographies(self):
        self.stdout.write(term.blue("Indexing Item Bibliographies"))
        self.solrconn.delete(q="type:itembibliography")
        objs = ItemBibliography.objects.all()
        self._index(objs, "", ItemBibliographySearchSerializer)

    def _index_voices(self):
        self.stdout.write(term.blue("Indexing voices"))
        self.solrconn.delete(q="type:voice")
        objs = Voice.objects.all()
        self._index(objs, "", VoiceSearchSerializer)

    def handle(self, *args, **kwargs):
        self.solrconn = pysolr.Solr(settings.SOLR['SERVER'])
        self._index_sources()
        self._index_inventories()
        self._index_archives()
        self._index_people()
        self._index_organizations()
        self._index_compositions()
        self._index_bibliography()
        self._index_pages()
        self._index_sets()
        self._index_voices()
        self._index_source_provenance()
        self._index_source_relationship()
        self._index_source_copyists()
        self._index_item_bibliographies()

        raw_input = input('Done indexing. Press any key to exit.')

