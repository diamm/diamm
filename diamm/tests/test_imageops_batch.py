"""Selection/planning tests do not require valid images or external tools."""

from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError

from diamm.imageops import RotationError, RotationResult, plan_rotations
from diamm.imageops.batch import format_plan
from diamm.management.commands.rotate import Command


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.images = self.root / "images with spaces"
        self.images.mkdir()
        self.a = self.images / "a.jpx"
        self.b = self.images / "b.JPX"
        self.c = self.images / "c.jp2"
        for path in (self.a, self.b, self.c, self.images/"notes.txt"):
            path.write_bytes(b"unchanged")
        self.nested = self.images / "sub"
        self.nested.mkdir()
        self.deep = self.nested / "deep.jpx"
        self.deep.write_bytes(b"unchanged")

    def test_file_preserves_single_output_filename_interface(self):
        output = self.root / "out.jpx"
        job, = plan_rotations(self.a, 180, output)
        self.assertEqual((job.input_path, job.output_path, job.rotation), (self.a, output, 180))
        self.assertFalse(job.in_place)
        self.assertFalse(output.exists())

    def test_file_defaults_to_in_place(self):
        job, = plan_rotations(self.a, 90)
        self.assertTrue(job.in_place)

    def test_directory_is_sorted_non_recursive_and_case_insensitive(self):
        jobs = plan_rotations(self.images, 180)
        self.assertEqual([job.input_path for job in jobs], [self.a, self.b, self.c])
        self.assertTrue(all(job.in_place for job in jobs))

    def test_quoted_glob_selects_only_matches(self):
        jobs = plan_rotations(str(self.images/"*.jpx"), 180)
        self.assertEqual([job.input_path for job in jobs], [self.a])

    def test_recursive_glob(self):
        jobs = plan_rotations(str(self.images/"**"/"*.jpx"), 270)
        self.assertEqual([job.input_path for job in jobs], [self.a, self.deep])

    def test_recursive_glob_duplicates_do_not_rotate_same_path_twice(self):
        jobs = plan_rotations(str(self.images/"**"/"**"/"*.jpx"), 180)
        self.assertEqual([job.input_path for job in jobs], [self.a, self.deep])

    def test_directory_output_maps_basenames_without_creating_files(self):
        destination = self.root / "output"
        destination.mkdir()
        jobs = plan_rotations(self.images, 180, destination)
        self.assertEqual([job.output_path for job in jobs],
                         [destination / path.name for path in (self.a, self.b, self.c)])
        self.assertEqual(list(destination.iterdir()), [])

    def test_glob_with_one_match_still_requires_output_directory(self):
        with self.assertRaisesRegex(RotationError, "batch output"):
            plan_rotations(str(self.images/"a*.jpx"), 180, self.root/"out.jpx")

    def test_basename_collision_is_rejected_before_processing(self):
        (self.nested/"a.jpx").write_bytes(b"duplicate basename")
        output = self.root / "output"
        output.mkdir()
        with self.assertRaisesRegex(RotationError, "same output"):
            plan_rotations(str(self.images/"**"/"*.jpx"), 180, output)
        self.assertEqual(list(output.iterdir()), [])

    def test_existing_output_rejects_whole_plan(self):
        output = self.root / "output"
        output.mkdir()
        (output/self.b.name).write_bytes(b"keep")
        with self.assertRaisesRegex(RotationError, "already exists"):
            plan_rotations(self.images, 180, output)
        self.assertEqual([path.name for path in output.iterdir()], [self.b.name])

    def test_same_directory_output_is_in_place(self):
        jobs = plan_rotations(self.images, 180, self.images)
        self.assertTrue(all(job.in_place for job in jobs))

    def test_empty_directory_no_glob_matches_and_missing_input_are_errors(self):
        empty = self.root / "empty"
        empty.mkdir()
        for selection in (empty, str(self.images/"missing*.jpx"), self.root/"missing"):
            with self.subTest(selection=selection), self.assertRaises(RotationError):
                plan_rotations(selection, 180)

    def test_batch_skips_symlink_files_but_explicit_symlink_rejected(self):
        link = self.images / "alias.jpx"
        link.symlink_to(self.a)
        dangling = self.images / "dangling.jpx"
        dangling.symlink_to(self.images/"missing")
        self.assertEqual(len(plan_rotations(self.images, 180)), 3)
        with self.assertRaisesRegex(RotationError, "symbolic-link"):
            plan_rotations(link, 180)

    def test_literal_filename_with_glob_characters_is_a_file(self):
        literal = self.images / "[page].jpx"
        literal.write_bytes(b"image")
        job, = plan_rotations(literal, 180)
        self.assertEqual(job.input_path, literal)

    def test_invalid_angle_and_unsupported_explicit_file(self):
        for angle in (0, 45, True, "180"):
            with self.assertRaises(RotationError):
                plan_rotations(self.a, angle)
        with self.assertRaises(RotationError):
            plan_rotations(self.images/"notes.txt", 180)

    def test_command_dry_run_never_invokes_rotation_or_tools(self):
        stdout = StringIO()
        with patch("diamm.management.commands.rotate.rotate_image") as rotate:
            call_command("rotate", str(self.images), "180", "--dry-run", stdout=stdout)
        rotate.assert_not_called()
        listing = stdout.getvalue()
        self.assertIn("3 image(s)", listing)
        self.assertIn("replace in place", listing)
        self.assertIn(str(self.a), listing)
        self.assertNotIn(str(self.deep), listing)
        self.assertEqual(self.a.read_bytes(), b"unchanged")
        self.assertEqual(list(self.images.glob(".diamm-imageops-*")), [])

    def test_dry_run_shows_new_destinations(self):
        output = self.root/"output"
        output.mkdir()
        jobs = plan_rotations(self.images, 90, output)
        listing = format_plan(jobs)
        self.assertIn(f"{self.a} -> {output/self.a.name}", listing)
        self.assertIn("90 degrees clockwise; new output", listing)
        self.assertEqual(list(output.iterdir()), [])

    def test_command_preflights_batch_before_any_rotation(self):
        output = self.root/"output"
        output.mkdir()
        (output/self.b.name).write_bytes(b"keep")
        with patch("diamm.management.commands.rotate.rotate_image") as rotate:
            with self.assertRaises(CommandError):
                call_command("rotate", str(self.images), "180", str(output))
        rotate.assert_not_called()

    def test_command_can_interrupt_planning_without_processing(self):
        with patch("diamm.management.commands.rotate.plan_rotations", side_effect=KeyboardInterrupt), \
                patch("diamm.management.commands.rotate.rotate_image") as rotate:
            with self.assertRaises(KeyboardInterrupt):
                call_command("rotate", str(self.images), "180")
        rotate.assert_not_called()

    def test_command_runs_each_selected_image_in_order(self):
        results = [RotationResult(path, path, 180, 48, 33) for path in (self.a, self.b, self.c)]
        stdout = StringIO()
        with patch("diamm.management.commands.rotate.rotate_image", side_effect=results) as rotate:
            call_command("rotate", str(self.images), "180", stdout=stdout)
        self.assertEqual([call.args[0] for call in rotate.call_args_list],
                          [self.a, self.b, self.c])
        self.assertIn("Completed 3 rotation(s).", stdout.getvalue())

    def test_command_stops_on_first_failure_and_reports_completed_count(self):
        first = RotationResult(self.a, self.a, 180, 48, 33)
        stdout = StringIO()
        with patch("diamm.management.commands.rotate.rotate_image", side_effect=[first, RotationError("failed")]) as rotate:
            with self.assertRaisesRegex(CommandError, r"1 image\(s\) completed"):
                call_command("rotate", str(self.images), "180", stdout=stdout)
        self.assertEqual(rotate.call_count, 2)
        self.assertIn(str(self.a), stdout.getvalue())
        self.assertNotIn("Completed", stdout.getvalue())

    def test_command_accepts_quoted_glob(self):
        stdout = StringIO()
        with patch("diamm.management.commands.rotate.rotate_image") as rotate:
            call_command("rotate", str(self.images / "*.jpx"), "180", "--dry-run", stdout=stdout)
        rotate.assert_not_called()
        self.assertIn(str(self.a), stdout.getvalue())
        self.assertNotIn(str(self.b), stdout.getvalue())

    def test_command_accepts_separate_output_file(self):
        output = self.root / "rotated.jpx"
        result = RotationResult(self.a, output, 90, 33, 48)
        stdout = StringIO()
        with patch("diamm.management.commands.rotate.rotate_image", return_value=result) as rotate:
            call_command("rotate", str(self.a), "90", str(output), stdout=stdout)
        self.assertEqual(rotate.call_args.args, (self.a, 90, output))
        self.assertIn(str(output), stdout.getvalue())

    def test_command_rejects_invalid_angle(self):
        with patch("diamm.management.commands.rotate.rotate_image") as rotate:
            with self.assertRaises(CommandError):
                call_command("rotate", str(self.a), "45")
        rotate.assert_not_called()

    def test_command_reports_filesystem_error_to_django_stderr(self):
        stderr = StringIO()
        with patch("diamm.management.commands.rotate.rotate_image", side_effect=PermissionError("cannot read source")), \
                patch("django.core.management.base.connections.close_all"):
            with self.assertRaises(SystemExit) as caught:
                Command(stdout=StringIO(), stderr=stderr).run_from_argv(
                    ["manage.py", "rotate", str(self.a), "180", "--skip-checks"]
                )
        self.assertEqual(caught.exception.code, 1)
        self.assertIn("CommandError:", stderr.getvalue())
        self.assertIn("cannot read source", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
