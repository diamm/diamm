from django_jinja import library


@library.global_function
def flatpage_delete(title, pages):
    new = pages.exclude(title=title)
    return new
