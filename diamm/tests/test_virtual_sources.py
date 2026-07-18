from decimal import Decimal

from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from model_bakery import baker

from diamm.models import (
    Image,
    Item,
    Page,
    SourceToSourceRelationship,
)
from diamm.serializers.website.source import SourceToSourceRelationshipSerializer
from diamm.services.virtual_sources import copy_pages_to_virtual_source


class VirtualSourceCopyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        baker.make("diamm_data.ImageType", id=1, name="Primary")

    def setUp(self):
        self.target = baker.make(
            "diamm_data.Source",
            is_virtual=True,
            public_images=True,
            open_images=True,
        )
        self.donor = baker.make(
            "diamm_data.Source", public_images=True, open_images=True
        )

    def copy(self, *pages, relationship_type=None):
        return copy_pages_to_virtual_source(
            target=self.target,
            donor=self.donor,
            pages=pages,
            relationship_type=relationship_type,
        )

    def test_clones_page_notes_images_and_clears_legacy_identifiers(self):
        page = baker.make(
            "diamm_data.Page",
            source=self.donor,
            numeration="12v",
            sort_order=Decimal("2.5"),
            legacy_id="old-page",
            iiif_canvas_uri="https://example.test/canvas",
        )
        baker.make("diamm_data.PageNote", page=page, note="Decoration")
        image = baker.make(
            "diamm_data.Image",
            page=page,
            location="images/12v",
            width=1200,
            height=900,
            public=True,
            external=True,
            legacy_id="old-image",
            legacy_filename="12v.tif",
        )
        baker.make("diamm_data.ImageNote", image=image, note="Good capture")

        result = self.copy(page)

        clone = result.pages[0]
        self.assertEqual(clone.copied_from, page)
        self.assertEqual(clone.numeration, "12v")
        self.assertFalse(clone.external)
        self.assertIsNone(clone.legacy_id)
        self.assertIsNone(clone.iiif_canvas_uri)
        self.assertEqual(clone.notes.get().note, "Decoration")
        cloned_image = clone.images.get()
        self.assertEqual(cloned_image.location, "images/12v")
        self.assertEqual((cloned_image.width, cloned_image.height), (1200, 900))
        self.assertTrue(cloned_image.external)
        self.assertTrue(cloned_image.public)
        self.assertEqual(cloned_image.legacy_filename, "12v.tif")
        self.assertIsNone(cloned_image.legacy_id)
        self.assertEqual(cloned_image.imagenote_set.get().note, "Good capture")

    def test_partial_item_is_created_once_and_later_page_is_attached(self):
        first = baker.make(
            "diamm_data.Page", source=self.donor, sort_order=Decimal("1")
        )
        second = baker.make(
            "diamm_data.Page", source=self.donor, sort_order=Decimal("2")
        )
        original = baker.make(
            "diamm_data.Item",
            source=self.donor,
            item_title="Multipart work",
            source_order=Decimal("7"),
        )
        original.pages.add(first, second)

        first_result = self.copy(first)
        clone = self.target.inventory.get()
        self.assertEqual(clone.copied_from, original)
        self.assertEqual(list(clone.pages.all()), list(first_result.pages))

        second_result = self.copy(second)
        clone.refresh_from_db()
        self.assertEqual(self.target.inventory.count(), 1)
        self.assertEqual(
            set(clone.pages.values_list("pk", flat=True)),
            {first_result.pages[0].pk, second_result.pages[0].pk},
        )
        self.assertEqual(second_result.items, ())

    def test_clones_item_children_and_voice_languages(self):
        page = baker.make("diamm_data.Page", source=self.donor)
        original = baker.make("diamm_data.Item", source=self.donor)
        original.pages.add(page)
        language = baker.make("diamm_data.Language")
        voice = baker.make("diamm_data.Voice", item=original, voice_text="Text")
        voice.languages.add(language)
        baker.make("diamm_data.ItemNote", item=original, note="A note")
        baker.make("diamm_data.ItemBibliography", item=original, pages="10-11")
        baker.make("diamm_data.ItemComposer", item=original, note="Unattributed")

        self.copy(page)

        clone = self.target.inventory.get()
        self.assertEqual(clone.voices.get().voice_text, "Text")
        self.assertEqual(list(clone.voices.get().languages.all()), [language])
        self.assertEqual(clone.notes.get().note, "A note")
        self.assertEqual(clone.itembibliography_set.get().pages, "10-11")
        self.assertEqual(clone.unattributed_composers.get().note, "Unattributed")

    def test_page_and_item_ordering_appends_deterministically(self):
        baker.make("diamm_data.Page", source=self.target, sort_order=Decimal("10"))
        baker.make("diamm_data.Item", source=self.target, source_order=Decimal("20"))
        later = baker.make(
            "diamm_data.Page", source=self.donor, sort_order=Decimal("8")
        )
        earlier = baker.make(
            "diamm_data.Page", source=self.donor, sort_order=Decimal("3")
        )
        later_item = baker.make(
            "diamm_data.Item", source=self.donor, source_order=Decimal("1")
        )
        earlier_item = baker.make(
            "diamm_data.Item", source=self.donor, source_order=Decimal("99")
        )
        later_item.pages.add(later)
        earlier_item.pages.add(earlier)

        result = self.copy(later, earlier)

        self.assertEqual([p.copied_from for p in result.pages], [earlier, later])
        self.assertEqual([p.sort_order for p in result.pages], [11, 12])
        self.assertEqual(
            [item.copied_from for item in result.items], [earlier_item, later_item]
        )
        self.assertEqual([item.source_order for item in result.items], [21, 22])

    def test_validation_and_optional_relationship(self):
        page = baker.make("diamm_data.Page", source=self.donor)
        relationship_type = baker.make(
            "diamm_data.SourceToSourceRelationshipType",
            forward_label="Reconstructs",
            inverse_label="Reconstructed by",
        )
        self.copy(page, relationship_type=relationship_type)
        self.assertTrue(
            SourceToSourceRelationship.objects.filter(
                from_source=self.target,
                to_source=self.donor,
                relationship_type=relationship_type,
            ).exists()
        )
        with self.assertRaises(ValidationError):
            self.copy(page)

        external = baker.make("diamm_data.Page", source=self.donor, external=True)
        with self.assertRaises(ValidationError):
            self.copy(external)

        self.donor.is_virtual = True
        self.donor.save()
        another = baker.make("diamm_data.Page", source=self.donor)
        with self.assertRaises(ValidationError):
            self.copy(another)

    def test_rights_downgrade_and_no_escalation(self):
        self.donor.public_images = False
        self.donor.open_images = False
        self.donor.save()
        page = baker.make("diamm_data.Page", source=self.donor)
        self.copy(page)
        self.target.refresh_from_db()
        self.assertFalse(self.target.public_images)
        self.assertFalse(self.target.open_images)

        self.target.public_images = True
        self.target.open_images = True
        with self.assertRaises(ValidationError):
            self.target.full_clean()

    def test_donor_change_downgrades_dependents(self):
        page = baker.make("diamm_data.Page", source=self.donor)
        self.copy(page)
        self.donor.public_images = False
        self.donor.open_images = False
        self.donor.save()
        self.target.refresh_from_db()
        self.assertFalse(self.target.public_images)
        self.assertFalse(self.target.open_images)

    def test_deleting_pages_removes_only_orphaned_copied_items(self):
        first = baker.make("diamm_data.Page", source=self.donor, sort_order=1)
        second = baker.make("diamm_data.Page", source=self.donor, sort_order=2)
        original = baker.make("diamm_data.Item", source=self.donor)
        original.pages.add(first, second)
        result = self.copy(first, second)
        copied_item = self.target.inventory.get()

        result.pages[0].delete()
        self.assertTrue(Item.objects.filter(pk=copied_item.pk).exists())
        result.pages[1].delete()
        self.assertFalse(Item.objects.filter(pk=copied_item.pk).exists())

    def test_provenance_protects_originals_and_virtual_flag(self):
        page = baker.make("diamm_data.Page", source=self.donor)
        self.copy(page)
        with self.assertRaises(ProtectedError):
            page.delete()

        self.target.is_virtual = False
        with self.assertRaises(ValidationError):
            self.target.full_clean()

    def test_atomic_rollback_if_image_copy_fails(self):
        page = baker.make("diamm_data.Page", source=self.donor)
        baker.make("diamm_data.Image", page=page)
        from unittest.mock import patch

        with (
            patch.object(Image.objects, "create", side_effect=RuntimeError("boom")),
            self.assertRaises(RuntimeError),
        ):
            self.copy(page)
        self.assertFalse(Page.objects.filter(source=self.target).exists())


class VirtualSourceAdminAndPublicTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Site.objects.create(domain="testserver", name="Test server")
        Site.objects.clear_cache()
        baker.make("diamm_data.ImageType", id=1, name="Primary")
        cls.user = baker.make(
            "diamm_site.CustomUserModel",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )

    def setUp(self):
        self.client.force_login(self.user)
        self.target = baker.make("diamm_data.Source", is_virtual=True)
        self.donor = baker.make("diamm_data.Source", is_virtual=False)

    def test_object_tool_is_only_visible_for_virtual_sources(self):
        virtual_response = self.client.get(
            reverse("admin:diamm_data_source_change", args=(self.target.pk,))
        )
        physical_response = self.client.get(
            reverse("admin:diamm_data_source_change", args=(self.donor.pk,))
        )
        self.assertContains(virtual_response, "Add pages from source")
        self.assertNotContains(physical_response, "Add pages from source")

    def test_donor_picker_uses_searchable_physical_source_autocomplete(self):
        self.donor.shelfmark = "Searchable MS 42"
        self.donor.save()
        baker.make("diamm_data.Page", source=self.donor)
        virtual_match = baker.make(
            "diamm_data.Source", is_virtual=True, shelfmark="Searchable virtual"
        )
        baker.make("diamm_data.Page", source=virtual_match)
        page_less_match = baker.make(
            "diamm_data.Source", is_virtual=False, shelfmark="Searchable page-less"
        )
        form_response = self.client.get(
            reverse("admin:add-virtual-pages", args=(self.target.pk,))
        )
        self.assertContains(form_response, "admin-autocomplete")
        self.assertNotContains(
            form_response, f'<option value="{self.donor.pk}">', html=False
        )

        response = self.client.get(
            reverse("admin:virtual-source-donor-autocomplete"),
            {"q": "Searchable"},
        )
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertEqual([result["id"] for result in results], [str(self.donor.pk)])
        self.assertIn("Searchable MS 42", results[0]["text"])
        self.assertNotIn(str(virtual_match.pk), [result["id"] for result in results])
        self.assertNotIn(str(page_less_match.pk), [result["id"] for result in results])

    def test_admin_import_filters_pages_previews_and_logs_additions(self):
        eligible = baker.make("diamm_data.Page", source=self.donor, numeration="1r")
        baker.make(
            "diamm_data.Page", source=self.donor, numeration="remote", external=True
        )
        item = baker.make("diamm_data.Item", source=self.donor)
        item.pages.add(eligible)
        baker.make("diamm_data.Image", page=eligible)
        url = reverse("admin:add-virtual-pages", args=(self.target.pk,))

        selection = self.client.get(url, {"donor": self.donor.pk})
        self.assertContains(selection, "1r")
        self.assertNotContains(selection, "remote")

        preview = self.client.post(
            url,
            {"donor": self.donor.pk, "pages": [eligible.pk], "preview": "1"},
        )
        self.assertContains(preview, "add 1 page(s)")
        self.assertContains(preview, "include 1 matching item(s)")

        response = self.client.post(
            url,
            {"donor": self.donor.pk, "pages": [eligible.pk], "do_action": "1"},
        )
        self.assertRedirects(
            response,
            reverse("admin:diamm_data_source_change", args=(self.target.pk,)),
        )
        self.assertEqual(self.target.pages.count(), 1)
        self.assertEqual(self.target.inventory.count(), 1)
        self.assertEqual(LogEntry.objects.filter(action_flag=ADDITION).count(), 3)

    def test_physical_target_cannot_open_import_workflow(self):
        response = self.client.get(
            reverse("admin:add-virtual-pages", args=(self.donor.pk,))
        )
        self.assertEqual(response.status_code, 404)

    def test_directional_public_labels_link_to_related_sources(self):
        relationship_type = baker.make(
            "diamm_data.SourceToSourceRelationshipType",
            forward_label="Uses leaves from",
            inverse_label="Contributes leaves to",
        )
        relation = baker.make(
            "diamm_data.SourceToSourceRelationship",
            from_source=self.target,
            to_source=self.donor,
            relationship_type=relationship_type,
        )
        request = RequestFactory().get("/")
        request.user = self.user

        outgoing = SourceToSourceRelationshipSerializer(
            relation, context={"request": request, "incoming": False}
        ).serialized
        incoming = SourceToSourceRelationshipSerializer(
            relation, context={"request": request, "incoming": True}
        ).serialized

        self.assertEqual(outgoing["relationship_type"], "Uses leaves from")
        self.assertEqual(outgoing["related_entity"]["name"], self.donor.display_name)
        self.assertEqual(incoming["relationship_type"], "Contributes leaves to")
        self.assertEqual(incoming["related_entity"]["name"], self.target.display_name)
