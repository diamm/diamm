from django_jinja import library
import markdown2


@library.filter
def markdown(content):
    return markdown2.markdown(content)
