from datetime import datetime, timedelta, timezone
from diamm.models.data.image import Image
from diamm.models.data.source import Source
from diamm.models.data.person import Person
from diamm.models.data.archive import Archive
from diamm.models.data.organization import Organization
from diamm.models.data.geographic_area import GeographicArea
from django_jinja import library


@library.global_function
@library.render_with("website/blocks/statistics.jinja2")
def statistics():
    now = datetime.now(timezone.utc)
    past_month = now - timedelta(days=30)

    num_images = Image.objects.filter(public=True, location__isnull=False).count()
    images_added_past_month = Image.objects.filter(created__gte=past_month).count()
    num_sources = Source.objects.count()
    sources_updated_past_month = Source.objects.filter(updated__gte=past_month).count()
    num_people = Person.objects.count()
    num_places = GeographicArea.objects.count()
    num_organizations = Organization.objects.count()
    num_archives = Archive.objects.count()

    return {
        "num_images": num_images,
        "images_added_past_month": images_added_past_month,
        "num_sources": num_sources,
        "sources_updated_past_month": sources_updated_past_month,
        "num_people": num_people,
        "num_places": num_places,
        "num_organizations": num_organizations,
        "num_archives": num_archives
    }

