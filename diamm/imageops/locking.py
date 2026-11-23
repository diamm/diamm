"""Stable advisory locks shared by the command and background workers (POSIX)."""

import fcntl
import hashlib
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from .rotation import RotationError


def path_key(path: Path) -> str:
    return hashlib.sha256(str(path.resolve()).encode()).hexdigest()


@contextmanager
def image_lock(path: Path) -> Iterator[Path]:
    # Never unlink a lock file: replacing/unlinking it permits two lock inodes.
    lock = path.parent / f".diamm-rotation-{path_key(path)}.lock"
    with lock.open("a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RotationError("Another process is rotating this file.") from error
        try:
            yield path
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)
