"""Read-only preflight and submission of independent image-rotation tasks."""

from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.db.models import QuerySet

from diamm.models import Image

from .rotation import CONTAINERS, RotationError, check_rotation_access


@dataclass(frozen=True)
class RotationSelection:
    image: Image
    path: Path | None
    issue: str


@dataclass(frozen=True)
class QueuedRotation:
    image_id: int
    location: str
    task_id: str = ""
    status: str = "Not queued"
    message: str = ""


def image_path(image: Image) -> Path:
    if image.external:
        raise RotationError("External image; cannot rotate a local file.")
    if not image.location:
        raise RotationError("Missing image location.")
    if not settings.IMAGE_DIR:
        raise RotationError("IMAGE_DIR is not configured on this server.")
    root = Path(settings.IMAGE_DIR).resolve()
    location = Path(image.location)
    # Leading-slash IIIF identifiers remain relative to IMAGE_DIR unless they
    # already name an absolute filesystem path inside that directory.
    candidate = location if location.is_absolute() and location.is_relative_to(root) else root / image.location.lstrip("/")
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root):
        raise RotationError("Image path escapes IMAGE_DIR.")
    if candidate.is_symlink() or resolved != candidate.absolute():
        raise RotationError("Symbolic-link image paths are not supported.")
    if not resolved.is_file():
        raise RotationError("Missing image file on this server.")
    if resolved.suffix.lower() not in CONTAINERS:
        raise RotationError("Image filename must end in .jp2, .jpx, or .jpf.")
    return check_rotation_access(resolved)


def selection_for(image: Image) -> RotationSelection:
    try:
        path = image_path(image)
    except (RotationError, OSError) as error:
        return RotationSelection(image, None, str(error))
    return RotationSelection(image, path, "")


def enqueue_rotations(images: QuerySet[Image], rotation: int) -> list[QueuedRotation]:
    from .tasks import rotate_image_task

    if rotation not in (90, 180, 270):
        raise RotationError("Rotation must be 90, 180, or 270.")
    submitted: list[QueuedRotation] = []
    paths: set[Path] = set()
    with transaction.atomic():
        for image in images.order_by("pk"):
            selected = selection_for(image)
            issue = selected.issue
            if selected.path in paths:
                issue = "The same file is already included in this request."
            if issue:
                submitted.append(QueuedRotation(image.pk, image.location or "", message=issue))
                continue
            result = rotate_image_task.enqueue(image.pk, image.location, rotation)
            submitted.append(QueuedRotation(image.pk, image.location, result.id, "Waiting"))
            if selected.path:
                paths.add(selected.path)
    return submitted
