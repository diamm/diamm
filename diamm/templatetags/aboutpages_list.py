from django_jinja import library
from diamm.models.site.aboutpages import AboutPages


@library.global_function
def aboutpages_list():
    pages = []
    sublist = []
    for page in AboutPages.objects.all().exclude(title="About"):
        if page.about_section.__str__() == "About":
            pages.append(page)
        else:
            sublist.append(page)

    return pages, sublist


