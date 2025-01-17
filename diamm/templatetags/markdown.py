import markdown2
from django_jinja import library


@library.filter
def markdown(content):
    return markdown2.markdown(content)
