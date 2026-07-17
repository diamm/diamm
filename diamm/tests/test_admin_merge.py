from __future__ import annotations

from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker

from diamm.admin.merge_models import MergeConflictError, merge
from diamm.models.data.composition import Composition
from diamm.models.data.cycle_composer import CycleComposer
from diamm.models.data.geographic_area import GeographicArea
from diamm.models.data.organization import Organization
from diamm.models.data.person import Person
from diamm.models.data.source_copyist import SourceCopyist
from diamm.models.data.source_provenance import SourceProvenance
from diamm.models.data.source_relationship import SourceRelationship
from diamm.models.site.problem_report import ProblemReport


class MergeModelTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        baker.make("diamm_data.OrganizationType", id=1, name="Institution")

    def test_composition_merge_moves_relations_genres_and_problem_reports(self) -> None:
        primary = baker.make(
            "diamm_data.Composition", title="Primary", legacy_genre=None
        )
        alias = baker.make(
            "diamm_data.Composition", title="Alias", legacy_genre="Motet"
        )
        primary_genre, alias_genre = baker.make("diamm_data.Genre", _quantity=2)
        primary.genres.add(primary_genre)
        alias.genres.add(alias_genre)
        related = [
            baker.make("diamm_data.CompositionBibliography", composition=alias),
            baker.make("diamm_data.CompositionComposer", composition=alias),
            baker.make("diamm_data.CompositionCycle", composition=alias),
            baker.make("diamm_data.CompositionNote", composition=alias),
            baker.make("diamm_data.Item", composition=alias),
        ]
        report = baker.make(
            "diamm_site.ProblemReport", record=alias, note="Composition report"
        )

        merged = merge(primary, [alias])

        self.assertEqual(merged.pk, primary.pk)
        self.assertFalse(Composition.objects.filter(pk=alias.pk).exists())
        merged.refresh_from_db()
        self.assertEqual(merged.title, "Primary")
        self.assertEqual(merged.legacy_genre, "Motet")
        self.assertEqual(
            set(merged.genres.values_list("pk", flat=True)),
            {primary_genre.pk, alias_genre.pk},
        )
        for obj in related:
            obj.refresh_from_db()
            self.assertEqual(obj.composition_id, primary.pk)
        report.refresh_from_db()
        self.assertEqual(report.record, primary)

    def test_person_merge_moves_normal_and_generic_relations(self) -> None:
        primary = baker.make("diamm_data.Person", last_name="Primary", title=None)
        alias = baker.make("diamm_data.Person", last_name="Alias", title="Duke")
        normal_relations = [
            baker.make("diamm_data.CompositionComposer", composer=alias),
            baker.make("diamm_data.ItemComposer", composer=alias),
            baker.make("diamm_data.PersonIdentifier", person=alias),
            baker.make("diamm_data.PersonNote", person=alias),
            baker.make("diamm_data.PersonRole", person=alias),
        ]
        source = baker.make("diamm_data.Source")
        copyist = SourceCopyist(source=source, copyist=alias)
        copyist.save()
        relationship = SourceRelationship(
            source=source,
            related_entity=alias,
            relationship_type=baker.make("diamm_data.SourceRelationshipType"),
        )
        relationship.save()
        provenance = SourceProvenance(source=source, entity=alias)
        provenance.save()
        report = baker.make(
            "diamm_site.ProblemReport", record=alias, note="Person report"
        )

        merged = merge(primary, alias)

        merged.refresh_from_db()
        self.assertEqual(merged.title, "Duke")
        self.assertFalse(Person.objects.filter(pk=alias.pk).exists())
        for obj in normal_relations:
            obj.refresh_from_db()
            self.assertEqual(obj.composer_id if hasattr(obj, "composer_id") else obj.person_id, primary.pk)
        for obj, field_name in (
            (copyist, "copyist"),
            (relationship, "related_entity"),
            (provenance, "entity"),
        ):
            obj.refresh_from_db()
            self.assertEqual(getattr(obj, field_name), primary)
        report.refresh_from_db()
        self.assertEqual(report.record, primary)

    def test_exact_unique_related_duplicates_are_collapsed(self) -> None:
        primary, alias = baker.make("diamm_data.Person", _quantity=2)
        cycle = baker.make("diamm_data.Cycle")
        baker.make(
            "diamm_data.CycleComposer",
            cycle=cycle,
            composer=primary,
            uncertain=True,
            notes="Same",
        )
        baker.make(
            "diamm_data.CycleComposer",
            cycle=cycle,
            composer=alias,
            uncertain=True,
            notes="Same",
        )

        merge(primary, alias)

        self.assertEqual(
            CycleComposer.objects.filter(cycle=cycle, composer=primary).count(), 1
        )

    def test_conflicting_unique_related_rows_roll_back_the_complete_merge(self) -> None:
        primary = baker.make("diamm_data.Person", first_name=None)
        alias = baker.make("diamm_data.Person", first_name="From alias")
        cycle = baker.make("diamm_data.Cycle")
        primary_relation = baker.make(
            "diamm_data.CycleComposer",
            cycle=cycle,
            composer=primary,
            notes="Primary note",
        )
        alias_relation = baker.make(
            "diamm_data.CycleComposer",
            cycle=cycle,
            composer=alias,
            notes="Different alias note",
        )

        with self.assertRaises(MergeConflictError):
            merge(primary, alias)

        primary.refresh_from_db()
        alias.refresh_from_db()
        primary_relation.refresh_from_db()
        alias_relation.refresh_from_db()
        self.assertIsNone(primary.first_name)
        self.assertEqual(alias.first_name, "From alias")
        self.assertEqual(primary_relation.composer_id, primary.pk)
        self.assertEqual(alias_relation.composer_id, alias.pk)

    def test_organization_merge_moves_subtypes_identifiers_and_generic_relations(self) -> None:
        primary, alias = baker.make("diamm_data.Organization", _quantity=2)
        primary_subtype, alias_subtype = baker.make(
            "diamm_data.OrganizationSubtype", _quantity=2
        )
        primary.subtypes.add(primary_subtype)
        alias.subtypes.add(alias_subtype)
        identifier = baker.make(
            "diamm_data.OrganizationIdentifier", organization=alias
        )
        source = baker.make("diamm_data.Source")
        copyist = SourceCopyist(source=source, copyist=alias)
        copyist.save()
        report = baker.make(
            "diamm_site.ProblemReport", record=alias, note="Organization report"
        )

        merge(primary, alias)

        self.assertFalse(Organization.objects.filter(pk=alias.pk).exists())
        identifier.refresh_from_db()
        copyist.refresh_from_db()
        report.refresh_from_db()
        self.assertEqual(identifier.organization_id, primary.pk)
        self.assertEqual(copyist.copyist, primary)
        self.assertEqual(report.record, primary)
        self.assertEqual(
            set(primary.subtypes.values_list("pk", flat=True)),
            {primary_subtype.pk, alias_subtype.pk},
        )

    def test_geographic_area_merge_moves_each_relation_and_legacy_ids(self) -> None:
        primary, alias = baker.make("diamm_data.GeographicArea", _quantity=2)
        primary_legacy, alias_legacy = baker.make("diamm_data.LegacyId", _quantity=2)
        primary.legacy_id.add(primary_legacy)
        alias.legacy_id.add(alias_legacy)
        archive = baker.make("diamm_data.Archive", city=alias)
        child = baker.make("diamm_data.GeographicArea", parent=alias)
        organization = baker.make("diamm_data.Organization", location=alias)
        provenance = baker.make(
            "diamm_data.SourceProvenance",
            city=alias,
            country=alias,
            region=alias,
            protectorate=alias,
        )

        merge(primary, alias)

        self.assertFalse(GeographicArea.objects.filter(pk=alias.pk).exists())
        archive.refresh_from_db()
        child.refresh_from_db()
        organization.refresh_from_db()
        provenance.refresh_from_db()
        self.assertEqual(archive.city_id, primary.pk)
        self.assertEqual(child.parent_id, primary.pk)
        self.assertEqual(organization.location_id, primary.pk)
        self.assertEqual(provenance.city_id, primary.pk)
        self.assertEqual(provenance.country_id, primary.pk)
        self.assertEqual(provenance.region_id, primary.pk)
        self.assertEqual(provenance.protectorate_id, primary.pk)
        self.assertEqual(
            set(primary.legacy_id.values_list("pk", flat=True)),
            {primary_legacy.pk, alias_legacy.pk},
        )

    def test_keep_old_preserves_emptied_alias_record(self) -> None:
        primary, alias = baker.make("diamm_data.Composition", _quantity=2)
        genre = baker.make("diamm_data.Genre")
        alias.genres.add(genre)
        note = baker.make("diamm_data.CompositionNote", composition=alias)

        merge(primary, alias, keep_old=True)

        self.assertTrue(Composition.objects.filter(pk=alias.pk).exists())
        self.assertTrue(primary.genres.filter(pk=genre.pk).exists())
        self.assertFalse(alias.genres.filter(pk=genre.pk).exists())
        note.refresh_from_db()
        self.assertEqual(note.composition_id, primary.pk)


class MergeAdminActionTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Site.objects.create(domain="testserver", name="Test server")
        Site.objects.clear_cache()
        cls.superuser = baker.make(
            "diamm_site.CustomUserModel",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )

    def setUp(self) -> None:
        self.client.force_login(self.superuser)

    def test_composition_action_uses_the_explicit_target(self) -> None:
        first = baker.make("diamm_data.Composition", title="A first")
        target = baker.make("diamm_data.Composition", title="Z target")
        url = reverse("admin:diamm_data_composition_changelist")
        selection = [str(first.pk), str(target.pk)]

        preview = self.client.post(
            url,
            {
                "action": "merge_compositions_action",
                "_selected_action": selection,
                "index": "0",
            },
        )
        self.assertEqual(preview.status_code, 200)
        self.assertContains(preview, f'<option value="{target.pk}">')

        response = self.client.post(
            url,
            {
                "action": "merge_compositions_action",
                "_selected_action": selection,
                "do_action": "yes",
                "target": str(target.pk),
                "index": "0",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Composition.objects.filter(pk=first.pk).exists())
        self.assertTrue(Composition.objects.filter(pk=target.pk).exists())

    def test_person_action_reports_conflict_and_preserves_records(self) -> None:
        primary, alias = baker.make("diamm_data.Person", _quantity=2)
        cycle = baker.make("diamm_data.Cycle")
        baker.make(
            "diamm_data.CycleComposer",
            cycle=cycle,
            composer=primary,
            notes="Primary",
        )
        baker.make(
            "diamm_data.CycleComposer",
            cycle=cycle,
            composer=alias,
            notes="Alias conflict",
        )
        url = reverse("admin:diamm_data_person_changelist")

        response = self.client.post(
            url,
            {
                "action": "merge_people_action",
                "_selected_action": [str(primary.pk), str(alias.pk)],
                "do_action": "yes",
                "target": str(primary.pk),
                "index": "0",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Resolve these related records first")
        self.assertTrue(Person.objects.filter(pk=primary.pk).exists())
        self.assertTrue(Person.objects.filter(pk=alias.pk).exists())
