from collections import defaultdict
from django_jinja import library
from diamm.models.site.aboutpages import AboutPages


@library.global_function
def aboutpages_list():
    pages = AboutPages.objects.exclude(title="About").values_list('title', 'url', 'about_section__title').order_by('about_section__title', 'id').values()
    p = defaultdict(list)

    for d in pages:
        p[(d['about_section_id'])].append(d)

    return p
