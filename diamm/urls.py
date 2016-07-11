"""diamm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import (
    password_reset, password_reset_done, password_reset_confirm, password_reset_complete
)
from diamm.views.auth import (
    LoginView, LogoutView, CreateAccount, ActivateAccount
)
from diamm.views.home import HomeView
from diamm.views.user import ProfileView
from diamm.views.website.search import SearchView, SaveSearch
from diamm.views.contribution import MakeContribution
from diamm.views.website.set import SetDetail
from diamm.views.website.source import (
    SourceList, SourceDetail, SourceManifest, SourceCanvasDetail
)
from diamm.views.website.source import SourceRangeDetail, SourceItemDetail
from diamm.views.website.archive import ArchiveDetail
from diamm.views.website.city import CityList, CityDetail
from diamm.views.website.country import CountryList, CountryDetail
from diamm.views.website.person import PersonDetail, legacy_composer_redirect
from diamm.views.website.organization import OrganizationDetail
from diamm.views.website.composition import CompositionList, CompositionDetail
from diamm.views.website.story import StoryDetail
from diamm.views.website.aboutpages import AboutPagesDetail
from diamm.views.website.image import image_serve
from diamm.views.website.bibliography_author import BibliographyAuthorDetail


urlpatterns = [
    url(r'^search.xml$', TemplateView.as_view(template_name='opensearch.jinja2',
                                              content_type="application/opensearchdescription+xml"), name='opensearch'),
    url(r'^admin/', admin.site.urls),
    url(r'^$', HomeView.as_view(), name="home"),

    url(r'^beta/$', TemplateView.as_view(template_name="beta.jinja2"), name="beta"),
    url(r'^introduction/$', TemplateView.as_view(template_name="introduction.jinja2"), name="introduction"),

    # Authentication and account resets
    url(r'^login/$', LoginView.as_view(), name="login"),
    url(r'^logout/$', LogoutView.as_view(), name="logout"),
    url(r'^register/$', CreateAccount.as_view(), name="register"),
    url(r'^reset/$', password_reset,
        {'post_reset_redirect': '/reset/sent/',
         'template_name': 'website/auth/reset.jinja2',
         'from_email': settings.DEFAULT_FROM_EMAIL}, name="reset"),
    url(r'^reset/sent/$', password_reset_done,
        {"template_name": "website/auth/reset_sent.jinja2"}),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm,
        {'post_reset_redirect': '/reset/complete/',
         'template_name': "website/auth/reset_confirm.jinja2"}, name="password_reset_confirm"),
    url(r'^reset/complete/$', password_reset_complete,
        {'template_name': "website/auth/reset_complete.jinja2"}),

    url(r'^activate/(?P<uuid>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
        ActivateAccount.as_view(), name="activate"),
    url(r'^user/(?P<pk>[0-9]+)/$', ProfileView.as_view(), name="user-profile"),

    # public website
    url(r'^search/$', SearchView.as_view(), name="search"),
    url(r'^search/save$', SaveSearch.as_view(), name="search-save"),
    url(r'^news/(?P<pk>[0-9]+)/$', StoryDetail.as_view(), name="story-detail"),
    url(r'^contribution/$', MakeContribution.as_view(), name="contribution"),

    url(r'^sources/$', SourceList.as_view(), name="source-list"),
    url(r'^sources/(?P<pk>[0-9]+)/$', SourceDetail.as_view(), name="source-detail"),
    url(r'^sources/(?P<pk>[0-9]+)/manifest/$', SourceManifest.as_view(), name="source-manifest"),

    # IIIF URIs. These do not necessarily always resolve, but are configured in the URLs so that they can reflect
    #  the host and protocol of the request.
    url(r'^sources/(?P<source_id>[0-9]+)/canvas/(?P<page_id>[0-9]+)/$', SourceCanvasDetail.as_view(), name="source-canvas-detail"),
    url(r'^sources/(?P<source_id>[0-9]+)/range/(?P<item_id>[0-9]+)/$', SourceRangeDetail.as_view(), name="source-range-detail"),
    url(r'^sources/(?P<source_id>[0-9]+)/item/(?P<item_id>[0-9]+)/$', SourceItemDetail.as_view(), name="source-item-detail"),

    # url(r'^archives/$', ArchiveList.as_view(), name="archive-list"),
    url(r'^archives/(?P<pk>[0-9]+)/$', ArchiveDetail.as_view(), name="archive-detail"),
    url(r'^cities/$', CityList.as_view(), name="city-list"),
    url(r'^cities/(?P<pk>[0-9]+)/$', CityDetail.as_view(), name="city-detail"),
    url(r'^countries/$', CountryList.as_view(), name="country-list"),
    url(r'^countries/(?P<pk>[0-9]+)/$', CountryDetail.as_view(), name="country-detail"),
    # url(r'^people/$', PersonList.as_view(), name="person-list"),
    url(r'^people/(?P<pk>[0-9]+)/$', PersonDetail.as_view(), name="person-detail"),
    url(r'^organizations/(?P<pk>[0-9]+)/$', OrganizationDetail.as_view(), name="organization-detail"),
    url(r'^composers/(?P<legacy_id>[0-9]+)/$', legacy_composer_redirect),
    url(r'^compositions/$', CompositionList.as_view(), name="composition-list"),
    url(r'^compositions/(?P<pk>[0-9]+)/$', CompositionDetail.as_view(), name="composition-detail"),

    url(r'^set/(?P<pk>[0-9]+)/$', SetDetail.as_view(), name="set-detail"),

    url(r'^authors/(?P<pk>[0-9]+)/$', BibliographyAuthorDetail.as_view(), name="author-detail"),

    url(r'^images/(?P<pk>[0-9]+)/(?:(?P<region>.*)/(?P<size>.*)/(?P<rotation>.*)/default\.jpg)$', image_serve, name="image-serve"),
    url(r'^images/(?P<pk>[0-9]+)/$', image_serve, name="image-serve-info"),

    url(r'^(?P<url>.*)/$', AboutPagesDetail.as_view(), name="aboutpages-detail"),
]
if settings.DEBUG:
    urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)

