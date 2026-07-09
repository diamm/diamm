from model_bakery import baker
from rest_framework.test import APITestCase


class TestSourceRelationship(APITestCase):
    def setUp(self):
        self.src = baker.make("diamm_data.Source", shelfmark="Q.15")
        self.person = baker.make("diamm_data.Person", last_name="Smith")
        self.org_type = baker.make("diamm_data.OrganizationType")
        self.org = baker.make(
            "diamm_data.Organization", name="Foo Corp.", type=self.org_type
        )

    def tearDown(self):
        pass

    def test_relationship_to_person(self):
        sr = baker.make(
            "diamm_data.SourceRelationship", source=self.src, related_entity=self.person
        )
        self.assertIsNotNone(sr)
        self.assertEqual(sr.related_entity, self.person)

    def test_relationship_to_organization(self):
        sr = baker.make(
            "diamm_data.SourceRelationship", source=self.src, related_entity=self.org
        )
        self.assertIsNotNone(sr)
        self.assertEqual(sr.related_entity, self.org)

    def test_multiple_relationships(self):
        sr1 = baker.make(
            "diamm_data.SourceRelationship", source=self.src, related_entity=self.person
        )
        sr2 = baker.make(
            "diamm_data.SourceRelationship", source=self.src, related_entity=self.org
        )

        self.assertEqual(self.src.relationships.count(), 2)
        self.assertEqual(sr1.source, self.src)
        self.assertEqual(sr2.source, self.src)

    def test_source_copyist_migration(self):
        """
        Tests the migration from a person to an organization for copyist.
        """
        sc = baker.make(
            "diamm_data.SourceCopyist", source=self.src, copyist=self.person
        )
        self.assertEqual(sc.copyist, self.person)

        sc.copyist = self.org
        sc.save()

        self.assertEqual(sc.copyist, self.org)

    def test_multiple_types_of_source_relationships(self):
        sc = baker.make(
            "diamm_data.SourceCopyist", source=self.src, copyist=self.person
        )
        pers2 = baker.make("diamm_data.Person", last_name="Jones")
        org2 = baker.make("diamm_data.Organization", name="Bar Inc.", type=self.org_type)

        sr = baker.make(
            "diamm_data.SourceRelationship", source=self.src, related_entity=self.person
        )

        sr2 = baker.make(
            "diamm_data.SourceRelationship", source=self.src, related_entity=self.org
        )

        sc1 = baker.make("diamm_data.SourceCopyist", source=self.src, copyist=pers2)
        sp1 = baker.make("diamm_data.SourceProvenance", source=self.src, entity=org2)

        src_relationship_ents = [s.related_entity for s in self.src.relationships.all()]
        src_copyists_ents = [s.copyist for s in self.src.copyists.all()]

        self.assertIn(self.person, src_relationship_ents)
        self.assertIn(pers2, src_copyists_ents)
