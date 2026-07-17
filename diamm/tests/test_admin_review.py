from __future__ import annotations

from unittest.mock import patch

from django.contrib import admin
from django.contrib.sites.models import Site
from django.db import connection
from django.test import RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from model_bakery import baker

from diamm.admin.data.composition import CompositionAdmin
from diamm.admin.data.image import IIIFDataListFilter, ImageAdmin, ImageSourceListFilter
from diamm.admin.data.notation import NotationAdmin
from diamm.admin.data.person import PersonAdmin, PersonBiography
from diamm.admin.data.source import SourceAdmin
from diamm.models.data.composition import Composition
from diamm.models.data.image import Image
from diamm.models.data.item import Item
from diamm.models.data.notation import Notation
from diamm.models.data.person import Person
from diamm.models.data.source import Source


class AdminReviewTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Site.objects.create(domain="testserver", name="Test server")
        Site.objects.clear_cache()
        baker.make("diamm_data.ImageType", id=1, name="Primary")
        cls.superuser = baker.make(
            "diamm_site.CustomUserModel",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        cls.staff_user = baker.make(
            "diamm_site.CustomUserModel",
            is_active=True,
            is_staff=True,
            is_superuser=False,
        )

    def setUp(self) -> None:
        self.client.force_login(self.superuser)

    def test_copy_inventory_preserves_source_and_copies_supported_relations(self) -> None:
        source, first_target, second_target = baker.make(
            "diamm_data.Source", _quantity=3
        )
        original = baker.make(
            "diamm_data.Item", source=source, item_title="Original title"
        )
        baker.make("diamm_data.Voice", item=original)
        baker.make("diamm_data.ItemNote", item=original, note="Original note")
        baker.make("diamm_data.ItemBibliography", item=original)
        baker.make("diamm_data.ItemComposer", item=original)
        baker.make("diamm_data.Item", source=first_target, item_title="Replace me")

        model_admin = SourceAdmin(Source, admin.site)
        copy_inventory = model_admin._SourceAdmin__copy_items_to_source
        copy_inventory(source, first_target)
        copy_inventory(source, second_target)

        original.refresh_from_db()
        self.assertEqual(original.item_title, "Original title")
        self.assertEqual(source.inventory.count(), 1)

        for target in (first_target, second_target):
            copied = target.inventory.get()
            self.assertEqual(copied.item_title, "Original title")
            self.assertEqual(copied.voices.count(), 1)
            self.assertEqual(copied.itembibliography_set.count(), 1)
            self.assertEqual(copied.unattributed_composers.count(), 1)
            self.assertEqual(copied.notes.count(), 2)
            self.assertTrue(
                copied.notes.filter(note=f"Bulk copied from source {source.pk}").exists()
            )

    def test_malformed_image_import_does_not_delete_existing_pages(self) -> None:
        source = baker.make("diamm_data.Source")
        page = baker.make("diamm_data.Page", source=source)

        response = self.client.post(
            reverse("admin:import-images", args=(source.pk,)),
            {"do_action": "yes", "public": "on", "imports": "not-valid"},
        )

        self.assertRedirects(
            response,
            reverse("admin:diamm_data_source_change", args=(source.pk,)),
        )
        self.assertTrue(type(page).objects.filter(pk=page.pk).exists())

    def test_image_import_accepts_trailing_newline(self) -> None:
        source = baker.make("diamm_data.Source")

        response = self.client.post(
            reverse("admin:import-images", args=(source.pk,)),
            {
                "do_action": "yes",
                "public": "on",
                "imports": "1r|first/image\n1v|second/image\n",
            },
        )

        self.assertRedirects(
            response,
            reverse("admin:diamm_data_source_change", args=(source.pk,)),
        )
        self.assertEqual(source.pages.count(), 2)
        self.assertEqual(Image.objects.filter(page__source=source, public=True).count(), 2)

    def test_custom_source_views_require_change_permission(self) -> None:
        source = baker.make("diamm_data.Source")
        self.client.force_login(self.staff_user)

        for name in ("admin:copy-inventory", "admin:import-images"):
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=(source.pk,)))
                self.assertEqual(response.status_code, 403)

    def test_notation_counts_are_not_multiplied_by_parallel_joins(self) -> None:
        notation = baker.make("diamm_data.Notation")
        sources = baker.make("diamm_data.Source", _quantity=2)
        for source in sources:
            source.notations.add(notation)
        baker.make("diamm_data.Item", notation=notation, _quantity=3)

        model_admin = NotationAdmin(Notation, admin.site)
        request = RequestFactory().get("/admin/diamm_data/notation/")
        request.user = self.superuser
        result = model_admin.get_queryset(request).get(pk=notation.pk)

        self.assertEqual(result.source_count, 2)
        self.assertEqual(result.item_count, 3)

    def test_person_biography_filter_handles_both_choices(self) -> None:
        with_biography = baker.make("diamm_data.Person")
        without_biography = baker.make("diamm_data.Person")
        baker.make("diamm_data.PersonNote", person=with_biography, type=1)
        model_admin = PersonAdmin(Person, admin.site)

        for value, included, excluded in (
            ("yes", with_biography.pk, without_biography.pk),
            ("no", without_biography.pk, with_biography.pk),
        ):
            with self.subTest(value=value):
                request = RequestFactory().get("/admin/", {"biography": value})
                params = {"biography": [value]}
                filter_instance = PersonBiography(
                    request, params, Person, model_admin
                )
                result = filter_instance.queryset(request, Person.objects.all())
                result_ids = set(result.values_list("pk", flat=True))
                self.assertIn(included, result_ids)
                self.assertNotIn(excluded, result_ids)

    def test_image_filters_do_not_hide_records_by_default_and_find_partial_info(self) -> None:
        attached = baker.make("diamm_data.Image", page=baker.make("diamm_data.Page"))
        unattached = baker.make("diamm_data.Image", page=None)
        partial = baker.make(
            "diamm_data.Image",
            location="partial/image",
            width=100,
            height=None,
        )
        model_admin = ImageAdmin(Image, admin.site)
        request = RequestFactory().get("/admin/")

        attachment_filter = ImageSourceListFilter(request, {}, Image, model_admin)
        unfiltered = attachment_filter.queryset(request, Image.objects.all())
        self.assertEqual(
            set(unfiltered.values_list("pk", flat=True)),
            {attached.pk, unattached.pk, partial.pk},
        )

        params = {"iiif_info": ["False"]}
        missing_filter = IIIFDataListFilter(request, params, Image, model_admin)
        missing = missing_filter.queryset(request, Image.objects.all())
        self.assertIn(partial, missing)

    def test_admin_generated_links_escape_database_content(self) -> None:
        source = baker.make(
            "diamm_data.Source", shelfmark='<script>alert("x")</script>'
        )
        composition = baker.make("diamm_data.Composition")
        baker.make("diamm_data.Item", source=source, composition=composition)
        model_admin = CompositionAdmin(Composition, admin.site)
        request = RequestFactory().get("/admin/diamm_data/composition/")
        request.user = self.superuser
        obj = model_admin.get_queryset(request).get(pk=composition.pk)

        rendered = str(model_admin.appears_in(obj))

        self.assertIn("&lt;script&gt;", rendered)
        self.assertNotIn("<script>", rendered)

    def test_failed_iiif_refresh_reports_failure_without_crashing(self) -> None:
        image = baker.make("diamm_data.Image", location="missing/image")

        with patch("diamm.admin.data.image.ImageAdmin._fetch_info", return_value=None):
            response = self.client.post(
                reverse("admin:diamm_data_image_changelist"),
                {
                    "action": "refetch_iiif_info",
                    "_selected_action": str(image.pk),
                    "index": "0",
                },
            )

        self.assertEqual(response.status_code, 302)

    def test_page_inline_uses_current_accessible_django_structure(self) -> None:
        page = baker.make("diamm_data.Page")
        image = baker.make("diamm_data.Image", page=page, location="test/image")

        response = self.client.get(
            reverse("admin:diamm_data_page_change", args=(page.pk,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "aria-labelledby=")
        self.assertContains(response, 'loading="lazy"')
        self.assertContains(
            response,
            reverse(
                "image-serve",
                args=(image.pk, "full/250,/0/default.jpg"),
            ),
        )

    def test_source_changelist_queries_do_not_grow_with_rows(self) -> None:
        archive = baker.make("diamm_data.Archive")
        baker.make("diamm_data.Source", archive=archive)
        url = reverse("admin:diamm_data_source_changelist")
        self.client.get(url)

        with CaptureQueriesContext(connection) as one_row_queries:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        baker.make("diamm_data.Source", archive=archive, _quantity=10)
        with CaptureQueriesContext(connection) as many_row_queries:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        self.assertLessEqual(len(many_row_queries), len(one_row_queries) + 1)
