from django_jinja import library
import markdown2
import jinja2


@library.filter
def markdown(content):
    return markdown2.markdown(content)
