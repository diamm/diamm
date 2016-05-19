from django_jinja import library
from django.contrib.flatpages.models import FlatPage


@library.global_function
def flatpage_about():
    pages = FlatPage.objects.all().exclude(title="About")
    return pages


