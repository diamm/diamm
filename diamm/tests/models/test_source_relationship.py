from rest_framework.test import APITestCase
from model_mommy import mommy
from django.db.models import signals
from diamm.models.data.source import Source
from diamm.models.data.person import Person
from diamm.signals.source_signals import index_source, delete_source
from diamm.signals.person_signals import index_person, delete_person


class TestSourceRelationship(APITestCase):
    def setUp(self):
        signals.post_save.disconnect(index_source, sender=Source)
        signals.post_save.disconnect(index_person, sender=Person)
        signals.post_delete.disconnect(delete_source, sender=Source)
        signals.post_delete.disconnect(delete_person, sender=Person)

        self.src = mommy.make("diamm_data.Source",
                              shelfmark="Q.15")
        self.person = mommy.make("diamm_data.Person",
                                 last_name="Smith")
        self.org = mommy.make("diamm_data.Organization",
                              name="Foo Corp.")

    def tearDown(self):
        pass

    def test_relationship_to_person(self):
        sr = mommy.make("diamm_data.SourceRelationship",
                        source=self.src,
                        related_entity=self.person)
        self.assertIsNotNone(sr)
        self.assertEqual(sr.related_entity, self.person)

    def test_relationship_to_organization(self):
        sr = mommy.make("diamm_data.SourceRelationship",
                        source=self.src,
                        related_entity=self.org)
        self.assertIsNotNone(sr)
        self.assertEqual(sr.related_entity, self.org)

    def test_multiple_relationships(self):
        sr1 = mommy.make("diamm_data.SourceRelationship",
                         source=self.src,
                         related_entity=self.person)
        sr2 = mommy.make("diamm_data.SourceRelationship",
                         source=self.src,
                         related_entity=self.org)

        self.assertEqual(self.src.relationships.count(), 2)
        self.assertEqual(sr1.source, self.src)
        self.assertEqual(sr2.source, self.src)
