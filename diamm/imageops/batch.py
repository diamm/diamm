"""Read-only batch planning, shared by the CLI and future job submission code."""

import glob
import os
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .rotation import CONTAINERS, PathInput, RotationError, _path_text


@dataclass(frozen=True)
class RotationJob:
    input_path: Path
    output_path: Path
    rotation: int

    @property
    def in_place(self) -> bool:
        return self.input_path == self.output_path


def _select_images(selection: PathInput) -> tuple[tuple[Path, ...], bool]:
    text = os.path.expanduser(_path_text(selection))
    if not text:
        raise RotationError("input must not be empty")
    path = Path(text)
    if path.is_file():
        if path.is_symlink():
            raise RotationError("symbolic-link input is not supported")
        if path.suffix.lower() not in CONTAINERS:
            raise RotationError("input suffix must be .jp2, .jpx, or .jpf")
        return (path.resolve(),), False
    if path.is_dir():
        candidates = path.iterdir()
    elif glob.has_magic(text):
        candidates = (Path(name) for name in glob.iglob(text, recursive=True))
    else:
        raise RotationError(f"input file or directory does not exist: {path}")
    # Snapshot, resolve and deduplicate before any output can be created.
    images = tuple(
        sorted(
            {
                candidate.resolve()
                for candidate in candidates
                if candidate.is_file()
                and not candidate.is_symlink()
                and candidate.suffix.lower() in CONTAINERS
            }
        )
    )
    if not images:
        raise RotationError(f"no supported images found for: {text}")
    return images, True


def plan_rotations(
    selection: PathInput, rotation: int, output: PathInput | None = None
) -> tuple[RotationJob, ...]:
    """Resolve a file/directory/glob into jobs, without changing files.

    Directories select immediate image children; glob patterns use Python glob
    semantics, including recursive **. Symlink files and non-images in batches
    are skipped. A batch output is an existing directory; basenames are retained.
    Every destination is checked before returning any jobs.
    """
    if type(rotation) is not int or rotation not in (90, 180, 270):
        raise RotationError("rotation must be 90, 180, or 270 clockwise degrees")
    images, batch = _select_images(selection)
    destination = None
    if output is not None:
        output_text = _path_text(output)
        if not output_text:
            raise RotationError("output filename must not be empty")
        destination = Path(os.path.abspath(os.path.expanduser(output_text)))
        if batch:
            if not destination.is_dir():
                raise RotationError("batch output must be an existing directory")
            destination = destination.resolve()
        else:
            if not destination.parent.is_dir():
                raise RotationError("output directory does not exist")
            destination = destination.parent.resolve() / destination.name

    jobs: list[RotationJob] = []
    destinations: set[Path] = set()
    for source in images:
        if destination is None:
            target = source
        elif batch:
            target = destination / source.name
        else:
            target = destination
        if target.suffix.lower() not in CONTAINERS:
            raise RotationError("output suffix must be .jp2 or .jpx")
        if target in destinations:
            raise RotationError(f"multiple inputs map to the same output: {target}")
        if target != source and (target.exists() or target.is_symlink()):
            raise RotationError(f"output already exists: {target}")
        destinations.add(target)
        jobs.append(RotationJob(source, target, rotation))
    return tuple(jobs)


def format_plan(jobs: Sequence[RotationJob]) -> str:
    """Format a dry-run listing; no codec or metadata tools are invoked."""
    lines = [f"Dry run: {len(jobs)} image(s); no files will be changed."]
    for job in jobs:
        mode = "replace in place" if job.in_place else "new output"
        lines.append(
            f"{job.input_path} -> {job.output_path} "
            f"({job.rotation} degrees clockwise; {mode})"
        )
    return "\n".join(lines)
