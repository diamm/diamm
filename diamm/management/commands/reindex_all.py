from django.core.management.base import BaseCommand
from django.conf import settings
import scorched
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
            self.stdout.write('{0} {1}: {2}'.format(term.blue('Indexing'),
                                                    term.green(obj.__class__.__name__),
                                                    term.yellow(getattr(obj, name_field))))
            data = serializer(obj).data
            docs.append(data)

            # queue up the docs and index them at every 100 records.
            # This saves expensive calls out to Solr so it should make
            # indexing quite quick.
            if i % 100 == 0:
                self.solrconn.add(docs)
                self.solrconn.commit()
                del docs
                docs = []

        pbar.finish()

    def _index_sources(self):
        self.stdout.write(term.blue('Indexing Sources'))
        objs = Source.objects.all()
        self._index(objs, 'shelfmark', SourceSearchSerializer)

    def _index_archives(self):
        self.stdout.write(term.blue('Indexing Archives'))
        objs = Archive.objects.all()
        self._index(objs, 'name', ArchiveSearchSerializer)

    def _index_people(self):
        self.stdout.write(term.blue("Indexing People"))
        objs = Person.objects.all()
        self._index(objs, 'full_name', PersonSearchSerializer)

    def _index_compositions(self):
        self.stdout.write(term.blue("Indexing Compositions"))
        objs = Composition.objects.all()
        self._index(objs, 'name', CompositionSearchSerializer)

    def _index_organizations(self):
        self.stdout.wirte(term.blue("Indexing Organizations"))
        objs = Organization.objects.all()
        self._index(objs, 'name', OrganizationSearchSerializer)

    def handle(self, *args, **kwargs):
        self.solrconn = scorched.SolrInterface(settings.SOLR['SERVER'])

        with term.fullscreen():
            self._index_sources()
            self._index_archives()
            self._index_people()
            self._index_compositions()
            raw_input = input('Done indexing. Press any key to exit.')

