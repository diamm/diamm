from __future__ import annotations

from unittest.mock import patch

from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import connection
from django.test import RequestFactory, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from model_bakery import baker

from diamm.admin.data.bibliography import BibliographyAdmin, LikelyDuplicatesFilter
from diamm.admin.data.composition import CompositionAdmin
from diamm.admin.data.image import IIIFDataListFilter, ImageAdmin, ImageSourceListFilter
from diamm.admin.data.notation import NotationAdmin
from diamm.admin.data.person import PersonAdmin, PersonBiography
from diamm.admin.data.source import (
    OutgoingSourceRelationshipInline,
    SourceAdmin,
    SourceRelationshipInline,
)
from diamm.admin.forms.copy_inventory import CopyInventoryForm
from diamm.admin.helpers.source_picker import source_picker_label
from diamm.models.data.bibliography import Bibliography
from diamm.models.data.composition import Composition
from diamm.models.data.image import Image
from diamm.models.data.item import Item
from diamm.models.data.notation import Notation
from diamm.models.data.page import PageTypeChoices
from diamm.models.data.person import Person
from diamm.models.data.source import Source
from diamm.models.data.source_relationship import SourceRelationship
from diamm.models.data.source_to_source_relationship import SourceToSourceRelationship


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

    def test_request_field_limit_is_enabled(self) -> None:
        self.assertEqual(settings.DATA_UPLOAD_MAX_NUMBER_FIELDS, 1000)

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

    def test_copy_inventory_uses_project_source_picker_labels(self) -> None:
        archive = baker.make("diamm_data.Archive", siglum="GB-Lbl")
        source = baker.make("diamm_data.Source", archive=archive)
        target = baker.make(
            "diamm_data.Source",
            archive=archive,
            shelfmark="Add. MS 1",
            date_statement="c. 1450",
        )

        form = CopyInventoryForm(instance=source)
        targets = form.fields["targets"]
        with CaptureQueriesContext(connection) as queries:
            choices = list(targets.queryset)

        self.assertNotIn(source, choices)
        self.assertIn(target, choices)
        self.assertEqual(
            targets.label_from_instance(target),
            source_picker_label(target),
        )
        self.assertEqual(
            targets.label_from_instance(target),
            "GB-Lbl Add. MS 1 — c. 1450",
        )
        self.assertEqual(len(queries), 1)

    def test_source_relationship_picker_labels_include_archive_siglum(self) -> None:
        archive = baker.make("diamm_data.Archive", siglum="GB-Lbl")
        source = baker.make(
            "diamm_data.Source",
            archive=archive,
            shelfmark="Add. MS 1",
            name="Discantus",
        )
        request = RequestFactory().get("/admin/diamm_data/source/")
        request.user = self.superuser
        inline = OutgoingSourceRelationshipInline(Source, admin.site)

        field = inline.formfield_for_foreignkey(
            SourceToSourceRelationship._meta.get_field("to_source"), request
        )

        self.assertEqual(
            field.label_from_instance(source),
            "GB-Lbl Add. MS 1 (Discantus)",
        )
        self.assertEqual(
            field.widget.get_url(),
            reverse("admin:source-relationship-autocomplete"),
        )

        for term in (str(source.pk), "GB-Lbl Add. MS 1"):
            response = self.client.get(
                reverse("admin:source-relationship-autocomplete"),
                {
                    "term": term,
                    "app_label": "diamm_data",
                    "model_name": "source",
                    "field_name": "incoming_source_relationships",
                },
            )

            self.assertEqual(response.status_code, 200)
            self.assertIn(
                {"id": str(source.pk), "text": "GB-Lbl Add. MS 1 (Discantus)"},
                response.json()["results"],
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

        for name in (
            "admin:copy-inventory",
            "admin:import-images",
            "admin:source-inventory",
            "admin:source-pages",
        ):
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=(source.pk,)))
                self.assertEqual(response.status_code, 403)

    def test_copy_inventory_breadcrumb_links_back_to_the_source(self) -> None:
        source = baker.make("diamm_data.Source")
        self.client.force_login(self.superuser)

        response = self.client.get(reverse("admin:copy-inventory", args=(source.pk,)))

        self.assertContains(
            response,
            reverse("admin:diamm_data_source_change", args=(source.pk,)),
        )
        self.assertContains(response, "Copy inventory")
        self.assertContains(response, "#id_targets_add_all")

    def test_copy_inventory_requires_confirmation_before_copying(self) -> None:
        source = baker.make("diamm_data.Source")
        target = baker.make("diamm_data.Source")
        baker.make("diamm_data.Item", source=source, item_title="To copy")
        baker.make("diamm_data.Item", source=target, item_title="To replace")

        preview = self.client.post(
            reverse("admin:copy-inventory", args=(source.pk,)),
            {"targets": [target.pk]},
        )

        self.assertEqual(preview.status_code, 200)
        self.assertContains(preview, "Confirm inventory copy")
        self.assertContains(preview, source.display_name)
        self.assertContains(preview, target.display_name)
        self.assertContains(preview, "Existing inventory will be deleted from:")
        self.assertContains(preview, 'class="closelink"')
        self.assertContains(preview, 'class="inventory-copy-confirm"')
        self.assertEqual(target.inventory.get().item_title, "To replace")

        confirmed = self.client.post(
            reverse("admin:copy-inventory", args=(source.pk,)),
            {"targets": [target.pk], "confirm": "yes"},
        )

        self.assertRedirects(
            confirmed,
            reverse("admin:diamm_data_source_change", args=(source.pk,)),
        )
        self.assertEqual(target.inventory.count(), 1)
        self.assertEqual(target.inventory.get().item_title, "To copy")

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

    def test_bibliography_likely_duplicates_filter_matches_author_title_and_year(self) -> None:
        duplicate_one, duplicate_two, different_year, different_author = baker.make(
            "diamm_data.Bibliography",
            title="A duplicated title",
            year="1999",
            _quantity=4,
        )
        different_year.year = "2000"
        different_year.save()
        author_one = baker.make("diamm_data.BibliographyAuthor", last_name="Smith")
        author_two = baker.make("diamm_data.BibliographyAuthor", last_name="Smith")
        other_author = baker.make("diamm_data.BibliographyAuthor", last_name="Jones")
        for entry, author in (
            (duplicate_one, author_one),
            (duplicate_two, author_two),
            (different_year, author_one),
            (different_author, other_author),
        ):
            baker.make(
                "diamm_data.BibliographyAuthorRole",
                bibliography_entry=entry,
                bibliography_author=author,
            )

        request = RequestFactory().get("/admin/", {"likely_duplicates": "yes"})
        model_admin = BibliographyAdmin(Bibliography, admin.site)
        result = LikelyDuplicatesFilter(
            request,
            {"likely_duplicates": ["yes"]},
            Bibliography,
            model_admin,
        ).queryset(request, Bibliography.objects.all())

        self.assertEqual(set(result.values_list("pk", flat=True)), {duplicate_one.pk, duplicate_two.pk})

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

    def test_source_edit_bibliography_author_queries_are_prefetched(self) -> None:
        source = baker.make("diamm_data.Source")
        for position in range(10):
            bibliography = baker.make("diamm_data.Bibliography")
            baker.make(
                "diamm_data.BibliographyAuthorRole",
                bibliography_entry=bibliography,
                bibliography_author=baker.make("diamm_data.BibliographyAuthor"),
                position=position,
            )
            baker.make(
                "diamm_data.SourceBibliography",
                source=source,
                bibliography=bibliography,
            )

        url = reverse("admin:diamm_data_source_change", args=(source.pk,))
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        bibliography_author_queries = [
            query["sql"]
            for query in queries.captured_queries
            if 'FROM "diamm_data_bibliographyauthor"' in query["sql"]
            or 'FROM "diamm_data_bibliographyauthorrole"' in query["sql"]
        ]
        self.assertLessEqual(len(bibliography_author_queries), 2)

    def test_source_edit_reuses_generic_entity_content_type_choices(self) -> None:
        source = baker.make("diamm_data.Source")
        person = baker.make("diamm_data.Person")
        organization = baker.make(
            "diamm_data.Organization",
            type=baker.make("diamm_data.OrganizationType"),
        )
        relationship_type = baker.make("diamm_data.SourceRelationshipType")
        for position in range(10):
            entity = person if position % 2 else organization
            baker.make(
                "diamm_data.SourceCopyist", source=source, copyist=entity
            )
            baker.make(
                "diamm_data.SourceRelationship",
                source=source,
                related_entity=entity,
                relationship_type=relationship_type,
            )

        url = reverse("admin:diamm_data_source_change", args=(source.pk,))
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        choice_queries = [
            query["sql"]
            for query in queries.captured_queries
            if 'FROM "django_content_type"' in query["sql"]
            and "'person'" in query["sql"]
            and "'organization'" in query["sql"]
        ]
        self.assertLessEqual(len(choice_queries), 2)
        relationship_type_queries = [
            query["sql"]
            for query in queries.captured_queries
            if 'FROM "diamm_data_sourcerelationshiptype"' in query["sql"]
        ]
        self.assertEqual(len(relationship_type_queries), 1)

    def test_cached_relationship_choices_clean_to_model_instances(self) -> None:
        request = RequestFactory().get("/admin/diamm_data/source/")
        request.user = self.superuser
        inline = SourceRelationshipInline(Source, admin.site)
        person_type = ContentType.objects.get_for_model(Person)
        relationship_type = baker.make("diamm_data.SourceRelationshipType")

        content_type_field = inline.formfield_for_foreignkey(
            SourceRelationship._meta.get_field("content_type"), request
        )
        relationship_type_field = inline.formfield_for_foreignkey(
            SourceRelationship._meta.get_field("relationship_type"), request
        )

        self.assertEqual(content_type_field.clean(str(person_type.pk)), person_type)
        self.assertEqual(
            relationship_type_field.clean(str(relationship_type.pk)),
            relationship_type,
        )

    def test_source_change_has_top_buttons_for_large_collections(self) -> None:
        source = baker.make("diamm_data.Source")
        baker.make("diamm_data.Page", source=source, _quantity=3)
        baker.make("diamm_data.Item", source=source, _quantity=2)

        response = self.client.get(
            reverse("admin:diamm_data_source_change", args=(source.pk,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse("admin:source-pages", args=(source.pk,)),
        )
        self.assertContains(
            response,
            reverse("admin:source-inventory", args=(source.pk,)),
        )
        self.assertContains(response, "Edit Pages")
        self.assertContains(response, "Edit Inventory")
        self.assertNotContains(response, "Large related collections")
        self.assertNotContains(response, 'name="pages-TOTAL_FORMS"')
        self.assertNotContains(response, 'name="inventory-TOTAL_FORMS"')

    def test_source_add_form_does_not_render_object_specific_buttons(self) -> None:
        response = self.client.get(reverse("admin:diamm_data_source_add"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Edit Pages")
        self.assertNotContains(response, "Edit Inventory")

    def test_source_inventory_editor_is_scoped_and_paginated(self) -> None:
        source, other_source = baker.make("diamm_data.Source", _quantity=2)
        baker.make(
            "diamm_data.Item",
            source=source,
            item_title="First source item",
            _quantity=51,
        )
        baker.make(
            "diamm_data.Item", source=other_source, item_title="Other source item"
        )
        url = reverse("admin:source-inventory", args=(source.pk,))

        first_page = self.client.get(url)
        second_page = self.client.get(url + "?page=2")

        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(len(first_page.context["formset"].initial_forms), 50)
        self.assertEqual(len(second_page.context["formset"].initial_forms), 1)
        self.assertContains(first_page, "First source item")
        self.assertNotContains(first_page, "Other source item")

    def test_source_inventory_editor_can_add_multiple_unsaved_items(self) -> None:
        source = baker.make("diamm_data.Source")

        response = self.client.get(
            reverse("admin:source-inventory", args=(source.pk,))
        )

        self.assertContains(response, 'id="add-inventory-entry"')
        self.assertContains(response, 'id="inventory-empty-form"')
        self.assertContains(response, 'id="inventory-formset"')
        self.assertContains(response, "admin/css/forms.css")
        self.assertContains(response, "admin/js/admin/RelatedObjectLookups.js")
        self.assertContains(
            response,
            'id="lookup_id_inventory-__prefix__-composition"',
        )
        self.assertContains(response, 'replaceAll("__prefix__", index)')

    def test_source_inventory_editor_updates_an_item(self) -> None:
        source = baker.make("diamm_data.Source")
        item = baker.make(
            "diamm_data.Item", source=source, item_title="Old title"
        )
        url = reverse("admin:source-inventory", args=(source.pk,))
        response = self.client.post(
            url,
            {
                "inventory-TOTAL_FORMS": "2",
                "inventory-INITIAL_FORMS": "1",
                "inventory-MIN_NUM_FORMS": "0",
                "inventory-MAX_NUM_FORMS": "1000",
                "inventory-0-id": str(item.pk),
                "inventory-0-source": str(source.pk),
                "inventory-0-composition": "",
                "inventory-0-fragment": "",
                "inventory-0-completeness": "",
                "inventory-0-item_title": "New title",
                "inventory-0-folio_start": "1r",
                "inventory-0-folio_end": "1v",
                "inventory-0-source_order": "1",
                "inventory-1-id": "",
                "inventory-1-source": str(source.pk),
                "inventory-1-composition": "",
                "inventory-1-fragment": "",
                "inventory-1-completeness": "",
                "inventory-1-item_title": "",
                "inventory-1-folio_start": "",
                "inventory-1-folio_end": "",
                "inventory-1-source_order": "",
            },
        )

        self.assertRedirects(response, url)
        item.refresh_from_db()
        self.assertEqual(item.item_title, "New title")
        self.assertEqual(item.folio_start, "1r")
        self.assertEqual(item.folio_end, "1v")

    def test_source_pages_editor_is_scoped_and_paginated(self) -> None:
        source, other_source = baker.make("diamm_data.Source", _quantity=2)
        baker.make(
            "diamm_data.Page",
            source=source,
            numeration="First source page",
            _quantity=51,
        )
        baker.make(
            "diamm_data.Page", source=other_source, numeration="Other source page"
        )
        url = reverse("admin:source-pages", args=(source.pk,))

        first_page = self.client.get(url)
        second_page = self.client.get(url + "?page=2")

        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(len(first_page.context["formset"].initial_forms), 50)
        self.assertEqual(len(second_page.context["formset"].initial_forms), 1)
        self.assertContains(first_page, "First source page")
        self.assertNotContains(first_page, "Other source page")

    def test_source_pages_editor_can_add_multiple_unsaved_pages(self) -> None:
        source = baker.make("diamm_data.Source")

        response = self.client.get(reverse("admin:source-pages", args=(source.pk,)))

        self.assertContains(response, 'id="add-page-entry"')
        self.assertContains(response, 'id="pages-empty-form"')
        self.assertContains(response, 'id="pages-formset"')
        self.assertContains(response, 'replaceAll("__prefix__", index)')

    def test_source_pages_editor_updates_a_page(self) -> None:
        source = baker.make("diamm_data.Source")
        page = baker.make(
            "diamm_data.Page", source=source, numeration="Old numeration"
        )
        url = reverse("admin:source-pages", args=(source.pk,))
        response = self.client.post(
            url,
            {
                "pages-TOTAL_FORMS": "2",
                "pages-INITIAL_FORMS": "1",
                "pages-MIN_NUM_FORMS": "0",
                "pages-MAX_NUM_FORMS": "1000",
                "pages-0-id": str(page.pk),
                "pages-0-source": str(source.pk),
                "pages-0-numeration": "1r",
                "pages-0-sort_order": "1.5",
                "pages-0-page_type": str(PageTypeChoices.FLYLEAF),
                "pages-0-external": "on",
                "pages-1-id": "",
                "pages-1-source": str(source.pk),
                "pages-1-numeration": "",
                "pages-1-sort_order": "0",
                "pages-1-page_type": str(PageTypeChoices.PAGE),
            },
        )

        self.assertRedirects(response, url)
        page.refresh_from_db()
        self.assertEqual(page.numeration, "1r")
        self.assertEqual(str(page.sort_order), "1.500")
        self.assertEqual(page.page_type, PageTypeChoices.FLYLEAF)
        self.assertTrue(page.external)

    @override_settings(DATA_UPLOAD_MAX_NUMBER_FIELDS=1000)
    def test_source_change_stays_under_safe_upload_field_limit(self) -> None:
        source = baker.make("diamm_data.Source")
        baker.make("diamm_data.Page", source=source, _quantity=1100)
        baker.make("diamm_data.Item", source=source, _quantity=1100)

        response = self.client.get(
            reverse("admin:diamm_data_source_change", args=(source.pk,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertLess(response.content.count(b'name="'), 1000)
