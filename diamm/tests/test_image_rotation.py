"""Queue/admin tests use temporary files, not production images."""

import os
import tempfile
from dataclasses import asdict
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.auth.models import Permission
from django.contrib.sites.models import Site
from django.core import signing
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import transaction
from django.tasks import task_backends
from django.tasks.exceptions import TaskResultDoesNotExist
from django.test import TestCase, override_settings
from django.urls import reverse
from django_ox.models import OxTask
from django_ox.worker import Worker
from model_bakery import baker

from diamm.admin.data.image import STATUS_SALT
from diamm.imageops import RotationError, RotationResult, Tools, rotate_image
from diamm.imageops.jobs import enqueue_rotations, image_path, selection_for
from diamm.imageops.locking import image_lock
from diamm.imageops.tasks import rotate_image_task
from diamm.models import Image


@override_settings(
    SECRET_KEY="rotation-tests",
    DIAMM_IMAGE_SERVER="http://127.0.0.1/iipsrv.fcgi?IIIF=",
    DIAMM_IMAGE_KEY="image-key", HOSTNAME="testserver",
)
class ImageRotationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Site.objects.update_or_create(
            id=1, defaults={"domain": "testserver", "name": "Test server"},
        )
        baker.make("diamm_data.ImageType", id=1)
        cls.user = baker.make(
            "diamm_site.CustomUserModel",
            is_staff=True, is_active=True, is_superuser=True,
        )
        cls.staff = baker.make(
            "diamm_site.CustomUserModel",
            is_staff=True, is_active=True, is_superuser=False,
        )

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        settings_override = override_settings(IMAGE_DIR=str(self.root))
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        self.a = self.make_image("a.jpx")
        self.b = self.make_image("b.jpx")
        self.client.force_login(self.user)

    def make_image(self, name):
        (self.root / name).write_bytes(b"original")
        return baker.make("diamm_data.Image", location=name, width=48, height=33)

    def enqueue(self, images=None):
        selected = images if images is not None else Image.objects.filter(pk=self.a.pk)
        return enqueue_rotations(selected, 90)

    def result(self, image=None):
        path = self.root / (image or self.a).location
        return RotationResult(path, path, 90, 33, 48)

    def status_page(self, submitted):
        return self.client.get(
            reverse("admin:diamm_data_image_rotation_status"),
            {"tasks": signing.dumps([asdict(row) for row in submitted], salt=STATUS_SALT)},
        )

    def test_path_mapping_relative_leading_slash_and_absolute_inside_root(self):
        for location in ("a.jpx", "/a.jpx", str(self.root / "a.jpx")):
            self.a.location = location
            self.assertEqual(image_path(self.a), self.root / "a.jpx")

    def test_path_escape_symlink_missing_external_and_unconfigured_root_rejected(self):
        for location in ("../outside.jpx", "missing.jpx", ""):
            self.a.location = location
            self.assertTrue(selection_for(self.a).issue)
        (self.root / "link.jpx").symlink_to(self.root / "a.jpx")
        self.a.location = "link.jpx"
        self.assertIn("Symbolic", selection_for(self.a).issue)
        self.a.location = "a.jpx"
        self.a.external = True
        self.assertIn("External", selection_for(self.a).issue)
        self.a.external = False
        with override_settings(IMAGE_DIR=""):
            self.assertIn("not configured", selection_for(self.a).issue)

    def test_one_durable_task_per_image_without_executing_in_http_worker(self):
        with patch("diamm.imageops.tasks.rotate_image") as rotate:
            submitted = self.enqueue(Image.objects.filter(pk__in=[self.a.pk, self.b.pk]))
        rotate.assert_not_called()
        self.assertEqual(OxTask.objects.count(), 2)
        for operation in submitted:
            result = task_backends["default"].get_result(operation.task_id)
            self.assertEqual(result.status, "READY")
            self.assertEqual(result.args, [operation.image_id, operation.location, 90])

    def test_ox_worker_executes_task_and_updates_dimensions(self):
        submitted = self.enqueue()
        with patch("diamm.imageops.tasks.rotate_image", return_value=self.result()) as rotate:
            self.assertTrue(Worker(queues=["image_rotation"]).run_once())
        rotate.assert_called_once()
        self.a.refresh_from_db()
        self.assertEqual((self.a.width, self.a.height), (33, 48))
        result = task_backends["default"].get_result(submitted[0].task_id)
        self.assertEqual(result.status, "SUCCESSFUL")
        self.assertEqual(result.return_value["width"], 33)
        self.assertEqual(rotate.call_args.kwargs["timeout"], 600)

    def test_queue_inserts_roll_back_together(self):
        with self.assertRaises(RuntimeError):
            with transaction.atomic():
                task_id = self.enqueue()[0].task_id
                raise RuntimeError("rollback")
        self.assertFalse(OxTask.objects.exists())
        with self.assertRaises(TaskResultDoesNotExist):
            task_backends["default"].get_result(task_id)

    def test_duplicate_file_reference_is_skipped_within_submission(self):
        duplicate = baker.make("diamm_data.Image", location="a.jpx")
        submitted = self.enqueue(Image.objects.filter(pk__in=[self.a.pk, duplicate.pk]))
        self.assertEqual(OxTask.objects.count(), 1)
        self.assertTrue(submitted[0].task_id)
        self.assertFalse(submitted[1].task_id)
        self.assertIn("same file", submitted[1].message)

    def test_new_submission_can_queue_the_same_image_again(self):
        first = self.enqueue()[0]
        second = self.enqueue()[0]
        self.assertNotEqual(first.task_id, second.task_id)
        self.assertEqual(OxTask.objects.count(), 2)

    def test_missing_images_are_not_queued_and_note_is_shown(self):
        (self.root / "a.jpx").unlink()
        submitted = self.enqueue()
        self.assertFalse(OxTask.objects.exists())
        self.assertFalse(submitted[0].task_id)
        response = self.status_page(submitted)
        self.assertContains(response, "Missing image file")
        self.assertContains(response, "Not queued")
        self.assertNotContains(response, 'http-equiv="refresh"')

    def test_permission_failure_is_visible_on_confirmation_page(self):
        with patch("diamm.imageops.rotation.os.access", return_value=False):
            response = self.client.post(reverse("admin:diamm_data_image_changelist"), {
                "action": "rotate_images", ACTION_CHECKBOX_NAME: [self.a.pk],
            })
        self.assertContains(response, "No read access to image file")
        self.assertFalse(OxTask.objects.exists())

    def test_directory_permission_failure_is_visible_on_confirmation_page(self):
        with patch("diamm.imageops.rotation.os.access", side_effect=[True, False]):
            response = self.client.post(reverse("admin:diamm_data_image_changelist"), {
                "action": "rotate_images", ACTION_CHECKBOX_NAME: [self.a.pk],
            })
        self.assertContains(response, "No write/search access to image directory")

    def test_permission_failure_is_not_queued(self):
        with patch("diamm.imageops.rotation.os.access", return_value=False):
            submitted = self.enqueue()
        self.assertFalse(OxTask.objects.exists())
        self.assertIn("No read access", submitted[0].message)

    def test_worker_rechecks_permissions_before_creating_lock_file(self):
        with patch("diamm.imageops.rotation.os.access", return_value=False), \
                patch("diamm.imageops.tasks.image_lock") as lock, \
                patch("diamm.imageops.tasks.rotate_image") as rotate:
            with self.assertRaisesRegex(RotationError, "No read access"):
                rotate_image_task.call(self.a.pk, self.a.location, 90)
        lock.assert_not_called()
        rotate.assert_not_called()

    def test_task_failure_does_not_stop_other_images(self):
        submitted = self.enqueue(Image.objects.filter(pk__in=[self.a.pk, self.b.pk]))
        with patch("diamm.imageops.tasks.rotate_image", side_effect=[
            RotationError("encoder failed"), self.result(self.b),
        ]) as rotate:
            worker = Worker(queues=["image_rotation"])
            self.assertTrue(worker.run_once())
            self.assertTrue(worker.run_once())
        self.assertEqual(rotate.call_count, 2)
        # The first task may be waiting for an automatic retry; the second
        # completes independently rather than being stopped by that failure.
        second = task_backends["default"].get_result(submitted[1].task_id)
        self.assertEqual(second.status, "SUCCESSFUL")

    def test_retry_can_repeat_a_rotation(self):
        with patch("diamm.imageops.tasks.rotate_image", return_value=self.result()) as rotate:
            rotate_image_task.call(self.a.pk, self.a.location, 90)
            rotate_image_task.call(self.a.pk, self.a.location, 90)
        self.assertEqual(rotate.call_count, 2)

    def test_changed_location_after_enqueue_does_not_rotate(self):
        Image.objects.filter(pk=self.a.pk).update(location="b.jpx")
        with patch("diamm.imageops.tasks.rotate_image") as rotate:
            with self.assertRaisesRegex(RotationError, "changed"):
                rotate_image_task.call(self.a.pk, "a.jpx", 90)
        rotate.assert_not_called()

    def test_file_disappears_after_enqueue(self):
        (self.root / "a.jpx").unlink()
        with patch("diamm.imageops.tasks.rotate_image") as rotate:
            with self.assertRaisesRegex(RotationError, "Missing"):
                rotate_image_task.call(self.a.pk, self.a.location, 90)
        rotate.assert_not_called()

    def test_file_lock_prevents_concurrent_rotation(self):
        with image_lock(self.root / "a.jpx"):
            with self.assertRaises(RotationError):
                with image_lock(self.root / "a.jpx"):
                    self.fail("should not acquire twice")

    def test_confirmation_page_previews_and_missing_note_without_queueing(self):
        (self.root / "b.jpx").unlink()
        response = self.client.post(reverse("admin:diamm_data_image_changelist"), {
            "action": "rotate_images", ACTION_CHECKBOX_NAME: [self.a.pk, self.b.pk],
        })
        self.assertContains(response, "Missing image file")
        self.assertContains(response, "rotation-preview")
        self.assertContains(response, 'value="270"')
        self.assertFalse(OxTask.objects.exists())

    def test_confirmation_redirects_to_progress_without_session_storage(self):
        session_before = dict(self.client.session)
        response = self.client.post(reverse("admin:diamm_data_image_changelist"), {
            "action": "rotate_images", ACTION_CHECKBOX_NAME: [self.a.pk],
            "rotation": "90", "apply_rotation": "Rotate images",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(dict(self.client.session), session_before)
        page = self.client.get(response.url)
        self.assertContains(page, "Waiting")
        self.assertContains(page, 'http-equiv="refresh"')
        self.assertContains(page, reverse("admin:django_ox_oxtask_changelist"))

    def test_done_status_comes_from_task_result(self):
        submitted = self.enqueue()
        with patch("diamm.imageops.tasks.rotate_image", return_value=self.result()):
            Worker(queues=["image_rotation"]).run_once()
        response = self.status_page(submitted)
        self.assertContains(response, "Done")
        self.assertContains(response, "Rotated 90")
        self.assertNotContains(response, 'http-equiv="refresh"')

    def test_failed_status_comes_from_task_result(self):
        submitted = self.enqueue()
        with patch("diamm.admin.data.image.task_backends") as backends:
            result = backends.__getitem__.return_value.get_result.return_value
            result.status = "FAILED"
            result.is_finished = True
            result.errors = [MagicMock(traceback="RotationError: encoder failed")]
            response = self.status_page(submitted)
        self.assertContains(response, "Error")
        self.assertContains(response, "encoder failed")
        self.assertNotContains(response, 'http-equiv="refresh"')

    def test_pruned_result_is_reported_without_error(self):
        submitted = self.enqueue()
        OxTask.objects.all().delete()
        response = self.status_page(submitted)
        self.assertContains(response, "Task result has been removed")
        self.assertNotContains(response, 'http-equiv="refresh"')

    def test_invalid_status_link_is_rejected(self):
        response = self.client.get(reverse("admin:diamm_data_image_rotation_status"), {"tasks": "tampered"})
        self.assertEqual(response.status_code, 400)

    def test_invalid_angle_is_not_queued(self):
        response = self.client.post(reverse("admin:diamm_data_image_changelist"), {
            "action": "rotate_images", ACTION_CHECKBOX_NAME: [self.a.pk],
            "rotation": "45", "apply_rotation": "Rotate images",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(OxTask.objects.exists())

    def test_admin_routes_require_change_permission(self):
        self.client.force_login(self.staff)
        preview = reverse("admin:diamm_data_image_rotation_preview", args=[self.a.pk])
        self.assertEqual(self.client.get(preview).status_code, 403)
        self.assertEqual(self.status_page(self.enqueue()).status_code, 403)
        self.staff.user_permissions.add(Permission.objects.get(
            codename="change_image", content_type__app_label="diamm_data",
        ))
        self.assertEqual(self.status_page(self.enqueue()).status_code, 200)
        self.client.logout()
        self.assertEqual(self.client.get(preview).status_code, 302)

    def test_preview_proxies_internal_iip_and_is_not_cached(self):
        upstream = MagicMock(status_code=200)
        upstream.headers = {"Content-Type": "image/jpeg"}
        upstream.iter_content.return_value = [b"jpeg"]
        with patch("diamm.admin.data.image.requests.get") as get:
            get.return_value.__enter__.return_value = upstream
            response = self.client.get(reverse("admin:diamm_data_image_rotation_preview", args=[self.a.pk]))
        self.assertEqual(response.content, b"jpeg")
        self.assertIn("private", response["Cache-Control"])
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(get.call_args.args[0], "http://127.0.0.1/iipsrv.fcgi?IIIF=a.jpx/full/!240,240/0/default.jpg")
        self.assertEqual(get.call_args.kwargs["headers"]["X-DIAMM"], "image-key")
        self.assertFalse(get.call_args.kwargs["allow_redirects"])

    def test_preview_rejects_external_images(self):
        self.a.external = True
        self.a.save(update_fields=["external"])
        with patch("diamm.admin.data.image.requests.get") as get:
            response = self.client.get(reverse("admin:diamm_data_image_rotation_preview", args=[self.a.pk]))
        self.assertEqual(response.status_code, 404)
        get.assert_not_called()

    def test_preview_rejects_non_jpeg_upstream_response(self):
        upstream = MagicMock(status_code=200)
        upstream.headers = {"Content-Type": "text/html"}
        with patch("diamm.admin.data.image.requests.get") as get:
            get.return_value.__enter__.return_value = upstream
            response = self.client.get(reverse("admin:diamm_data_image_rotation_preview", args=[self.a.pk]))
        self.assertEqual(response.status_code, 502)
        upstream.iter_content.assert_not_called()

    def test_management_command_directory_and_dry_run(self):
        output = StringIO()
        with patch("diamm.management.commands.rotate.rotate_image") as rotate:
            call_command("rotate", str(self.root), 180, dry_run=True, stdout=output)
        rotate.assert_not_called()
        self.assertIn("a.jpx", output.getvalue())
        self.assertIn("b.jpx", output.getvalue())
        self.assertEqual((self.root / "a.jpx").read_bytes(), b"original")

    def test_management_command_uses_rotation_limits(self):
        output = StringIO()
        with override_settings(IMAGE_ROTATION_TIMEOUT=123, IMAGE_ROTATION_MAX_PIXELS=456):
            with patch("diamm.management.commands.rotate.rotate_image", return_value=self.result()) as rotate:
                call_command("rotate", str(self.root / "a.jpx"), 90, stdout=output)
        self.assertEqual(rotate.call_args.kwargs["timeout"], 123)
        self.assertEqual(rotate.call_args.kwargs["max_pixels"], 456)
        self.assertIn("33 x 48", output.getvalue())

    def test_management_command_reports_failure(self):
        with patch("diamm.management.commands.rotate.rotate_image", side_effect=RotationError("failed")):
            with self.assertRaises(CommandError):
                call_command("rotate", str(self.root / "a.jpx"), 90)

    def test_rotation_reads_tool_settings_without_mutating_environment(self):
        before = os.environ.copy()
        with override_settings(
            GM="/configured/gm", KDU_EXPAND="/configured/expand",
            KDU_COMPRESS="/trusted/compress",
        ):
            with patch.object(Tools, "validate", autospec=True, side_effect=RotationError("stop")) as validate:
                with self.assertRaises(RotationError):
                    rotate_image(self.root / "a.jpx", 90)
        tools = validate.call_args.args[0]
        self.assertEqual(tools.gm, "/configured/gm")
        self.assertEqual(tools.expand, "/configured/expand")
        self.assertEqual(tools.compress, "/trusted/compress")
        self.assertEqual(os.environ.copy(), before)
