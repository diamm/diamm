"""Rotate local JPEG 2000 files without involving the HTTP/task workers."""

from argparse import ArgumentParser
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from diamm.imageops import RotationError, plan_rotations, rotate_image
from diamm.imageops.batch import format_plan
from diamm.imageops.locking import image_lock


class Command(BaseCommand):
    help = "Losslessly rotate a JPEG 2000 file, directory, or quoted glob clockwise."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("input", help="File, directory, or quoted glob")
        parser.add_argument("rotation", type=int, choices=(90, 180, 270))
        parser.add_argument("output", nargs="?", help="Output file or existing batch directory")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args: object, **options: Any) -> str:
        try:
            jobs = plan_rotations(options["input"], options["rotation"], options["output"])
        except (RotationError, OSError) as error:
            raise CommandError(str(error)) from error
        if options["dry_run"]:
            return format_plan(jobs)
        completed = 0
        for job in jobs:
            try:
                with image_lock(job.input_path):
                    result = rotate_image(
                        job.input_path, job.rotation, job.output_path,
                        timeout=settings.IMAGE_ROTATION_TIMEOUT,
                        max_pixels=settings.IMAGE_ROTATION_MAX_PIXELS,
                    )
            except (RotationError, OSError) as error:
                raise CommandError(
                    f"{job.input_path}: {error}. Stopped; {completed} image(s) completed."
                ) from error
            completed += 1
            self.stdout.write(
                f"Rotated {result.rotation} degrees: {result.output_path} "
                f"({result.width} x {result.height})"
            )
        return f"Completed {completed} rotation(s)."
