from diamm.models.site.news_page import NewsPage
from django_jinja import library


@library.global_function
@library.render_with("website/blocks/latest_news.jinja2")
def latest_news():
    return {
        "news": NewsPage.objects.filter(live=True).order_by('-first_published_at')[:3]
    }
