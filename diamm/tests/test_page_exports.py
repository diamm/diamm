from decimal import Decimal
from unittest.mock import patch

from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker

from diamm.models import Image, Page
from diamm.services.page_exports import export_pages_to_source


class PageExportServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        baker.make("diamm_data.ImageType", id=1, name="Primary")

    def setUp(self):
        self.source = baker.make("diamm_data.Source")
        self.target = baker.make("diamm_data.Source")

    def test_copies_pages_and_images_and_appends_in_source_order(self):
        baker.make("diamm_data.Page", source=self.target, sort_order=Decimal("10"))
        later = baker.make(
            "diamm_data.Page",
            source=self.source,
            numeration="2v",
            sort_order=Decimal("8"),
            external=True,
        )
        earlier = baker.make(
            "diamm_data.Page",
            source=self.source,
            numeration="1r",
            sort_order=Decimal("3"),
            legacy_id="source-page",
            iiif_canvas_uri="https://example.test/canvas",
        )
        original_image = baker.make(
            "diamm_data.Image",
            page=earlier,
            location="images/1r",
            legacy_id="source-image",
            external=True,
        )

        result = export_pages_to_source(
            source=self.source, target=self.target, pages=[later, earlier]
        )

        self.assertEqual([page.numeration for page in result.pages], ["1r", "2v"])
        self.assertEqual([page.sort_order for page in result.pages], [11, 12])
        self.assertTrue(result.pages[1].external)
        self.assertIsNone(result.pages[0].copied_from)
        self.assertEqual(result.pages[0].legacy_id, "source-page")
        self.assertEqual(result.pages[0].iiif_canvas_uri, "https://example.test/canvas")
        self.assertEqual(len(result.images), 1)
        copied_image = result.images[0]
        self.assertEqual(copied_image.page, result.pages[0])
        self.assertEqual(copied_image.location, "images/1r")
        self.assertEqual(copied_image.legacy_id, "source-image")
        self.assertTrue(copied_image.external)
        self.assertNotEqual(copied_image.pk, original_image.pk)

    def test_rolls_back_pages_when_an_image_cannot_be_copied(self):
        page = baker.make("diamm_data.Page", source=self.source)
        baker.make("diamm_data.Image", page=page)

        with (
            patch.object(Image.objects, "create", side_effect=RuntimeError("boom")),
            self.assertRaises(RuntimeError),
        ):
            export_pages_to_source(source=self.source, target=self.target, pages=[page])

        self.assertFalse(Page.objects.filter(source=self.target).exists())


class PageExportAdminTests(TestCase):
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
        self.source = baker.make("diamm_data.Source")
        self.target = baker.make("diamm_data.Source")

    def test_admin_reviews_then_exports_selected_pages(self):
        page = baker.make("diamm_data.Page", source=self.source, numeration="3r")
        baker.make("diamm_data.Image", page=page)
        url = reverse("admin:export-pages", args=(self.source.pk,))

        change_response = self.client.get(
            reverse("admin:diamm_data_source_change", args=(self.source.pk,))
        )
        self.assertContains(change_response, "Export pages to...")

        form_response = self.client.get(url)
        self.assertContains(form_response, "admin-autocomplete")
        self.assertContains(form_response, "3r")
        self.assertContains(
            form_response,
            "This tool creates new copies of the selected pages and their images",
        )
        self.assertContains(form_response, "admin/css/forms.css")
        self.assertContains(form_response, '<select name="pages" size="16"', html=False)
        self.assertContains(form_response, 'id="id_pages" multiple>', html=False)
        self.assertNotContains(
            form_response, f'<option value="{self.target.pk}">', html=False
        )

        preview = self.client.post(
            url, {"target": self.target.pk, "pages": [page.pk]}
        )
        self.assertContains(preview, "Confirm page export")
        self.assertContains(preview, "Copy 1 page(s) and 1 image(s)")
        self.assertContains(preview, "taken to the target source’s edit page")
        self.assertEqual(self.target.pages.count(), 0)

        response = self.client.post(
            url,
            {"target": self.target.pk, "pages": [page.pk], "confirm": "yes"},
        )
        self.assertRedirects(
            response,
            reverse("admin:diamm_data_source_change", args=(self.target.pk,)),
        )
        self.assertEqual(self.target.pages.count(), 1)
        self.assertEqual(self.target.pages.get().images.count(), 1)
        self.assertEqual(LogEntry.objects.filter(action_flag=ADDITION).count(), 2)

    def test_self_target_is_not_accepted(self):
        page = baker.make("diamm_data.Page", source=self.source)
        response = self.client.post(
            reverse("admin:export-pages", args=(self.source.pk,)),
            {"target": self.source.pk, "pages": [page.pk]},
        )
        self.assertContains(response, "Select a valid choice")
