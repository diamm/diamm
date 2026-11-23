"""One Django task per image; Ox owns status, results, errors and retries."""

from django.conf import settings
from django.tasks import task
from django.utils import timezone

from diamm.models import Image

from .jobs import image_path
from .locking import image_lock
from .rotation import RotationError, rotate_image


@task(queue_name="image_rotation")
def rotate_image_task(image_id: int, location: str, rotation: int) -> dict[str, str | int]:
    image = Image.objects.get(pk=image_id)
    if image.location != location:
        raise RotationError("Image location changed after queueing.")
    path = image_path(image)
    with image_lock(path):
        image.refresh_from_db()
        if image.location != location or image_path(image) != path:
            raise RotationError("Image location changed after queueing.")
        result = rotate_image(
            path, rotation, timeout=settings.IMAGE_ROTATION_TIMEOUT,
            max_pixels=settings.IMAGE_ROTATION_MAX_PIXELS,
        )
        updated = Image.objects.filter(pk=image_id, location=location).update(
            width=result.width, height=result.height, updated=timezone.now(),
        )
        if not updated:
            raise RotationError("File rotated, but the Image record changed. Check its dimensions.")
    return {
        "image_id": image_id, "location": location, "rotation": rotation,
        "width": result.width, "height": result.height,
        "message": f"Rotated {rotation}° ({result.width} × {result.height}).",
    }
